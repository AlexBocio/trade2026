# Appendix F: System Tree Maps & Architecture Diagrams

**Purpose**: Visual representations of Trade2026 system architecture, directory structure, and component relationships.

**Last Updated**: 2025-10-21

---

## 1. Complete Directory Tree

```
C:\claudedesktop_projects\trade2026\
│
├── frontend/                          # React application
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── pages/                    # 50+ page components
│   │   ├── api/                      # API clients (REAL, no mocks)
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── utils/                    # Utility functions
│   │   └── styles/                   # CSS/styling
│   ├── public/                       # Static assets
│   ├── nginx/                        # Nginx configuration
│   ├── Dockerfile                    # Frontend container
│   └── package.json                  # Dependencies
│
├── backend/
│   ├── apps/                         # 16 microservices
│   │   ├── order/                    # Order service (8000)
│   │   │   ├── main.py              # Service entry point
│   │   │   ├── config.yaml          # Configuration
│   │   │   ├── requirements.txt     # Python dependencies
│   │   │   └── Dockerfile           # Container build
│   │   ├── execution/                # Execution service (8010)
│   │   ├── positions/                # Positions service (8020)
│   │   ├── analytics/                # Analytics service (8030)
│   │   ├── accounting/               # Accounting service (8040)
│   │   ├── marketdata/               # Market data service (8050)
│   │   ├── fills/                    # Fills service (8060)
│   │   ├── instruments/              # Instruments service (8070)
│   │   ├── gateway/                  # Market data gateway (8080)
│   │   ├── portfolio/                # Portfolio service (8100)
│   │   ├── risk/                     # Risk service (8150)
│   │   ├── live_gateway/             # Live trading gateway (8200)
│   │   ├── auth/                     # Auth service (8300)
│   │   ├── reference/                # Reference data (8310)
│   │   ├── compliance/               # Compliance service (8320)
│   │   └── reports/                  # Reports service (8330)
│   └── core/                         # Shared libraries
│       ├── messaging/                # NATS client wrappers
│       ├── database/                 # Database clients
│       ├── models/                   # Shared data models
│       └── utils/                    # Common utilities
│
├── library/                          # ML Strategy Library
│   ├── service/                      # Library registry service (8350)
│   │   ├── main.py                  # FastAPI application
│   │   ├── database.py              # PostgreSQL connection
│   │   ├── models.py                # SQLAlchemy models
│   │   └── api/                     # REST API endpoints
│   ├── pipelines/                    # ML pipelines
│   │   ├── default_ml/              # XGBoost ML pipeline
│   │   │   ├── training/            # Model training
│   │   │   ├── serving/             # Model serving
│   │   │   └── feast/               # Feature store config
│   │   └── prism/                   # PRISM pipeline (moved to top-level)
│   └── registry/                     # Strategy registry
│
├── prism/                            # PRISM Physics Engine (Native Python)
│   ├── main.py                       # Entry point
│   ├── agents/                       # 40 trading agents
│   │   ├── base_agent.py            # Base agent class
│   │   ├── market_maker.py          # Market making agents
│   │   ├── trend_follower.py        # Trend following agents
│   │   ├── mean_reverter.py         # Mean reversion agents
│   │   └── random_agent.py          # Random agents
│   ├── core/                         # Core engine
│   │   ├── order_book.py            # Central limit order book
│   │   ├── matching_engine.py       # Order matching
│   │   └── market.py                # Market simulation
│   ├── analytics/                    # Analytics
│   │   ├── portfolio.py             # Portfolio tracking
│   │   ├── metrics.py               # Performance metrics
│   │   └── persistence.py           # QuestDB + ClickHouse
│   ├── tests/                        # Integration tests
│   └── config/                       # Configuration files
│
├── infrastructure/
│   ├── docker/                       # Docker Compose files
│   │   ├── docker-compose.core.yml           # 8 infrastructure services
│   │   ├── docker-compose.apps.yml           # 16 application services
│   │   ├── docker-compose.frontend.yml       # Nginx + React
│   │   ├── docker-compose.library-db.yml     # PostgreSQL
│   │   └── .env                              # Environment variables
│   └── configs/                      # Configuration files
│       ├── nats/                     # NATS configuration
│       ├── nginx/                    # Nginx configuration
│       ├── questdb/                  # QuestDB configuration
│       └── opa/                      # OPA policies
│
├── data/                             # All persistent data (Docker volumes)
│   ├── nats/                         # NATS JetStream data
│   ├── valkey/                       # Valkey cache snapshots
│   ├── questdb/                      # Time-series database
│   ├── clickhouse/                   # Analytics database
│   ├── seaweedfs/                    # Object storage
│   ├── opensearch/                   # Search indices
│   ├── postgres/                     # SQL database
│   └── opa/                          # Policy bundles
│
├── docs/                             # Documentation
│   ├── system_overview/              # THIS DOCUMENTATION
│   │   ├── 00_TRADE2026_5W_OVERVIEW.md      # Main 5W overview
│   │   ├── appendix_A_infrastructure.md     # Infrastructure details
│   │   ├── appendix_B_backend_services.md   # Backend services
│   │   ├── appendix_C_frontend.md           # Frontend details
│   │   ├── appendix_D_ml_library.md         # ML Library details
│   │   ├── appendix_E_prism.md              # PRISM Physics
│   │   ├── appendix_F_tree_maps.md          # This file
│   │   ├── appendix_G_data_flow.md          # Data flow diagrams
│   │   ├── appendix_H_network.md            # Network topology
│   │   ├── appendix_I_deployment.md         # Deployment guide
│   │   └── appendix_J_external_venues.md    # External venue integration
│   └── appendices/                   # Phase appendices (old structure)
│
├── archive/                          # Archived documentation
│   ├── old_sessions/                 # Historical session files
│   └── old_documentation/            # Superseded docs
│
├── MASTER_PLAN.md                    # 8-phase integration roadmap
├── README.md                         # Project README
├── README_START_HERE.md              # Executive summary
├── SYSTEM_STATUS_2025-10-20.md       # Latest system audit
├── COMPLETION_TRACKER_UPDATED.md     # Phase completion tracking
├── QUICK_HANDOFF.md                  # Session handoff
└── CLICKHOUSE_FIX_SUMMARY.md         # ClickHouse persistence fix
```

