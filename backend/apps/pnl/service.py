"""
P&L (Profit & Loss) Calculation Service
Real-time P&L calculation and position valuation
Phase 2: Priority 2 Services
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import statistics

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


@dataclass
class Position:
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    side: str  # LONG/SHORT
    opened_at: datetime
    updated_at: datetime
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    fees: float = 0.0


@dataclass
class PnLSnapshot:
    timestamp: datetime
    total_realized: float
    total_unrealized: float
    total_pnl: float
    positions_count: int
    winning_positions: int
    losing_positions: int
    largest_winner: float
    largest_loser: float
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None


class PnLCalculator:
    """P&L calculation engine"""

    def __init__(self, config_path: str = '/app/config.yaml'):
        self.config = self._load_config(config_path)
        self.nc = None
        self.redis_client = None
        self.questdb_client = None

        # Position tracking
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []

        # P&L tracking
        self.daily_pnl: List[float] = []
        self.pnl_history: List[PnLSnapshot] = []
        self.current_snapshot: Optional[PnLSnapshot] = None

        # Price cache
        self.price_cache: Dict[str, float] = {}

        # Stats
        self.stats = {
            'positions_opened': 0,
            'positions_closed': 0,
            'total_realized': 0.0,
            'total_unrealized': 0.0,
            'total_fees': 0.0,
            'win_rate': 0.0,
            'average_win': 0.0,
            'average_loss': 0.0,
            'profit_factor': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'peak_balance': 0.0
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
                'questdb_url': 'http://questdb:9000',
                'update_interval': 1.0,
                'snapshot_interval': 60.0,
                'health_port': 8100
            }

    async def connect_services(self):
        """Connect to NATS, Redis, and QuestDB"""
        try:
            # Connect to NATS
            self.nc = await nats.connect(self.config.get('nats_url', 'nats://nats:4222'))
            logger.info(f"Connected to NATS at {self.config.get('nats_url')}")

            # Connect to Redis/Valkey
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'valkey'),
                port=self.config.get('redis_port', 6379),
                db=2,  # Use db 2 for P&L
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.config.get('redis_host')}")

            # QuestDB client
            self.questdb_url = self.config.get('questdb_url', 'http://questdb:9000')
            logger.info(f"QuestDB configured at {self.questdb_url}")

        except Exception as e:
            logger.error(f"Failed to connect services: {e}")
            raise

    async def subscribe_events(self):
        """Subscribe to trading events"""

        # Subscribe to fill events
        async def fill_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await self.handle_fill(data)
            except Exception as e:
                logger.error(f"Error handling fill: {e}")

        # Subscribe to price updates
        async def price_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                symbol = data.get('symbol')
                price = data.get('price') or data.get('last')
                if symbol and price:
                    self.price_cache[symbol] = float(price)
                    await self.update_position_prices(symbol, float(price))
            except Exception as e:
                logger.error(f"Error handling price update: {e}")

        await self.nc.subscribe("fills.confirmed", cb=fill_handler)
        await self.nc.subscribe("market.tick.*", cb=price_handler)
        logger.info("Subscribed to fill and price events")

    async def handle_fill(self, fill_data: dict):
        """Handle fill event and update positions"""
        try:
            symbol = fill_data['symbol']
            side = fill_data['side']  # BUY/SELL
            quantity = float(fill_data['quantity'])
            price = float(fill_data['price'])
            fees = float(fill_data.get('fees', 0))
            order_id = fill_data.get('order_id')

            # Check if we have an existing position
            position_key = f"{symbol}_{side}"

            if position_key in self.positions:
                # Update existing position
                position = self.positions[position_key]

                # Calculate average price for additional quantity
                total_quantity = position.quantity + quantity
                total_value = (position.quantity * position.average_price) + (quantity * price)
                position.average_price = total_value / total_quantity
                position.quantity = total_quantity
                position.fees += fees
                position.updated_at = datetime.utcnow()

            else:
                # Create new position
                position = Position(
                    symbol=symbol,
                    quantity=quantity,
                    average_price=price,
                    current_price=price,
                    side='LONG' if side == 'BUY' else 'SHORT',
                    opened_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    fees=fees
                )
                self.positions[position_key] = position
                self.stats['positions_opened'] += 1

            # Update P&L
            await self.calculate_pnl()

            # Store in Redis
            await self.store_position(position)

            # Publish P&L update
            await self.publish_pnl_update(symbol)

            logger.info(f"Processed fill for {symbol}: {quantity} @ {price}")

        except Exception as e:
            logger.error(f"Failed to handle fill: {e}")

    async def update_position_prices(self, symbol: str, price: float):
        """Update current price for positions"""
        updated = False
        for key, position in self.positions.items():
            if position.symbol == symbol:
                position.current_price = price
                position.updated_at = datetime.utcnow()
                updated = True

        if updated:
            await self.calculate_pnl()

    async def calculate_pnl(self):
        """Calculate P&L for all positions"""
        total_realized = 0.0
        total_unrealized = 0.0
        winning_positions = 0
        losing_positions = 0
        largest_winner = 0.0
        largest_loser = 0.0

        for position in self.positions.values():
            # Calculate unrealized P&L
            if position.side == 'LONG':
                position.unrealized_pnl = (
                    (position.current_price - position.average_price) * position.quantity
                ) - position.fees
            else:  # SHORT
                position.unrealized_pnl = (
                    (position.average_price - position.current_price) * position.quantity
                ) - position.fees

            total_unrealized += position.unrealized_pnl

            if position.unrealized_pnl > 0:
                winning_positions += 1
                largest_winner = max(largest_winner, position.unrealized_pnl)
            else:
                losing_positions += 1
                largest_loser = min(largest_loser, position.unrealized_pnl)

        # Add realized P&L from closed positions
        total_realized = self.stats['total_realized']

        # Create snapshot
        self.current_snapshot = PnLSnapshot(
            timestamp=datetime.utcnow(),
            total_realized=total_realized,
            total_unrealized=total_unrealized,
            total_pnl=total_realized + total_unrealized,
            positions_count=len(self.positions),
            winning_positions=winning_positions,
            losing_positions=losing_positions,
            largest_winner=largest_winner,
            largest_loser=largest_loser,
            sharpe_ratio=self.calculate_sharpe_ratio(),
            max_drawdown=self.stats['max_drawdown']
        )

        # Update stats
        self.stats['total_unrealized'] = total_unrealized

        # Calculate drawdown
        current_balance = total_realized + total_unrealized
        if current_balance > self.stats['peak_balance']:
            self.stats['peak_balance'] = current_balance

        if self.stats['peak_balance'] > 0:
            drawdown = (self.stats['peak_balance'] - current_balance) / self.stats['peak_balance']
            self.stats['current_drawdown'] = drawdown
            self.stats['max_drawdown'] = max(self.stats['max_drawdown'], drawdown)

    def calculate_sharpe_ratio(self) -> Optional[float]:
        """Calculate Sharpe ratio from daily returns"""
        if len(self.daily_pnl) < 2:
            return None

        try:
            returns = []
            for i in range(1, len(self.daily_pnl)):
                if self.daily_pnl[i-1] != 0:
                    returns.append((self.daily_pnl[i] - self.daily_pnl[i-1]) / abs(self.daily_pnl[i-1]))

            if not returns:
                return None

            avg_return = statistics.mean(returns)
            std_return = statistics.stdev(returns) if len(returns) > 1 else 0

            if std_return == 0:
                return None

            # Annualized Sharpe ratio (assuming daily returns)
            return (avg_return * 252**0.5) / std_return

        except Exception as e:
            logger.error(f"Failed to calculate Sharpe ratio: {e}")
            return None

    async def close_position(self, symbol: str, side: str, quantity: float, price: float):
        """Close or reduce a position"""
        position_key = f"{symbol}_{side}"

        if position_key not in self.positions:
            logger.warning(f"No position found for {position_key}")
            return

        position = self.positions[position_key]

        if quantity >= position.quantity:
            # Close entire position
            realized_pnl = position.unrealized_pnl
            position.realized_pnl = realized_pnl

            self.stats['total_realized'] += realized_pnl
            self.stats['positions_closed'] += 1

            # Update win/loss stats
            if realized_pnl > 0:
                wins = self.stats.get('total_wins', 0) + 1
                self.stats['total_wins'] = wins
                self.stats['average_win'] = (
                    (self.stats['average_win'] * (wins - 1) + realized_pnl) / wins
                )
            else:
                losses = self.stats.get('total_losses', 0) + 1
                self.stats['total_losses'] = losses
                self.stats['average_loss'] = (
                    (self.stats['average_loss'] * (losses - 1) + abs(realized_pnl)) / losses
                )

            # Move to closed positions
            self.closed_positions.append(position)
            del self.positions[position_key]

        else:
            # Partial close
            close_ratio = quantity / position.quantity
            realized_pnl = position.unrealized_pnl * close_ratio

            position.realized_pnl += realized_pnl
            position.quantity -= quantity
            self.stats['total_realized'] += realized_pnl

        # Recalculate stats
        await self.calculate_pnl()
        await self.calculate_performance_metrics()

    async def calculate_performance_metrics(self):
        """Calculate advanced performance metrics"""
        total_wins = self.stats.get('total_wins', 0)
        total_losses = self.stats.get('total_losses', 0)
        total_trades = total_wins + total_losses

        if total_trades > 0:
            self.stats['win_rate'] = total_wins / total_trades

            if total_losses > 0 and self.stats['average_loss'] > 0:
                self.stats['profit_factor'] = (
                    (total_wins * self.stats['average_win']) /
                    (total_losses * self.stats['average_loss'])
                )

    async def store_position(self, position: Position):
        """Store position in Redis"""
        try:
            position_data = {
                'symbol': position.symbol,
                'quantity': position.quantity,
                'average_price': position.average_price,
                'current_price': position.current_price,
                'side': position.side,
                'unrealized_pnl': position.unrealized_pnl,
                'realized_pnl': position.realized_pnl,
                'fees': position.fees,
                'opened_at': position.opened_at.isoformat(),
                'updated_at': position.updated_at.isoformat()
            }

            key = f"position:{position.symbol}_{position.side}"
            self.redis_client.hset(key, mapping=position_data)
            self.redis_client.expire(key, 86400)  # 24 hour TTL

        except Exception as e:
            logger.error(f"Failed to store position: {e}")

    async def publish_pnl_update(self, symbol: str = None):
        """Publish P&L update to NATS"""
        try:
            update = {
                'timestamp': datetime.utcnow().isoformat(),
                'symbol': symbol,
                'total_realized': self.stats['total_realized'],
                'total_unrealized': self.stats['total_unrealized'],
                'total_pnl': self.stats['total_realized'] + self.stats['total_unrealized'],
                'positions_count': len(self.positions),
                'win_rate': self.stats['win_rate'],
                'sharpe_ratio': self.current_snapshot.sharpe_ratio if self.current_snapshot else None,
                'max_drawdown': self.stats['max_drawdown']
            }

            await self.nc.publish("pnl.update", json.dumps(update).encode())

        except Exception as e:
            logger.error(f"Failed to publish P&L update: {e}")

    async def periodic_snapshot(self):
        """Create periodic P&L snapshots"""
        while True:
            try:
                await asyncio.sleep(self.config.get('snapshot_interval', 60))

                if self.current_snapshot:
                    # Store snapshot
                    self.pnl_history.append(self.current_snapshot)

                    # Keep only last 24 hours of snapshots
                    cutoff = datetime.utcnow() - timedelta(hours=24)
                    self.pnl_history = [
                        s for s in self.pnl_history if s.timestamp > cutoff
                    ]

                    # Update daily P&L
                    self.daily_pnl.append(self.current_snapshot.total_pnl)
                    if len(self.daily_pnl) > 365:
                        self.daily_pnl.pop(0)

                    # Store in QuestDB
                    await self.store_snapshot_to_questdb(self.current_snapshot)

                    logger.info(f"P&L Snapshot: Realized={self.current_snapshot.total_realized:.2f}, "
                              f"Unrealized={self.current_snapshot.total_unrealized:.2f}, "
                              f"Total={self.current_snapshot.total_pnl:.2f}")

            except Exception as e:
                logger.error(f"Failed to create snapshot: {e}")

    async def store_snapshot_to_questdb(self, snapshot: PnLSnapshot):
        """Store P&L snapshot to QuestDB"""
        try:
            query = f"""
            INSERT INTO pnl_snapshots(
                timestamp, total_realized, total_unrealized, total_pnl,
                positions_count, winning_positions, losing_positions,
                largest_winner, largest_loser, sharpe_ratio, max_drawdown
            ) VALUES(
                '{snapshot.timestamp.isoformat()}',
                {snapshot.total_realized},
                {snapshot.total_unrealized},
                {snapshot.total_pnl},
                {snapshot.positions_count},
                {snapshot.winning_positions},
                {snapshot.losing_positions},
                {snapshot.largest_winner},
                {snapshot.largest_loser},
                {snapshot.sharpe_ratio if snapshot.sharpe_ratio else 'null'},
                {snapshot.max_drawdown if snapshot.max_drawdown else 'null'}
            )
            """

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.questdb_url}/exec",
                    params={'query': query}
                )
                if response.status_code == 200:
                    logger.debug("Stored P&L snapshot to QuestDB")

        except Exception as e:
            logger.error(f"Failed to store snapshot to QuestDB: {e}")

    def get_stats(self) -> dict:
        """Get current P&L statistics"""
        return {
            **self.stats,
            'active_positions': len(self.positions),
            'closed_positions': len(self.closed_positions),
            'current_snapshot': {
                'total_realized': self.current_snapshot.total_realized,
                'total_unrealized': self.current_snapshot.total_unrealized,
                'total_pnl': self.current_snapshot.total_pnl,
                'timestamp': self.current_snapshot.timestamp.isoformat()
            } if self.current_snapshot else None
        }

    async def run(self):
        """Run the P&L service"""
        await self.connect_services()
        await self.subscribe_events()

        # Start periodic snapshot
        asyncio.create_task(self.periodic_snapshot())

        logger.info("P&L service started")


# FastAPI app for health and metrics
app = FastAPI(title="P&L Service")
pnl_engine = None


@app.on_event("startup")
async def startup_event():
    global pnl_engine
    pnl_engine = PnLCalculator()
    await pnl_engine.run()


@app.get("/health")
async def health():
    """Health check endpoint"""
    global pnl_engine

    try:
        # Check if engine is initialized
        if not pnl_engine:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "service": "pnl",
                    "reason": "Engine not initialized"
                }
            )

        # Check NATS connection
        if not pnl_engine.nc or not pnl_engine.nc.is_connected:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "service": "pnl",
                    "reason": "NATS not connected"
                }
            )

        # Check Redis connection
        if pnl_engine.redis_client:
            pnl_engine.redis_client.ping()
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "service": "pnl",
                    "reason": "Redis not connected"
                }
            )

        # Check QuestDB connection
        async with httpx.AsyncClient(timeout=httpx.Timeout(2.0)) as client:
            response = await client.get(f"{pnl_engine.questdb_url}/")
            if response.status_code != 200:
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "service": "pnl",
                        "reason": "QuestDB not responding"
                    }
                )

        return {
            "status": "healthy",
            "service": "pnl",
            "timestamp": datetime.utcnow().isoformat(),
            "positions_count": len(pnl_engine.positions) if pnl_engine.positions else 0
        }

    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "pnl",
                "error": str(e)
            }
        )


@app.get("/stats")
async def stats():
    """Get P&L statistics"""
    global pnl_engine
    if pnl_engine:
        return pnl_engine.get_stats()
    return {"error": "Engine not initialized"}


@app.get("/positions")
async def get_positions():
    """Get all active positions"""
    global pnl_engine
    if pnl_engine:
        positions = []
        for position in pnl_engine.positions.values():
            positions.append({
                'symbol': position.symbol,
                'side': position.side,
                'quantity': position.quantity,
                'average_price': position.average_price,
                'current_price': position.current_price,
                'unrealized_pnl': position.unrealized_pnl,
                'realized_pnl': position.realized_pnl
            })
        return positions
    return []


@app.get("/snapshot")
async def get_snapshot():
    """Get current P&L snapshot"""
    global pnl_engine
    if pnl_engine and pnl_engine.current_snapshot:
        snapshot = pnl_engine.current_snapshot
        return {
            'timestamp': snapshot.timestamp.isoformat(),
            'total_realized': snapshot.total_realized,
            'total_unrealized': snapshot.total_unrealized,
            'total_pnl': snapshot.total_pnl,
            'positions_count': snapshot.positions_count,
            'sharpe_ratio': snapshot.sharpe_ratio,
            'max_drawdown': snapshot.max_drawdown
        }
    return {"error": "No snapshot available"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)