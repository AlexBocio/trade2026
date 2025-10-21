"""
Core PRISM data models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order(BaseModel):
    """Order model."""
    order_id: UUID = Field(default_factory=uuid4)
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None  # None for market orders
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trader_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class Fill(BaseModel):
    """Order fill model."""
    fill_id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    liquidity: str  # "maker" or "taker"


class OrderBookLevel(BaseModel):
    """Single level in order book."""
    price: float
    quantity: float
    num_orders: int = 1


class OrderBook(BaseModel):
    """Complete order book snapshot."""
    symbol: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    bids: List[OrderBookLevel] = Field(default_factory=list)
    asks: List[OrderBookLevel] = Field(default_factory=list)
    last_trade_price: Optional[float] = None

    def get_mid_price(self) -> Optional[float]:
        """Calculate mid price."""
        if not self.bids or not self.asks:
            return None
        return (self.bids[0].price + self.asks[0].price) / 2.0

    def get_spread(self) -> Optional[float]:
        """Calculate bid-ask spread."""
        if not self.bids or not self.asks:
            return None
        return self.asks[0].price - self.bids[0].price

    def get_depth(self, levels: int = 5) -> dict:
        """Get order book depth."""
        return {
            "bids": self.bids[:levels],
            "asks": self.asks[:levels],
            "mid_price": self.get_mid_price(),
            "spread": self.get_spread()
        }


class MarketState(BaseModel):
    """Current market state."""
    symbol: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    last_price: float
    volume: float = 0.0
    volatility: float = 0.0
    momentum: float = 0.0
    liquidity: float = 0.0
    order_book: Optional[OrderBook] = None
