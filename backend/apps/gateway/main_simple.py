"""
Simplified Market Gateway for testing
"""
import asyncio
import json
import time
import random
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Trade2025 Market Gateway (Simple)", version="1.0.0")
startup_time = time.time()
tick_count = 0

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "services": {
            "nats": "simulated",
            "questdb": "simulated",
            "valkey": "simulated"
        },
        "tick_count": tick_count,
        "error_count": 0,
        "uptime": time.time() - startup_time
    }

@app.get("/stats")
async def get_stats():
    """Get gateway statistics"""
    global tick_count
    tick_count += random.randint(1, 10)  # Simulate tick generation

    return {
        "tick_count": tick_count,
        "error_count": 0,
        "uptime": time.time() - startup_time,
        "last_ticks": {
            "BTC/USDT": time.time(),
            "ETH/USDT": time.time() - 1
        },
        "config": {
            "exchange": "binance",
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "refresh_interval": 5
        }
    }

@app.get("/")
async def root():
    return {
        "service": "Trade2025 Market Gateway",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)