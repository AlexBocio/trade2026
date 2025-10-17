"""
Execution & Queueing Service (ExeQ)
Smart order routing and execution management
Phase 2: Priority 2 Services
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import uuid

import nats
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import redis
import yaml
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderStatus(Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    ROUTING = "ROUTING"
    SENT = "SENT"
    FILLED = "FILLED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class VenueType(Enum):
    BINANCE = "BINANCE"
    COINBASE = "COINBASE"
    FTX = "FTX"
    PAPER = "PAPER"
    MOCK = "MOCK"


@dataclass
class Order:
    order_id: str
    symbol: str
    side: str  # BUY/SELL
    quantity: float
    price: Optional[float]  # None for market orders
    order_type: str  # MARKET/LIMIT
    venue: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    filled_quantity: float = 0.0
    average_price: float = 0.0
    metadata: Dict[str, Any] = None


class SmartRouter:
    """Smart order routing logic"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.venue_priorities = config.get('venue_priorities', ['MOCK', 'PAPER'])
        self.routing_rules = config.get('routing_rules', {})

    def select_venue(self, order: Order) -> str:
        """Select best venue for order execution"""
        # Simple routing logic - can be enhanced
        symbol = order.symbol

        # Check if symbol has specific routing rules
        if symbol in self.routing_rules:
            return self.routing_rules[symbol]

        # Use default priority list
        for venue in self.venue_priorities:
            if self._check_venue_availability(venue):
                return venue

        return 'MOCK'  # Fallback to mock

    def _check_venue_availability(self, venue: str) -> bool:
        """Check if venue is available and healthy"""
        # TODO: Implement actual health checks
        return True

    def split_order(self, order: Order) -> List[Order]:
        """Split large orders across venues"""
        # Simple implementation - can be enhanced for actual order splitting
        return [order]


