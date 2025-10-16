"""
Data Normalizer Service - Phase 3
Subscribes to raw tick data from NATS and produces normalized OHLCV bars
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import httpx
import redis
import nats
from nats.js import JetStreamContext
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OHLCV:
    """OHLCV bar data structure"""
    exchange: str
    symbol: str
    interval: str  # 1m, 5m, 15m, 1h, 1d
    timestamp: int  # milliseconds
    open: float
    high: float
    low: float
    close: float
    volume: float
    trades: int = 0

    def to_questdb_line(self) -> str:
        """Convert to QuestDB line protocol"""
        return (
            f"ohlcv,exchange={self.exchange},symbol={self.symbol},interval={self.interval} "
            f"open={self.open},high={self.high},low={self.low},close={self.close},"
            f"volume={self.volume},trades={self.trades} {self.timestamp}000000"
        )

class TickAggregator:
    """Aggregates ticks into OHLCV bars"""

    def __init__(self):
        self.bars: Dict[str, Dict] = {}  # key: "exchange:symbol:interval"
        self.intervals = {
            '1m': 60000,      # 1 minute in ms
            '5m': 300000,     # 5 minutes in ms
            '15m': 900000,    # 15 minutes in ms
            '1h': 3600000,    # 1 hour in ms
            '1d': 86400000,   # 1 day in ms
        }

    def process_tick(self, tick_data: Dict) -> List[OHLCV]:
        """Process a tick and return completed bars"""
        completed_bars = []

        exchange = tick_data.get('exchange', 'unknown')
        symbol = tick_data.get('symbol', '').replace('/', '')
        timestamp = tick_data.get('timestamp', int(time.time() * 1000))
        price = tick_data.get('last', 0.0)
        volume = tick_data.get('volume', 0.0)

        if not price:
            return completed_bars

        # Process each interval
        for interval_name, interval_ms in self.intervals.items():
            # Calculate bar timestamp (floor to interval)
            bar_timestamp = (timestamp // interval_ms) * interval_ms
            bar_key = f"{exchange}:{symbol}:{interval_name}:{bar_timestamp}"

            if bar_key not in self.bars:
                # Start new bar
                self.bars[bar_key] = {
                    'exchange': exchange,
                    'symbol': symbol,
                    'interval': interval_name,
                    'timestamp': bar_timestamp,
                    'open': price,
                    'high': price,
                    'low': price,
                    'close': price,
                    'volume': volume,
                    'trades': 1,
                    'last_update': timestamp
                }
            else:
                # Update existing bar
                bar = self.bars[bar_key]
                bar['high'] = max(bar['high'], price)
                bar['low'] = min(bar['low'], price)
                bar['close'] = price
                bar['volume'] = volume  # Use latest cumulative volume
                bar['trades'] += 1
                bar['last_update'] = timestamp

            # Check if we should close bars (new period started)
            current_bar_timestamp = (timestamp // interval_ms) * interval_ms
            for key in list(self.bars.keys()):
                if key.startswith(f"{exchange}:{symbol}:{interval_name}:"):
                    bar_data = self.bars[key]
                    if bar_data['timestamp'] < current_bar_timestamp:
                        # Bar is complete
                        completed_bars.append(OHLCV(
                            exchange=bar_data['exchange'],
                            symbol=bar_data['symbol'],
                            interval=bar_data['interval'],
                            timestamp=bar_data['timestamp'],
                            open=bar_data['open'],
                            high=bar_data['high'],
                            low=bar_data['low'],
                            close=bar_data['close'],
                            volume=bar_data['volume'],
                            trades=bar_data['trades']
                        ))
                        del self.bars[key]

        return completed_bars

    def flush_incomplete_bars(self, max_age_ms: int = 120000) -> List[OHLCV]:
        """Flush bars that haven't been updated recently"""
        completed_bars = []
        current_time = int(time.time() * 1000)

        for key in list(self.bars.keys()):
            bar = self.bars[key]
            if current_time - bar['last_update'] > max_age_ms:
                completed_bars.append(OHLCV(
                    exchange=bar['exchange'],
                    symbol=bar['symbol'],
                    interval=bar['interval'],
                    timestamp=bar['timestamp'],
                    open=bar['open'],
                    high=bar['high'],
                    low=bar['low'],
                    close=bar['close'],
                    volume=bar['volume'],
                    trades=bar['trades']
                ))
                del self.bars[key]

        return completed_bars

