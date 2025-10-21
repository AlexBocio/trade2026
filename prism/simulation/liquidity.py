"""
Liquidity Model - calculates market impact and liquidity dynamics.
"""
import logging
import math
from ..core.models import Order, OrderSide
from ..config.settings import settings

logger = logging.getLogger(__name__)


class LiquidityModel:
    """
    Models market liquidity and calculates price impact.
    """

    def __init__(self, engine):
        self.engine = engine
        # Track liquidity depletion per symbol
        self.liquidity_depletion = {}
        logger.info("LiquidityModel initialized")

    async def update(self, symbol: str):
        """Update liquidity for symbol."""
        if symbol not in self.engine.symbols:
            return

        # Recover liquidity over time
        if symbol in self.liquidity_depletion:
            recovery = settings.LIQUIDITY_DECAY_RATE * self.liquidity_depletion[symbol]
            self.liquidity_depletion[symbol] = max(0, self.liquidity_depletion[symbol] - recovery)

        # Update market state
        current_liquidity = settings.BASE_LIQUIDITY - self.liquidity_depletion.get(symbol, 0)
        self.engine.symbols[symbol].liquidity = current_liquidity

    def calculate_market_impact(self, order: Order) -> float:
        """
        Calculate price impact of an order using square-root model.
        Impact = coefficient * sqrt(order_size / liquidity)
        """
        symbol = order.symbol
        if symbol not in self.engine.symbols:
            return 0.0

        current_liquidity = self.engine.symbols[symbol].liquidity
        if current_liquidity <= 0:
            return 0.0

        # Square-root market impact model
        size_ratio = order.quantity / current_liquidity
        impact = settings.IMPACT_COEFFICIENT * math.sqrt(size_ratio)

        # Apply directional impact
        if order.side == OrderSide.BUY:
            return impact  # Pushes price up
        else:
            return -impact  # Pushes price down

    def apply_liquidity_depletion(self, order: Order, filled_quantity: float):
        """Apply liquidity depletion from an executed order."""
        symbol = order.symbol
        if symbol not in self.liquidity_depletion:
            self.liquidity_depletion[symbol] = 0

        # Deplete liquidity proportional to fill size
        depletion = filled_quantity * settings.IMPACT_COEFFICIENT
        self.liquidity_depletion[symbol] += depletion

        logger.debug(f"Liquidity depleted for {symbol}: {depletion:.2f}")

    def get_available_liquidity(self, symbol: str, price_level: float) -> float:
        """Get available liquidity at a price level."""
        if symbol not in self.engine.symbols:
            return 0.0

        # Simplified: use overall liquidity
        # In advanced version, would calculate per-level liquidity
        return self.engine.symbols[symbol].liquidity
