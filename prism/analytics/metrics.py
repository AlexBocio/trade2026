"""
Analytics & Metrics - market microstructure analytics.
"""
import logging
import math
from typing import Dict, List, Optional
from collections import defaultdict, deque

from ..core.models import Fill, OrderBook
from ..config.settings import settings

logger = logging.getLogger(__name__)


class Analytics:
    """
    Calculate market microstructure metrics.
    """

    def __init__(self, engine):
        self.engine = engine

        # Track fills for analytics
        self.recent_fills: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # Cached metrics
        self.metrics_cache: Dict[str, dict] = {}

        logger.info("Analytics initialized")

    async def update(self, symbol: str):
        """Update analytics for symbol."""
        if symbol not in self.engine.symbols:
            return

        # Calculate metrics periodically
        total_fills = len(self.engine.fills)
        if total_fills > 0 and total_fills % settings.CALCULATE_ANALYTICS_EVERY_N_TRADES == 0:
            await self._calculate_metrics(symbol)

    async def _calculate_metrics(self, symbol: str):
        """Calculate all metrics for symbol."""
        metrics = {}

        # Order book metrics
        if symbol in self.engine.order_books:
            order_book = self.engine.order_books[symbol]
            metrics['bid_ask_spread'] = self.calculate_bid_ask_spread(order_book)
            metrics['mid_price'] = self.calculate_mid_price(order_book)
            metrics['order_book_imbalance'] = self.calculate_order_book_imbalance(order_book)
            metrics['depth_5'] = self.calculate_book_depth(order_book, levels=5)

        # Fill-based metrics
        symbol_fills = [f for f in self.engine.fills if f.symbol == symbol]
        if symbol_fills:
            metrics['effective_spread'] = self.calculate_effective_spread(symbol_fills)
            metrics['price_impact'] = self.calculate_price_impact(symbol_fills)
            metrics['realized_volatility'] = self.calculate_realized_volatility(symbol)

        # Market state metrics
        if symbol in self.engine.symbols:
            market_state = self.engine.symbols[symbol]
            metrics['volume'] = market_state.volume
            metrics['volatility'] = market_state.volatility
            metrics['momentum'] = market_state.momentum
            metrics['liquidity'] = market_state.liquidity

        self.metrics_cache[symbol] = metrics
        logger.debug(f"Calculated metrics for {symbol}: {metrics}")

    def calculate_bid_ask_spread(self, order_book: OrderBook) -> Optional[float]:
        """Calculate bid-ask spread."""
        if not order_book.bids or not order_book.asks:
            return None

        best_bid = order_book.bids[0].price
        best_ask = order_book.asks[0].price

        spread = best_ask - best_bid
        return spread

    def calculate_mid_price(self, order_book: OrderBook) -> Optional[float]:
        """Calculate mid price."""
        if not order_book.bids or not order_book.asks:
            return None

        best_bid = order_book.bids[0].price
        best_ask = order_book.asks[0].price

        return (best_bid + best_ask) / 2.0

    def calculate_order_book_imbalance(self, order_book: OrderBook) -> Optional[float]:
        """
        Calculate order book imbalance.
        Imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
        """
        if not order_book.bids or not order_book.asks:
            return None

        # Sum top 5 levels
        bid_volume = sum(level.quantity for level in order_book.bids[:5])
        ask_volume = sum(level.quantity for level in order_book.asks[:5])

        total_volume = bid_volume + ask_volume
        if total_volume == 0:
            return 0.0

        imbalance = (bid_volume - ask_volume) / total_volume
        return imbalance

    def calculate_book_depth(self, order_book: OrderBook, levels: int = 5) -> dict:
        """Calculate order book depth at specified levels."""
        bid_depth = sum(level.quantity for level in order_book.bids[:levels])
        ask_depth = sum(level.quantity for level in order_book.asks[:levels])

        return {
            'bid_depth': bid_depth,
            'ask_depth': ask_depth,
            'total_depth': bid_depth + ask_depth
        }

    def calculate_effective_spread(self, fills: List[Fill]) -> Optional[float]:
        """
        Calculate effective spread.
        Effective spread = 2 * |trade_price - mid_price|
        """
        if not fills or len(fills) < 10:
            return None

        # Use recent fills
        recent_fills = fills[-100:]

        spreads = []
        for fill in recent_fills:
            symbol = fill.symbol
            if symbol not in self.engine.order_books:
                continue

            order_book = self.engine.order_books[symbol]
            mid_price = self.calculate_mid_price(order_book)

            if mid_price:
                effective_spread = 2 * abs(fill.price - mid_price)
                spreads.append(effective_spread)

        if spreads:
            return sum(spreads) / len(spreads)
        return None

    def calculate_price_impact(self, fills: List[Fill]) -> Optional[float]:
        """
        Calculate average price impact.
        Impact = (execution_price - pre_trade_price) / pre_trade_price
        """
        if not fills or len(fills) < 10:
            return None

        # Simplified: use recent fills
        recent_fills = fills[-100:]

        impacts = []
        for i in range(1, len(recent_fills)):
            prev_price = recent_fills[i-1].price
            curr_price = recent_fills[i].price

            if prev_price > 0:
                impact = abs(curr_price - prev_price) / prev_price
                impacts.append(impact)

        if impacts:
            return sum(impacts) / len(impacts)
        return None

    def calculate_realized_volatility(self, symbol: str) -> Optional[float]:
        """
        Calculate realized volatility from price history.
        """
        if symbol not in self.engine.symbols:
            return None

        # Get price discovery component
        if not self.engine.price_discovery:
            return None

        price_history = self.engine.price_discovery.price_history.get(symbol, [])

        if len(price_history) < 20:
            return None

        # Calculate returns
        prices = list(price_history)[-50:]  # Use last 50 prices
        returns = []

        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                ret = (prices[i] / prices[i-1]) - 1
                returns.append(ret)

        if not returns:
            return None

        # Calculate standard deviation of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = math.sqrt(variance)

        return volatility

    def calculate_vwap(self, fills: List[Fill]) -> Optional[float]:
        """
        Calculate volume-weighted average price.
        VWAP = sum(price * quantity) / sum(quantity)
        """
        if not fills:
            return None

        total_value = sum(f.price * f.quantity for f in fills)
        total_volume = sum(f.quantity for f in fills)

        if total_volume == 0:
            return None

        return total_value / total_volume

    def get_metrics(self, symbol: str) -> dict:
        """Get cached metrics for symbol."""
        return self.metrics_cache.get(symbol, {})

    def get_all_metrics(self) -> Dict[str, dict]:
        """Get all cached metrics."""
        return self.metrics_cache.copy()
