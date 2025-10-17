#!/usr/bin/env python3
"""
Hot Cache Service - High-Performance Multi-Layer Caching
Provides L1 in-memory and L2 Redis caching for frequently accessed data
"""

import os
import json
import yaml
import asyncio
import logging
import msgpack
import time
import gc
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from collections import OrderedDict
from functools import wraps

import uvicorn
import redis.asyncio as redis
import nats
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Prometheus metrics
cache_hits = Counter('hot_cache_hits_total', 'Total cache hits', ['layer', 'category'])
cache_misses = Counter('hot_cache_misses_total', 'Total cache misses', ['layer', 'category'])
cache_sets = Counter('hot_cache_sets_total', 'Total cache sets', ['layer', 'category'])
cache_evictions = Counter('hot_cache_evictions_total', 'Total cache evictions')
cache_size = Gauge('hot_cache_size_bytes', 'Current cache size in bytes', ['layer'])
cache_items = Gauge('hot_cache_items_count', 'Number of items in cache', ['layer'])

cache_latency = Histogram('hot_cache_operation_latency_seconds', 'Cache operation latency', ['operation', 'layer'])
hit_ratio = Gauge('hot_cache_hit_ratio', 'Cache hit ratio', ['layer'])

# FastAPI app
app = FastAPI(title="Hot Cache Service", version="1.0.0")


class CacheEntry(BaseModel):
    """Cache entry model"""
    key: str
    value: Any
    category: str = "default"
    ttl: Optional[int] = None
    compressed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0


class CacheStats(BaseModel):
    """Cache statistics"""
    l1_hits: int
    l1_misses: int
    l2_hits: int
    l2_misses: int
    l1_size_mb: float
    l2_items: int
    hit_ratio: float
    evictions: int


class LRUCache:
    """Thread-safe LRU cache implementation"""

    def __init__(self, max_size_mb: int):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: OrderedDict = OrderedDict()
        self.size_bytes = 0
        self.lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        async with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                entry = self.cache[key]
                entry['accessed_at'] = datetime.utcnow()
                entry['access_count'] += 1
                return entry['value']
            return None

    async def set(self, key: str, value: Any, ttl: int = None, category: str = "default"):
        """Set item in cache"""
        async with self.lock:
            # Calculate size
            value_size = len(msgpack.packb(value))

            # Check if we need to evict
            while self.size_bytes + value_size > self.max_size_bytes and self.cache:
                # Evict least recently used
                evicted_key, evicted_entry = self.cache.popitem(last=False)
                self.size_bytes -= evicted_entry['size']
                cache_evictions.inc()

            # Add/update entry
            if key in self.cache:
                self.size_bytes -= self.cache[key]['size']

            expires_at = None
            if ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)

            self.cache[key] = {
                'value': value,
                'size': value_size,
                'category': category,
                'created_at': datetime.utcnow(),
                'accessed_at': datetime.utcnow(),
                'expires_at': expires_at,
                'access_count': 0
            }
            self.size_bytes += value_size

    async def delete(self, key: str) -> bool:
        """Delete item from cache"""
        async with self.lock:
            if key in self.cache:
                self.size_bytes -= self.cache[key]['size']
                del self.cache[key]
                return True
            return False

    async def clear(self):
        """Clear entire cache"""
        async with self.lock:
            self.cache.clear()
            self.size_bytes = 0

    async def cleanup_expired(self):
        """Remove expired entries"""
        async with self.lock:
            now = datetime.utcnow()
            keys_to_remove = []

            for key, entry in self.cache.items():
                if entry.get('expires_at') and entry['expires_at'] < now:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                self.size_bytes -= self.cache[key]['size']
                del self.cache[key]


