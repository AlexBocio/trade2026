"""
Deduplication for Market Ticks
Phase 7B: Data Lake Sinks
"""

import logging
from collections import OrderedDict
from typing import Set, Optional
import redis
import time

logger = logging.getLogger(__name__)


class DedupManager:
    """Two-tier deduplication: in-memory LRU + Valkey/Redis"""

    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 redis_db: int = 0, ttl_hours: int = 72, lru_size: int = 100000):
        """
        Initialize dedup manager

        Args:
            redis_host: Redis/Valkey host
            redis_port: Redis/Valkey port
            redis_db: Redis database number
            ttl_hours: TTL for Redis keys in hours
            lru_size: Max size of in-memory LRU cache
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.ttl_seconds = ttl_hours * 3600
        self.lru_size = lru_size

        # In-memory LRU cache
        self.lru_cache: OrderedDict = OrderedDict()

        # Redis client
        self.redis_client = None
        self.redis_connected = False

        # Stats
        self.stats = {
            'checked': 0,
            'duplicates': 0,
            'lru_hits': 0,
            'redis_hits': 0,
            'added': 0
        }

        # Skip Redis connection during init to avoid blocking
        logger.info(f"DedupManager initialized (lazy Redis connection to {redis_host}:{redis_port})")

    def _connect_redis(self):
        """Connect to Redis/Valkey"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            self.redis_client.ping()
            self.redis_connected = True
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}/{self.redis_db}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache only.")
            self.redis_connected = False

    def is_duplicate(self, hash_id: str) -> bool:
        """
        Check if hash_id is a duplicate

        Args:
            hash_id: Hash ID to check

        Returns:
            True if duplicate
        """
        self.stats['checked'] += 1

        # Check in-memory LRU first
        if hash_id in self.lru_cache:
            # Move to end (most recently used)
            self.lru_cache.move_to_end(hash_id)
            self.stats['lru_hits'] += 1
            self.stats['duplicates'] += 1
            return True

        # Lazy connect to Redis on first use
        if not self.redis_connected and self.redis_client is None:
            self._connect_redis()

        # Check Redis if connected
        if self.redis_connected:
            try:
                key = f"dedup:tick:{hash_id}"
                if self.redis_client.exists(key):
                    self.stats['redis_hits'] += 1
                    self.stats['duplicates'] += 1
                    # Add to LRU cache
                    self._add_to_lru(hash_id)
                    return True
            except Exception as e:
                logger.debug(f"Redis check failed: {e}")

        return False

    def add(self, hash_id: str) -> bool:
        """
        Add hash_id to dedup caches

        Args:
            hash_id: Hash ID to add

        Returns:
            True if added (not duplicate)
        """
        # Check if duplicate first
        if self.is_duplicate(hash_id):
            return False

        # Add to LRU cache
        self._add_to_lru(hash_id)

        # Add to Redis if connected
        if self.redis_connected:
            try:
                key = f"dedup:tick:{hash_id}"
                # Set with TTL
                self.redis_client.setex(key, self.ttl_seconds, "1")
            except Exception as e:
                logger.debug(f"Redis add failed: {e}")

        self.stats['added'] += 1
        return True

    def _add_to_lru(self, hash_id: str):
        """Add to LRU cache, evicting oldest if needed"""
        # Check size limit
        if len(self.lru_cache) >= self.lru_size:
            # Remove oldest (first item)
            self.lru_cache.popitem(last=False)

        # Add new item at end
        self.lru_cache[hash_id] = True

    def filter_duplicates(self, records: list) -> list:
        """
        Filter duplicate records

        Args:
            records: List of records with hash_id field

        Returns:
            List of unique records
        """
        unique_records = []

        for record in records:
            hash_id = record.get('hash_id') if isinstance(record, dict) else getattr(record, 'hash_id', None)

            if not hash_id:
                logger.warning("Record missing hash_id, skipping")
                continue

            if not self.is_duplicate(hash_id):
                unique_records.append(record)
                self.add(hash_id)

        return unique_records

    def get_stats(self) -> dict:
        """Get dedup statistics"""
        stats = self.stats.copy()
        stats['lru_size'] = len(self.lru_cache)
        stats['redis_connected'] = self.redis_connected
        if self.stats['checked'] > 0:
            stats['duplicate_rate'] = self.stats['duplicates'] / self.stats['checked']
            stats['lru_hit_rate'] = self.stats['lru_hits'] / self.stats['checked']
        return stats

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'checked': 0,
            'duplicates': 0,
            'lru_hits': 0,
            'redis_hits': 0,
            'added': 0
        }

    def clear_lru(self):
        """Clear in-memory LRU cache"""
        self.lru_cache.clear()
        logger.info("Cleared LRU cache")

    def health_check(self) -> bool:
        """Check if dedup manager is healthy"""
        if not self.redis_connected:
            # Try to reconnect
            self._connect_redis()

        return True  # Always return True - can work with LRU only