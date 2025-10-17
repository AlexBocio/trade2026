"""
Order Management System (OMS)
Core order lifecycle management and routing
Phase 2A: Critical Trading Core
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

import nats
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import redis
import yaml
import uvicorn
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderStatus(Enum):
    NEW = "NEW"
    PENDING_RISK = "PENDING_RISK"
    RISK_REJECTED = "RISK_REJECTED"
    ACCEPTED = "ACCEPTED"
    ROUTING = "ROUTING"
    SENT = "SENT"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class TimeInForce(Enum):
    DAY = "DAY"
    GTC = "GTC"  # Good Till Cancelled
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill
    GTD = "GTD"  # Good Till Date


@dataclass
class Order:
    order_id: str
    symbol: str
    side: str  # BUY/SELL
    quantity: float
    order_type: OrderType
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    account: str
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: TimeInForce = TimeInForce.DAY
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    remaining_quantity: float = 0.0
    commission: float = 0.0
    venue: Optional[str] = None
    external_order_id: Optional[str] = None
    risk_check_result: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class OrderManager:
    """Main order management engine"""

    def __init__(self, config_path: str = '/app/config.yaml'):
        self.config = self._load_config(config_path)
        self.nc = None
        self.redis_client = None

        # Order tracking
        self.orders: Dict[str, Order] = {}
        self.active_orders: Dict[str, Order] = {}
        self.order_history: List[Order] = []

        # Stats
        self.stats = {
            'orders_received': 0,
            'orders_accepted': 0,
            'orders_rejected': 0,
            'orders_filled': 0,
            'orders_cancelled': 0,
            'orders_failed': 0,
            'risk_rejects': 0,
            'total_volume': 0.0,
            'commission_collected': 0.0
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            return {
                'nats_url': 'nats://nats:4222',
                'redis_host': 'valkey',
                'redis_port': 6379,
                'risk_service_url': 'http://risk:8103',
                'exeq_service_url': 'http://exeq:8095',
                'max_orders_per_account': 100,
                'max_order_value': 1000000.0,
                'health_port': 8099
            }

    async def connect_services(self):
        """Connect to NATS and Redis"""
        try:
            # Connect to NATS
            self.nc = await nats.connect(self.config.get('nats_url', 'nats://nats:4222'))
            logger.info(f"Connected to NATS at {self.config.get('nats_url')}")

            # Connect to Redis/Valkey
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'valkey'),
                port=self.config.get('redis_port', 6379),
                db=4,  # Use db 4 for OMS
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.config.get('redis_host')}")

        except Exception as e:
            logger.error(f"Failed to connect services: {e}")
            raise

    async def subscribe_events(self):
        """Subscribe to order-related events"""

        # Subscribe to fill events
        async def fill_handler(msg):
            try:
                fill_data = json.loads(msg.data.decode())
                await self.handle_fill(fill_data)
            except Exception as e:
                logger.error(f"Error handling fill: {e}")

        # Subscribe to order cancellation requests
        async def cancel_handler(msg):
            try:
                cancel_data = json.loads(msg.data.decode())
                await self.handle_cancel(cancel_data)
            except Exception as e:
                logger.error(f"Error handling cancel: {e}")

        # Subscribe to order status updates
        async def status_handler(msg):
            try:
                status_data = json.loads(msg.data.decode())
                await self.handle_status_update(status_data)
            except Exception as e:
                logger.error(f"Error handling status update: {e}")

        await self.nc.subscribe("fills.confirmed", cb=fill_handler)
        await self.nc.subscribe("orders.cancel", cb=cancel_handler)
        await self.nc.subscribe("orders.status", cb=status_handler)

        logger.info("Subscribed to order events")

    async def submit_order(self, order_request: Dict[str, Any]) -> Order:
        """Submit a new order"""
        self.stats['orders_received'] += 1

        try:
            # Create order object
            order = Order(
                order_id=str(uuid.uuid4()),
                symbol=order_request['symbol'],
                side=order_request['side'].upper(),
                quantity=float(order_request['quantity']),
                order_type=OrderType[order_request.get('type', 'LIMIT').upper()],
                status=OrderStatus.NEW,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                account=order_request.get('account', 'default'),
                price=float(order_request.get('price', 0)) if order_request.get('price') else None,
                stop_price=float(order_request.get('stop_price', 0)) if order_request.get('stop_price') else None,
                time_in_force=TimeInForce[order_request.get('time_in_force', 'DAY').upper()],
                remaining_quantity=float(order_request['quantity']),
                metadata=order_request.get('metadata', {})
            )

            # Basic validation
            if not self._validate_order(order):
                order.status = OrderStatus.REJECTED
                order.error_message = "Order validation failed"
                self.stats['orders_rejected'] += 1
                await self._store_order(order)
                raise ValueError("Order validation failed")

            # Store order
            self.orders[order.order_id] = order
            await self._store_order(order)

            # Risk check
            order.status = OrderStatus.PENDING_RISK
            order.updated_at = datetime.utcnow()

            risk_result = await self._check_risk(order)

            if not risk_result.get('approved', False):
                order.status = OrderStatus.RISK_REJECTED
                order.error_message = risk_result.get('reason', 'Risk check failed')
                order.risk_check_result = risk_result
                self.stats['risk_rejects'] += 1
                self.stats['orders_rejected'] += 1
                await self._store_order(order)

                # Publish rejection event
                await self._publish_order_event(order, 'rejected')

                return order

            # Risk approved
            order.status = OrderStatus.ACCEPTED
            order.risk_check_result = risk_result
            order.updated_at = datetime.utcnow()
            self.stats['orders_accepted'] += 1

            # Add to active orders
            self.active_orders[order.order_id] = order

            # Store updated order
            await self._store_order(order)

            # Route to execution
            await self._route_order(order)

            # Publish acceptance event
            await self._publish_order_event(order, 'accepted')

            logger.info(f"Order {order.order_id} accepted and routed")

            return order

        except Exception as e:
            logger.error(f"Failed to submit order: {e}")
            if 'order' in locals():
                order.status = OrderStatus.FAILED
                order.error_message = str(e)
                await self._store_order(order)
                self.stats['orders_failed'] += 1
            raise

    def _validate_order(self, order: Order) -> bool:
        """Validate order parameters"""
        # Symbol validation
        if not order.symbol or len(order.symbol) < 3:
            return False

        # Quantity validation
        if order.quantity <= 0:
            return False

        # Side validation
        if order.side not in ['BUY', 'SELL']:
            return False

        # Price validation for limit orders
        if order.order_type == OrderType.LIMIT and (not order.price or order.price <= 0):
            return False

        # Account validation
        if not order.account:
            return False

        # Check max orders per account
        account_orders = [o for o in self.active_orders.values() if o.account == order.account]
        if len(account_orders) >= self.config.get('max_orders_per_account', 100):
            return False

        # Check max order value
        order_value = order.quantity * (order.price or 0)
        if order_value > self.config.get('max_order_value', 1000000.0):
            return False

        return True

    async def _check_risk(self, order: Order) -> Dict[str, Any]:
        """Check order with risk service"""
        try:
            # Prepare risk check request
            risk_request = {
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': order.quantity,
                'price': order.price,
                'order_type': order.order_type.value,
                'account': order.account,
                'metadata': order.metadata
            }

            # Make request-reply call to risk service via NATS
            request_data = json.dumps(risk_request).encode()

            try:
                response = await self.nc.request(
                    "risk.check.order",
                    request_data,
                    timeout=1.0  # 1 second timeout
                )

                result = json.loads(response.data.decode())
                logger.info(f"Risk check for {order.order_id}: {result.get('approved')}")
                return result

            except asyncio.TimeoutError:
                logger.error("Risk service timeout")
                return {
                    'approved': False,
                    'reason': 'Risk service timeout',
                    'risk_level': 'UNKNOWN'
                }

        except Exception as e:
            logger.error(f"Risk check failed: {e}")
            return {
                'approved': False,
                'reason': f'Risk check error: {str(e)}',
                'risk_level': 'ERROR'
            }

    async def _route_order(self, order: Order):
        """Route order to execution service"""
        try:
            order.status = OrderStatus.ROUTING
            order.updated_at = datetime.utcnow()

            # Prepare order for execution
            exec_order = {
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': order.quantity,
                'price': order.price,
                'order_type': order.order_type.value,
                'time_in_force': order.time_in_force.value,
                'account': order.account,
                'venue': order.venue or 'AUTO',
                'metadata': order.metadata
            }

            # Publish to execution queue
            await self.nc.publish(
                "orders.new",
                json.dumps(exec_order).encode()
            )

            order.status = OrderStatus.SENT
            order.updated_at = datetime.utcnow()
            await self._store_order(order)

            logger.info(f"Order {order.order_id} routed to execution")

        except Exception as e:
            logger.error(f"Failed to route order {order.order_id}: {e}")
            order.status = OrderStatus.FAILED
            order.error_message = f"Routing failed: {str(e)}"
            await self._store_order(order)

    async def handle_fill(self, fill_data: Dict[str, Any]):
        """Handle fill event from execution"""
        try:
            order_id = fill_data.get('order_id')
            if order_id not in self.orders:
                logger.warning(f"Fill for unknown order {order_id}")
                return

            order = self.orders[order_id]

            # Update fill information
            filled_qty = float(fill_data.get('filled_quantity', 0))
            fill_price = float(fill_data.get('price', 0))

            # Update average fill price
            if order.filled_quantity == 0:
                order.average_fill_price = fill_price
            else:
                total_value = (order.filled_quantity * order.average_fill_price) + (filled_qty * fill_price)
                order.filled_quantity += filled_qty
                order.average_fill_price = total_value / order.filled_quantity

            order.filled_quantity += filled_qty
            order.remaining_quantity = order.quantity - order.filled_quantity
            order.commission += float(fill_data.get('commission', 0))

            # Update status
            if order.remaining_quantity <= 0:
                order.status = OrderStatus.FILLED
                self.stats['orders_filled'] += 1

                # Remove from active orders
                if order_id in self.active_orders:
                    del self.active_orders[order_id]

                # Add to history
                self.order_history.append(order)
                if len(self.order_history) > 1000:
                    self.order_history.pop(0)

            else:
                order.status = OrderStatus.PARTIALLY_FILLED

            order.updated_at = datetime.utcnow()

            # Update volume stats
            self.stats['total_volume'] += filled_qty * fill_price
            self.stats['commission_collected'] += float(fill_data.get('commission', 0))

            # Store updated order
            await self._store_order(order)

            # Publish fill event
            await self._publish_order_event(order, 'fill')

            # Notify PTRC for position tracking
            await self.nc.publish(
                "fills.confirmed",
                json.dumps({
                    'order_id': order_id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'quantity': filled_qty,
                    'price': fill_price,
                    'account': order.account,
                    'timestamp': datetime.utcnow().isoformat()
                }).encode()
            )

            logger.info(f"Order {order_id} filled: {filled_qty} @ {fill_price}")

        except Exception as e:
            logger.error(f"Failed to handle fill: {e}")

    async def handle_cancel(self, cancel_data: Dict[str, Any]):
        """Handle order cancellation request"""
        try:
            order_id = cancel_data.get('order_id')
            if order_id not in self.orders:
                logger.warning(f"Cancel request for unknown order {order_id}")
                return

            order = self.orders[order_id]

            # Check if order can be cancelled
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                logger.warning(f"Cannot cancel order {order_id} in status {order.status}")
                return

            # Send cancellation to execution
            await self.nc.publish(
                "orders.cancel",
                json.dumps({'order_id': order_id}).encode()
            )

            # Update order status
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.utcnow()
            self.stats['orders_cancelled'] += 1

            # Remove from active orders
            if order_id in self.active_orders:
                del self.active_orders[order_id]

            # Store updated order
            await self._store_order(order)

            # Publish cancellation event
            await self._publish_order_event(order, 'cancelled')

            logger.info(f"Order {order_id} cancelled")

        except Exception as e:
            logger.error(f"Failed to handle cancel: {e}")

    async def handle_status_update(self, status_data: Dict[str, Any]):
        """Handle order status update from execution"""
        try:
            order_id = status_data.get('order_id')
            if order_id not in self.orders:
                return

            order = self.orders[order_id]

            # Update status
            new_status = status_data.get('status')
            if new_status:
                order.status = OrderStatus[new_status]
                order.updated_at = datetime.utcnow()

                # Update other fields if provided
                if 'external_order_id' in status_data:
                    order.external_order_id = status_data['external_order_id']
                if 'venue' in status_data:
                    order.venue = status_data['venue']
                if 'error_message' in status_data:
                    order.error_message = status_data['error_message']

                await self._store_order(order)
                logger.info(f"Order {order_id} status updated to {new_status}")

        except Exception as e:
            logger.error(f"Failed to handle status update: {e}")

    async def _store_order(self, order: Order):
        """Store order in Redis"""
        try:
            order_data = {
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': order.quantity,
                'order_type': order.order_type.value,
                'status': order.status.value,
                'account': order.account,
                'price': order.price or 0,
                'filled_quantity': order.filled_quantity,
                'average_fill_price': order.average_fill_price,
                'remaining_quantity': order.remaining_quantity,
                'commission': order.commission,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            }

            # Store in Redis
            self.redis_client.hset(f"order:{order.order_id}", mapping=order_data)

            # Set expiry for completed orders
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                self.redis_client.expire(f"order:{order.order_id}", 86400)  # 24 hours

            # Update account orders index
            self.redis_client.sadd(f"account:{order.account}:orders", order.order_id)

        except Exception as e:
            logger.error(f"Failed to store order: {e}")

    async def _publish_order_event(self, order: Order, event_type: str):
        """Publish order event to NATS"""
        try:
            event_data = {
                'event_type': event_type,
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side,
                'status': order.status.value,
                'quantity': order.quantity,
                'price': order.price,
                'filled_quantity': order.filled_quantity,
                'average_fill_price': order.average_fill_price,
                'account': order.account,
                'timestamp': datetime.utcnow().isoformat()
            }

            await self.nc.publish(
                f"orders.{event_type}",
                json.dumps(event_data).encode()
            )

        except Exception as e:
            logger.error(f"Failed to publish order event: {e}")

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self.orders.get(order_id)

    def get_account_orders(self, account: str) -> List[Order]:
        """Get all orders for an account"""
        return [o for o in self.orders.values() if o.account == account]

    def get_active_orders(self) -> List[Order]:
        """Get all active orders"""
        return list(self.active_orders.values())

    def get_stats(self) -> Dict[str, Any]:
        """Get OMS statistics"""
        return {
            **self.stats,
            'total_orders': len(self.orders),
            'active_orders': len(self.active_orders),
            'order_history_size': len(self.order_history)
        }

    async def run(self):
        """Run the OMS"""
        await self.connect_services()
        await self.subscribe_events()
        logger.info("OMS started")


# FastAPI app for REST API
app = FastAPI(title="OMS Service")
oms = None


@app.on_event("startup")
async def startup_event():
    global oms
    oms = OrderManager()
    await oms.run()


@app.get("/health")
async def health():
    """Health check endpoint"""
    global oms
    if oms and oms.nc and oms.redis_client:
        try:
            oms.redis_client.ping()
            return {"status": "healthy", "service": "oms"}
        except:
            pass
    return JSONResponse(status_code=503, content={"status": "unhealthy"})


@app.post("/orders")
async def submit_order(order_request: dict):
    """Submit a new order"""
    global oms
    if not oms:
        raise HTTPException(status_code=503, detail="OMS not initialized")

    try:
        order = await oms.submit_order(order_request)
        return {
            'order_id': order.order_id,
            'status': order.status.value,
            'symbol': order.symbol,
            'side': order.side,
            'quantity': order.quantity,
            'price': order.price,
            'error_message': order.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get order by ID"""
    global oms
    if not oms:
        raise HTTPException(status_code=503, detail="OMS not initialized")

    order = oms.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        'order_id': order.order_id,
        'status': order.status.value,
        'symbol': order.symbol,
        'side': order.side,
        'quantity': order.quantity,
        'price': order.price,
        'filled_quantity': order.filled_quantity,
        'average_fill_price': order.average_fill_price,
        'remaining_quantity': order.remaining_quantity,
        'commission': order.commission,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat()
    }


@app.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel an order"""
    global oms
    if not oms:
        raise HTTPException(status_code=503, detail="OMS not initialized")

    await oms.handle_cancel({'order_id': order_id})
    return {"status": "cancellation requested", "order_id": order_id}


@app.get("/orders")
async def get_orders(account: Optional[str] = None, active_only: bool = False):
    """Get orders"""
    global oms
    if not oms:
        raise HTTPException(status_code=503, detail="OMS not initialized")

    if account:
        orders = oms.get_account_orders(account)
    elif active_only:
        orders = oms.get_active_orders()
    else:
        orders = list(oms.orders.values())

    return [{
        'order_id': o.order_id,
        'status': o.status.value,
        'symbol': o.symbol,
        'side': o.side,
        'quantity': o.quantity,
        'price': o.price,
        'filled_quantity': o.filled_quantity
    } for o in orders]


@app.get("/stats")
async def get_stats():
    """Get OMS statistics"""
    global oms
    if oms:
        return oms.get_stats()
    return {"error": "OMS not initialized"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8099)