"""
Trade2025 Market Data Gateway Service
Ingests market data from exchanges and publishes to NATS/QuestDB/Valkey
"""

import asyncio
import json
import logging
import signal
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import ccxt.async_support as ccxt
import nats
import redis
import requests
import yaml
from cryptofeed import FeedHandler
from cryptofeed.callback import BookCallback, TradeCallback
from cryptofeed.defines import BID, ASK, TRADES, L2_BOOK
from cryptofeed.exchanges import Binance
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Global variables for connections
nc: Optional[nats.NATS] = None
redis_client: Optional[redis.Redis] = None
feed_handler: Optional[FeedHandler] = None
exchange: Optional[ccxt.Exchange] = None
config: Dict[str, Any] = {}
last_tick_time: Dict[str, float] = {}
tick_count = 0
error_count = 0


class HealthStatus(BaseModel):
    """Health check response model"""
    status: str
    services: Dict[str, str]
    tick_count: int
    error_count: int
    uptime: float


class MarketTick(BaseModel):
    """Normalized market tick data"""
    exchange: str
    symbol: str
    timestamp: int
    bid: float
    ask: float
    last: float
    volume: float


# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Market Gateway...")
    await startup()
    yield
    logger.info("Shutting down Market Gateway...")
    await shutdown()


app = FastAPI(title="Trade2025 Market Gateway", version="1.0.0", lifespan=lifespan)
startup_time = time.time()


def load_config(config_path: str = "/app/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {
            "exchange": "binance",
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "refresh_interval": 5,
            "nats_url": "nats://localhost:4222",
            "redis_host": "localhost",
            "redis_port": 6379,
            "questdb_url": "http://localhost:9000"
        }


async def connect_nats() -> nats.NATS:
    """Connect to NATS server with retry logic"""
    nats_url = config.get("nats_url", "nats://localhost:4222")
    max_retries = 5
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            nc = await asyncio.wait_for(
                nats.connect(
                    nats_url,
                    connect_timeout=10,
                    reconnect_time_wait=2,
                    max_reconnect_attempts=10
                ),
                timeout=15
            )
            logger.info(f"Connected to NATS at {nats_url} (attempt {attempt + 1})")
            return nc
        except (asyncio.TimeoutError, Exception) as e:
            if attempt < max_retries - 1:
                logger.warning(f"NATS connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"Failed to connect to NATS after {max_retries} attempts: {e}")
                raise


def connect_redis() -> redis.Redis:
    """Connect to Redis/Valkey"""
    try:
        client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            decode_responses=True
        )
        client.ping()
        logger.info(f"Connected to Valkey at {config.get('redis_host')}:{config.get('redis_port')}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Valkey: {e}")
        raise


def insert_to_questdb(tick: MarketTick):
    """Insert tick data into QuestDB using InfluxDB line protocol"""
    try:
        # Convert to InfluxDB line protocol format
        # Format: table_name,tag1=value1,tag2=value2 field1=value1,field2=value2 timestamp
        line = (
            f"ticks,exchange={tick.exchange},symbol={tick.symbol.replace('/', '')} "
            f"bid={tick.bid},ask={tick.ask},last={tick.last},volume={tick.volume} "
            f"{tick.timestamp}000000"  # Convert ms to ns
        )

        # Send to QuestDB ILP endpoint
        response = requests.post(
            f"{config.get('questdb_url', 'http://localhost:9000')}/write",
            params={"precision": "n"},
            data=line,
            timeout=1
        )

        if response.status_code != 204:
            logger.error(f"QuestDB insert failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Failed to insert to QuestDB: {e}")
        global error_count
        error_count += 1


async def publish_tick(tick: MarketTick):
    """Publish tick to NATS, QuestDB, and Valkey"""
    global tick_count, nc, redis_client

    try:
        # Publish to NATS
        if nc:
            subject = f"market.tick.{tick.symbol.replace('/', '')}"
            await nc.publish(subject, json.dumps(tick.dict()).encode())
            tick_count += 1

        # Insert into QuestDB
        insert_to_questdb(tick)

        # Cache in Valkey
        if redis_client:
            key = f"last:{tick.symbol.replace('/', '')}"
            redis_client.hset(key, mapping={
                "price": tick.last,
                "bid": tick.bid,
                "ask": tick.ask,
                "timestamp": tick.timestamp
            })
            redis_client.expire(key, 3600)  # Expire after 1 hour

        # Update last tick time
        last_tick_time[tick.symbol] = time.time()

    except Exception as e:
        logger.error(f"Failed to publish tick: {e}")
        global error_count
        error_count += 1


async def book_callback(data, receipt_timestamp):
    """Handle order book updates from CryptoFeed"""
    try:
        symbol = data.symbol

        # Get best bid/ask
        best_bid = float(data.book[BID].iloc[0]) if len(data.book[BID]) > 0 else 0.0
        best_ask = float(data.book[ASK].iloc[0]) if len(data.book[ASK]) > 0 else 0.0

        # Create normalized tick
        tick = MarketTick(
            exchange=data.exchange.lower(),
            symbol=symbol,
            timestamp=int(receipt_timestamp * 1000),
            bid=best_bid,
            ask=best_ask,
            last=(best_bid + best_ask) / 2,  # Mid price as last
            volume=0.0  # Order book doesn't have volume
        )

        await publish_tick(tick)

    except Exception as e:
        logger.error(f"Error in book callback: {e}")