class DataNormalizer:
    """Main normalizer service"""

    def __init__(self, config: Dict):
        self.config = config
        self.nc: Optional[nats.Client] = None
        self.js: Optional[JetStreamContext] = None
        self.redis_client: Optional[redis.Redis] = None
        self.aggregator = TickAggregator()
        self.stats = {
            'ticks_processed': 0,
            'bars_created': 0,
            'errors': 0,
            'start_time': time.time()
        }
        self.questdb_url = config.get('questdb_url', 'http://localhost:9000')
        self.running = False

    async def connect(self):
        """Connect to all services"""
        try:
            # Connect to NATS
            nats_url = self.config.get('nats_url', 'nats://localhost:4222')
            self.nc = await nats.connect(nats_url)
            self.js = self.nc.jetstream()
            logger.info(f"Connected to NATS at {nats_url}")

            # Connect to Redis/Valkey
            redis_host = self.config.get('redis_host', 'localhost')
            redis_port = self.config.get('redis_port', 6379)
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info(f"Connected to Valkey at {redis_host}:{redis_port}")

            # Create QuestDB table if not exists
            await self.setup_questdb_schema()

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise

    async def setup_questdb_schema(self):
        """Create OHLCV table in QuestDB"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ohlcv (
            exchange SYMBOL,
            symbol SYMBOL,
            interval SYMBOL,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume DOUBLE,
            trades INT,
            timestamp TIMESTAMP
        ) timestamp(timestamp) PARTITION BY DAY;
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.questdb_url}/exec",
                    params={"query": create_table_sql}
                )
                if response.status_code == 200:
                    logger.info("QuestDB OHLCV table ready")
                else:
                    logger.warning(f"QuestDB table creation: {response.text}")
        except Exception as e:
            logger.error(f"Failed to create QuestDB table: {e}")

    async def process_message(self, msg):
        """Process incoming tick message"""
        try:
            # Parse tick data
            tick_data = json.loads(msg.data.decode())
            self.stats['ticks_processed'] += 1

            # Aggregate into OHLCV bars
            completed_bars = self.aggregator.process_tick(tick_data)

            # Store completed bars
            for bar in completed_bars:
                await self.store_ohlcv(bar)
                self.stats['bars_created'] += 1

            # Acknowledge message
            await msg.ack()

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.stats['errors'] += 1

    async def store_ohlcv(self, bar: OHLCV):
        """Store OHLCV bar in QuestDB and cache in Valkey"""
        try:
            # Write to QuestDB using line protocol
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.questdb_url}/write?precision=n",
                    content=bar.to_questdb_line()
                )
                if response.status_code != 200:
                    logger.warning(f"QuestDB write failed: {response.text}")

            # Cache in Valkey with TTL
            cache_key = f"ohlcv:{bar.exchange}:{bar.symbol}:{bar.interval}"
            bar_data = asdict(bar)
            self.redis_client.hset(cache_key, mapping=bar_data)
            self.redis_client.expire(cache_key, 3600)  # 1 hour TTL

            # Also maintain a sorted set of recent bars
            score = bar.timestamp
            member = f"{bar.exchange}:{bar.symbol}:{bar.interval}:{bar.timestamp}"
            self.redis_client.zadd(f"ohlcv:recent:{bar.interval}", {member: score})

            logger.debug(f"Stored OHLCV: {bar.exchange} {bar.symbol} {bar.interval} @ {bar.timestamp}")

        except Exception as e:
            logger.error(f"Failed to store OHLCV: {e}")
            self.stats['errors'] += 1

    async def subscribe_to_ticks(self):
        """Subscribe to tick streams from all exchanges"""
        try:
            # Subscribe to wildcard topic for all exchanges
            subject = "market.tick.*.*"  # market.tick.<exchange>.<symbol>

            # Try to get existing consumer or create new one
            try:
                stream_info = await self.js.stream_info("MARKET_TICKS")
                logger.info(f"Using existing stream: MARKET_TICKS")
            except:
                # Create stream if it doesn't exist
                await self.js.add_stream(
                    name="MARKET_TICKS",
                    subjects=["market.tick.>"],
                    max_age=86400_000_000_000  # 1 day in nanoseconds
                )
                logger.info("Created new stream: MARKET_TICKS")

            # Create pull subscription
            psub = await self.js.pull_subscribe(
                subject,
                "normalizer-consumer",
                stream="MARKET_TICKS"
            )

            logger.info(f"Subscribed to {subject}")
            self.running = True

            # Process messages
            while self.running:
                try:
                    msgs = await psub.fetch(batch=10, timeout=1)
                    for msg in msgs:
                        await self.process_message(msg)

                    # Periodically flush incomplete bars
                    if int(time.time()) % 30 == 0:
                        completed_bars = self.aggregator.flush_incomplete_bars()
                        for bar in completed_bars:
                            await self.store_ohlcv(bar)
                            self.stats['bars_created'] += 1

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error fetching messages: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Subscription error: {e}")
            self.stats['errors'] += 1

    async def disconnect(self):
        """Disconnect from all services"""
        self.running = False
        if self.nc:
            await self.nc.close()
        if self.redis_client:
            self.redis_client.close()
        logger.info("Disconnected from all services")

    def get_stats(self) -> Dict:
        """Get service statistics"""
        uptime = int(time.time() - self.stats['start_time'])
        return {
            'status': 'running' if self.running else 'stopped',
            'uptime_seconds': uptime,
            'ticks_processed': self.stats['ticks_processed'],
            'bars_created': self.stats['bars_created'],
            'errors': self.stats['errors'],
            'active_bars': len(self.aggregator.bars),
            'ticks_per_second': round(self.stats['ticks_processed'] / max(uptime, 1), 2)
        }

# FastAPI app
normalizer: Optional[DataNormalizer] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage service lifecycle"""
    global normalizer

    # Load configuration
    try:
        with open('/app/config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except:
        # Fallback config (should not be used in production)
        config = {
            'nats_url': 'nats://nats:4222',
            'redis_host': 'valkey',
            'redis_port': 6379,
            'questdb_url': 'http://questdb:9000'
        }

    # Startup
    normalizer = DataNormalizer(config)
    await normalizer.connect()

    # Start processing in background
    asyncio.create_task(normalizer.subscribe_to_ticks())
    logger.info("Data normalizer service started")

    yield

    # Shutdown
    if normalizer:
        await normalizer.disconnect()
    logger.info("Data normalizer service stopped")

app = FastAPI(title="Data Normalizer", version="1.0.0", lifespan=lifespan)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if normalizer and normalizer.running:
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "service": "normalizer"}
        )
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "service": "normalizer"}
        )

