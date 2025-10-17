#!/usr/bin/env python3
"""
QuestDB Writer Service - High-Performance Time-Series Data Writer
Handles efficient batching and writing of time-series data to QuestDB
"""

import os
import json
import yaml
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from queue import Queue, Empty
import threading

import uvicorn
import redis.asyncio as redis
import nats
import asyncpg
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Prometheus metrics
writes_total = Counter('questdb_writes_total', 'Total writes to QuestDB', ['table', 'status'])
batch_size = Histogram('questdb_batch_size', 'Batch sizes written', ['table'])
write_latency = Histogram('questdb_write_latency_seconds', 'Write latency', ['table'])
buffer_size = Gauge('questdb_buffer_size_bytes', 'Current buffer size')
connection_pool = Gauge('questdb_connection_pool_active', 'Active connections')
errors_total = Counter('questdb_errors_total', 'Total errors', ['type'])

# FastAPI app
app = FastAPI(title="QuestDB Writer Service", version="1.0.0")


class TimeSeriesData(BaseModel):
    """Generic time-series data model"""
    table: str
    timestamp: datetime
    data: Dict[str, Any]
    tags: Optional[Dict[str, str]] = None


class Trade(BaseModel):
    """Trade data model"""
    trade_id: str
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    venue: str
    account_id: str
    execution_time: datetime


class MarketData(BaseModel):
    """Market data model"""
    symbol: str
    bid_price: float
    ask_price: float
    bid_size: float
    ask_size: float
    last_price: float
    volume: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WriteBatch:
    """Batch of data to write"""

    def __init__(self, table: str):
        self.table = table
        self.data = []
        self.created_at = time.time()

    def add(self, record: Dict[str, Any]):
        self.data.append(record)

    def size(self) -> int:
        return len(self.data)

    def age_ms(self) -> float:
        return (time.time() - self.created_at) * 1000


