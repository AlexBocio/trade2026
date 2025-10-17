#!/usr/bin/env python3
"""
Feast Pipeline Service - Feature Engineering and ML Pipeline
Handles real-time feature computation and serving for trading platform
"""

import os
import json
import yaml
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from collections import deque

import uvicorn
import redis.asyncio as redis
import nats
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
features_computed = Counter('feast_features_computed_total', 'Total features computed', ['feature_set'])
feature_latency = Histogram('feast_feature_computation_latency_seconds', 'Feature computation latency', ['feature_set'])
cache_hits = Counter('feast_cache_hits_total', 'Cache hits')
cache_misses = Counter('feast_cache_misses_total', 'Cache misses')
feature_values = Gauge('feast_feature_value', 'Current feature values', ['feature_name'])

# FastAPI app
app = FastAPI(title="Feast Pipeline Service", version="1.0.0")


class FeatureRequest(BaseModel):
    """Feature request model"""
    entity_id: str
    feature_set: str
    features: Optional[List[str]] = None
    timestamp: Optional[datetime] = None


class FeatureResponse(BaseModel):
    """Feature response model"""
    entity_id: str
    feature_set: str
    features: Dict[str, Any]
    timestamp: datetime
    cached: bool = False


class FeatureEngineering:
    """Feature engineering and computation"""

    def __init__(self):
        self.data_buffer = {}
        self.feature_cache = {}
        self.window_data = {}

    def compute_market_features(self, symbol: str, data: pd.DataFrame) -> Dict[str, float]:
        """Compute market-based features"""
        features = {}

        try:
            # Price features
            if 'price' in data.columns:
                features['price_sma_5'] = data['price'].rolling(5).mean().iloc[-1]
                features['price_sma_20'] = data['price'].rolling(20).mean().iloc[-1]
                features['price_volatility'] = data['price'].rolling(20).std().iloc[-1]

            # Volume features
            if 'volume' in data.columns:
                features['volume_sma_10'] = data['volume'].rolling(10).mean().iloc[-1]
                features['volume_ratio'] = data['volume'].iloc[-1] / features['volume_sma_10'] if features['volume_sma_10'] > 0 else 1

            # Spread features
            if 'bid_price' in data.columns and 'ask_price' in data.columns:
                features['bid_ask_spread'] = data['ask_price'].iloc[-1] - data['bid_price'].iloc[-1]

        except Exception as e:
            logger.error(f"Error computing market features: {e}")

        return features

    def compute_account_features(self, account_id: str, trades: List[Dict]) -> Dict[str, float]:
        """Compute account-based features"""
        features = {}

        try:
            if trades:
                df = pd.DataFrame(trades)

                # Basic statistics
                features['total_positions'] = len(df)
                features['total_exposure'] = df['quantity'].abs().sum() if 'quantity' in df.columns else 0

                # Performance metrics
                if 'pnl' in df.columns:
                    wins = df[df['pnl'] > 0]
                    features['win_rate'] = len(wins) / len(df) if len(df) > 0 else 0
                    features['daily_pnl'] = df['pnl'].sum()

                # Trade size
                if 'quantity' in df.columns and 'price' in df.columns:
                    features['avg_trade_size'] = (df['quantity'] * df['price']).abs().mean()

                # Risk score (simplified)
                features['risk_score'] = min(100, features.get('total_exposure', 0) / 10000 * 100)

        except Exception as e:
            logger.error(f"Error computing account features: {e}")

        return features

    def compute_risk_features(self, positions: pd.DataFrame, returns: pd.Series) -> Dict[str, float]:
        """Compute risk-based features"""
        features = {}

        try:
            if len(returns) > 0:
                # VaR calculations
                features['var_95'] = np.percentile(returns, 5)
                features['var_99'] = np.percentile(returns, 1)

                # Maximum drawdown
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max
                features['max_drawdown'] = drawdown.min()

                # Sharpe ratio (simplified)
                if returns.std() > 0:
                    features['sharpe_ratio'] = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
                else:
                    features['sharpe_ratio'] = 0

                # Beta (simplified - against market)
                features['beta'] = 1.0  # Placeholder

        except Exception as e:
            logger.error(f"Error computing risk features: {e}")

        return features


