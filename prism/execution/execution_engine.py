"""
Execution Engine - processes and executes orders realistically.
"""
import logging
import asyncio
from typing import List
from ..core.models import Order, Fill, OrderType, OrderStatus, OrderSide
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Processes incoming orders and executes them with realistic slippage.
    """

    def __init__(self, engine):
        self.engine = engine
        logger.info("ExecutionEngine initialized")

    async def process_order(self, order: Order):
        """Process an incoming order."""
        # Simulate execution latency
        await asyncio.sleep(settings.LATENCY_MS / 1000.0)

        if order.order_type == OrderType.MARKET:
            await self._execute_market_order(order)
        elif order.order_type == OrderType.LIMIT:
            await self._execute_limit_order(order)
        else:
            logger.warning(f"Order type {order.order_type} not yet implemented")
            order.status = OrderStatus.REJECTED

    async def _execute_market_order(self, order: Order):
        """Execute a market order immediately."""
        if not self.engine.order_book_sim:
            logger.error("Order book simulator not available")
            order.status = OrderStatus.REJECTED
            return

        # Match against order book
        fills = self.engine.order_book_sim.match_order(order)

        # If partial fill, cancel remainder (market order)
        if order.filled_quantity < order.quantity and order.filled_quantity > 0:
            order.status = OrderStatus.PARTIALLY_FILLED
            logger.info(f"Market order partially filled: {order.filled_quantity}/{order.quantity}")
        elif order.filled_quantity == 0:
            order.status = OrderStatus.REJECTED
            logger.warning(f"Market order rejected: no liquidity")

        # Apply liquidity depletion
        if self.engine.liquidity_model and order.filled_quantity > 0:
            self.engine.liquidity_model.apply_liquidity_depletion(order, order.filled_quantity)

        # Record fills
        self.engine.fills.extend(fills)

        # Store fills to persistence layer
        for fill in fills:
            asyncio.create_task(self.engine.store_fill(fill))

        # Update market state
        if fills and order.symbol in self.engine.symbols:
            # Update last trade price
            last_fill = fills[-1]
            self.engine.symbols[order.symbol].last_price = last_fill.price
            self.engine.symbols[order.symbol].volume += order.filled_quantity

            # Update order book last trade price
            if order.symbol in self.engine.order_books:
                self.engine.order_books[order.symbol].last_trade_price = last_fill.price

        logger.info(f"Market order executed: {order.symbol} {order.side.value} {order.filled_quantity} @ avg ${order.average_fill_price:.2f}")

    async def _execute_limit_order(self, order: Order):
        """Execute a limit order (add to book or match)."""
        if not self.engine.order_book_sim:
            logger.error("Order book simulator not available")
            order.status = OrderStatus.REJECTED
            return

        # Try to match immediately
        fills = self.engine.order_book_sim.match_order(order)

        if fills:
            # Apply liquidity depletion
            if self.engine.liquidity_model:
                self.engine.liquidity_model.apply_liquidity_depletion(order, order.filled_quantity)

            # Record fills
            self.engine.fills.extend(fills)

            # Store fills to persistence layer
            for fill in fills:
                asyncio.create_task(self.engine.store_fill(fill))

            # Update market state
            if order.symbol in self.engine.symbols:
                last_fill = fills[-1]
                self.engine.symbols[order.symbol].last_price = last_fill.price
                self.engine.symbols[order.symbol].volume += order.filled_quantity

                if order.symbol in self.engine.order_books:
                    self.engine.order_books[order.symbol].last_trade_price = last_fill.price

        # If not fully filled, add to book
        if order.filled_quantity < order.quantity:
            self.engine.order_book_sim.add_order(order)

        logger.info(f"Limit order processed: {order.symbol} {order.side.value} {order.quantity} @ ${order.price} (filled: {order.filled_quantity})")

    def calculate_slippage(self, order: Order) -> float:
        """Calculate slippage for an order."""
        if not self.engine.liquidity_model:
            return 0.0

        # Get market impact
        impact = self.engine.liquidity_model.calculate_market_impact(order)

        # Get current price
        if order.symbol in self.engine.symbols:
            current_price = self.engine.symbols[order.symbol].last_price
            return current_price * abs(impact)

        return 0.0
