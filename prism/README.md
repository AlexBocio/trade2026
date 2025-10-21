# PRISM Physics Engine

**Physics-based Realistic Integrated Simulation Model for Market Dynamics**

PRISM is a sophisticated market simulation and execution engine that uses physics-based models to create realistic market microstructure, agent-based trading, and order execution with accurate slippage modeling.

## Overview

PRISM provides:
- **Physics-Based Price Discovery**: Brownian motion + momentum + mean reversion
- **Realistic Order Matching**: FIFO limit order book with price-time priority
- **Market Impact Modeling**: Square-root impact model with liquidity dynamics
- **Multi-Agent Simulation**: 40 autonomous trading agents (market makers, noise traders, informed traders, momentum traders)
- **Analytics & Metrics**: Real-time market microstructure metrics (spread, imbalance, volatility, impact)
- **Data Persistence**: QuestDB for execution data, ClickHouse for analytics (optional)

## Architecture

### Core Components

1. **Order Book Simulator** (`prism/simulation/order_book.py`)
   - FIFO matching engine
   - Price-time priority
   - Multi-level aggregated order book

2. **Liquidity Model** (`prism/simulation/liquidity.py`)
   - Square-root market impact: `Impact = coefficient * sqrt(size/liquidity)`
   - Liquidity depletion and recovery
   - Dynamic liquidity tracking

3. **Price Discovery** (`prism/simulation/price_discovery.py`)
   - Brownian motion (random walk)
   - Momentum component
   - Mean reversion to fair price
   - Physics-based price evolution

4. **Execution Engine** (`prism/execution/execution_engine.py`)
   - Market order execution
   - Limit order placement
   - Realistic execution latency (10ms default)
   - Fill generation and tracking

5. **Agent Simulator** (`prism/agents/agent_simulator.py`)
   - **Market Makers** (5 agents): Provide liquidity with bid/ask quotes
   - **Noise Traders** (20 agents): Random order generation
   - **Informed Traders** (10 agents): Momentum-based strategies
   - **Momentum Traders** (5 agents): Trend following

6. **Analytics** (`prism/analytics/metrics.py`)
   - Bid-ask spread
   - Order book imbalance
   - Effective spread
   - Price impact
   - Realized volatility
   - VWAP

7. **Persistence Layer** (`prism/persistence/`)
   - **QuestDB**: Execution fills & market state (time-series)
   - **ClickHouse**: Analytics metrics (columnar storage)
   - Graceful degradation if databases unavailable

## Quick Start

### Installation

```bash
cd /path/to/trade2026/prism
pip install -r requirements.txt
```

### Running PRISM

```bash
# Start PRISM server
python -m prism.main

# Or with uvicorn directly
uvicorn prism.main:app --host 0.0.0.0 --port 8360
```

### Configuration

Edit `prism/config/settings.py`:

```python
HOST = "0.0.0.0"
PORT = 8360

# Physics parameters
VOLATILITY = 0.0001          # Base volatility
MOMENTUM_FACTOR = 0.3        # Momentum strength
MEAN_REVERSION_SPEED = 0.1   # Mean reversion rate

# Liquidity parameters
BASE_LIQUIDITY = 1000000     # Initial liquidity
IMPACT_COEFFICIENT = 0.1     # Market impact strength
LIQUIDITY_RECOVERY_RATE = 0.05

# Agent parameters
NUM_MARKET_MAKERS = 5
NUM_NOISE_TRADERS = 20
NUM_INFORMED_TRADERS = 10
NUM_MOMENTUM_TRADERS = 5

# Execution
LATENCY_MS = 10              # Execution latency

# Persistence
QUESTDB_HOST = "localhost"
QUESTDB_PORT = 9000
CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_HTTP_PORT = 8123
```

## API Reference

### Health Check
```
GET /health
```
Returns system status, components, agent count, persistence status.

### Submit Order
```
POST /orders
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "side": "buy",           # "buy" or "sell"
  "order_type": "market",  # "market" or "limit"
  "quantity": 0.5,
  "price": 60000.0         # Required for limit orders
}
```

Returns:
```json
{
  "order_id": "uuid",
  "status": "filled",
  "filled_quantity": 0.5,
  "average_fill_price": 60000.25
}
```

### Get Order Book
```
GET /orderbook/{symbol}
```

Returns aggregated order book with bids/asks.

### Get Market State
```
GET /market/{symbol}
```

Returns current market state: price, volume, liquidity, volatility, momentum.

### List Symbols
```
GET /symbols
```

Returns available trading symbols.

## Testing

### Integration Tests

```bash
# Run full integration test suite
python -m prism.tests.test_integration

# Tests include:
# - Health check
# - Symbol listing
# - Market state retrieval
# - Order book access
# - Market order execution
# - Limit order placement
# - Agent simulation validation
# - Price discovery verification
```

### Performance Benchmarks

```bash
# Run performance benchmarks
python -m prism.tests.benchmark_performance

# Benchmarks measure:
# - Order throughput (orders/sec)
# - Execution latency (ms)
# - Market data access speed
# - Order book query performance
# - Agent simulation volume generation
```

