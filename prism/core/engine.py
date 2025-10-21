"""
PRISM Core Engine - orchestrates all components.
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID

from .models import Order, Fill, OrderBook, MarketState
from ..config.settings import settings

logger = logging.getLogger(__name__)


class PRISMEngine:
    """
    Main PRISM Physics Engine.
    Orchestrates order book, liquidity, execution, and agents.
    """

    def __init__(self):
        self.symbols: Dict[str, MarketState] = {}
        self.order_books: Dict[str, OrderBook] = {}
        self.active_orders: Dict[UUID, Order] = {}
        self.fills: List[Fill] = []
        self.running = False

        # Components (will be initialized when implemented)
        self.order_book_sim = None
        self.liquidity_model = None
        self.price_discovery = None
        self.execution_engine = None
        self.agent_simulator = None
        self.analytics = None

        # Persistence layer
        self.questdb_client = None
        self.clickhouse_client = None
        self.persistence_enabled = False

        logger.info("PRISM Engine initialized")

    async def initialize(self):
        """Initialize all PRISM components."""
        logger.info("Initializing PRISM components...")

        # Import and initialize components
        try:
            from ..simulation.order_book import OrderBookSimulator
            from ..simulation.liquidity import LiquidityModel
            from ..simulation.price_discovery import PriceDiscovery
            from ..execution.execution_engine import ExecutionEngine
            from ..agents.agent_simulator import AgentSimulator
            from ..analytics.metrics import Analytics

            self.order_book_sim = OrderBookSimulator(self)
            self.liquidity_model = LiquidityModel(self)
            self.price_discovery = PriceDiscovery(self)
            self.execution_engine = ExecutionEngine(self)
            self.agent_simulator = AgentSimulator(self)
            self.analytics = Analytics(self)

            logger.info("All PRISM components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PRISM components: {e}")
            raise

        # Initialize persistence layer (optional - graceful degradation)
        try:
            from ..persistence import questdb_client, clickhouse_client

            self.questdb_client = questdb_client
            self.clickhouse_client = clickhouse_client

            # Try to initialize database tables
            await self.questdb_client.initialize()
            await self.clickhouse_client.initialize()

            self.persistence_enabled = True
            logger.info("Persistence layer initialized (QuestDB + ClickHouse)")
        except Exception as e:
            logger.warning(f"Persistence layer initialization failed: {e} - continuing without persistence")
            self.persistence_enabled = False

    async def start(self):
        """Start the PRISM engine."""
        if self.running:
            logger.warning("PRISM already running")
            return

        self.running = True
        self.simulation_tick = 0
        logger.info("Starting PRISM Engine...")

        # Start simulation loop
        asyncio.create_task(self._simulation_loop())

        # Start analytics storage loop (every 5 seconds)
        if self.persistence_enabled:
            asyncio.create_task(self._analytics_storage_loop())

        logger.info("PRISM Engine started")

    async def stop(self):
        """Stop the PRISM engine."""
        self.running = False
        logger.info("PRISM Engine stopped")

    async def _simulation_loop(self):
        """Main simulation loop."""
        while self.running:
            try:
                # Update market states
                await self._update_markets()

                # Sleep for simulation tick
                await asyncio.sleep(0.1)  # 100ms ticks

            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                await asyncio.sleep(1)

    async def _update_markets(self):
        """Update all market states."""
        for symbol in self.symbols:
            # Update price discovery
            if self.price_discovery:
                await self.price_discovery.update(symbol)

            # Update liquidity
            if self.liquidity_model:
                await self.liquidity_model.update(symbol)

            # Update agents
            if self.agent_simulator:
                await self.agent_simulator.update(symbol)

            # Update analytics
            if self.analytics:
                await self.analytics.update(symbol)

    def add_symbol(self, symbol: str, initial_price: float):
        """Add a symbol to simulate."""
        self.symbols[symbol] = MarketState(
            symbol=symbol,
            last_price=initial_price,
            liquidity=settings.BASE_LIQUIDITY
        )

        self.order_books[symbol] = OrderBook(
            symbol=symbol,
            bids=[],
            asks=[],
            last_trade_price=initial_price
        )

        logger.info(f"Added symbol {symbol} at ${initial_price}")

    async def submit_order(self, order: Order) -> UUID:
        """Submit an order to PRISM."""
        self.active_orders[order.order_id] = order

        # Route to execution engine
        if self.execution_engine:
            await self.execution_engine.process_order(order)
        else:
            logger.warning(f"Execution engine not available for order {order.order_id}")

        return order.order_id

    def get_order_book(self, symbol: str) -> Optional[OrderBook]:
        """Get current order book for symbol."""
        return self.order_books.get(symbol)

    def get_market_state(self, symbol: str) -> Optional[MarketState]:
        """Get current market state for symbol."""
        return self.symbols.get(symbol)

    async def store_fill(self, fill: Fill):
        """Store a fill to persistence layer."""
        if self.persistence_enabled and self.questdb_client:
            await self.questdb_client.store_fill(fill)

    async def store_analytics(self, symbol: str):
        """Store analytics metrics for a symbol."""
        if not self.persistence_enabled:
            return

        try:
            # Get metrics from analytics component
            if not self.analytics:
                return

            metrics = self.analytics.get_metrics(symbol)
            market_state = self.symbols.get(symbol)

            if not market_state:
                return

            # Store to ClickHouse
            if self.clickhouse_client:
                market_state_dict = {
                    'volume': market_state.volume,
                    'volatility': market_state.volatility,
                    'momentum': market_state.momentum,
                    'liquidity': market_state.liquidity
                }
                await self.clickhouse_client.store_analytics(symbol, metrics, market_state_dict)

            # Store market state snapshot to QuestDB
            if self.questdb_client:
                spread = metrics.get('bid_ask_spread', 0.0) or 0.0
                await self.questdb_client.store_market_state(market_state, spread)

            # Store order book snapshot to ClickHouse (every N seconds)
            if self.clickhouse_client and symbol in self.order_books:
                order_book = self.order_books[symbol]
                order_book_dict = {
                    'bids': [{'price': level.price, 'quantity': level.quantity, 'num_orders': level.num_orders}
                             for level in order_book.bids],
                    'asks': [{'price': level.price, 'quantity': level.quantity, 'num_orders': level.num_orders}
                             for level in order_book.asks]
                }
                await self.clickhouse_client.store_orderbook_snapshot(symbol, order_book_dict)

        except Exception as e:
            logger.error(f"Error storing analytics for {symbol}: {e}")

    async def _analytics_storage_loop(self):
        """Periodic analytics storage loop."""
        while self.running:
            try:
                # Store analytics for all symbols
                for symbol in self.symbols:
                    await self.store_analytics(symbol)

                # Sleep for 5 seconds
                await asyncio.sleep(5.0)

            except Exception as e:
                logger.error(f"Error in analytics storage loop: {e}")
                await asyncio.sleep(5.0)


# Global PRISM engine instance
prism_engine = PRISMEngine()