---

## 2. Service Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                     INFRASTRUCTURE LAYER                         │
│  ┌──────┐  ┌──────┐  ┌────────┐  ┌──────────┐  ┌──────────┐   │
│  │ NATS │  │Valkey│  │QuestDB │  │ClickHouse│  │SeaweedFS │   │
│  └───┬──┘  └───┬──┘  └────┬───┘  └─────┬────┘  └─────┬────┘   │
│      │         │          │            │             │          │
│  ┌───┴─────────┴──────────┴────────────┴─────────────┴──────┐  │
│  │         OpenSearch, PostgreSQL, OPA                       │  │
│  └───────────────────────────┬────────────────────────────────┘  │
└────────────────────────────┬─┴───────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│   Gateway      │  │ Live Gateway    │  │  Market Data   │
│   (8080)       │  │   (8200)        │  │   (8050)       │
│   Binance Mock │  │   IBKR SHADOW   │  │   Distribution │
└───────┬────────┘  └────────┬────────┘  └───────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  NATS Topics    │
                    │  (Pub/Sub)      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  Order Service │  │ Portfolio Svc   │  │  Risk Service  │
│    (8000)      │  │    (8100)       │  │    (8150)      │
│  Validation    │  │  Position Track │  │  Risk Checks   │
└───────┬────────┘  └─────────────────┘  └────────────────┘
        │
        │ NATS: order.execute
        ▼
┌────────────────┐
│ Execution Svc  │
│    (8010)      │
│  Smart Routing │
└───────┬────────┘
        │
        │ NATS: order.fill
        ▼
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│  Fills Service │──────▶│ Accounting Svc │──────▶│ Positions Svc  │
│    (8060)      │       │    (8040)      │       │    (8020)      │
│  Fill Matching │       │  P&L Booking   │       │  Position Agg  │
└────────────────┘       └────────────────┘       └────────────────┘
        │
        │ Updates
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PERSISTENCE LAYER                            │
│  QuestDB (orders, fills, ticks) + Valkey (cache)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Architecture

### Order Flow (End-to-End)