Expected Performance:
- **Order Throughput**: 100-500 orders/sec (depending on concurrency)
- **Execution Latency**: 10-50ms (including network + processing)
- **Market Data Access**: 500-1000 req/sec
- **Agent Volume**: 100-200 units/sec across all symbols

## Data Persistence

### QuestDB Schema

**prism_fills** (execution data):
- timestamp, fill_id, order_id
- symbol, side, price, quantity
- Partitioned by DAY
- Indexed by timestamp

**prism_market_state** (market snapshots):
- timestamp, symbol
- last_price, volume, liquidity
- volatility, momentum, spread
- Partitioned by DAY

### ClickHouse Schema

**prism_analytics** (metrics):
- timestamp, symbol
- bid_ask_spread, mid_price, imbalance
- bid/ask depth, effective_spread
- price_impact, realized_volatility
- Partitioned by MONTH
- Ordered by (symbol, timestamp)

**prism_orderbook_snapshots**:
- timestamp, symbol, level
- bid_price, bid_quantity, bid_num_orders
- ask_price, ask_quantity, ask_num_orders
- Top 10 levels stored every cycle

### Querying Data

```python
from prism.persistence import questdb_client

# Query recent fills
fills = await questdb_client.query_fills(
    symbol="BTCUSDT",
    limit=1000
)

# Query from specific time range
from datetime import datetime, timedelta
fills = await questdb_client.query_fills(
    symbol="ETHUSDT",
    start_time=datetime.utcnow() - timedelta(hours=1),
    limit=5000
)
```

## Integration with Library Service

PRISM integrates with the Library Service (port 8350) for strategy execution:

```python
import requests

# Library Service loads strategy
strategy_response = requests.get("http://localhost:8350/api/v1/entities?type=strategy")

# Strategy generates signals, submits orders to PRISM
order_response = requests.post(
    "http://localhost:8360/orders",
    json={"symbol": "BTCUSDT", "side": "buy", "order_type": "market", "quantity": 0.1}
)

# PRISM executes and returns fills
fill_data = order_response.json()
```

## Production Deployment

### Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY prism/ ./prism/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8360

CMD ["uvicorn", "prism.main:app", "--host", "0.0.0.0", "--port", "8360"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  prism:
    build: .
    ports:
      - "8360:8360"
    environment:
      - HOST=0.0.0.0
      - PORT=8360
      - QUESTDB_HOST=questdb
      - CLICKHOUSE_HOST=clickhouse
    depends_on:
      - questdb
      - clickhouse

  questdb:
    image: questdb/questdb:latest
    ports:
      - "9000:9000"
      - "9009:9009"
    volumes:
      - questdb-data:/var/lib/questdb

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse-data:/var/lib/clickhouse

volumes:
  questdb-data:
  clickhouse-data:
```

### Environment Variables

```bash
# Server
HOST=0.0.0.0
PORT=8360

# Databases
QUESTDB_HOST=localhost
QUESTDB_PORT=9000
CLICKHOUSE_HOST=localhost
CLICKHOUSE_HTTP_PORT=8123

# Simulation Parameters
BASE_LIQUIDITY=1000000
VOLATILITY=0.0001
NUM_MARKET_MAKERS=5
NUM_NOISE_TRADERS=20
```

## Monitoring

### Metrics Endpoints

- `/health` - Component status, agent count, persistence state
- `/symbols` - Available symbols and count
- `/market/{symbol}` - Real-time market state

### Logging

PRISM uses Python's standard logging module:

```python
import logging

# Set log level
logging.basicConfig(level=logging.INFO)

# Component-specific logging
logger = logging.getLogger("prism.execution")
logger.setLevel(logging.DEBUG)
```

Logs include:
- Component initialization
- Order execution (filled quantity, price)
- Agent activity
- Persistence operations
- Errors with stack traces

## Troubleshooting

### Port Already in Use
```bash
# Find process on port 8360
netstat -ano | findstr :8360

# Kill process (Windows)
taskkill /PID <pid> /F

# Kill process (Linux/Mac)
kill -9 <pid>
```

### QuestDB Connection Failed
- Ensure QuestDB is running on port 9000
- Check firewall settings
- Verify network connectivity

### ClickHouse Errors
- PRISM continues with graceful degradation
- Analytics won't be stored but system remains functional
- Check ClickHouse is running and accessible
- Verify HTTP interface enabled (port 8123)

### No Agent Activity
- Check logs for agent initialization
- Verify 40 agents created
- Check `agent_simulator.update()` being called in simulation loop

## Performance Tuning

### Increase Throughput
```python
# Increase concurrent agent activity
NUM_NOISE_TRADERS = 50  # More random orders

# Reduce execution latency
LATENCY_MS = 1  # Faster execution

# Increase simulation tick rate
# In engine.py: await asyncio.sleep(0.05)  # 50ms ticks instead of 100ms
```

### Reduce Latency
```python
# Optimize matching engine
# Use smaller order book depth for faster matching

# Disable analytics calculation
CALCULATE_ANALYTICS_EVERY_N_TRADES = 10000  # Less frequent

# Disable persistence
# Comment out persistence initialization in engine.py
```

## License

Proprietary - Part of Trade2026 Platform

## Support

For issues, questions, or contributions, contact the Trade2026 development team.
