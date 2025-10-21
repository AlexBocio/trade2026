"""
Agent Simulator - multi-agent market simulation.
"""
import logging
import random
import asyncio
from typing import Dict, List
from datetime import datetime

from ..core.models import Order, OrderSide, OrderType
from ..config.settings import settings

logger = logging.getLogger(__name__)


class Agent:
    """Base agent class."""

    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.positions: Dict[str, float] = {}  # symbol -> quantity
        self.cash = 1000000.0  # Starting capital

    async def generate_orders(self, symbol: str, engine) -> List[Order]:
        """Generate orders for this agent. Override in subclasses."""
        return []


class MarketMaker(Agent):
    """
    Market maker agent - provides liquidity by quoting bid/ask.
    """

    def __init__(self, agent_id: str):
        super().__init__(agent_id, "market_maker")
        self.spread = 0.001  # 0.1% spread
        self.quote_size = 100.0

    async def generate_orders(self, symbol: str, engine) -> List[Order]:
        """Generate bid/ask quotes around current price."""
        orders = []

        if symbol not in engine.symbols:
            return orders

        current_price = engine.symbols[symbol].last_price

        # Get mid price from order book if available
        if engine.order_book_sim:
            mid_price = engine.order_book_sim.get_mid_price(symbol)
            if mid_price:
                current_price = mid_price

        # Calculate bid/ask prices
        half_spread = current_price * self.spread / 2
        bid_price = current_price - half_spread
        ask_price = current_price + half_spread

        # Create bid order (buy)
        bid = Order(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=self.quote_size,
            price=round(bid_price, 2),
            trader_id=self.agent_id
        )
        orders.append(bid)

        # Create ask order (sell)
        ask = Order(
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=self.quote_size,
            price=round(ask_price, 2),
            trader_id=self.agent_id
        )
        orders.append(ask)

        return orders


class NoiseTrader(Agent):
    """
    Noise trader - generates random orders with no alpha.
    """

    def __init__(self, agent_id: str):
        super().__init__(agent_id, "noise_trader")
        self.order_probability = 0.05  # 5% chance per tick
        self.max_order_size = 50.0

    async def generate_orders(self, symbol: str, engine) -> List[Order]:
        """Generate random orders."""
        orders = []

        # Random chance to place order
        if random.random() > self.order_probability:
            return orders

        if symbol not in engine.symbols:
            return orders

        current_price = engine.symbols[symbol].last_price

        # Random side
        side = random.choice([OrderSide.BUY, OrderSide.SELL])

        # Random quantity
        quantity = random.uniform(10, self.max_order_size)

        # Random order type (70% market, 30% limit)
        if random.random() < 0.7:
            # Market order
            order = Order(
                symbol=symbol,
                side=side,
                order_type=OrderType.MARKET,
                quantity=quantity,
                trader_id=self.agent_id
            )
        else:
            # Limit order with random price offset
            offset_pct = random.uniform(-0.01, 0.01)  # +/- 1%
            price = current_price * (1 + offset_pct)

            order = Order(
                symbol=symbol,
                side=side,
                order_type=OrderType.LIMIT,
                quantity=quantity,
                price=round(price, 2),
                trader_id=self.agent_id
            )

        orders.append(order)
        return orders


class InformedTrader(Agent):
    """
    Informed trader - trades based on price momentum signals.
    """

    def __init__(self, agent_id: str):
        super().__init__(agent_id, "informed_trader")
        self.signal_threshold = 0.002  # 0.2% momentum threshold
        self.order_size = 75.0
        self.order_probability = 0.1  # 10% chance per tick

    async def generate_orders(self, symbol: str, engine) -> List[Order]:
        """Generate orders based on momentum signals."""
        orders = []

        # Random chance to trade
        if random.random() > self.order_probability:
            return orders

        if symbol not in engine.symbols:
            return orders

        market_state = engine.symbols[symbol]
        momentum = market_state.momentum

        # Trade in direction of strong momentum
        if abs(momentum) < self.signal_threshold:
            return orders  # No signal

        # Determine side based on momentum
        side = OrderSide.BUY if momentum > 0 else OrderSide.SELL

        # Use market orders for informed trading
        order = Order(
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=self.order_size,
            trader_id=self.agent_id
        )

        orders.append(order)
        return orders


class MomentumTrader(Agent):
    """
    Momentum trader - follows trends.
    """

    def __init__(self, agent_id: str):
        super().__init__(agent_id, "momentum_trader")
        self.momentum_threshold = 0.001  # 0.1% threshold
        self.order_size = 60.0
        self.order_probability = 0.08  # 8% chance per tick

    async def generate_orders(self, symbol: str, engine) -> List[Order]:
        """Generate orders following momentum."""
        orders = []

        # Random chance to trade
        if random.random() > self.order_probability:
            return orders

        if symbol not in engine.symbols:
            return orders

        market_state = engine.symbols[symbol]
        momentum = market_state.momentum

        # Trade with momentum
        if abs(momentum) < self.momentum_threshold:
            return orders  # Momentum too weak

        side = OrderSide.BUY if momentum > 0 else OrderSide.SELL
        current_price = market_state.last_price

        # Use limit orders slightly better than current price
        price_offset = 0.0005 if side == OrderSide.BUY else -0.0005
        price = current_price * (1 + price_offset)

        order = Order(
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            quantity=self.order_size,
            price=round(price, 2),
            trader_id=self.agent_id
        )

        orders.append(order)
        return orders


class AgentSimulator:
    """
    Manages all simulated agents and generates their orders.
    """

    def __init__(self, engine):
        self.engine = engine
        self.agents: List[Agent] = []

        # Create market makers
        for i in range(settings.NUM_MARKET_MAKERS):
            self.agents.append(MarketMaker(f"mm_{i}"))

        # Create noise traders
        for i in range(settings.NUM_NOISE_TRADERS):
            self.agents.append(NoiseTrader(f"noise_{i}"))

        # Create informed traders
        for i in range(settings.NUM_INFORMED_TRADERS):
            self.agents.append(InformedTrader(f"informed_{i}"))

        # Create momentum traders (using NUM_INFORMED_TRADERS as proxy)
        for i in range(settings.NUM_INFORMED_TRADERS // 2):
            self.agents.append(MomentumTrader(f"momentum_{i}"))

        logger.info(f"AgentSimulator initialized with {len(self.agents)} agents")

    async def update(self, symbol: str):
        """Generate orders from all agents for symbol."""
        # Collect orders from all agents
        all_orders = []

        for agent in self.agents:
            try:
                orders = await agent.generate_orders(symbol, self.engine)
                all_orders.extend(orders)
            except Exception as e:
                logger.error(f"Error generating orders for {agent.agent_id}: {e}")

        # Submit orders to engine
        for order in all_orders:
            try:
                await self.engine.submit_order(order)
            except Exception as e:
                logger.error(f"Error submitting agent order: {e}")

        if all_orders:
            logger.debug(f"Generated {len(all_orders)} agent orders for {symbol}")
