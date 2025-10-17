"""
Mock Gateway - Generates test market data
"""
import asyncio
import json
import random
import time
from datetime import datetime
from typing import List
import nats
import redis
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn

# Global connections
nc = None
redis_client = None
tick_count = 0
current_prices = {}  # Store current prices for /tickers endpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    global nc, redis_client
    # Connect to NATS
    nc = await nats.connect("nats://nats:4222")
    print("Connected to NATS")

    # Connect to Redis
    redis_client = redis.Redis(host='valkey', port=6379)
    redis_client.ping()
    print("Connected to Valkey")

    # Start mock data generator
    asyncio.create_task(generate_mock_data())

    yield

    await nc.close()
    redis_client.close()

app = FastAPI(lifespan=lifespan)

class Ticker(BaseModel):
    symbol: str
    last_price: float
    bid: float
    ask: float
    volume_24h: float
    change_24h: float
    timestamp: str

async def generate_mock_data():
    """Generate mock market ticks"""
    global nc, tick_count, current_prices

    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    prices = {"BTCUSDT": 45000.0, "ETHUSDT": 2500.0, "SOLUSDT": 100.0}
    volumes = {"BTCUSDT": 1000000.0, "ETHUSDT": 500000.0, "SOLUSDT": 250000.0}
    changes = {"BTCUSDT": 2.5, "ETHUSDT": 1.8, "SOLUSDT": -0.5}

    while True:
        for symbol in symbols:
            price = prices[symbol]
            # Random walk
            price *= (1 + random.uniform(-0.001, 0.001))
            prices[symbol] = price

            tick = {
                "timestamp": int(time.time() * 1000),
                "exchange": "mock",
                "venue": "mock",  # Required by sink schema
                "symbol": symbol,
                "price": price,
                "last": price,
                "size": random.uniform(0.01, 1.0),  # Required by sink schema
                "volume": random.uniform(0.01, 1.0),
                "bid": price - 1,
                "ask": price + 1
            }

            # Update current prices for /tickers endpoint
            current_prices[symbol] = {
                "price": price,
                "bid": price - 1,
                "ask": price + 1,
                "volume_24h": volumes.get(symbol, 1000000.0),
                "change_24h": changes.get(symbol, 0.0),
                "timestamp": datetime.utcnow().isoformat()
            }

            # Publish to NATS
            await nc.publish(f"market.tick.{symbol}", json.dumps(tick).encode())
            tick_count += 1

        await asyncio.sleep(1)  # Generate data every second

@app.get("/health")
async def health():
    return {"status": "ok", "ticks_sent": tick_count}

@app.get("/tickers", response_model=List[Ticker])
async def get_tickers():
    """Get list of all available tickers"""
    global current_prices

    tickers = []
    for symbol, data in current_prices.items():
        tickers.append(Ticker(
            symbol=symbol,
            last_price=data["price"],
            bid=data["bid"],
            ask=data["ask"],
            volume_24h=data["volume_24h"],
            change_24h=data["change_24h"],
            timestamp=data["timestamp"]
        ))

    # If no data yet, return mock data
    if not tickers:
        tickers = [
            Ticker(
                symbol="BTCUSDT",
                last_price=45000.0,
                bid=44999.0,
                ask=45001.0,
                volume_24h=1000000.0,
                change_24h=2.5,
                timestamp=datetime.utcnow().isoformat()
            ),
            Ticker(
                symbol="ETHUSDT",
                last_price=2500.0,
                bid=2499.5,
                ask=2500.5,
                volume_24h=500000.0,
                change_24h=1.8,
                timestamp=datetime.utcnow().isoformat()
            ),
            Ticker(
                symbol="SOLUSDT",
                last_price=100.0,
                bid=99.95,
                ask=100.05,
                volume_24h=250000.0,
                change_24h=-0.5,
                timestamp=datetime.utcnow().isoformat()
            )
        ]

    return tickers

@app.get("/ticker/{symbol}", response_model=Ticker)
async def get_ticker(symbol: str):
    """Get ticker for specific symbol"""
    global current_prices

    if symbol in current_prices:
        data = current_prices[symbol]
        return Ticker(
            symbol=symbol,
            last_price=data["price"],
            bid=data["bid"],
            ask=data["ask"],
            volume_24h=data["volume_24h"],
            change_24h=data["change_24h"],
            timestamp=data["timestamp"]
        )

    # Return mock data if symbol not found
    return Ticker(
        symbol=symbol,
        last_price=45000.0,
        bid=44999.0,
        ask=45001.0,
        volume_24h=1000000.0,
        change_24h=2.5,
        timestamp=datetime.utcnow().isoformat()
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)