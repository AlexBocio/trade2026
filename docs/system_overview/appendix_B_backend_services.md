# Appendix B: Backend Services

**Purpose**: Detailed documentation for all 16 backend application services.

**Last Updated**: 2025-10-21
**Health Status**: 15/16 services operational (94%)

---

## Service Overview

### Low-Latency Services (8000-8199)

| Service | Port | Purpose | Code Location | Health |
|---------|------|---------|---------------|--------|
| Order | 8000 | Order management, validation, routing | `backend/apps/order/` | ✅ |
| Execution | 8010 | Order execution, smart routing | `backend/apps/execution/` | ✅ |
| Positions | 8020 | Real-time position tracking | `backend/apps/positions/` | ✅ |
| Analytics | 8030 | Real-time market analytics | `backend/apps/analytics/` | ✅ |
| Accounting | 8040 | P&L accounting, trade booking | `backend/apps/accounting/` | ✅ |
| Market Data | 8050 | Market data ingestion, distribution | `backend/apps/marketdata/` | ✅ |
| Fills | 8060 | Fill management, matching | `backend/apps/fills/` | ✅ |
| Instruments | 8070 | Instrument reference database | `backend/apps/instruments/` | ✅ |
| Gateway | 8080 | Market data gateway (Binance mock) | `backend/apps/gateway/` | ✅ |
| Portfolio | 8100 | Portfolio management | `backend/apps/portfolio/` | ✅ |
| Risk | 8150 | Risk management | `backend/apps/risk/` | ✅ |
| Live Gateway | 8200 | Live trading gateway (IBKR SHADOW) | `backend/apps/live_gateway/` | ✅ |

### Backend Services (8300-8499)

| Service | Port | Purpose | Code Location | Health |
|---------|------|---------|---------------|--------|
| Auth | 8300 | Authentication, JWT tokens | `backend/apps/auth/` | ✅ |
| Reference | 8310 | Reference data management | `backend/apps/reference/` | ✅ |
| Compliance | 8320 | Pre-trade compliance checks | `backend/apps/compliance/` | ✅ |
| Reports | 8330 | Report generation, scheduling | `backend/apps/reports/` | ✅ |
| Library | 8350 | ML strategy library registry | `library/service/` | ✅ |

---

## 1. Order Service (Port 8000)

### Purpose
Central order management service. Validates, routes, and tracks all orders.

### Key Features
- Order validation (price, size, symbol)
- Order book integration
- NATS messaging for order flow
- QuestDB persistence

### API Endpoints
```
POST   /orders              Create new order
GET    /orders              List orders
GET    /orders/{id}         Get order details
PUT    /orders/{id}/cancel  Cancel order
GET    /health              Health check
```

### Configuration
```yaml
# backend/apps/order/config.yaml
nats_url: nats://nats:4222
questdb_host: questdb
questdb_port: 9009
port: 8000
```

### Data Flow
```
Client → POST /orders → Validation → NATS (order.create) → Execution Service
                     ↓
                  QuestDB (persistence)
```

---

## 2. Execution Service (Port 8010)

### Purpose
Executes orders by routing to appropriate venues (IBKR, Binance, etc.).

### Key Features
- Smart order routing
- Venue selection logic
- Fill generation
- Execution reports

### Trading Modes
- **SHADOW**: Log orders, don't send to broker (current)
- **CANARY**: Send small % to broker for validation
- **LIVE**: Full production trading

### Configuration
```yaml
# backend/apps/execution/config.yaml
trading_mode: SHADOW
venues:
  - IBKR
  - BINANCE
nats_url: nats://nats:4222
```

---

## 3. Market Data Service (Port 8050)

### Purpose
Ingests and distributes market data (ticks, quotes, trades).

### Key Features
- Multi-venue data ingestion
- Real-time tick distribution via NATS
- QuestDB persistence (ticks table)
- Valkey caching for latest prices

### Data Sources
- Gateway Service (Binance mock)
- Live Gateway (IBKR)
- CCXT adapters (100+ exchanges)

### Performance
- Ingestion: 100,000+ ticks/second
- Latency: Sub-millisecond (NATS pub/sub)
- Storage: QuestDB (ILP protocol)

---

## 4. Portfolio Service (Port 8100)

### Purpose
Tracks real-time portfolio state (positions, cash, P&L).

### Key Features
- Position aggregation
- Real-time P&L calculation
- Multi-currency support
- Historical portfolio snapshots

### Data Sources
- Order Service (order updates)
- Fills Service (fill notifications)
- Market Data (price updates for mark-to-market)

---

## 5. Risk Service (Port 8150)

