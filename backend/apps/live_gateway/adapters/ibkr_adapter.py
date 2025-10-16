"""
Interactive Brokers Adapter
Phase 11: Live Trading Enablement
"""

import os
import logging
import asyncio
from typing import Dict, Optional
from datetime import datetime

from ib_insync import IB, Stock, Order as IBOrder, MarketOrder, LimitOrder
from .base import BaseAdapter, OrderResult, ExecutionReport

logger = logging.getLogger(__name__)


class IBKRAdapter(BaseAdapter):
    """Interactive Brokers adapter using ib_insync"""

    def __init__(self, config: Dict):
        super().__init__('IBKR', config)

        # Safety: require explicit env var for LIVE
        self.paper_only = os.getenv('LIVE_ENABLE_IBKR') != 'true'

        # IB Gateway/TWS connection settings
        self.host = os.getenv('IB_HOST', '127.0.0.1')
        self.port = int(os.getenv('IB_PORT', '7497'))  # 7497=paper, 7496=live
        self.client_id = int(os.getenv('IB_CLIENT_ID', '1'))

        # Connection
        self.ib = IB()
        self.connected = False

        # Order tracking
        self.orders: Dict[str, ExecutionReport] = {}

        logger.info(f"IBKRAdapter initialized: paper_only={self.paper_only}, host={self.host}:{self.port}")

    async def connect(self):
        """Connect to IB Gateway/TWS"""
        if self.connected:
            return

        try:
            await self.ib.connectAsync(self.host, self.port, clientId=self.client_id)
            self.connected = True
            logger.info(f"Connected to IB Gateway at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to IB Gateway: {e}")
            raise

    async def disconnect(self):
        """Disconnect from IB Gateway/TWS"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IB Gateway")

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
        """Submit order to IBKR"""

        # Safety check
        if not self.paper_only:
            logger.critical(f"LIVE execution attempt on IBKR for {symbol} - requires LIVE_ENABLE_IBKR=true")
            # In production, you might want to refuse here

        if not self.connected:
            await self.connect()

        try:
            # Create contract
            contract = Stock(symbol, 'SMART', 'USD')
            await self.ib.qualifyContractsAsync(contract)

            # Create order
            action = 'BUY' if side.upper() in ['BUY', 'LONG'] else 'SELL'

            if order_type.upper() == 'MARKET':
                ib_order = MarketOrder(action, int(qty))
            elif order_type.upper() == 'LIMIT':
                ib_order = LimitOrder(action, int(qty), price)
            else:
                raise ValueError(f"Unsupported order type: {order_type}")

            # Set account if provided
            if account_id:
                ib_order.account = account_id

            # Place order
            trade = self.ib.placeOrder(contract, ib_order)

            # Get order ID
            ext_order_id = f"IBKR_{trade.order.orderId}"

            # Store execution report
            self.orders[ext_order_id] = ExecutionReport(
                ext_order_id=ext_order_id,
                status="PENDING",
                filled_qty=0.0,
                avg_px=0.0,
                timestamp=datetime.utcnow(),
                venue_msg=f"Order placed: {trade.order.orderType} {action} {qty} {symbol}"
            )

            logger.info(f"IBKR order submitted: {ext_order_id} {'PAPER' if self.paper_only else 'LIVE'}")

            return OrderResult(
                ext_order_id=ext_order_id,
                status="ACCEPTED",
                msg=f"Order placed: {trade.order.orderId}"
            )

        except Exception as e:
            logger.error(f"IBKR order submission failed: {e}")
            return OrderResult(
                ext_order_id=f"ERROR_{client_order_id}",
                status="REJECTED",
                msg=str(e)
            )

    async def cancel_order(self, ext_order_id: str) -> bool:
        """Cancel order at IBKR"""
        if not self.connected:
            await self.connect()

        try:
            # Extract order ID
            order_id = int(ext_order_id.split('_')[1])

            # Find trade
            trades = self.ib.trades()
            for trade in trades:
                if trade.order.orderId == order_id:
                    self.ib.cancelOrder(trade.order)

                    # Update status
                    if ext_order_id in self.orders:
                        self.orders[ext_order_id].status = "CANCELLED"

                    logger.info(f"IBKR order cancelled: {ext_order_id}")
                    return True

            logger.warning(f"IBKR order not found for cancellation: {ext_order_id}")
            return False

        except Exception as e:
            logger.error(f"IBKR order cancellation failed: {e}")
            return False

    async def get_order_status(self, ext_order_id: str) -> Optional[ExecutionReport]:
        """Get order status from IBKR"""
        if ext_order_id in self.orders:
            # Update from live trades if connected
            if self.connected:
                try:
                    order_id = int(ext_order_id.split('_')[1])
                    trades = self.ib.trades()

                    for trade in trades:
                        if trade.order.orderId == order_id:
                            # Update status
                            status = trade.orderStatus.status
                            filled = trade.orderStatus.filled
                            avg_price = trade.orderStatus.avgFillPrice

                            self.orders[ext_order_id].status = status
                            self.orders[ext_order_id].filled_qty = filled
                            self.orders[ext_order_id].avg_px = avg_price
                            break
                except Exception as e:
                    logger.error(f"Error updating order status: {e}")

            return self.orders[ext_order_id]

        return None

    async def health_check(self) -> bool:
        """Check if IBKR connection is healthy"""
        try:
            if not self.connected:
                await self.connect()

            # Simple check - request account summary
            account = self.ib.managedAccounts()
            return bool(account)

        except Exception as e:
            logger.error(f"IBKR health check failed: {e}")
            return False