class HotCacheService:
    """Multi-layer caching service"""

    def __init__(self):
        self.l1_cache = None  # In-memory cache
        self.redis_client = None  # L2 cache
        self.nc = None
        self.stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'evictions': 0
        }
        self.running = False

    async def start(self):
        """Start the hot cache service"""
        logger.info("Starting Hot Cache service...")

        # Initialize L1 cache
        if config['cache']['l1_cache']['enabled']:
            max_size_mb = config['cache']['l1_cache']['max_size_mb']
            self.l1_cache = LRUCache(max_size_mb)
            logger.info(f"L1 cache initialized with {max_size_mb}MB limit")

        # Connect to Redis (L2 cache)
        if config['cache']['l2_cache']['enabled']:
            self.redis_client = await redis.from_url(
                f"redis://{config['redis_host']}:{config['redis_port']}/{config['redis_db']}",
                max_connections=config['cache']['l2_cache']['max_connections']
            )
            logger.info("L2 cache (Redis) connected")

        # Connect to NATS
        self.nc = await nats.connect(config['nats_url'])

        # Subscribe to invalidation events
        await self.nc.subscribe("cache.invalidate", "hot_cache", self.handle_invalidation)
        await self.nc.subscribe("cache.warm", "hot_cache", self.handle_warm_request)

        # Start background tasks
        self.running = True
        asyncio.create_task(self.cleanup_loop())
        asyncio.create_task(self.warmup_loop())
        asyncio.create_task(self.metrics_loop())

        # Preload data if configured
        if config['preload']['enabled']:
            asyncio.create_task(self.preload_data())

        logger.info("Hot Cache service started successfully")

    async def stop(self):
        """Stop the hot cache service"""
        self.running = False
        if self.nc:
            await self.nc.close()
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str, category: str = "default") -> Optional[Any]:
        """Get value from cache (L1 -> L2 -> miss)"""
        start_time = time.time()

        # Check L1 cache
        if self.l1_cache:
            value = await self.l1_cache.get(key)
            if value is not None:
                self.stats['l1_hits'] += 1
                cache_hits.labels(layer='l1', category=category).inc()
                cache_latency.labels(operation='get', layer='l1').observe(time.time() - start_time)
                return value

        self.stats['l1_misses'] += 1
        cache_misses.labels(layer='l1', category=category).inc()

        # Check L2 cache
        if self.redis_client:
            try:
                serialized = await self.redis_client.get(key)
                if serialized:
                    value = msgpack.unpackb(serialized, raw=False)
                    self.stats['l2_hits'] += 1
                    cache_hits.labels(layer='l2', category=category).inc()

                    # Promote to L1
                    if self.l1_cache:
                        ttl = config['data_categories'].get(category, {}).get('ttl', 60)
                        await self.l1_cache.set(key, value, ttl=ttl, category=category)

                    cache_latency.labels(operation='get', layer='l2').observe(time.time() - start_time)
                    return value
            except Exception as e:
                logger.error(f"L2 cache get error: {e}")

        self.stats['l2_misses'] += 1
        cache_misses.labels(layer='l2', category=category).inc()
        cache_latency.labels(operation='get', layer='miss').observe(time.time() - start_time)
        return None

    async def set(self, key: str, value: Any, category: str = "default", ttl: Optional[int] = None):
        """Set value in cache (both L1 and L2)"""
        start_time = time.time()

        # Get TTL from config if not provided
        if ttl is None:
            ttl = config['data_categories'].get(category, {}).get('ttl', 60)

        # Serialize value
        serialized = msgpack.packb(value)

        # Set in L1 cache
        if self.l1_cache:
            await self.l1_cache.set(key, value, ttl=ttl, category=category)
            cache_sets.labels(layer='l1', category=category).inc()

        # Set in L2 cache
        if self.redis_client:
            try:
                if ttl > 0:
                    await self.redis_client.setex(key, ttl, serialized)
                else:
                    await self.redis_client.set(key, serialized)
                cache_sets.labels(layer='l2', category=category).inc()
            except Exception as e:
                logger.error(f"L2 cache set error: {e}")

        cache_latency.labels(operation='set', layer='both').observe(time.time() - start_time)

    async def delete(self, key: str):
        """Delete value from cache"""
        start_time = time.time()

        # Delete from L1
        if self.l1_cache:
            await self.l1_cache.delete(key)

        # Delete from L2
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"L2 cache delete error: {e}")

        cache_latency.labels(operation='delete', layer='both').observe(time.time() - start_time)

    async def mget(self, keys: List[str], category: str = "default") -> Dict[str, Any]:
        """Get multiple values at once"""
        result = {}

        # Try L1 first
        l1_misses = []
        if self.l1_cache:
            for key in keys:
                value = await self.l1_cache.get(key)
                if value is not None:
                    result[key] = value
                else:
                    l1_misses.append(key)
        else:
            l1_misses = keys

        # Try L2 for L1 misses
        if l1_misses and self.redis_client:
            try:
                values = await self.redis_client.mget(l1_misses)
                for key, serialized in zip(l1_misses, values):
                    if serialized:
                        value = msgpack.unpackb(serialized, raw=False)
                        result[key] = value

                        # Promote to L1
                        if self.l1_cache:
                            ttl = config['data_categories'].get(category, {}).get('ttl', 60)
                            await self.l1_cache.set(key, value, ttl=ttl, category=category)
            except Exception as e:
                logger.error(f"L2 cache mget error: {e}")

        return result

    async def handle_invalidation(self, msg):
        """Handle cache invalidation requests"""
        try:
            data = json.loads(msg.data.decode())
            pattern = data.get('pattern', '')
            keys = data.get('keys', [])

            if pattern:
                await self.invalidate_pattern(pattern)
            elif keys:
                for key in keys:
                    await self.delete(key)

            logger.info(f"Cache invalidated: pattern={pattern}, keys={len(keys)}")

        except Exception as e:
            logger.error(f"Error handling invalidation: {e}")

    async def handle_warm_request(self, msg):
        """Handle cache warming requests"""
        try:
            data = json.loads(msg.data.decode())
            keys = data.get('keys', [])
            category = data.get('category', 'default')

            # Fetch data and cache it
            for key in keys:
                # This would normally fetch from the source
                # For now, we just log
                logger.info(f"Warming cache for key: {key}")

        except Exception as e:
            logger.error(f"Error handling warm request: {e}")

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        # Invalidate L1
        if self.l1_cache:
            async with self.l1_cache.lock:
                keys_to_remove = [k for k in self.l1_cache.cache if k.startswith(pattern.replace('*', ''))]
                for key in keys_to_remove:
                    await self.l1_cache.delete(key)

        # Invalidate L2
        if self.redis_client:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.error(f"Error invalidating pattern in L2: {e}")

    async def preload_data(self):
        """Preload frequently accessed data"""
        await asyncio.sleep(config['preload']['startup_delay'])
        logger.info("Starting cache preload...")

        for category, settings in config['data_categories'].items():
            if settings.get('preload', False):
                # This would normally fetch data from source
                logger.info(f"Preloading {category} data...")
                # Simulated preload
                for i in range(10):
                    key = f"{category}:{i}"
                    value = {category: f"preloaded_{i}"}
                    await self.set(key, value, category=category)

        logger.info("Cache preload completed")

    async def cleanup_loop(self):
        """Periodically cleanup expired entries"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Run every 30 seconds

                # Cleanup L1 expired entries
                if self.l1_cache:
                    await self.l1_cache.cleanup_expired()

                # Force garbage collection
                gc.collect()

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def warmup_loop(self):
        """Periodically warm cache with patterns"""
        while self.running:
            try:
                if not config['warming']['enabled']:
                    await asyncio.sleep(60)
                    continue

                await asyncio.sleep(config['warming']['interval'])

                for pattern in config['warming']['patterns']:
                    # This would normally fetch and cache matching data
                    logger.debug(f"Warming cache for pattern: {pattern}")

            except Exception as e:
                logger.error(f"Error in warmup loop: {e}")

    async def metrics_loop(self):
        """Update metrics periodically"""
        while self.running:
            try:
                await asyncio.sleep(10)

                # Update cache size metrics
                if self.l1_cache:
                    cache_size.labels(layer='l1').set(self.l1_cache.size_bytes)
                    cache_items.labels(layer='l1').set(len(self.l1_cache.cache))

                # Update hit ratio
                total_l1 = self.stats['l1_hits'] + self.stats['l1_misses']
                if total_l1 > 0:
                    l1_ratio = self.stats['l1_hits'] / total_l1
                    hit_ratio.labels(layer='l1').set(l1_ratio)

                total_l2 = self.stats['l2_hits'] + self.stats['l2_misses']
                if total_l2 > 0:
                    l2_ratio = self.stats['l2_hits'] / total_l2
                    hit_ratio.labels(layer='l2').set(l2_ratio)

            except Exception as e:
                logger.error(f"Error in metrics loop: {e}")

    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        total_requests = self.stats['l1_hits'] + self.stats['l1_misses']
        hit_ratio_val = self.stats['l1_hits'] / total_requests if total_requests > 0 else 0

        l1_size_mb = self.l1_cache.size_bytes / (1024 * 1024) if self.l1_cache else 0
        l1_items = len(self.l1_cache.cache) if self.l1_cache else 0

        return CacheStats(
            l1_hits=self.stats['l1_hits'],
            l1_misses=self.stats['l1_misses'],
            l2_hits=self.stats['l2_hits'],
            l2_misses=self.stats['l2_misses'],
            l1_size_mb=l1_size_mb,
            l2_items=l1_items,  # Using L1 items for now
            hit_ratio=hit_ratio_val,
            evictions=self.stats['evictions']
        )


# Service instance
cache_service = HotCacheService()


@app.on_event("startup")
async def startup_event():
    """Start the cache service on app startup"""
    await cache_service.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    await cache_service.stop()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Hot Cache",
        "version": "1.0.0",
        "status": "running",
        "description": "High-Performance Multi-Layer Caching Service"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    checks = {
        "l1_cache": cache_service.l1_cache is not None,
        "l2_cache": False,
        "nats": False,
        "service": cache_service.running
    }

    # Check L2 (Redis)
    try:
        if cache_service.redis_client:
            await cache_service.redis_client.ping()
            checks["l2_cache"] = True
    except:
        pass

    # Check NATS
    if cache_service.nc and cache_service.nc.is_connected:
        checks["nats"] = True

    is_healthy = all(checks.values())

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/cache/{key}")
async def get_cached_value(key: str, category: str = Query("default")):
    """Get value from cache"""
    value = await cache_service.get(key, category=category)

    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")

    return {"key": key, "value": value, "category": category}


@app.post("/cache/{key}")
async def set_cached_value(key: str, value: Dict[str, Any], category: str = Query("default"), ttl: Optional[int] = None):
    """Set value in cache"""
    await cache_service.set(key, value, category=category, ttl=ttl)
    return {"status": "cached", "key": key, "category": category}


@app.delete("/cache/{key}")
async def delete_cached_value(key: str):
    """Delete value from cache"""
    await cache_service.delete(key)
    return {"status": "deleted", "key": key}


@app.post("/cache/mget")
async def multi_get(keys: List[str], category: str = Query("default")):
    """Get multiple values at once"""
    values = await cache_service.mget(keys, category=category)
    return {"values": values, "found": len(values), "requested": len(keys)}


@app.post("/cache/invalidate")
async def invalidate_cache(pattern: Optional[str] = None, keys: Optional[List[str]] = None):
    """Invalidate cache entries"""
    if pattern:
        await cache_service.invalidate_pattern(pattern)
        return {"status": "invalidated", "pattern": pattern}
    elif keys:
        for key in keys:
            await cache_service.delete(key)
        return {"status": "invalidated", "keys": keys}
    else:
        raise HTTPException(status_code=400, detail="Provide pattern or keys")


@app.post("/cache/clear")
async def clear_cache():
    """Clear entire cache"""
    if cache_service.l1_cache:
        await cache_service.l1_cache.clear()

    if cache_service.redis_client:
        await cache_service.redis_client.flushdb()

    # Reset stats
    cache_service.stats = {
        'l1_hits': 0,
        'l1_misses': 0,
        'l2_hits': 0,
        'l2_misses': 0,
        'evictions': 0
    }

    return {"status": "cleared"}


@app.get("/stats")
async def get_stats():
    """Get cache statistics"""
    return cache_service.get_stats()


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)