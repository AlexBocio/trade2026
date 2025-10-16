"""
Base Adapter Interface
Phase 11: Live Trading Enablement
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class OrderResult(BaseModel):
    """Result of order submission"""
    ext_order_id: str
    status: str
    msg: Optional[str] = None


class ExecutionReport(BaseModel):
    """Execution report from venue"""
    ext_order_id: str
    status: str  # PENDING, FILLED, PARTIAL, REJECTED, CANCELLED
    filled_qty: float = 0.0
    avg_px: float = 0.0
    timestamp: datetime
    venue_msg: Optional[str] = None


class BaseAdapter(ABC):
    """Base class for venue adapters"""

    def __init__(self, venue: str, config: Dict):
        self.venue = venue
        self.config = config

    @abstractmethod
    async def submit_order(
        self,
        account_id: str,
        symbol: str,
        side: str,
        order_type: str,
        qty: float,
        price: Optional[float] = None,
        client_order_id: Optional[str] = None
    ) -> OrderResult:
        """Submit order to venue"""
        pass

    @abstractmethod
    async def cancel_order(self, ext_order_id: str) -> bool:
        """Cancel order at venue"""
        pass

    @abstractmethod
    async def get_order_status(self, ext_order_id: str) -> Optional[ExecutionReport]:
        """Get order status from venue"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if venue connection is healthy"""
        pass