class ExecutionEngine:
    """Main execution engine"""

    def __init__(self, config_path: str = '/app/config.yaml'):
        self.config = self._load_config(config_path)
        self.nc = None
        self.redis_client = None
        self.router = SmartRouter(self.config)
        self.order_queue = asyncio.Queue()
        self.active_orders: Dict[str, Order] = {}
        self.stats = {
            'orders_received': 0,
            'orders_routed': 0,
            'orders_filled': 0,
            'orders_failed': 0,
            'total_volume': 0.0
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
                'venue_priorities': ['MOCK', 'PAPER'],
                'max_queue_size': 10000,
                'batch_size': 10,
                'health_port': 8095
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
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.config.get('redis_host')}")

        except Exception as e:
            logger.error(f"Failed to connect services: {e}")
            raise

    async def subscribe_orders(self):
        """Subscribe to order stream from OMS"""
        async def order_handler(msg):
            try:
                order_data = json.loads(msg.data.decode())
                logger.info(f"Received order: {order_data.get('order_id')}")

                # Create Order object
                order = Order(
                    order_id=order_data.get('order_id', str(uuid.uuid4())),
                    symbol=order_data['symbol'],
                    side=order_data['side'],
                    quantity=order_data['quantity'],
                    price=order_data.get('price'),
                    order_type=order_data.get('order_type', 'MARKET'),
                    venue=order_data.get('venue', 'AUTO'),
                    status=OrderStatus.PENDING,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    metadata=order_data.get('metadata', {})
                )

                # Add to queue
                await self.order_queue.put(order)
                self.stats['orders_received'] += 1

                # Store in Redis for tracking
                self.redis_client.hset(
                    f"order:{order.order_id}",
                    mapping={
                        'status': order.status.value,
                        'symbol': order.symbol,
                        'quantity': order.quantity,
                        'created_at': order.created_at.isoformat()
                    }
                )

            except Exception as e:
                logger.error(f"Error handling order: {e}")

        # Subscribe to order topics
        await self.nc.subscribe("orders.new", cb=order_handler)
        await self.nc.subscribe("orders.cancel", cb=order_handler)
        logger.info("Subscribed to order streams")

    async def process_queue(self):
        """Process order queue and route orders"""
        while True:
            try:
                # Get batch of orders
                orders = []
                for _ in range(min(self.config.get('batch_size', 10), self.order_queue.qsize())):
                    if not self.order_queue.empty():
                        order = await asyncio.wait_for(self.order_queue.get(), timeout=0.1)
                        orders.append(order)

                if orders:
                    await self._route_orders(orders)

                await asyncio.sleep(0.1)  # Small delay between batches

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing queue: {e}")
                await asyncio.sleep(1)

    async def _route_orders(self, orders: List[Order]):
        """Route orders to appropriate venues"""
        for order in orders:
            try:
                # Update status
                order.status = OrderStatus.ROUTING
                order.updated_at = datetime.utcnow()
                self.active_orders[order.order_id] = order

                # Select venue if AUTO
                if order.venue == 'AUTO':
                    order.venue = self.router.select_venue(order)

                # Split order if needed
                sub_orders = self.router.split_order(order)

                for sub_order in sub_orders:
                    await self._send_to_venue(sub_order)

                self.stats['orders_routed'] += 1

            except Exception as e:
                logger.error(f"Failed to route order {order.order_id}: {e}")
                order.status = OrderStatus.FAILED
                self.stats['orders_failed'] += 1

    async def _send_to_venue(self, order: Order):
        """Send order to specific venue"""
        try:
            # Prepare order message
            venue_order = {
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': order.quantity,
                'price': order.price,
                'order_type': order.order_type,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Publish to venue-specific topic
            topic = f"venue.{order.venue.lower()}.order"
            await self.nc.publish(topic, json.dumps(venue_order).encode())

            # Update status
            order.status = OrderStatus.SENT
            order.updated_at = datetime.utcnow()

            # Update Redis
            self.redis_client.hset(
                f"order:{order.order_id}",
                mapping={'status': order.status.value, 'venue': order.venue}
            )

            logger.info(f"Sent order {order.order_id} to {order.venue}")

        except Exception as e:
            logger.error(f"Failed to send order to venue: {e}")
            order.status = OrderStatus.FAILED

    async def handle_fills(self):
        """Handle fill notifications from venues"""
        async def fill_handler(msg):
            try:
                fill_data = json.loads(msg.data.decode())
                order_id = fill_data['order_id']

                if order_id in self.active_orders:
                    order = self.active_orders[order_id]

                    # Update order with fill
                    order.filled_quantity = fill_data.get('filled_quantity', order.quantity)
                    order.average_price = fill_data.get('price', order.price or 0)

                    if order.filled_quantity >= order.quantity:
                        order.status = OrderStatus.FILLED
                        self.stats['orders_filled'] += 1
                        del self.active_orders[order_id]
                    else:
                        order.status = OrderStatus.PARTIAL

                    order.updated_at = datetime.utcnow()

                    # Update Redis
                    self.redis_client.hset(
                        f"order:{order_id}",
                        mapping={
                            'status': order.status.value,
                            'filled_quantity': order.filled_quantity,
                            'average_price': order.average_price
                        }
                    )

                    # Publish fill event
                    await self.nc.publish(
                        "fills.confirmed",
                        json.dumps({
                            'order_id': order_id,
                            'status': order.status.value,
                            'filled_quantity': order.filled_quantity,
                            'price': order.average_price
                        }).encode()
                    )

                    self.stats['total_volume'] += order.filled_quantity * order.average_price

            except Exception as e:
                logger.error(f"Error handling fill: {e}")

        await self.nc.subscribe("venue.*.fill", cb=fill_handler)
        logger.info("Subscribed to fill notifications")

    def get_stats(self) -> dict:
        """Get execution statistics"""
        return {
            **self.stats,
            'active_orders': len(self.active_orders),
            'queue_size': self.order_queue.qsize()
        }

    async def run(self):
        """Run the execution engine"""
        await self.connect_services()
        await self.subscribe_orders()
        await self.handle_fills()

        # Start queue processor
        asyncio.create_task(self.process_queue())

        logger.info("Execution engine started")


# FastAPI app for health and metrics
app = FastAPI(title="ExeQ Service")
engine = None


@app.on_event("startup")
async def startup_event():
    global engine
    engine = ExecutionEngine()
    await engine.run()


@app.get("/health")
async def health():
    """Health check endpoint"""
    global engine
    if engine and engine.nc and engine.redis_client:
        try:
            engine.redis_client.ping()
            return {"status": "healthy", "service": "exeq"}
        except:
            pass
    return JSONResponse(status_code=503, content={"status": "unhealthy"})


@app.get("/stats")
async def stats():
    """Get execution statistics"""
    global engine
    if engine:
        return engine.get_stats()
    return {"error": "Engine not initialized"}


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get order status"""
    global engine
    if engine and engine.redis_client:
        order_data = engine.redis_client.hgetall(f"order:{order_id}")
        if order_data:
            return order_data
    raise HTTPException(status_code=404, detail="Order not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8095)