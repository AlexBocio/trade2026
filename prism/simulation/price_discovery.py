"""
Price Discovery - physics-based price formation.
"""
import logging
import random
import math
from ..config.settings import settings

logger = logging.getLogger(__name__)


class PriceDiscovery:
    """
    Physics-based price discovery mechanism.
    Models price movement using momentum, mean reversion, and volatility.
    """

    def __init__(self, engine):
        self.engine = engine
        self.price_history = {}  # Track price history for momentum
        logger.info("PriceDiscovery initialized")

    async def update(self, symbol: str):
        """Update price discovery for symbol."""
        if symbol not in self.engine.symbols:
            return

        market_state = self.engine.symbols[symbol]
        current_price = market_state.last_price

        # Initialize history
        if symbol not in self.price_history:
            self.price_history[symbol] = [current_price]

        # Get mid price from order book if available
        if self.engine.order_book_sim:
            mid_price = self.engine.order_book_sim.get_mid_price(symbol)
            if mid_price:
                # Price discovery based on order book mid price
                target_price = mid_price
            else:
                # No order book, use physics model
                target_price = self._calculate_physics_price(symbol, current_price)
        else:
            target_price = self._calculate_physics_price(symbol, current_price)

        # Update price with momentum and mean reversion
        new_price = self._apply_price_dynamics(current_price, target_price)

        # Update market state
        market_state.last_price = new_price
        market_state.momentum = (new_price / current_price - 1.0) if current_price > 0 else 0
        market_state.volatility = self._calculate_volatility(symbol)

        # Update history
        self.price_history[symbol].append(new_price)
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]

    def _calculate_physics_price(self, symbol: str, current_price: float) -> float:
        """Calculate price using physics-based model."""
        # Brownian motion component (random walk)
        volatility = settings.VOLATILITY
        random_shock = random.gauss(0, volatility)

        # Mean reversion to initial price
        initial_price = self.price_history[symbol][0] if self.price_history.get(symbol) else current_price
        mean_reversion = settings.MEAN_REVERSION_RATE * (initial_price - current_price) / current_price

        # Momentum component
        momentum = self._calculate_momentum(symbol)

        # Combine forces
        price_change = (
            random_shock +
            mean_reversion +
            settings.MOMENTUM_FACTOR * momentum
        )

        return current_price * (1 + price_change)

    def _calculate_momentum(self, symbol: str) -> float:
        """Calculate price momentum."""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 5:
            return 0.0

        prices = self.price_history[symbol][-5:]
        returns = [(prices[i] / prices[i-1] - 1) for i in range(1, len(prices))]

        return sum(returns) / len(returns) if returns else 0.0

    def _calculate_volatility(self, symbol: str) -> float:
        """Calculate realized volatility."""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 10:
            return settings.VOLATILITY

        prices = self.price_history[symbol][-20:]
        returns = [(prices[i] / prices[i-1] - 1) for i in range(1, len(prices))]

        if not returns:
            return settings.VOLATILITY

        variance = sum((r - sum(returns)/len(returns))**2 for r in returns) / len(returns)
        return math.sqrt(variance)

    def _apply_price_dynamics(self, current_price: float, target_price: float) -> float:
        """Apply price dynamics to move towards target."""
        # Gradual movement towards target
        alpha = 0.1  # Adjustment speed
        new_price = current_price + alpha * (target_price - current_price)

        # Ensure price stays positive
        return max(new_price, current_price * 0.5)
