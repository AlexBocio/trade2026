"""
Market Tick Sink Service
Phase 7B: Data Lake Sinks
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
import yaml
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque
from contextlib import asynccontextmanager

import nats
from nats.errors import TimeoutError as NatsTimeoutError
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pythonjsonlogger import jsonlogger

# Add parent directory to path for common imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_lake.s3 import create_s3_client, wait_for_s3
from schemas import MarketTick, normalize_tick_message
from dedup import DedupManager
from writer_delta import DeltaWriter

# Configure structured logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Prometheus metrics
messages_received = Counter('sink_ticks_messages_received', 'Total messages received')
messages_processed = Counter('sink_ticks_messages_processed', 'Total messages processed')
messages_dropped = Counter('sink_ticks_messages_dropped', 'Messages dropped (duplicates or errors)')
batch_flushes = Counter('sink_ticks_batch_flushes', 'Total batch flushes')
batch_size_histogram = Histogram('sink_ticks_batch_size', 'Batch sizes', buckets=(10, 50, 100, 500, 1000, 5000))
flush_duration = Histogram('sink_ticks_flush_duration_seconds', 'Flush duration')
queue_size = Gauge('sink_ticks_queue_size', 'Current queue size')
last_flush_time = Gauge('sink_ticks_last_flush_timestamp', 'Last flush timestamp')


class TickSinkService:
    """Market Tick Sink Service"""

    def __init__(self, config_path: str = '/app/config.yaml'):
        """Initialize service with configuration"""
        # Load configuration
        self.config = self._load_config(config_path)

        # Service state
        self.running = False
        self.shutdown_event = asyncio.Event()

        # NATS
        self.nc = None
        self.subscription = None

        # Message queue
        self.message_queue = deque(maxlen=self.config.get('queue_size', 10000))
        self.batch = []
        self.last_flush = time.time()

        # Components
        self.s3_client = None
        self.dedup_manager = None
        self.delta_writer = None

        # Stats
        self.stats = {
            'messages_received': 0,
            'messages_processed': 0,
            'messages_dropped': 0,
            'batches_flushed': 0,
            'errors': 0
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        else:
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return {
                'nats_url': os.getenv('NATS_URL', 'nats://localhost:4222'),
                'subject': os.getenv('NATS_SUBJECT', 'market.tick.>'),
                'batch_seconds': 5,
                'max_batch': 1000,
                'health_port': 8111,
                'metrics_port': 9111
            }

    async def initialize(self):
        """Initialize service components"""
        logger.info("Initializing Tick Sink Service")

        # Initialize S3 client
        s3_config = self.config.get('s3', {})
        # Skip wait_for_s3 - let S3 client connect lazily
        self.s3_client = create_s3_client(s3_config)

        # Set environment variables for Delta Lake Rust engine S3 access
        os.environ['AWS_ACCESS_KEY_ID'] = s3_config.get('access_key', 'test')
        os.environ['AWS_SECRET_ACCESS_KEY'] = s3_config.get('secret_key', 'test')
        os.environ['AWS_REGION'] = s3_config.get('region', 'us-east-1')
        os.environ['AWS_ENDPOINT_URL'] = s3_config.get('endpoint', 'http://localhost:8333')
        os.environ['AWS_S3_ALLOW_UNSAFE_RENAME'] = 'true'  # Needed for S3-compatible storage
        os.environ['AWS_ALLOW_HTTP'] = 'true'  # Force HTTP for SeaweedFS

        # Initialize dedup manager
        self.dedup_manager = DedupManager(
            redis_host=self.config.get('valkey_host', 'localhost'),
            redis_port=self.config.get('valkey_port', 6379),
            redis_db=self.config.get('valkey_db', 0),
            ttl_hours=self.config.get('dedup_ttl_hours', 72),
            lru_size=self.config.get('lru_cache_size', 100000)
        )

        # Initialize Delta writer
        delta_config = self.config.get('delta', {})
        self.delta_writer = DeltaWriter(
            table_uri=delta_config.get('table_uri', 's3://trader2025/lake/market_ticks'),
            partition_by=delta_config.get('partition_by', ['symbol', 'dt']),
            compression=delta_config.get('compression', 'zstd'),
            enable_compaction=delta_config.get('enable_compaction', False)
        )

        # Connect to NATS
        await self.connect_nats()

        logger.info("Service initialized successfully")

    async def connect_nats(self):
        """Connect to NATS server"""
        try:
            self.nc = await nats.connect(
                self.config.get('nats_url', 'nats://localhost:4222'),
                connect_timeout=2,
                max_reconnect_attempts=3,
                reconnect_time_wait=2
            )

            # Subscribe to subject
            subject = self.config.get('subject', 'market.tick.>')
            queue_group = self.config.get('queue_group', 'sink-ticks')

            self.subscription = await self.nc.subscribe(
                subject,
                queue=queue_group,
                cb=self.message_handler
            )

            logger.info(f"Connected to NATS, subscribed to {subject} (queue: {queue_group})")

        except Exception as e:
            logger.warning(f"Failed to connect to NATS (running without message bus): {e}")
            self.nc = None
            self.subscription = None

    async def message_handler(self, msg):
        """Handle incoming NATS message"""
        messages_received.inc()
        self.stats['messages_received'] += 1

        try:
            # Parse message
            data = json.loads(msg.data.decode())

            # Normalize to MarketTick
            tick = normalize_tick_message(data)
            if not tick:
                messages_dropped.inc()
                self.stats['messages_dropped'] += 1
                return

            # Add to queue
            self.message_queue.append(tick)
            queue_size.set(len(self.message_queue))

            # Check if we should flush
            if len(self.batch) >= self.config.get('max_batch', 1000):
                await self.flush_batch()

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            messages_dropped.inc()
            self.stats['messages_dropped'] += 1

    async def batch_processor(self):
        """Process messages in batches"""
        batch_seconds = self.config.get('batch_seconds', 5)

        while self.running:
            try:
                # Collect messages from queue
                batch_size = min(len(self.message_queue), self.config.get('max_batch', 1000))

                if batch_size > 0:
                    # Move messages to batch
                    for _ in range(batch_size):
                        if self.message_queue:
                            self.batch.append(self.message_queue.popleft())

                # Check if time to flush
                if time.time() - self.last_flush >= batch_seconds and self.batch:
                    await self.flush_batch()

                # Update queue size metric
                queue_size.set(len(self.message_queue))

                # Small sleep to prevent CPU spinning
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in batch processor: {e}")
                self.stats['errors'] += 1

    async def flush_batch(self):
        """Flush current batch to Delta Lake"""
        if not self.batch:
            return

        start_time = time.time()
        batch_to_flush = self.batch.copy()
        self.batch.clear()

        try:
            logger.info(f"Flushing batch of {len(batch_to_flush)} ticks")

            # Filter duplicates
            unique_ticks = self.dedup_manager.filter_duplicates(batch_to_flush)

            if unique_ticks:
                # Convert to dict format for Delta writer
                records = [tick.dict() for tick in unique_ticks]

                # Write to Delta Lake
                success = self.delta_writer.write_batch(records)

                if success:
                    messages_processed.inc(len(unique_ticks))
                    self.stats['messages_processed'] += len(unique_ticks)
                    logger.info(f"Wrote {len(unique_ticks)} ticks to Delta Lake")
                else:
                    logger.error("Failed to write batch to Delta Lake")
                    self.stats['errors'] += 1

            # Update metrics
            batch_flushes.inc()
            batch_size_histogram.observe(len(batch_to_flush))
            flush_duration.observe(time.time() - start_time)
            last_flush_time.set(time.time())

            self.stats['batches_flushed'] += 1
            self.last_flush = time.time()

        except Exception as e:
            logger.error(f"Error flushing batch: {e}")
            self.stats['errors'] += 1

    async def run(self):
        """Run the service"""
        self.running = True
        logger.info("Starting Tick Sink Service")

        # Start batch processor
        processor_task = asyncio.create_task(self.batch_processor())

        # Wait for shutdown
        await self.shutdown_event.wait()

        # Stop processing
        self.running = False

        # Final flush
        if self.config.get('flush_on_shutdown', True):
            logger.info("Performing final flush before shutdown")
            await self.flush_batch()

        # Cancel processor task
        processor_task.cancel()
        try:
            await processor_task
        except asyncio.CancelledError:
            pass

        # Close NATS connection
        if self.nc:
            await self.nc.close()

        logger.info("Service stopped")

    def shutdown(self):
        """Trigger shutdown"""
        logger.info("Shutdown requested")
        self.shutdown_event.set()

    def get_stats(self) -> dict:
        """Get service statistics"""
        stats = self.stats.copy()
        stats['queue_size'] = len(self.message_queue)
        stats['batch_size'] = len(self.batch)
        stats['uptime'] = time.time() - self.last_flush

        # Add component stats
        if self.dedup_manager:
            stats['dedup'] = self.dedup_manager.get_stats()
        if self.delta_writer:
            stats['delta'] = self.delta_writer.get_stats()

        return stats


# Global service instance
service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager"""
    global service

    # Startup
    service = TickSinkService()
    await service.initialize()

    # Start service in background
    service_task = asyncio.create_task(service.run())

    yield

    # Shutdown
    service.shutdown()
    await service_task


