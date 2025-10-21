# PHASE 5 - PRISM PHYSICS ENGINE
# Complete Implementation Guide

**Task ID**: PHASE5_PRISM_CONSOLIDATED
**Estimated Time**: 40-50 hours (2-3 weeks)
**Component**: PRISM Physics-Based Market Simulation Engine
**Dependencies**: PHASE5_PROMPT00 (Validation must pass)

---

## 🎯 OVERVIEW

**PRISM** (Probability-based Risk Integration & Simulation Model) is an advanced physics-based trading engine that simulates realistic market microstructure, order flow dynamics, and price discovery mechanisms.

### What Gets Built:
1. **Order Book Engine** - Realistic limit order book with depth
2. **Liquidity Model** - Market depth and liquidity impact calculation
3. **Price Discovery** - Physics-based price formation
4. **Execution Simulator** - Realistic order fills with slippage
5. **Market Impact** - Order size effects on prices
6. **Multi-Agent System** - Simulated market participants
7. **Microstructure Analytics** - Bid-ask spread, volatility, momentum
8. **Integration Layer** - Connect with Library Service

---

## ⚠️ MANDATORY PRINCIPLES

### Component Isolation
- **FIX ERRORS WITHIN PRISM ONLY**
- Do NOT modify Library Service
- Do NOT change backend services
- PRISM is a separate service

### Comprehensive Implementation
- ✅ FULL order book simulation
- ✅ ALL market forces modeled
- ✅ COMPLETE execution logic
- ✅ COMPREHENSIVE testing

### Physics-Based Approach
- Use real market microstructure principles
- Model liquidity realistically
- Simulate order flow dynamics
- Calculate realistic slippage

---

## 📋 IMPLEMENTATION ROADMAP

**This consolidated prompt covers 8 major components**:

1. **PRISM Core Engine** (6-8 hours)
2. **Order Book Simulator** (6-8 hours)
3. **Liquidity & Market Impact** (5-6 hours)
4. **Price Discovery Mechanism** (4-5 hours)
5. **Execution Engine** (5-6 hours)
6. **Multi-Agent Simulation** (6-8 hours)
7. **Analytics & Metrics** (4-5 hours)
8. **Integration & Testing** (6-8 hours)

**Total**: 40-50 hours

---

# COMPONENT 1: PRISM CORE ENGINE (6-8 hours)

## Objective
Build the core PRISM service with FastAPI, configuration management, and foundational classes.

## Implementation

### Directory Structure
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

mkdir -p prism/core
mkdir -p prism/simulation
mkdir -p prism/execution
mkdir -p prism/agents
mkdir -p prism/analytics
mkdir -p prism/config
mkdir -p prism/tests