async def trade_callback(data, receipt_timestamp):
    """Handle trade updates from CryptoFeed"""
    try:
        # Create normalized tick from trade
        tick = MarketTick(
            exchange=data.exchange.lower(),
            symbol=data.symbol,
            timestamp=int(receipt_timestamp * 1000),
            bid=float(data.price) - 0.01,  # Approximate bid
            ask=float(data.price) + 0.01,  # Approximate ask
            last=float(data.price),
            volume=float(data.amount)
        )

        await publish_tick(tick)

    except Exception as e:
        logger.error(f"Error in trade callback: {e}")


async def fetch_rest_data():
    """Fetch market data via REST API using CCXT"""
    global exchange

    while True:
        try:
            for symbol in config.get("symbols", ["BTC/USDT"]):
                try:
                    # Fetch ticker data
                    ticker = await exchange.fetch_ticker(symbol)

                    # Create normalized tick
                    tick = MarketTick(
                        exchange=config.get("exchange", "binance"),
                        symbol=symbol,
                        timestamp=ticker.get("timestamp", int(time.time() * 1000)),
                        bid=ticker.get("bid", 0.0),
                        ask=ticker.get("ask", 0.0),
                        last=ticker.get("last", 0.0),
                        volume=ticker.get("baseVolume", 0.0)
                    )

                    await publish_tick(tick)

                except Exception as e:
                    logger.error(f"Failed to fetch {symbol}: {e}")

                await asyncio.sleep(1)  # Small delay between symbols

            # Wait for refresh interval
            await asyncio.sleep(config.get("refresh_interval", 5))

        except Exception as e:
            logger.error(f"Error in REST fetch loop: {e}")
            await asyncio.sleep(5)


def setup_websocket_feeds():
    """Setup CryptoFeed WebSocket connections"""
    global feed_handler

    # Configure feedhandler with writable log directory
    feed_config = {
        'log': {
            'filename': '/app/logs/feedhandler.log',
            'level': 'INFO'
        }
    }
    feed_handler = FeedHandler(config=feed_config)

    # Convert symbols to CryptoFeed format
    symbols = []
    for symbol in config.get("symbols", ["BTC/USDT"]):
        # CryptoFeed uses - instead of /
        cf_symbol = symbol.replace("/", "-")
        symbols.append(cf_symbol)

    # Add Binance feed
    feed_handler.add_feed(
        Binance(
            channels=[L2_BOOK, TRADES],
            symbols=symbols,
            callbacks={
                L2_BOOK: BookCallback(book_callback),
                TRADES: TradeCallback(trade_callback)
            }
        )
    )

    logger.info(f"WebSocket feeds configured for symbols: {symbols}")


async def startup():
    """Initialize all connections and services"""
    global nc, redis_client, exchange, config

    # Load configuration
    config = load_config()
    logger.info(f"Loaded configuration: {config}")

    # Connect to services
    nc = await connect_nats()
    redis_client = connect_redis()

    # Initialize CCXT exchange
    exchange_name = config.get("exchange", "binance")
    if exchange_name == "binance":
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
    else:
        raise ValueError(f"Unsupported exchange: {exchange_name}")

    logger.info(f"Initialized {exchange_name} exchange")

    # Setup WebSocket feeds
    setup_websocket_feeds()

    # Start WebSocket handler in background
    if feed_handler:
        asyncio.create_task(asyncio.to_thread(feed_handler.run))
        logger.info("WebSocket feeds started")

    # Start REST data fetcher
    asyncio.create_task(fetch_rest_data())
    logger.info("REST data fetcher started")


async def shutdown():
    """Cleanup connections on shutdown"""
    global nc, redis_client, exchange, feed_handler

    logger.info("Shutting down connections...")

    if feed_handler:
        feed_handler.stop()

    if exchange:
        await exchange.close()

    if nc:
        await nc.close()

    if redis_client:
        redis_client.close()

    logger.info("All connections closed")


# API Endpoints

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    global nc, redis_client

    services = {}

    # Check NATS
    if nc and nc.is_connected:
        services["nats"] = "healthy"
    else:
        services["nats"] = "unhealthy"

    # Check Valkey
    try:
        if redis_client:
            redis_client.ping()
            services["valkey"] = "healthy"
        else:
            services["valkey"] = "unhealthy"
    except:
        services["valkey"] = "unhealthy"

    # Check QuestDB
    try:
        response = requests.get(f"{config.get('questdb_url', 'http://localhost:9000')}/", timeout=1)
        if response.status_code == 200:
            services["questdb"] = "healthy"
        else:
            services["questdb"] = "unhealthy"
    except:
        services["questdb"] = "unhealthy"

    # Overall status
    all_healthy = all(s == "healthy" for s in services.values())

    return HealthStatus(
        status="ok" if all_healthy else "degraded",
        services=services,
        tick_count=tick_count,
        error_count=error_count,
        uptime=time.time() - startup_time
    )


@app.get("/stats")
async def get_stats():
    """Get gateway statistics"""
    return {
        "tick_count": tick_count,
        "error_count": error_count,
        "uptime": time.time() - startup_time,
        "last_ticks": last_tick_time,
        "config": {
            "exchange": config.get("exchange"),
            "symbols": config.get("symbols"),
            "refresh_interval": config.get("refresh_interval")
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Trade2025 Market Gateway",
        "version": "1.0.0",
        "status": "running"
    }


# Signal handlers for graceful shutdown
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, shutting down...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)