### Purpose
Real-time risk monitoring and pre-trade risk checks.

### Key Features
- Position limits
- Drawdown monitoring
- VaR calculation
- Pre-trade risk checks (size, concentration)

### Risk Checks
1. **Position Limit**: Max position size per symbol
2. **Concentration**: Max % of portfolio in single symbol
3. **Drawdown**: Max loss from peak
4. **Leverage**: Max leverage allowed

---

## 6. Gateway Service (Port 8080)

### Purpose
Market data gateway for external venues (Binance).

### Current Config
```yaml
exchange: mock  # Was 'binance', changed to avoid rate limits
symbols:
  - BTC/USDT
  - ETH/USDT
refresh_interval: 5
```

### Note
Currently in mock mode to avoid API rate limits during development.

---

## 7. Live Gateway (Port 8200)

### Purpose
Live trading gateway for IBKR (Interactive Brokers).

### Current Config
```yaml
modes:
  global: "SHADOW"  # SHADOW | CANARY | LIVE
  venues:
    IBKR:
      mode: "SHADOW"
      canary_pct: 0.0
```

### IBKR Connection
```yaml
venues:
  ibkr:
    host: "127.0.0.1"
    port: 7497  # Paper trading
    client_id: 7
    paper_only: true
```

### Trading Modes Progression
1. **SHADOW** (Current): All orders logged, none sent
2. **CANARY** (Future): 1-5% orders sent live for validation
3. **LIVE** (Production): 100% live trading

---

## 8. Library Service (Port 8350)

### Purpose
ML strategy library registry and API.

### Key Features
- Strategy CRUD API
- Model version management
- Backtest results storage
- PostgreSQL metadata database

### API Endpoints
```
GET    /api/v1/health           Health check
GET    /api/v1/strategies       List strategies
POST   /api/v1/strategies       Register strategy
GET    /api/v1/strategies/{id}  Get strategy
PUT    /api/v1/strategies/{id}  Update strategy
DELETE /api/v1/strategies/{id}  Delete strategy
```

### Database
- **PostgreSQL**: `library` database
- **Tables**: strategies, models, features, backtests

---

## Common Patterns

### Health Checks
All services expose `/health` endpoint returning:
```json
{
  "status": "healthy",
  "service": "order",
  "version": "1.0.0",
  "uptime": 3600
}
```

### NATS Messaging
All services use NATS for inter-service communication:
```python
# Publish
await nc.publish("order.create", order_json.encode())

# Subscribe
await nc.subscribe("order.create", cb=handle_order)

# Request/Reply
response = await nc.request("order.get", {"id": "ORD123"}.encode())
```

### Configuration
All services load config from:
1. Environment variables (`.env`)
2. YAML config file (`config.yaml`)
3. Command-line arguments

### Docker Build
Standard Dockerfile pattern:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## Service Dependencies

```
┌─────────────────────────────────────────────────────┐
│                   Infrastructure                     │
│  NATS, Valkey, QuestDB, ClickHouse, PostgreSQL      │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼──────────┐       ┌───────▼──────┐
│   Gateway    │       │ Live Gateway │
│   (8080)     │       │    (8200)    │
└───┬──────────┘       └───────┬──────┘
    │                          │
    └──────────┬───────────────┘
               │
         ┌─────▼──────┐
         │Market Data │
         │   (8050)   │
         └─────┬──────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼──┐   ┌───▼───┐  ┌──▼────┐
│Order │   │Portfolio│ │Risk   │
│(8000)│   │ (8100) │ │(8150) │
└───┬──┘   └────────┘ └───────┘
    │
┌───▼─────┐
│Execution│
│ (8010)  │
└───┬─────┘
    │
┌───▼──┐
│Fills │
│(8060)│
└──────┘
```

---

## Monitoring

### Health Check All Services
```bash
# Low-latency services
for port in 8000 8010 8020 8030 8040 8050 8060 8070 8080 8100 8150 8200; do
  echo -n "Port $port: "
  curl -sf http://localhost:$port/health && echo "✅" || echo "❌"
done

# Backend services
for port in 8300 8310 8320 8330; do
  echo -n "Port $port: "
  curl -sf http://localhost:$port/health && echo "✅" || echo "❌"
done

# Library service (different health path)
echo -n "Port 8350: "
curl -sf http://localhost:8350/api/v1/health && echo "✅" || echo "❌"
```

### View Logs
```bash
# Specific service
docker logs -f order-service

# All services
docker-compose -f infrastructure/docker/docker-compose.apps.yml logs -f
```

---

## Next: Frontend

See [Appendix C: Frontend Application](./appendix_C_frontend.md)

---