class FeastPipeline:
    """Main Feast Pipeline service"""

    def __init__(self):
        self.redis_client = None
        self.nc = None
        self.feature_eng = FeatureEngineering()
        self.running = False

    async def start(self):
        """Start the Feast Pipeline service"""
        logger.info("Starting Feast Pipeline service...")

        # Connect to Redis
        self.redis_client = await redis.from_url(
            f"redis://{config['redis_host']}:{config['redis_port']}/{config['redis_db']}"
        )

        # Connect to NATS
        self.nc = await nats.connect(config['nats_url'])

        # Subscribe to data streams
        await self.nc.subscribe("market.data", "feast", self.handle_market_data)
        await self.nc.subscribe("trades.executed", "feast", self.handle_trade)
        await self.nc.subscribe("positions.updated", "feast", self.handle_position_update)

        # Start background tasks
        self.running = True
        asyncio.create_task(self.feature_computation_loop())
        asyncio.create_task(self.cache_cleanup_loop())

        logger.info("Feast Pipeline service started successfully")

    async def stop(self):
        """Stop the Feast Pipeline service"""
        self.running = False
        if self.nc:
            await self.nc.close()
        if self.redis_client:
            await self.redis_client.close()

    async def handle_market_data(self, msg):
        """Handle market data for feature computation"""
        try:
            data = json.loads(msg.data.decode())
            symbol = data.get('symbol')

            # Buffer data for feature computation
            if symbol not in self.feature_eng.data_buffer:
                self.feature_eng.data_buffer[symbol] = deque(maxlen=100)

            self.feature_eng.data_buffer[symbol].append(data)

        except Exception as e:
            logger.error(f"Error handling market data: {e}")

    async def handle_trade(self, msg):
        """Handle trade execution for feature updates"""
        try:
            trade = json.loads(msg.data.decode())
            account_id = trade.get('account_id')

            # Store trade for account features
            trade_key = f"trades:{account_id}"
            await self.redis_client.lpush(trade_key, json.dumps(trade))
            await self.redis_client.ltrim(trade_key, 0, 999)  # Keep last 1000 trades

        except Exception as e:
            logger.error(f"Error handling trade: {e}")

    async def handle_position_update(self, msg):
        """Handle position updates for risk features"""
        try:
            position = json.loads(msg.data.decode())
            account_id = position.get('account_id')

            # Store position for risk features
            position_key = f"positions:{account_id}"
            await self.redis_client.hset(
                position_key,
                position.get('symbol'),
                json.dumps(position)
            )

        except Exception as e:
            logger.error(f"Error handling position update: {e}")

    async def get_features(self, entity_id: str, feature_set: str, features: List[str] = None) -> Dict[str, Any]:
        """Get features for an entity"""

        # Check cache first
        cache_key = f"features:{feature_set}:{entity_id}"
        cached = await self.redis_client.get(cache_key)

        if cached:
            cache_hits.inc()
            return json.loads(cached)

        cache_misses.inc()

        # Compute features based on feature set
        computed_features = {}

        if feature_set == "market_features":
            computed_features = await self.compute_market_features_for_entity(entity_id)
        elif feature_set == "account_features":
            computed_features = await self.compute_account_features_for_entity(entity_id)
        elif feature_set == "risk_features":
            computed_features = await self.compute_risk_features_for_entity(entity_id)

        # Filter requested features
        if features:
            computed_features = {k: v for k, v in computed_features.items() if k in features}

        # Cache features
        if config['cache']['enabled']:
            await self.redis_client.setex(
                cache_key,
                config['cache']['ttl_seconds'],
                json.dumps(computed_features, default=str)
            )

        return computed_features

    async def compute_market_features_for_entity(self, symbol: str) -> Dict[str, float]:
        """Compute market features for a symbol"""
        if symbol in self.feature_eng.data_buffer:
            data = list(self.feature_eng.data_buffer[symbol])
            if data:
                df = pd.DataFrame(data)
                return self.feature_eng.compute_market_features(symbol, df)
        return {}

    async def compute_account_features_for_entity(self, account_id: str) -> Dict[str, float]:
        """Compute account features"""
        # Get recent trades
        trade_key = f"trades:{account_id}"
        trades_data = await self.redis_client.lrange(trade_key, 0, 99)
        trades = [json.loads(t) for t in trades_data]

        return self.feature_eng.compute_account_features(account_id, trades)

    async def compute_risk_features_for_entity(self, account_id: str) -> Dict[str, float]:
        """Compute risk features"""
        # Get positions
        position_key = f"positions:{account_id}"
        positions_data = await self.redis_client.hgetall(position_key)
        positions = [json.loads(p) for p in positions_data.values()]

        if positions:
            df = pd.DataFrame(positions)
            # Simplified returns calculation
            returns = pd.Series(np.random.randn(100) * 0.01)  # Placeholder
            return self.feature_eng.compute_risk_features(df, returns)
        return {}

    async def feature_computation_loop(self):
        """Background loop for feature computation"""
        while self.running:
            try:
                # Compute features for each feature set
                for feature_set_name, feature_set_config in config['feature_sets'].items():
                    interval = feature_set_config.get('update_interval', 10)
                    await asyncio.sleep(interval)

                    # This would compute features for all entities
                    features_computed.labels(feature_set=feature_set_name).inc()

            except Exception as e:
                logger.error(f"Error in feature computation loop: {e}")
                await asyncio.sleep(1)

    async def cache_cleanup_loop(self):
        """Clean up old cache entries"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Run every minute

                # Clean up old feature cache entries
                # In production, this would be more sophisticated

            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")


# Service instance
feast_service = FeastPipeline()


@app.on_event("startup")
async def startup_event():
    """Start the Feast Pipeline service on app startup"""
    await feast_service.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    await feast_service.stop()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Feast Pipeline",
        "version": "1.0.0",
        "status": "running",
        "description": "Feature Engineering and ML Pipeline Service"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    checks = {
        "redis": False,
        "nats": False,
        "service": feast_service.running
    }

    # Check Redis
    try:
        if feast_service.redis_client:
            await feast_service.redis_client.ping()
            checks["redis"] = True
    except:
        pass

    # Check NATS
    if feast_service.nc and feast_service.nc.is_connected:
        checks["nats"] = True

    is_healthy = all(checks.values())

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/features/get")
async def get_features(request: FeatureRequest):
    """Get features for an entity"""
    features = await feast_service.get_features(
        request.entity_id,
        request.feature_set,
        request.features
    )

    return FeatureResponse(
        entity_id=request.entity_id,
        feature_set=request.feature_set,
        features=features,
        timestamp=datetime.utcnow(),
        cached=bool(features)
    )


@app.get("/features/sets")
async def list_feature_sets():
    """List available feature sets"""
    return {
        "feature_sets": list(config['feature_sets'].keys()),
        "details": config['feature_sets']
    }


@app.get("/features/{feature_set}/{entity_id}")
async def get_entity_features(feature_set: str, entity_id: str):
    """Get all features for an entity in a feature set"""
    if feature_set not in config['feature_sets']:
        raise HTTPException(status_code=404, detail="Feature set not found")

    features = await feast_service.get_features(entity_id, feature_set)

    return {
        "entity_id": entity_id,
        "feature_set": feature_set,
        "features": features,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    return {
        "buffer_sizes": {
            symbol: len(buffer)
            for symbol, buffer in feast_service.feature_eng.data_buffer.items()
        },
        "cache_size": len(feast_service.feature_eng.feature_cache),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8091)