```
┌─────────────┐
│   Frontend  │  User submits order
│  (React UI) │
└──────┬──────┘
       │ HTTP POST /orders
       ▼
┌──────────────┐
│    Nginx     │  Reverse proxy
│   (port 80)  │
└──────┬───────┘
       │ Forward to backend
       ▼
┌──────────────────┐
│  Order Service   │  1. Validate order (size, price, symbol)
│    (8000)        │  2. Check OPA policy
└──────┬───────────┘  3. Persist to QuestDB
       │              4. Publish to NATS
       │ NATS: order.create
       ▼
┌──────────────────┐
│  Risk Service    │  1. Pre-trade risk checks
│    (8150)        │  2. Position limits, concentration
└──────┬───────────┘  3. Approve/Reject
       │ NATS: order.risk.approved
       ▼
┌───────────────────┐
│ Execution Service │  1. Smart order routing
│    (8010)         │  2. Venue selection (IBKR, Binance)
└──────┬────────────┘  3. Send to Live Gateway (if LIVE mode)
       │ NATS: order.execute
       ▼
┌───────────────────┐
│  Live Gateway     │  1. Check trading mode (SHADOW/CANARY/LIVE)
│    (8200)         │  2. If SHADOW: log only
└──────┬────────────┘  3. If LIVE: send to IBKR
       │ NATS: order.fill (simulated or real)
       ▼
┌──────────────────┐
│  Fills Service   │  1. Match fills to orders
│    (8060)        │  2. Persist to QuestDB
└──────┬───────────┘  3. Notify downstream services
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌──────────────┐
│ Accounting  │   │ Positions   │   │  Portfolio   │
│   (8040)    │   │   (8020)    │   │   (8100)     │
│ Book P&L    │   │ Update Pos  │   │ Recalc Value │
└─────────────┘   └─────────────┘   └──────────────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │    QuestDB      │  Persist all events
                │  (Time-series)  │
                └─────────────────┘
```

### Market Data Flow

```
┌──────────────────┐         ┌──────────────────┐
│   Gateway        │         │  Live Gateway    │
│   (Binance Mock) │         │  (IBKR)          │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │ Ticks (BTC/USDT)          │ Ticks (AAPL, SPY)
         │                            │
         └──────────┬─────────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Market Data Svc    │  1. Normalize ticks
         │      (8050)         │  2. Publish to NATS
         └──────────┬──────────┘  3. Cache in Valkey
                    │              4. Persist to QuestDB
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│Portfolio │  │   Risk   │  │Analytics │
│ (8100)   │  │  (8150)  │  │ (8030)   │
│Mark-to-  │  │Real-time │  │Technical │
│Market    │  │VaR calc  │  │Indicators│
└──────────┘  └──────────┘  └──────────┘
       │            │            │
       └────────────┴────────────┘
                    │
                    ▼
              ┌──────────┐
              │  Valkey  │  Cache latest prices
              │ (Redis)  │  TTL: 60 seconds
              └──────────┘
                    │
                    ▼
              ┌──────────┐
              │ QuestDB  │  Persist all ticks
              │  (ILP)   │  Retention: 90 days
              └──────────┘
```

---

## 4. Network Topology (CPGS v1.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Internet / External                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Port 80       │
                    │   (Nginx)       │
                    └────────┬────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                   Docker Network: frontend                        │
