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
from typing import Dict, Optional, Union

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Import adapters
from adapters.ibkr_adapter import create_ibkr_adapter, IBKRAdapter
from adapters.alpaca_adapter import create_alpaca_adapter, AlpacaAdapter
from adapters.fred_adapter import create_fred_adapter, FREDAdapter


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
    - Market Data: IBKR (requires subscriptions) or Alpaca (FREE)
    - FRED Adapter (economic indicators)
    - Crypto Adapter (Binance, Fear & Greed) - TODO
    - ETF Adapter (sector/benchmark tracking) - TODO
    - Breadth Calculator (A-D ratio, new H-L) - TODO
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config: Optional[Dict] = None
        self.running = False

        # Adapters
        self.market_data_adapter: Optional[Union[IBKRAdapter, AlpacaAdapter]] = None  # Either IBKR or Alpaca
        self.ibkr_adapter: Optional[IBKRAdapter] = None  # Legacy reference (deprecated)
        self.alpaca_adapter: Optional[AlpacaAdapter] = None  # Legacy reference (deprecated)
        self.fred_adapter: Optional[FREDAdapter] = None
        # TODO: Add other adapters as they're implemented
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
            market_data_healthy = self.market_data_adapter.is_healthy() if self.market_data_adapter else False
            fred_healthy = self.fred_adapter.is_healthy() if self.fred_adapter else False

            overall_healthy = market_data_healthy and fred_healthy

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
            market_data_status = self.market_data_adapter.get_status() if self.market_data_adapter else {"error": "not initialized"}
            fred_status = self.fred_adapter.get_status() if self.fred_adapter else {"error": "not initialized"}

            # Determine which market data source is being used
            market_data_source = self.config.get("market_data_source", "unknown") if self.config else "unknown"

            return {
                "service": "data-ingestion",
                "version": "1.0.0",
                "running": self.running,
                "market_data_source": market_data_source,
                "adapters": {
                    "market_data": market_data_status,
                    "fred": fred_status,
                    # Add other adapters as they're implemented
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
                    "/api/market-data",
                    "/api/economic-indicators",
                    "/docs"
                ]
            }

        @self.app.get("/api/market-data")
        async def get_market_data():
            """Get latest market data from Valkey cache"""
            if not self.market_data_adapter or not self.market_data_adapter.valkey_client:
                raise HTTPException(status_code=503, detail="Market data adapter not ready")

            try:
                # Get all market:l1:* keys from Valkey (async client)
                keys = await self.market_data_adapter.valkey_client.keys("market:l1:*")

                if not keys:
                    return []

                # Fetch all values
                import json
                market_data = []
                for key in keys:
                    data_str = await self.market_data_adapter.valkey_client.get(key)
                    if data_str:
                        data = json.loads(data_str)
                        market_data.append(data)

                return market_data

            except Exception as e:
                logger.error(f"Failed to fetch market data: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/economic-indicators")
        async def get_economic_indicators():
            """Get latest FRED economic indicators from Valkey cache"""
            if not self.fred_adapter or not self.fred_adapter.valkey_client:
                raise HTTPException(status_code=503, detail="FRED adapter not ready")

            try:
                # Get all fred:* keys from Valkey (async client)
                keys = await self.fred_adapter.valkey_client.keys("fred:*")

                if not keys:
                    return []

                # Fetch all values
                import json
                indicators = []
                for key in keys:
                    data_str = await self.fred_adapter.valkey_client.get(key)
                    if data_str:
                        data = json.loads(data_str)
                        indicators.append(data)

                return indicators

            except Exception as e:
                logger.error(f"Failed to fetch economic indicators: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/bars")
        async def get_bars(
            symbol: str,
            timeframe: str = "5m",
            lookback: str = "7d"
        ):
            """
            Get OHLCV bars aggregated from tick data using QuestDB SAMPLE BY

            Args:
                symbol: Stock symbol (e.g., SPY, QQQ)
                timeframe: Bar timeframe - 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M (default: 5m)
                lookback: How far back to query - 1h, 6h, 1d, 7d, 30d, 90d, 1y, 3y (default: 7d)

            Returns:
                List of OHLCV bars: [{"timestamp": ..., "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...}]

            Example:
                GET /api/bars?symbol=SPY&timeframe=5m&lookback=1d
            """
            import httpx

            # Validate timeframe
            valid_timeframes = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                               "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w", "1M": "1M"}
            if timeframe not in valid_timeframes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes.keys())}"
                )

            # Validate lookback
            valid_lookbacks = {"1h": "1h", "6h": "6h", "1d": "1d", "7d": "7d", "30d": "30d", "90d": "90d", "1y": "1y", "3y": "3y"}
            if lookback not in valid_lookbacks:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid lookback. Must be one of: {', '.join(valid_lookbacks.keys())}"
                )

            try:
                # Build QuestDB SAMPLE BY query
                # Convert lookback to QuestDB dateadd format
                lookback_map = {
                    "1h": ("'h'", 1),
                    "6h": ("'h'", 6),
                    "1d": ("'d'", 1),
                    "7d": ("'d'", 7),
                    "30d": ("'d'", 30),
                    "90d": ("'d'", 90),
                    "1y": ("'y'", 1),
                    "3y": ("'y'", 3)
                }
                period_type, period_count = lookback_map[lookback]

                query = f"""
                SELECT
                    timestamp,
                    first(last) as open,
                    max(last) as high,
                    min(last) as low,
                    last(last) as close,
                    sum(bid_size + ask_size) as volume
                FROM market_data_l1
                WHERE symbol = '{symbol}'
                    AND timestamp > dateadd({period_type}, -{period_count}, now())
                SAMPLE BY {timeframe} ALIGN TO CALENDAR
                """

                # Query QuestDB
                questdb_url = self.config["stores"]["questdb"]["url"]
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{questdb_url}/exec",
                        params={"query": query}
                    )
                    response.raise_for_status()
                    result = response.json()

                # Transform QuestDB response to OHLCV format
                if "dataset" not in result or not result["dataset"]:
                    return []

                bars = []
                for row in result["dataset"]:
                    bars.append({
                        "timestamp": row[0],
                        "open": float(row[1]) if row[1] is not None else None,
                        "high": float(row[2]) if row[2] is not None else None,
                        "low": float(row[3]) if row[3] is not None else None,
                        "close": float(row[4]) if row[4] is not None else None,
                        "volume": int(row[5]) if row[5] is not None else 0
                    })

                return bars

            except httpx.HTTPStatusError as e:
                logger.error(f"QuestDB query failed: {e.response.text}")
                raise HTTPException(status_code=500, detail=f"QuestDB error: {e.response.text}")
            except Exception as e:
                logger.error(f"Failed to fetch bars: {e}")
                raise HTTPException(status_code=500, detail=str(e))

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

        # Get symbols from config (all tiers for sector rotation analysis)
        symbols_config = self.config.get("symbols", {})
        symbols = (
            symbols_config.get("sector_etfs", []) +           # Tier 1: Core sectors
            symbols_config.get("benchmark_etfs", []) +         # Benchmarks
            symbols_config.get("subsector_etfs", []) +         # Tier 2: Sub-sectors
            symbols_config.get("thematic_etfs", []) +          # Tier 3: Thematic
            symbols_config.get("commodity_etfs", []) +         # Tier 4: Commodities
            symbols_config.get("niche_thematic_etfs", [])      # Tier 5: Niche & Thematic
        )

        if not symbols:
            logger.warning("No symbols configured, using defaults")
            symbols = ["SPY", "QQQ", "IWM"]

        logger.info(f"Subscribing to {len(symbols)} symbols across all tiers")
        logger.info(f"Tier 1 (Core Sectors): {len(symbols_config.get('sector_etfs', []))} symbols")
        logger.info(f"Tier 1 (Benchmarks): {len(symbols_config.get('benchmark_etfs', []))} symbols")
        logger.info(f"Tier 2 (Sub-Sectors): {len(symbols_config.get('subsector_etfs', []))} symbols")
        logger.info(f"Tier 3 (Thematic): {len(symbols_config.get('thematic_etfs', []))} symbols")
        logger.info(f"Tier 4 (Commodities): {len(symbols_config.get('commodity_etfs', []))} symbols")
        logger.info(f"Tier 5 (Niche & Thematic): {len(symbols_config.get('niche_thematic_etfs', []))} symbols")

        # Determine which market data source to use
        market_data_source = self.config.get("market_data_source", "alpaca")
        logger.info(f"Market data source: {market_data_source}")

        # Store configuration (shared by both adapters)
        store_config = {
            "questdb_http_host": self.config["stores"]["questdb"]["ilp_host"],
            "questdb_http_port": 9000,  # HTTP endpoint
            "valkey_host": self.config["stores"]["valkey"]["host"],
            "valkey_port": self.config["stores"]["valkey"]["port"],
            "valkey_ttl_seconds": self.config["stores"]["valkey"].get("ttl_seconds", 300)
        }

        # Initialize Market Data Adapter (IBKR or Alpaca)
        try:
            if market_data_source == "alpaca":
                # Initialize Alpaca Adapter
                alpaca_config = self.config.get("alpaca", {})

                self.market_data_adapter = create_alpaca_adapter(
                    alpaca_config,
                    store_config,
                    symbols,
                    logger
                )
                self.alpaca_adapter = self.market_data_adapter  # Legacy reference

                await self.market_data_adapter.start()
                logger.info("Alpaca Adapter started successfully")

            elif market_data_source == "ibkr":
                # Initialize IBKR Adapter
                ibkr_config = {
                    "host": self.config["ibkr"]["host"],
                    "port": self.config["ibkr"]["port"],
                    "client_id": self.config["ibkr"]["client_id"],
                    "reconnect_delay_seconds": self.config["ibkr"].get("reconnect_delay_seconds", 5),
                    "max_reconnect_attempts": self.config["ibkr"].get("max_reconnect_attempts", 5)
                }

                self.market_data_adapter = create_ibkr_adapter(
                    ibkr_config,
                    store_config,
                    symbols,
                    logger
                )
                self.ibkr_adapter = self.market_data_adapter  # Legacy reference

                await self.market_data_adapter.start()
                logger.info("IBKR Adapter started successfully")

            else:
                raise ValueError(f"Invalid market_data_source: {market_data_source}. Must be 'alpaca' or 'ibkr'")

        except Exception as e:
            logger.error(f"Failed to start market data adapter ({market_data_source}): {e}")
            raise

        # Initialize FRED Adapter
        try:
            fred_config = self.config.get("fred", {})

            self.fred_adapter = create_fred_adapter(
                fred_config,
                store_config,
                logger
            )

            await self.fred_adapter.start()
            logger.info("FRED Adapter started successfully")

        except Exception as e:
            logger.error(f"Failed to start FRED Adapter: {e}")
            raise

        # TODO: Initialize other adapters
        # await self.crypto_adapter.start()
        # await self.etf_adapter.start()

        self.running = True
        logger.info("Data Ingestion Service started successfully")

    async def stop(self):
        """Stop the service and all adapters"""
        logger.info("Stopping Data Ingestion Service...")

        self.running = False

        # Stop Market Data Adapter (IBKR or Alpaca)
        if self.market_data_adapter:
            try:
                await self.market_data_adapter.stop()
                logger.info("Market Data Adapter stopped")
            except Exception as e:
                logger.error(f"Error stopping Market Data Adapter: {e}")

        # Stop FRED Adapter
        if self.fred_adapter:
            try:
                await self.fred_adapter.stop()
                logger.info("FRED Adapter stopped")
            except Exception as e:
                logger.error(f"Error stopping FRED Adapter: {e}")

        # TODO: Stop other adapters
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
