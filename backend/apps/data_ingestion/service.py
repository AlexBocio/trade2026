"""
Data Ingestion Service - Phase 6
FastAPI service that manages data adapters (IBKR, FRED, Crypto, ETF)

Responsibilities:
1. Load configuration
2. Initialize adapters (IBKR, FRED, Crypto, ETF, Breadth)
3. Provide HTTP API for health checks and status
4. Publish status updates to NATS
5. Graceful shutdown handling
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Optional

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Import adapters
from adapters.ibkr_adapter import create_ibkr_adapter, IBKRAdapter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataIngestionService:
    """
    Main service orchestrator for data ingestion

    Manages lifecycle of all data adapters:
    - IBKR Adapter (Level 1, Level 2, Time & Sales)
    - FRED Adapter (economic indicators) - TODO Week 1 Day 3
    - Crypto Adapter (Binance, Fear & Greed) - TODO Week 1 Day 4
    - ETF Adapter (sector/benchmark tracking) - TODO Week 1 Day 5
    - Breadth Calculator (A-D ratio, new H-L) - TODO Week 1 Day 6
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config: Optional[Dict] = None
        self.running = False

        # Adapters
        self.ibkr_adapter: Optional[IBKRAdapter] = None
        # TODO: Add other adapters as they're implemented
        # self.fred_adapter = None
        # self.crypto_adapter = None
        # self.etf_adapter = None
        # self.breadth_calculator = None

        # FastAPI app
        self.app = FastAPI(
            title="Data Ingestion Service",
            description="Phase 6 - External data augmentation for ML trading",
            version="1.0.0"
        )
        self._setup_routes()

    def _setup_routes(self):
        """Setup HTTP API routes"""

        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            if not self.running:
                raise HTTPException(status_code=503, detail="Service not running")

            # Check adapter health
            ibkr_healthy = self.ibkr_adapter.is_healthy() if self.ibkr_adapter else False

            overall_healthy = ibkr_healthy  # Add more adapters as implemented

            if not overall_healthy:
                raise HTTPException(status_code=503, detail="One or more adapters unhealthy")

            return {
                "status": "healthy",
                "service": "data-ingestion",
                "version": "1.0.0"
            }

        @self.app.get("/status")
        async def status():
            """Detailed status endpoint"""
            ibkr_status = self.ibkr_adapter.get_status() if self.ibkr_adapter else {"error": "not initialized"}

            return {
                "service": "data-ingestion",
                "version": "1.0.0",
                "running": self.running,
                "adapters": {
                    "ibkr": ibkr_status,
                    # Add other adapters as they're implemented
                    # "fred": self.fred_adapter.get_status() if self.fred_adapter else {"error": "not implemented"},
                    # "crypto": self.crypto_adapter.get_status() if self.crypto_adapter else {"error": "not implemented"},
                }
            }

        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "service": "data-ingestion",
                "version": "1.0.0",
                "endpoints": [
                    "/health",
                    "/status",
                    "/docs"
                ]
            }

    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    async def start(self):
        """Start the service and all adapters"""
        logger.info("Starting Data Ingestion Service...")

        # Load configuration
        self.load_config()

        # Get symbols from config
        symbols = (
            self.config.get("ibkr", {}).get("sector_etfs", []) +
            self.config.get("ibkr", {}).get("benchmark_etfs", [])
        )

        if not symbols:
            logger.warning("No symbols configured, using defaults")
            symbols = ["SPY", "QQQ", "IWM"]

        logger.info(f"Subscribing to {len(symbols)} symbols: {symbols}")

        # Initialize IBKR Adapter
        try:
            ibkr_config = {
                "host": self.config["ibkr"]["host"],
                "port": self.config["ibkr"]["port"],
                "client_id": self.config["ibkr"]["client_id"],
                "reconnect_delay_seconds": self.config["ibkr"].get("reconnect_delay_seconds", 5),
                "max_reconnect_attempts": self.config["ibkr"].get("max_reconnect_attempts", 5)
            }

            store_config = {
                "questdb_ilp_host": self.config["stores"]["questdb"]["ilp_host"],
                "questdb_ilp_port": self.config["stores"]["questdb"]["ilp_port"],
                "valkey_host": self.config["stores"]["valkey"]["host"],
                "valkey_port": self.config["stores"]["valkey"]["port"],
                "valkey_ttl_seconds": self.config["stores"]["valkey"].get("ttl_seconds", 300)
            }

            self.ibkr_adapter = create_ibkr_adapter(
                ibkr_config,
                store_config,
                symbols,
                logger
            )

            await self.ibkr_adapter.start()
            logger.info("IBKR Adapter started successfully")

        except Exception as e:
            logger.error(f"Failed to start IBKR Adapter: {e}")
            raise

        # TODO: Initialize other adapters
        # await self.fred_adapter.start()
        # await self.crypto_adapter.start()
        # await self.etf_adapter.start()

        self.running = True
        logger.info("Data Ingestion Service started successfully")

    async def stop(self):
        """Stop the service and all adapters"""
        logger.info("Stopping Data Ingestion Service...")

        self.running = False

        # Stop IBKR Adapter
        if self.ibkr_adapter:
            try:
                await self.ibkr_adapter.stop()
                logger.info("IBKR Adapter stopped")
            except Exception as e:
                logger.error(f"Error stopping IBKR Adapter: {e}")

        # TODO: Stop other adapters
        # await self.fred_adapter.stop()
        # await self.crypto_adapter.stop()

        logger.info("Data Ingestion Service stopped")

    async def run_forever(self):
        """Keep service running"""
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Service run loop cancelled")


# Global service instance
service: Optional[DataIngestionService] = None


async def lifespan_startup():
    """Startup event handler"""
    global service
    service = DataIngestionService()
    await service.start()


async def lifespan_shutdown():
    """Shutdown event handler"""
    global service
    if service:
        await service.stop()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    if service:
        asyncio.create_task(service.stop())
    sys.exit(0)


def main():
    """Main entry point"""
    global service

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create service
    service = DataIngestionService()

    # Create event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Start service
        loop.run_until_complete(service.start())

        # Get configuration
        host = service.config["service"]["host"]
        port = service.config["service"]["port"]

        logger.info(f"Starting HTTP server on {host}:{port}")

        # Run FastAPI server with uvicorn
        config = uvicorn.Config(
            service.app,
            host=host,
            port=port,
            log_level="info",
            loop="asyncio"
        )
        server = uvicorn.Server(config)

        # Run server
        loop.run_until_complete(server.serve())

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Service error: {e}", exc_info=True)
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        if service:
            loop.run_until_complete(service.stop())
        loop.close()


if __name__ == "__main__":
    main()