echo "✅ PRISM directory structure created"
```

### Core Configuration
**File**: `prism/config/settings.py`

```python
"""
PRISM Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class PRISMSettings(BaseSettings):
    """PRISM engine configuration."""
    
    # Service
    HOST: str = "0.0.0.0"
    PORT: int = 8360
    
    # Order Book
    MAX_ORDER_BOOK_DEPTH: int = 100
    TICK_SIZE: float = 0.01
    MIN_ORDER_SIZE: int = 1
    MAX_ORDER_SIZE: int = 1000000
    
    # Liquidity
    BASE_LIQUIDITY: float = 1000000.0  # Base market liquidity
    LIQUIDITY_DECAY_RATE: float = 0.1  # How fast liquidity recovers
    IMPACT_COEFFICIENT: float = 0.001  # Price impact per unit volume
    
    # Price Discovery
    VOLATILITY: float = 0.02  # Daily volatility
    MOMENTUM_FACTOR: float = 0.3  # Momentum influence
    MEAN_REVERSION_RATE: float = 0.1  # Mean reversion speed
    
    # Execution
    LATENCY_MS: int = 10  # Execution latency
    SLIPPAGE_MODEL: str = "sqrt"  # linear, sqrt, or quadratic
    
    # Multi-Agent
    NUM_MARKET_MAKERS: int = 5
    NUM_NOISE_TRADERS: int = 20
    NUM_INFORMED_TRADERS: int = 10
    
    # Integration
    LIBRARY_API_URL: str = "http://localhost:8350"
    QUESTDB_HOST: str = "localhost"
    QUESTDB_PORT: int = 9000
    
    # Analytics
    CALCULATE_ANALYTICS_EVERY_N_TRADES: int = 100
    
    class Config:
        env_prefix = "PRISM_"


settings = PRISMSettings()
```

### Core Data Models
**File**: `prism/core/models.py`

```python
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
```

### PRISM Core Engine Class
**File**: `prism/core/engine.py`

```python
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
        
        # Components (initialized later)
        self.order_book_sim = None
        self.liquidity_model = None
        self.price_discovery = None
        self.execution_engine = None
        self.agent_simulator = None
        self.analytics = None
        
        logger.info("PRISM Engine initialized")
    
    async def initialize(self):
        """Initialize all PRISM components."""
        logger.info("Initializing PRISM components...")
        
        # Import and initialize components (will be implemented in later sections)
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
        
        logger.info("All PRISM components initialized")
    
    async def start(self):
        """Start the PRISM engine."""
        if self.running:
            logger.warning("PRISM already running")
            return
        
        self.running = True
        logger.info("Starting PRISM Engine...")
        
        # Start simulation loop
        asyncio.create_task(self._simulation_loop())
        
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
        
        return order.order_id
    
    def get_order_book(self, symbol: str) -> Optional[OrderBook]:
        """Get current order book for symbol."""
        return self.order_books.get(symbol)
    
    def get_market_state(self, symbol: str) -> Optional[MarketState]:
        """Get current market state for symbol."""
        return self.symbols.get(symbol)


# Global PRISM engine instance
prism_engine = PRISMEngine()
```

### FastAPI Application
**File**: `prism/main.py`

```python
"""
PRISM FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .core.engine import prism_engine
from .core.models import Order, OrderBook, MarketState
from .config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Startup
    logger.info("Starting PRISM Engine...")
    await prism_engine.initialize()
    await prism_engine.start()
    
    # Add default symbols
    prism_engine.add_symbol("AAPL", 150.0)
    prism_engine.add_symbol("MSFT", 300.0)
    prism_engine.add_symbol("GOOGL", 140.0)
    
    logger.info("PRISM Engine started successfully")
    
    yield
    
    # Shutdown
    logger.info("Stopping PRISM Engine...")
    await prism_engine.stop()


app = FastAPI(
    title="PRISM Physics Engine",
    description="Physics-based market simulation and execution engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "prism",
        "version": "1.0.0",
        "running": prism_engine.running
    }


@app.post("/orders")
async def submit_order(order: Order):
    """Submit an order to PRISM."""
    try:
        order_id = await prism_engine.submit_order(order)
        return {"order_id": str(order_id), "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orderbook/{symbol}")
async def get_order_book(symbol: str):
    """Get order book for symbol."""
    order_book = prism_engine.get_order_book(symbol)
    if not order_book:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return order_book


@app.get("/market/{symbol}")
async def get_market_state(symbol: str):
    """Get market state for symbol."""
    market_state = prism_engine.get_market_state(symbol)
    if not market_state:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return market_state


