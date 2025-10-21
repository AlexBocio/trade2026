"""
Order Book Simulator - realistic limit order book dynamics.
"""
import logging
from typing import List, Optional, Tuple
from collections import defaultdict
from datetime import datetime

from ..core.models import Order, OrderSide, OrderType, OrderStatus, OrderBookLevel, Fill
from ..config.settings import settings

logger = logging.getLogger(__name__)


class OrderBookSimulator:
    """
    Simulates a realistic limit order book with proper matching logic.
    """

    def __init__(self, engine):
        self.engine = engine

        # Order book: symbol -> {side -> price -> [orders]}
        self.orders = defaultdict(lambda: {
            "buy": defaultdict(list),
            "sell": defaultdict(list)
        })

        logger.info("OrderBookSimulator initialized")

    def add_order(self, order: Order):
        """Add an order to the order book."""
        symbol = order.symbol
        side = "buy" if order.side == OrderSide.BUY else "sell"
        price = order.price

        if not price:
            # Market orders don't go in book
            return

        self.orders[symbol][side][price].append(order)
        order.status = OrderStatus.OPEN

        # Update order book snapshot
        self._update_order_book_snapshot(symbol)

        logger.debug(f"Added {side} order for {symbol} at ${price}")

    def remove_order(self, order: Order):
        """Remove an order from the order book."""
        symbol = order.symbol
        side = "buy" if order.side == OrderSide.BUY else "sell"
        price = order.price

        if price and symbol in self.orders:
            orders_at_price = self.orders[symbol][side].get(price, [])
            if order in orders_at_price:
                orders_at_price.remove(order)

                # Clean up empty price level
                if not orders_at_price:
                    del self.orders[symbol][side][price]

        # Update snapshot
        self._update_order_book_snapshot(symbol)

    def match_order(self, order: Order) -> List[Fill]:
        """
        Match an incoming order against the order book.
        Returns list of fills.
        """
        symbol = order.symbol
        fills = []

        # Get opposite side of book
        if order.side == OrderSide.BUY:
            # Buy order matches against asks (sell orders)
            opposite_side = "sell"
            compare = lambda order_price, book_price: order.order_type == OrderType.MARKET or order_price >= book_price
        else:
            # Sell order matches against bids (buy orders)
            opposite_side = "buy"
            compare = lambda order_price, book_price: order.order_type == OrderType.MARKET or order_price <= book_price

        if symbol not in self.orders:
            return fills

        # Get sorted price levels
        price_levels = sorted(
            self.orders[symbol][opposite_side].keys(),
            reverse=(opposite_side == "buy")  # Best prices first
        )

        remaining_qty = order.quantity - order.filled_quantity

        for price in price_levels:
            if remaining_qty <= 0:
                break

            # Check if price acceptable
            if not compare(order.price, price):
                break

            # Match against orders at this price level
            orders_at_level = self.orders[symbol][opposite_side][price]

            for book_order in orders_at_level[:]:  # Copy list to modify during iteration
                if remaining_qty <= 0:
                    break

                # Calculate fill quantity
                available = book_order.quantity - book_order.filled_quantity
                fill_qty = min(remaining_qty, available)

                # Create fill
                fill = Fill(
                    order_id=order.order_id,
                    symbol=symbol,
                    side=order.side,
                    quantity=fill_qty,
                    price=price,
                    liquidity="taker"  # Incoming order is taker
                )
                fills.append(fill)

                # Update order
                order.filled_quantity += fill_qty
                order.average_fill_price = (
                    (order.average_fill_price * (order.filled_quantity - fill_qty) + price * fill_qty)
                    / order.filled_quantity
                )

                # Update book order
                book_order.filled_quantity += fill_qty
                book_order.average_fill_price = (
                    (book_order.average_fill_price * (book_order.filled_quantity - fill_qty) + price * fill_qty)
                    / book_order.filled_quantity
                )

                # Update statuses
                if book_order.filled_quantity >= book_order.quantity:
                    book_order.status = OrderStatus.FILLED
                    self.remove_order(book_order)
                else:
                    book_order.status = OrderStatus.PARTIALLY_FILLED

                remaining_qty -= fill_qty

                logger.debug(f"Matched {fill_qty} @ ${price} for {symbol}")

        # Update incoming order status
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
        elif order.filled_quantity > 0:
            order.status = OrderStatus.PARTIALLY_FILLED

        # Update order book snapshot
        self._update_order_book_snapshot(symbol)

        return fills

    def _update_order_book_snapshot(self, symbol: str):
        """Update the order book snapshot in engine."""
        if symbol not in self.orders:
            return

        # Aggregate bids (buy orders) - sorted high to low
        bids = []
        buy_prices = sorted(self.orders[symbol]["buy"].keys(), reverse=True)
        for price in buy_prices[:settings.MAX_ORDER_BOOK_DEPTH]:
            orders = self.orders[symbol]["buy"][price]
            total_qty = sum(o.quantity - o.filled_quantity for o in orders)
            if total_qty > 0:
                bids.append(OrderBookLevel(
                    price=price,
                    quantity=total_qty,
                    num_orders=len(orders)
                ))

        # Aggregate asks (sell orders) - sorted low to high
        asks = []
        sell_prices = sorted(self.orders[symbol]["sell"].keys())
        for price in sell_prices[:settings.MAX_ORDER_BOOK_DEPTH]:
            orders = self.orders[symbol]["sell"][price]
            total_qty = sum(o.quantity - o.filled_quantity for o in orders)
            if total_qty > 0:
                asks.append(OrderBookLevel(
                    price=price,
                    quantity=total_qty,
                    num_orders=len(orders)
                ))

        # Update engine's order book
        if symbol in self.engine.order_books:
            self.engine.order_books[symbol].bids = bids
            self.engine.order_books[symbol].asks = asks
            self.engine.order_books[symbol].timestamp = datetime.utcnow()

    def get_best_bid(self, symbol: str) -> Optional[float]:
        """Get best bid price."""
        if symbol not in self.orders or not self.orders[symbol]["buy"]:
            return None
        return max(self.orders[symbol]["buy"].keys())

    def get_best_ask(self, symbol: str) -> Optional[float]:
        """Get best ask price."""
        if symbol not in self.orders or not self.orders[symbol]["sell"]:
            return None
        return min(self.orders[symbol]["sell"].keys())

    def get_mid_price(self, symbol: str) -> Optional[float]:
        """Get mid price."""
        bid = self.get_best_bid(symbol)
        ask = self.get_best_ask(symbol)

        if bid and ask:
            return (bid + ask) / 2.0
        elif bid:
            return bid
        elif ask:
            return ask
        else:
            return None