│                   Subnet: 172.20.0.0/16                          │
│                                                                   │
│  ┌──────────────────┐          ┌──────────────────┐            │
│  │  Nginx Container │          │  React Build     │            │
│  │  172.20.0.10     │────────▶ │  (static files)  │            │
│  │  Port: 80        │          └──────────────────┘            │
│  └────────┬─────────┘                                           │
└───────────┼─────────────────────────────────────────────────────┘
            │
            │ Reverse Proxy Routing:
            │ /api/order/* → http://order-service:8000
            │ /api/marketdata/* → http://marketdata-service:8050
            │ /api/portfolio/* → http://portfolio-service:8100
            │
┌───────────▼─────────────────────────────────────────────────────┐
│              Docker Network: lowlatency                          │
│              Subnet: 172.21.0.0/16                              │
│              (Latency-critical services)                         │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Services on 8000-8199 (low-latency tier)              │    │
│  │                                                        │    │
│  │ order-service        172.21.0.10:8000                 │    │
│  │ execution-service    172.21.0.11:8010                 │    │
│  │ positions-service    172.21.0.12:8020                 │    │
│  │ analytics-service    172.21.0.13:8030                 │    │
│  │ accounting-service   172.21.0.14:8040                 │    │
│  │ marketdata-service   172.21.0.15:8050                 │    │
│  │ fills-service        172.21.0.16:8060                 │    │
│  │ instruments-service  172.21.0.17:8070                 │    │
│  │ gateway-service      172.21.0.18:8080                 │    │
│  │ portfolio-service    172.21.0.19:8100                 │    │
│  │ risk-service         172.21.0.20:8150                 │    │
│  │ live-gateway         172.21.0.21:8200                 │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────┬─────────────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────────────┐
│              Docker Network: backend                             │
│              Subnet: 172.22.0.0/16                              │
│              (Backend services + Infrastructure)                 │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Services on 8300-8499 (backend tier)                  │    │
│  │                                                        │    │
│  │ auth-service         172.22.0.10:8300                 │    │
│  │ reference-service    172.22.0.11:8310                 │    │
│  │ compliance-service   172.22.0.12:8320                 │    │
│  │ reports-service      172.22.0.13:8330                 │    │
│  │ library-service      172.22.0.14:8350                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Infrastructure Services (accessible from all networks) │    │
│  │                                                        │    │
│  │ nats             172.22.0.20:4222, 8222               │    │
│  │ valkey           172.22.0.21:6379                     │    │
│  │ questdb          172.22.0.22:9000, 9009               │    │
│  │ clickhouse       172.22.0.23:8123, 9000               │    │
│  │ seaweedfs        172.22.0.24:8333, 8080               │    │
│  │ opensearch       172.22.0.25:9200                     │    │
│  │ postgres-library 172.22.0.26:5432                     │    │
│  │ opa              172.22.0.27:8181                     │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│            Native Python Process (Host: 127.0.0.1)              │
│                                                                   │
│  PRISM Physics Engine                                           │
│  - Connects to NATS (localhost:4222)                           │
│  - Writes to QuestDB (localhost:9009)                          │
│  - Writes to ClickHouse (localhost:8123)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Component Relationship Matrix

| Component | Depends On | Used By | Data Stores |
|-----------|-----------|---------|-------------|
| NATS | None | All services | JetStream |
| Valkey | None | Market Data, Risk, Portfolio | Memory |
| QuestDB | None | Order, Execution, Fills, Market Data, PRISM | Disk (columnar) |
| ClickHouse | None | PRISM, Analytics, Reports | Disk (columnar) |
| PostgreSQL | None | Library Service | Disk (relational) |
| Order Service | NATS, QuestDB, OPA | Frontend, Execution | QuestDB |
| Execution Service | NATS, Order | Live Gateway | QuestDB |
| Market Data | NATS, QuestDB, Valkey | Portfolio, Risk, Analytics | QuestDB, Valkey |
| Portfolio | NATS, Market Data, Positions | Frontend, Risk | Valkey, QuestDB |
| Risk | NATS, Portfolio, Market Data | Order, Frontend | Valkey |
| PRISM | NATS, QuestDB, ClickHouse | Analytics | QuestDB, ClickHouse |
| Library Service | PostgreSQL | Frontend, ML Pipelines | PostgreSQL |
| Frontend | All backend services | Users | None (stateless) |

---

## 6. File Size & Service Counts

### Code Statistics

```
Total Lines of Code: ~50,000
- Backend (Python): ~25,000 lines
- Frontend (TypeScript/React): ~20,000 lines
- PRISM (Python): ~3,000 lines
- Library (Python): ~2,000 lines
```

### Service Breakdown

```
Infrastructure:      8 services
Backend Apps:       16 services
Frontend:            1 service (Nginx)
PRISM:               1 service (native Python)
─────────────────────────────────
Total:              26 services
```

### Docker Images Size

```
Total Docker Images: ~5 GB
- Infrastructure images: ~2 GB
- Backend images: ~2.5 GB
- Frontend image: ~500 MB
```

---

## Summary

This appendix provides complete visual documentation of Trade2026's architecture:

- **Directory Tree**: Complete file structure
- **Dependency Graph**: Service relationships
- **Data Flow**: Order and market data pipelines
- **Network Topology**: CPGS v1.0 implementation
- **Component Matrix**: Dependencies and data stores
- **Statistics**: Code size and service counts

**Next**: [Appendix G: Data Flow & Integration](./appendix_G_data_flow.md)

---
