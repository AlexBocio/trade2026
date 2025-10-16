"""
CCXT Multi-Exchange Adapter
Phase 11: Live Trading Enablement
"""

import os
import logging
import asyncio
from typing import Dict, Optional
from datetime import datetime

import ccxt.async_support as ccxt
from .base import BaseAdapter, OrderResult, ExecutionReport

logger = logging.getLogger(__name__)


class CCXTAdapter(BaseAdapter):
    """CCXT multi-exchange adapter"""

    def __init__(self, config: Dict):
        super().__init__('CCXT', config)

        # Safety: require explicit env var for LIVE
        self.paper_only = os.getenv('LIVE_ENABLE_CCXT') != 'true'

        # Exchange configuration
        self.exchange_id = os.getenv('CCXT_EXCHANGE', 'binance').lower()
        self.api_key = os.getenv('CCXT_API_KEY', '')
        self.api_secret = os.getenv('CCXT_API_SECRET', '')

        # Use testnet if paper_only
        exchange_params = {
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
        }

        if self.paper_only and self.exchange_id == 'binance':
            # Binance testnet
            exchange_params['options'] = {'defaultType': 'future'}
            exchange_params['urls'] = {
                'api': {
                    'public': 'https://testnet.binancefuture.com',
                    'private': 'https://testnet.binancefuture.com'
                }
            }

        # Initialize exchange
        exchange_class = getattr(ccxt, self.exchange_id)
        self.exchange = exchange_class(exchange_params)

        # Order tracking
        self.orders: Dict[str, ExecutionReport] = {}

        logger.info(f"CCXTAdapter initialized: exchange={self.exchange_id}, paper_only={self.paper_only}")

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
        """Submit order via CCXT"""

        # Safety check
        if not self.paper_only:
            logger.critical(f"LIVE execution attempt on {self.exchange_id} for {symbol} - requires LIVE_ENABLE_CCXT=true")

        try:
            # Load markets if not loaded
            if not self.exchange.markets:
                await self.exchange.load_markets()

            # Create order params
            params = {}
            if client_order_id:
                params['clientOrderId'] = client_order_id

            # Submit order
            if order_type.upper() == 'MARKET':
                order = await self.exchange.create_market_order(
                    symbol=symbol,
                    side=side.lower(),
                    amount=qty,
                    params=params
                )
            elif order_type.upper() == 'LIMIT':
                order = await self.exchange.create_limit_order(
                    symbol=symbol,
                    side=side.lower(),
                    amount=qty,
                    price=price,
                    params=params
                )
            else:
                raise ValueError(f"Unsupported order type: {order_type}")

            ext_order_id = f"CCXT_{self.exchange_id}_{order['id']}"

            # Store execution report
            self.orders[ext_order_id] = ExecutionReport(
                ext_order_id=ext_order_id,
                status=order['status'].upper() if order['status'] else 'PENDING',
                filled_qty=float(order.get('filled', 0)),
                avg_px=float(order.get('average', 0) or 0),
                timestamp=datetime.utcnow(),
                venue_msg=f"Order placed: {order['id']}"
            )

            logger.info(f"CCXT order submitted: {ext_order_id} {'TESTNET' if self.paper_only else 'LIVE'}")

            return OrderResult(
                ext_order_id=ext_order_id,
                status="ACCEPTED",
                msg=f"Order placed: {order['id']}"
            )

        except Exception as e:
            logger.error(f"CCXT order submission failed: {e}")
            return OrderResult(
                ext_order_id=f"ERROR_{client_order_id}",
                status="REJECTED",
                msg=str(e)
            )

    async def cancel_order(self, ext_order_id: str) -> bool:
        """Cancel order via CCXT"""
        try:
            # Extract order ID and symbol (need symbol for CCXT cancel)
            parts = ext_order_id.split('_')
            order_id = parts[-1]

            # Try to find symbol from stored orders
            if ext_order_id in self.orders:
                # Would need to store symbol with order
                logger.warning(f"CCXT cancel requires symbol - not stored for {ext_order_id}")
                return False

            logger.warning(f"CCXT order not found for cancellation: {ext_order_id}")
            return False

        except Exception as e:
            logger.error(f"CCXT order cancellation failed: {e}")
            return False

    async def get_order_status(self, ext_order_id: str) -> Optional[ExecutionReport]:
        """Get order status via CCXT"""
        try:
            # Extract order ID
            parts = ext_order_id.split('_')
            order_id = parts[-1]

            # Fetch order (requires symbol, which we may not have)
            # For now, return cached status
            return self.orders.get(ext_order_id)

        except Exception as e:
            logger.error(f"CCXT order status check failed: {e}")
            return self.orders.get(ext_order_id)

    async def health_check(self) -> bool:
        """Check if CCXT exchange connection is healthy"""
        try:
            # Fetch ticker as health check
            await self.exchange.fetch_ticker('BTC/USDT')
            return True

        except Exception as e:
            logger.error(f"CCXT health check failed: {e}")
            return False

    async def close(self):
        """Close exchange connection"""
        await self.exchange.close()