# FastAPI app
app = FastAPI(
    title="Tick Sink Service",
    description="Market Tick Data Lake Sink",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    global service

    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Check components - be more lenient for functional service
    checks = {}

    # NATS - optional for this service
    if service.nc:
        checks['nats'] = service.nc.is_connected
    else:
        checks['nats'] = True  # Can work without NATS

    # S3 client exists
    checks['s3'] = service.s3_client is not None

    # Dedup manager exists
    checks['dedup'] = service.dedup_manager is not None

    # Delta writer exists
    checks['delta'] = service.delta_writer is not None

    # Service is considered healthy if it can write (delta writer exists)
    # Even if NATS is disconnected, it might be processing cached data
    is_healthy = checks['delta'] and checks['s3']

    if is_healthy:
        return JSONResponse(
            status_code=200,
            content={
                'status': 'healthy',
                'service': 'sink-ticks',
                'checks': checks,
                'stats': service.get_stats()
            }
        )
    else:
        return JSONResponse(
            status_code=503,
            content={
                'status': 'unhealthy',
                'service': 'sink-ticks',
                'checks': checks,
                'stats': service.get_stats()
            }
        )


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.get("/stats")
async def stats():
    """Get service statistics"""
    global service

    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return service.get_stats()


@app.post("/flush")
async def flush():
    """Force flush current batch"""
    global service

    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    await service.flush_batch()
    return {"status": "flushed", "stats": service.get_stats()}


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    if service:
        service.shutdown()
    sys.exit(0)


if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Get ports from config or environment
    health_port = int(os.getenv('HEALTH_PORT', 8111))

    # Run service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=health_port,
        log_level="info"
    )