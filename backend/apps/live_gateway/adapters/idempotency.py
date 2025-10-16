"""
Idempotency Management
Phase 11: Live Trading Enablement
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import redis

logger = logging.getLogger(__name__)


class IdempotencyManager:
    """Manages idempotent order mapping"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.ttl = 86400 * 7  # 7 days

    def get_key(self, tenant: str, account_id: str, client_order_id: str) -> str:
        """Generate Redis key for idempotency"""
        return f"ltg:idem:{tenant}:{account_id}:{client_order_id}"

    def check_and_set(self, tenant: str, account_id: str, client_order_id: str, ext_order_id: str) -> Optional[str]:
        """
        Check if order already submitted, set if not

        Returns:
            Existing ext_order_id if duplicate, None if new
        """
        key = self.get_key(tenant, account_id, client_order_id)

        # Check if exists
        existing = self.redis.get(key)
        if existing:
            logger.warning(f"Duplicate order detected: {client_order_id} → {existing.decode('utf-8')}")
            return existing.decode('utf-8')

        # Set with TTL
        self.redis.setex(key, self.ttl, ext_order_id)
        logger.info(f"Idempotency recorded: {client_order_id} → {ext_order_id}")
        return None

    def get_external_id(self, tenant: str, account_id: str, client_order_id: str) -> Optional[str]:
        """Get external order ID for client order"""
        key = self.get_key(tenant, account_id, client_order_id)
        val = self.redis.get(key)
        return val.decode('utf-8') if val else None