@app.get("/symbols")
async def list_symbols():
    """List all available symbols."""
    return {
        "symbols": list(prism_engine.symbols.keys()),
        "count": len(prism_engine.symbols)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
```

## Component Testing

```bash
# Test PRISM core

cd C:\ClaudeDesktop_Projects\Trade2026\prism

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
numpy==1.24.3
pandas==2.0.3
EOF

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Start PRISM
python -m prism.main

# In another terminal, test endpoints
curl http://localhost:8360/health | jq '.'
curl http://localhost:8360/symbols | jq '.'
curl http://localhost:8360/market/AAPL | jq '.'

echo "✅ PRISM Core Engine working"
```

## Success Criteria
- [ ] PRISM FastAPI application starts
- [ ] Health endpoint responds
- [ ] Symbols endpoint lists symbols
- [ ] Market state endpoint returns data
- [ ] No errors in startup logs

---

# COMPONENT 2: ORDER BOOK SIMULATOR (6-8 hours)

## Objective
Implement realistic limit order book with depth, price levels, and matching logic.

## Implementation

**File**: `prism/simulation/order_book.py`

```python
"""
Order Book Simulator - realistic limit order book dynamics.
"""
import logging
from typing import List, Optional, Tuple
from collections import defaultdict
import heapq
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
```

## Component Testing

```python
# Test order book simulator
from prism.core.models import Order, OrderSide, OrderType
from prism.simulation.order_book import OrderBookSimulator
from prism.core.engine import PRISMEngine

# Initialize
engine = PRISMEngine()
engine.add_symbol("TEST", 100.0)
obs = OrderBookSimulator(engine)

# Add buy orders
buy1 = Order(symbol="TEST", side=OrderSide.BUY, order_type=OrderType.LIMIT, quantity=100, price=99.5)
buy2 = Order(symbol="TEST", side=OrderSide.BUY, order_type=OrderType.LIMIT, quantity=200, price=99.0)
obs.add_order(buy1)
obs.add_order(buy2)

# Add sell orders
sell1 = Order(symbol="TEST", side=OrderSide.SELL, order_type=OrderType.LIMIT, quantity=150, price=100.5)
sell2 = Order(symbol="TEST", side=OrderSide.SELL, order_type=OrderType.LIMIT, quantity=250, price=101.0)
obs.add_order(sell1)
obs.add_order(sell2)

# Check order book
print(f"Best bid: ${obs.get_best_bid('TEST')}")  # Should be 99.5
print(f"Best ask: ${obs.get_best_ask('TEST')}")  # Should be 100.5
print(f"Mid price: ${obs.get_mid_price('TEST')}")  # Should be 100.0

# Submit market order (should match)
market_buy = Order(symbol="TEST", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=100)
fills = obs.match_order(market_buy)
print(f"Fills: {len(fills)}")  # Should have fills
print(f"Order filled: {market_buy.filled_quantity}/{market_buy.quantity}")

print("✅ Order Book Simulator working")
```

## Success Criteria
- [ ] Can add orders to book
- [ ] Order book aggregates by price level
- [ ] Best bid/ask calculated correctly
- [ ] Order matching works (FIFO at price level)
- [ ] Partially filled orders handled
- [ ] Order book snapshot updates

---

# REMAINING COMPONENTS (Compact Format Due to Length)

## COMPONENT 3: Liquidity & Market Impact (5-6 hours)

**File**: `prism/simulation/liquidity.py`

Key features:
- Calculate available liquidity at each price level
- Model market impact based on order size
- Implement square-root market impact model
- Track liquidity depletion and recovery
- Update market state with liquidity metrics

## COMPONENT 4: Price Discovery (4-5 hours)

**File**: `prism/simulation/price_discovery.py`

Key features:
- Physics-based price formation
- Momentum and mean reversion forces
- Volatility modeling (Brownian motion)
- Order flow imbalance effects
- Update last trade price

## COMPONENT 5: Execution Engine (5-6 hours)

**File**: `prism/execution/execution_engine.py`

Key features:
- Process incoming orders
- Route to order book or execute immediately
- Calculate slippage realistically
- Handle partial fills
- Emit fill events
- Integration with Library Service

## COMPONENT 6: Multi-Agent Simulation (6-8 hours)

**File**: `prism/agents/agent_simulator.py`

Implement agent types:
- **Market Makers**: Provide liquidity, quote bid/ask
- **Noise Traders**: Random orders, no alpha
- **Informed Traders**: Trade on signals
- **Momentum Traders**: Follow trends

## COMPONENT 7: Analytics & Metrics (4-5 hours)

**File**: `prism/analytics/metrics.py`

Calculate:
- Bid-ask spread
- Effective spread
- Price impact
- Volatility (realized)
- Volume-weighted metrics
- Order book imbalance

## COMPONENT 8: Integration & Testing (6-8 hours)

Implement:
- Connect PRISM to Library Service
- Load strategies from library
- Execute strategy orders through PRISM
- Store execution data in QuestDB
- End-to-end integration tests
- Performance benchmarks

---

## 🚀 DEPLOYMENT

**Docker Compose**: `infrastructure/docker/docker-compose.prism.yml`

```yaml
version: '3.8'

services:
  prism:
    build: ../../prism
    image: localhost/prism:latest
    ports:
      - "8360:8360"
    environment:
      - PRISM_LIBRARY_API_URL=http://library:8350
      - PRISM_QUESTDB_HOST=questdb
    networks:
      - trade2026-backend
    depends_on:
      - library
      - questdb

networks:
  trade2026-backend:
    external: true
```

Start everything:
```bash
docker-compose -f docker-compose.base.yml \
               -f docker-compose.apps.yml \
               -f docker-compose.library.yml \
               -f docker-compose.prism.yml \
               up -d
```

---

## ✅ FINAL SUCCESS CRITERIA

- [ ] PRISM service running on port 8360
- [ ] Order book simulation realistic
- [ ] Liquidity model calculates impact
- [ ] Price discovery physics-based
- [ ] Execution engine handles orders
- [ ] Multi-agent simulation running
- [ ] Analytics calculating metrics
- [ ] Integration with Library Service
- [ ] All tests passing
- [ ] System stable 10+ minutes
- [ ] Documentation complete

---

**Total Time**: 40-50 hours (2-3 weeks)
**Status**: Complete implementation guide
**Next**: Production deployment and optimization