@app.get("/stats")
async def get_statistics():
    """Get service statistics"""
    if normalizer:
        return normalizer.get_stats()
    else:
        raise HTTPException(status_code=503, detail="Service not initialized")

@app.get("/bars/{exchange}/{symbol}/{interval}")
async def get_recent_bars(exchange: str, symbol: str, interval: str, limit: int = 100):
    """Get recent OHLCV bars from cache"""
    if not normalizer or not normalizer.redis_client:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Get recent bars from sorted set
        key = f"ohlcv:recent:{interval}"
        pattern = f"{exchange}:{symbol}:{interval}:*"

        # Get all members and filter
        all_bars = normalizer.redis_client.zrevrange(key, 0, -1, withscores=True)
        matching_bars = []

        for member, score in all_bars:
            if member.startswith(f"{exchange}:{symbol}:{interval}:"):
                parts = member.split(':')
                timestamp = int(parts[3])

                # Get full bar data from hash
                cache_key = f"ohlcv:{exchange}:{symbol}:{interval}"
                bar_data = normalizer.redis_client.hgetall(cache_key)
                if bar_data:
                    bar_data['timestamp'] = timestamp
                    matching_bars.append(bar_data)

                if len(matching_bars) >= limit:
                    break

        return {
            'exchange': exchange,
            'symbol': symbol,
            'interval': interval,
            'count': len(matching_bars),
            'bars': matching_bars
        }

    except Exception as e:
        logger.error(f"Failed to get bars: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)