class QuestDBWriter:
    """QuestDB writer with batching and buffering"""

    def __init__(self):
        self.pg_pool = None
        self.redis_client = None
        self.nc = None
        self.batches: Dict[str, WriteBatch] = {}
        self.buffer_lock = asyncio.Lock()
        self.write_queue = asyncio.Queue()
        self.running = False
        self.stats = {
            'total_writes': 0,
            'failed_writes': 0,
            'bytes_written': 0
        }

    async def start(self):
        """Start the QuestDB writer service"""
        logger.info("Starting QuestDB Writer service...")

        # Create connection pool to QuestDB (PostgreSQL wire protocol)
        self.pg_pool = await asyncpg.create_pool(
            host=config['questdb']['host'],
            port=config['questdb']['pg_port'],
            user=config['questdb']['user'],
            password=config['questdb']['password'],
            database=config['questdb']['database'],
            min_size=2,
            max_size=config['performance']['connection_pool_size']
        )

        # Connect to Redis for buffering
        self.redis_client = await redis.from_url(
            f"redis://{config['redis_host']}:{config['redis_port']}/{config['redis_db']}"
        )

        # Connect to NATS
        self.nc = await nats.connect(config['nats_url'])

        # Subscribe to data streams
        await self.nc.subscribe("trades.executed", "questdb_writer", self.handle_trade)
        await self.nc.subscribe("market.data", "questdb_writer", self.handle_market_data)
        await self.nc.subscribe("orders.*", "questdb_writer", self.handle_order_event)
        await self.nc.subscribe("positions.updated", "questdb_writer", self.handle_position_update)
        await self.nc.subscribe("risk.metrics", "questdb_writer", self.handle_risk_metrics)

        # Initialize tables
        await self.initialize_tables()

        # Start background workers
        self.running = True
        for _ in range(config['performance']['worker_threads']):
            asyncio.create_task(self.write_worker())

        asyncio.create_task(self.flush_worker())
        asyncio.create_task(self.metrics_reporter())

        logger.info("QuestDB Writer service started successfully")

    async def stop(self):
        """Stop the QuestDB writer service"""
        self.running = False

        # Flush remaining batches
        await self.flush_all_batches()

        if self.nc:
            await self.nc.close()
        if self.redis_client:
            await self.redis_client.close()
        if self.pg_pool:
            await self.pg_pool.close()

    async def initialize_tables(self):
        """Create tables if they don't exist"""
        async with self.pg_pool.acquire() as conn:
            for table_name, table_config in config['tables'].items():
                try:
                    # Create table with proper schema
                    await self.create_table(conn, table_name, table_config)
                except Exception as e:
                    logger.error(f"Error creating table {table_name}: {e}")

    async def create_table(self, conn, table_name: str, table_config: Dict):
        """Create a QuestDB table"""
        # Build column definitions
        columns = []
        for col in table_config['columns']:
            if col in ['price', 'quantity', 'volume', 'pnl']:
                columns.append(f"{col} DOUBLE")
            elif col in ['side', 'status', 'order_type']:
                columns.append(f"{col} SYMBOL")
            else:
                columns.append(f"{col} STRING")

        # Add timestamp column
        timestamp_col = table_config['timestamp_column']
        columns.append(f"{timestamp_col} TIMESTAMP")

        # Build CREATE TABLE statement
        create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {table_config['name']} (
            {', '.join(columns)}
        ) TIMESTAMP({timestamp_col})
        PARTITION BY {table_config['partition']}
        """

        try:
            await conn.execute(create_stmt)
            logger.info(f"Table {table_name} initialized")
        except Exception as e:
            logger.warning(f"Table {table_name} might already exist: {e}")

    async def handle_trade(self, msg):
        """Handle trade execution events"""
        try:
            data = json.loads(msg.data.decode())
            trade = Trade(**data)

            await self.buffer_write('trades', {
                'trade_id': trade.trade_id,
                'order_id': trade.order_id,
                'symbol': trade.symbol,
                'side': trade.side,
                'quantity': trade.quantity,
                'price': trade.price,
                'venue': trade.venue,
                'account_id': trade.account_id,
                'execution_time': trade.execution_time
            })

        except Exception as e:
            logger.error(f"Error handling trade: {e}")
            errors_total.labels(type='trade_processing').inc()

    async def handle_market_data(self, msg):
        """Handle market data events"""
        try:
            data = json.loads(msg.data.decode())
            market_data = MarketData(**data)

            await self.buffer_write('market_data', {
                'symbol': market_data.symbol,
                'bid_price': market_data.bid_price,
                'ask_price': market_data.ask_price,
                'bid_size': market_data.bid_size,
                'ask_size': market_data.ask_size,
                'last_price': market_data.last_price,
                'volume': market_data.volume,
                'timestamp': market_data.timestamp
            })

        except Exception as e:
            logger.error(f"Error handling market data: {e}")
            errors_total.labels(type='market_data_processing').inc()

    async def handle_order_event(self, msg):
        """Handle order events"""
        try:
            data = json.loads(msg.data.decode())

            await self.buffer_write('orders', {
                'order_id': data.get('order_id'),
                'symbol': data.get('symbol'),
                'side': data.get('side'),
                'order_type': data.get('order_type'),
                'quantity': data.get('quantity'),
                'price': data.get('price'),
                'status': data.get('status'),
                'account_id': data.get('account_id'),
                'created_at': datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat()))
            })

        except Exception as e:
            logger.error(f"Error handling order event: {e}")
            errors_total.labels(type='order_processing').inc()

    async def handle_position_update(self, msg):
        """Handle position updates"""
        try:
            data = json.loads(msg.data.decode())

            await self.buffer_write('positions', {
                'account_id': data.get('account_id'),
                'symbol': data.get('symbol'),
                'quantity': data.get('quantity'),
                'avg_price': data.get('avg_price'),
                'pnl': data.get('pnl'),
                'unrealized_pnl': data.get('unrealized_pnl'),
                'updated_at': datetime.utcnow()
            })

        except Exception as e:
            logger.error(f"Error handling position update: {e}")
            errors_total.labels(type='position_processing').inc()

    async def handle_risk_metrics(self, msg):
        """Handle risk metrics"""
        try:
            data = json.loads(msg.data.decode())

            await self.buffer_write('risk_metrics', {
                'account_id': data.get('account_id'),
                'var_95': data.get('var_95'),
                'var_99': data.get('var_99'),
                'max_drawdown': data.get('max_drawdown'),
                'sharpe_ratio': data.get('sharpe_ratio'),
                'exposure': data.get('exposure'),
                'calculated_at': datetime.utcnow()
            })

        except Exception as e:
            logger.error(f"Error handling risk metrics: {e}")
            errors_total.labels(type='risk_metrics_processing').inc()

    async def buffer_write(self, table: str, data: Dict[str, Any]):
        """Buffer data for batch writing"""
        async with self.buffer_lock:
            if table not in self.batches:
                self.batches[table] = WriteBatch(table)

            batch = self.batches[table]
            batch.add(data)

            # Check if batch should be flushed
            if batch.size() >= config['writer']['batch_size']:
                await self.flush_batch(table)

    async def flush_batch(self, table: str):
        """Flush a batch to the write queue"""
        if table not in self.batches:
            return

        batch = self.batches.pop(table)
        if batch.size() > 0:
            await self.write_queue.put(batch)
            batch_size.labels(table=table).observe(batch.size())

    async def flush_all_batches(self):
        """Flush all pending batches"""
        async with self.buffer_lock:
            for table in list(self.batches.keys()):
                await self.flush_batch(table)

    async def write_worker(self):
        """Worker to write batches to QuestDB"""
        while self.running:
            try:
                # Get batch from queue with timeout
                batch = await asyncio.wait_for(self.write_queue.get(), timeout=1.0)
                await self.write_batch_to_db(batch)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in write worker: {e}")
                errors_total.labels(type='write_worker').inc()

    async def write_batch_to_db(self, batch: WriteBatch):
        """Write a batch to QuestDB"""
        start_time = time.time()
        table_config = config['tables'].get(batch.table, {})

        if not table_config:
            logger.error(f"Unknown table: {batch.table}")
            return

        try:
            async with self.pg_pool.acquire() as conn:
                # Build INSERT statement
                if batch.data:
                    df = pd.DataFrame(batch.data)

                    # Convert to SQL values
                    for record in batch.data:
                        columns = list(record.keys())
                        values = list(record.values())

                        # Format values for SQL
                        formatted_values = []
                        for val in values:
                            if isinstance(val, datetime):
                                formatted_values.append(f"'{val.isoformat()}'")
                            elif isinstance(val, str):
                                formatted_values.append(f"'{val}'")
                            elif val is None:
                                formatted_values.append('NULL')
                            else:
                                formatted_values.append(str(val))

                        insert_stmt = f"""
                        INSERT INTO {table_config['name']}
                        ({', '.join(columns)})
                        VALUES ({', '.join(formatted_values)})
                        """

                        await conn.execute(insert_stmt)

                    self.stats['total_writes'] += len(batch.data)
                    writes_total.labels(table=batch.table, status='success').inc(len(batch.data))
                    write_latency.labels(table=batch.table).observe(time.time() - start_time)

                    logger.debug(f"Wrote {len(batch.data)} records to {batch.table}")

        except Exception as e:
            logger.error(f"Error writing batch to {batch.table}: {e}")
            self.stats['failed_writes'] += len(batch.data)
            writes_total.labels(table=batch.table, status='failed').inc(len(batch.data))
            errors_total.labels(type='batch_write').inc()

            # Store failed batch in Redis for retry
            if self.redis_client:
                await self.redis_client.lpush(
                    f"failed_batch:{batch.table}",
                    json.dumps([r for r in batch.data], default=str)
                )

    async def flush_worker(self):
        """Periodically flush batches based on time"""
        while self.running:
            try:
                await asyncio.sleep(config['writer']['flush_interval_ms'] / 1000)

                async with self.buffer_lock:
                    for table, batch in list(self.batches.items()):
                        if batch.age_ms() >= config['writer']['max_batch_wait_ms']:
                            await self.flush_batch(table)

            except Exception as e:
                logger.error(f"Error in flush worker: {e}")

    async def metrics_reporter(self):
        """Report metrics periodically"""
        while self.running:
            try:
                await asyncio.sleep(config['metrics']['interval'])

                # Update buffer size
                total_buffer_size = sum(
                    batch.size() for batch in self.batches.values()
                )
                buffer_size.set(total_buffer_size)

                # Update connection pool
                if self.pg_pool:
                    connection_pool.set(self.pg_pool._holders_count)

            except Exception as e:
                logger.error(f"Error in metrics reporter: {e}")

    async def query(self, table: str, filters: Dict = None, limit: int = 100) -> List[Dict]:
        """Query data from QuestDB"""
        try:
            async with self.pg_pool.acquire() as conn:
                query = f"SELECT * FROM {table}"

                if filters:
                    conditions = []
                    for key, value in filters.items():
                        if isinstance(value, str):
                            conditions.append(f"{key} = '{value}'")
                        else:
                            conditions.append(f"{key} = {value}")
                    query += f" WHERE {' AND '.join(conditions)}"

                query += f" ORDER BY timestamp DESC LIMIT {limit}"

                rows = await conn.fetch(query)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error querying {table}: {e}")
            return []


# Service instance
writer_service = QuestDBWriter()


@app.on_event("startup")
async def startup_event():
    """Start the writer service on app startup"""
    await writer_service.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    await writer_service.stop()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "QuestDB Writer",
        "version": "1.0.0",
        "status": "running",
        "description": "High-Performance Time-Series Data Writer for QuestDB"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    checks = {
        "questdb": False,
        "redis": False,
        "nats": False,
        "service": writer_service.running
    }

    # Check QuestDB
    try:
        if writer_service.pg_pool:
            async with writer_service.pg_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                checks["questdb"] = True
    except:
        pass

    # Check Redis
    try:
        if writer_service.redis_client:
            await writer_service.redis_client.ping()
            checks["redis"] = True
    except:
        pass

    # Check NATS
    if writer_service.nc and writer_service.nc.is_connected:
        checks["nats"] = True

    is_healthy = all(checks.values())

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/write")
async def write_data(data: TimeSeriesData):
    """Write time-series data"""
    await writer_service.buffer_write(data.table, data.data)
    return {"status": "buffered", "table": data.table}


@app.post("/write/batch")
async def write_batch(table: str, data: List[Dict[str, Any]]):
    """Write batch of data"""
    for record in data:
        await writer_service.buffer_write(table, record)
    return {"status": "buffered", "table": table, "records": len(data)}


@app.post("/flush")
async def flush_buffers():
    """Force flush all buffers"""
    await writer_service.flush_all_batches()
    return {"status": "flushed"}


@app.get("/query/{table}")
async def query_table(table: str, limit: int = 100):
    """Query data from a table"""
    results = await writer_service.query(table, limit=limit)
    return {"table": table, "records": results, "count": len(results)}


@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    return {
        "total_writes": writer_service.stats['total_writes'],
        "failed_writes": writer_service.stats['failed_writes'],
        "buffer_count": len(writer_service.batches),
        "queue_size": writer_service.write_queue.qsize(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)