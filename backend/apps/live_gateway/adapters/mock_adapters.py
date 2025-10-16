"""
Mock Venue Adapters (Simplified for MVP)
Phase 11: Live Trading Enablement
"""

import os
import logging
import asyncio
from typing import Dict, Optional
from datetime import datetime
from .base import BaseAdapter, OrderResult, ExecutionReport

logger = logging.getLogger(__name__)


class MockIBKRAdapter(BaseAdapter):
    """Mock IBKR adapter - paper-first safety"""

    def __init__(self, config: Dict):
        super().__init__('IBKR', config)
        self.paper_only = os.getenv('LIVE_ENABLE_IBKR') != 'true'
        self.orders: Dict[str, ExecutionReport] = {}
        logger.info(f"MockIBKRAdapter initialized: paper_only={self.paper_only}")

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
        """Submit order - refuses LIVE unless env var set"""

        if not self.paper_only:
            logger.warning("LIVE execution not implemented in mock adapter - would execute real order here")

        # Generate mock ext_order_id
        ext_order_id = f"IBKR_{datetime.utcnow().timestamp()}"

        # Store mock execution
        self.orders[ext_order_id] = ExecutionReport(
            ext_order_id=ext_order_id,
            status="FILLED",
            filled_qty=qty,
            avg_px=price or 0.0,
            timestamp=datetime.utcnow(),
            venue_msg=f"Mock IBKR {'PAPER' if self.paper_only else 'LIVE'} fill"
        )

        logger.info(f"IBKR order submitted: {ext_order_id} {side} {qty} {symbol} @ {price}")
        return OrderResult(ext_order_id=ext_order_id, status="ACCEPTED")

    async def cancel_order(self, ext_order_id: str) -> bool:
        """Cancel order"""
        if ext_order_id in self.orders:
            self.orders[ext_order_id].status = "CANCELLED"
            logger.info(f"IBKR order cancelled: {ext_order_id}")
            return True
        return False

    async def get_order_status(self, ext_order_id: str) -> Optional[ExecutionReport]:
        """Get order status"""
        return self.orders.get(ext_order_id)

    async def health_check(self) -> bool:
        """Health check"""
        return True


class MockAlpacaAdapter(BaseAdapter):
    """Mock Alpaca adapter - paper-first safety"""

    def __init__(self, config: Dict):
        super().__init__('ALPACA', config)
        self.paper_only = os.getenv('LIVE_ENABLE_ALPACA') != 'true'
        self.orders: Dict[str, ExecutionReport] = {}
        logger.info(f"MockAlpacaAdapter initialized: paper_only={self.paper_only}")

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
        """Submit order"""

        if not self.paper_only:
            logger.warning("LIVE execution not implemented in mock adapter - would execute real order here")

        ext_order_id = f"ALP_{datetime.utcnow().timestamp()}"

        self.orders[ext_order_id] = ExecutionReport(
            ext_order_id=ext_order_id,
            status="FILLED",
            filled_qty=qty,
            avg_px=price or 0.0,
            timestamp=datetime.utcnow(),
            venue_msg=f"Mock Alpaca {'PAPER' if self.paper_only else 'LIVE'} fill"
        )

        logger.info(f"ALPACA order submitted: {ext_order_id} {side} {qty} {symbol} @ {price}")
        return OrderResult(ext_order_id=ext_order_id, status="ACCEPTED")

    async def cancel_order(self, ext_order_id: str) -> bool:
        """Cancel order"""
        if ext_order_id in self.orders:
            self.orders[ext_order_id].status = "CANCELLED"
            return True
        return False

    async def get_order_status(self, ext_order_id: str) -> Optional[ExecutionReport]:
        """Get order status"""
        return self.orders.get(ext_order_id)

    async def health_check(self) -> bool:
        """Health check"""
        return True


class MockCCXTAdapter(BaseAdapter):
    """Mock CCXT adapter - paper-first safety"""

    def __init__(self, config: Dict):
        super().__init__('CCXT', config)
        self.paper_only = os.getenv('LIVE_ENABLE_CCXT') != 'true'
        self.orders: Dict[str, ExecutionReport] = {}
        logger.info(f"MockCCXTAdapter initialized: paper_only={self.paper_only}")

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
        """Submit order"""

        if not self.paper_only:
            logger.warning("LIVE execution not implemented in mock adapter - would execute real order here")

        ext_order_id = f"CCXT_{datetime.utcnow().timestamp()}"

        self.orders[ext_order_id] = ExecutionReport(
            ext_order_id=ext_order_id,
            status="FILLED",
            filled_qty=qty,
            avg_px=price or 0.0,
            timestamp=datetime.utcnow(),
            venue_msg=f"Mock CCXT {'PAPER' if self.paper_only else 'LIVE'} fill"
        )

        logger.info(f"CCXT order submitted: {ext_order_id} {side} {qty} {symbol} @ {price}")
        return OrderResult(ext_order_id=ext_order_id, status="ACCEPTED")

    async def cancel_order(self, ext_order_id: str) -> bool:
        """Cancel order"""
        if ext_order_id in self.orders:
            self.orders[ext_order_id].status = "CANCELLED"
            return True
        return False

    async def get_order_status(self, ext_order_id: str) -> Optional[ExecutionReport]:
        """Get order status"""
        return self.orders.get(ext_order_id)

    async def health_check(self) -> bool:
        """Health check"""
        return True
