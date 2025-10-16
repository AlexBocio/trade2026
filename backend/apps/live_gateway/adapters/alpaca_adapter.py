"""
Alpaca Markets Adapter
Phase 11: Live Trading Enablement
"""

import os
import logging
import asyncio
from typing import Dict, Optional
from datetime import datetime

import httpx
from .base import BaseAdapter, OrderResult, ExecutionReport

logger = logging.getLogger(__name__)


class AlpacaAdapter(BaseAdapter):
    """Alpaca Markets adapter using REST API"""

    def __init__(self, config: Dict):
        super().__init__('ALPACA', config)

        # Safety: require explicit env var for LIVE
        self.paper_only = os.getenv('LIVE_ENABLE_ALPACA') != 'true'

        # API credentials
        self.api_key = os.getenv('ALPACA_API_KEY', '')
        self.api_secret = os.getenv('ALPACA_API_SECRET', '')

        # API endpoints
        if self.paper_only:
            self.base_url = 'https://paper-api.alpaca.markets'
        else:
            self.base_url = 'https://api.alpaca.markets'

        # HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                'APCA-API-KEY-ID': self.api_key,
                'APCA-API-SECRET-KEY': self.api_secret
            }
        )

        # Order tracking
        self.orders: Dict[str, ExecutionReport] = {}

        logger.info(f"AlpacaAdapter initialized: paper_only={self.paper_only}, base_url={self.base_url}")

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
        """Submit order to Alpaca"""

        # Safety check
        if not self.paper_only:
            logger.critical(f"LIVE execution attempt on Alpaca for {symbol} - requires LIVE_ENABLE_ALPACA=true")

        try:
            # Build order payload
            payload = {
                'symbol': symbol,
                'qty': int(qty),
                'side': side.lower(),
                'type': order_type.lower(),
                'time_in_force': 'day'
            }

            if order_type.upper() == 'LIMIT' and price:
                payload['limit_price'] = str(price)

            if client_order_id:
                payload['client_order_id'] = client_order_id

            # Submit order
            response = await self.client.post('/v2/orders', json=payload)
            response.raise_for_status()

            order_data = response.json()
            ext_order_id = f"ALP_{order_data['id']}"

            # Store execution report
            self.orders[ext_order_id] = ExecutionReport(
                ext_order_id=ext_order_id,
                status=order_data['status'].upper(),
                filled_qty=float(order_data.get('filled_qty', 0)),
                avg_px=float(order_data.get('filled_avg_price', 0) or 0),
                timestamp=datetime.utcnow(),
                venue_msg=f"Order placed: {order_data['id']}"
            )

            logger.info(f"Alpaca order submitted: {ext_order_id} {'PAPER' if self.paper_only else 'LIVE'}")

            return OrderResult(
                ext_order_id=ext_order_id,
                status="ACCEPTED",
                msg=f"Order placed: {order_data['id']}"
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Alpaca order submission failed: {e.response.text}")
            return OrderResult(
                ext_order_id=f"ERROR_{client_order_id}",
                status="REJECTED",
                msg=e.response.text
            )
        except Exception as e:
            logger.error(f"Alpaca order submission failed: {e}")
            return OrderResult(
                ext_order_id=f"ERROR_{client_order_id}",
                status="REJECTED",
                msg=str(e)
            )

    async def cancel_order(self, ext_order_id: str) -> bool:
        """Cancel order at Alpaca"""
        try:
            # Extract Alpaca order ID
            alpaca_order_id = ext_order_id.split('_')[1]

            # Cancel via API
            response = await self.client.delete(f'/v2/orders/{alpaca_order_id}')
            response.raise_for_status()

            # Update status
            if ext_order_id in self.orders:
                self.orders[ext_order_id].status = "CANCELLED"

            logger.info(f"Alpaca order cancelled: {ext_order_id}")
            return True

        except Exception as e:
            logger.error(f"Alpaca order cancellation failed: {e}")
            return False

    async def get_order_status(self, ext_order_id: str) -> Optional[ExecutionReport]:
        """Get order status from Alpaca"""
        try:
            # Extract Alpaca order ID
            alpaca_order_id = ext_order_id.split('_')[1]

            # Get order via API
            response = await self.client.get(f'/v2/orders/{alpaca_order_id}')
            response.raise_for_status()

            order_data = response.json()

            # Update execution report
            self.orders[ext_order_id] = ExecutionReport(
                ext_order_id=ext_order_id,
                status=order_data['status'].upper(),
                filled_qty=float(order_data.get('filled_qty', 0)),
                avg_px=float(order_data.get('filled_avg_price', 0) or 0),
                timestamp=datetime.utcnow(),
                venue_msg=order_data.get('status')
            )

            return self.orders[ext_order_id]

        except Exception as e:
            logger.error(f"Alpaca order status check failed: {e}")
            return self.orders.get(ext_order_id)

    async def health_check(self) -> bool:
        """Check if Alpaca connection is healthy"""
        try:
            # Check account endpoint
            response = await self.client.get('/v2/account')
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Alpaca health check failed: {e}")
            return False

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
