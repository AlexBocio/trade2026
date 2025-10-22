# Trade2026 - Complete System Overview (5W Framework)

**Document Purpose**: This is the master reference document for understanding the Trade2026 unified trading platform. It provides a comprehensive overview using the 5W framework (Who, What, When, Where, Why) and links to detailed technical appendices.

**Status**: Phases 1-5 COMPLETE (85% overall) - Production-ready for development/testing
**Last Updated**: 2025-10-21
**Location**: C:\claudedesktop_projects\trade2026\

---

## Table of Contents

1. [The 5W Framework](#the-5w-framework)
2. [System Components Overview](#system-components-overview)
3. [Detailed Appendices](#detailed-appendices)
4. [Quick Reference](#quick-reference)

---

## The 5W Framework

### WHO - Stakeholders & Users

**Primary User**: Algorithmic trader using Interactive Brokers (IBKR) as primary broker

**System Operators**:
- Development team maintaining 26 services
- Claude Code AI assistant for development and maintenance
- DevOps managing Docker infrastructure

**Target Markets**:
- Equities (US markets via IBKR)
- Cryptocurrencies (Binance configured but in mock mode)
- Multi-asset class support via CCXT library (100+ exchanges)

**System Personas**:
- **Portfolio Manager**: Monitors positions, risk, P&L
- **Strategy Developer**: Creates and tests ML-based trading strategies
- **Market Analyst**: Analyzes market data, backtests strategies
- **System Administrator**: Maintains infrastructure, monitors health

---

### WHAT - System Description

**Trade2026** is a unified algorithmic trading platform that integrates:

1. **Backend Services** (16 microservices)
   - Order management and execution
   - Market data ingestion and processing
   - Portfolio and risk management
   - Analytics and reporting
   - Live trading gateways

2. **Infrastructure Services** (8 systems)
   - Message streaming (NATS)
   - Time-series databases (QuestDB, ClickHouse)
   - Caching (Valkey)
   - Search (OpenSearch)
   - Object storage (SeaweedFS)
   - SQL database (PostgreSQL)
   - Policy engine (OPA)

3. **Frontend Application**
   - React + TypeScript UI (50+ pages)
   - Nginx reverse proxy
   - Real-time dashboard
   - Strategy management interface

4. **ML Pipelines** (2 systems)
   - **Strategy Library**: Central registry for trading strategies
   - **Default ML Pipeline**: XGBoost-based alpha generation with Feast feature store
   - **PRISM Physics Engine**: 40-agent market simulation for backtesting

**Current Scale**:
- 26 total services operational (25 Docker containers + 1 native Python)
- Infrastructure: 8/8 healthy (100%)
- Applications: 15/16 healthy (94%)
- System uptime: 13+ hours continuous, zero crashes

---

### WHEN - Timeline & Development Phases

**Project Start**: 2025-10-14
**Current Status**: 2025-10-21 (7 days of development)
**Time Invested**: ~120 hours of development work

**Development Timeline**:

| Phase | Name | Duration | Status | Completed Date |
|-------|------|----------|--------|---------------|
| 1 | Foundation | Week 1 | ✅ COMPLETE | 2025-10-14 |
| 2 | Backend Migration | Week 1-2 | ✅ COMPLETE | 2025-10-15 |
| 3 | Frontend Integration | Week 2 | ✅ COMPLETE | 2025-10-15 |
| 4 | ML Library | Week 2-3 | ✅ COMPLETE | 2025-10-16 |
| 5 | PRISM Physics | Week 3 | ✅ COMPLETE | 2025-10-17 |
| 6 | Hybrid Pipeline | N/A | ⏸️ SKIPPED | N/A (optional) |
| 7 | Testing & Validation | Future | ⏸️ PENDING | Est. 10-15 hours |
| 8 | Documentation | Ongoing | 🚀 IN PROGRESS | Est. 5-8 hours |

**Key Milestones**:
- **2025-10-14**: Infrastructure deployed, all 8 core services healthy
- **2025-10-15**: Backend services migrated, frontend integrated
- **2025-10-16**: ML Library operational with PostgreSQL
- **2025-10-17**: PRISM Physics Engine deployed with 40 agents
- **2025-10-20**: ClickHouse persistence fixed, comprehensive system audit
- **2025-10-21**: Complete system documentation created

**Trading Progression** (Future):
- **SHADOW Mode** (Current): All orders logged but not sent to broker
- **CANARY Mode** (Planned): Small percentage of orders sent live for validation
- **LIVE Mode** (Production): Full production trading

---

### WHERE - System Architecture & Deployment

**Physical Location**: C:\claudedesktop_projects\trade2026\

**Directory Structure**:
```
Trade2026/
├── frontend/              # React application (50+ pages)
│   ├── src/
│   ├── public/
│   └── nginx/            # Reverse proxy configuration
├── backend/
│   ├── apps/             # 16 application services
│   │   ├── order/        # Order management (port 8000)
│   │   ├── marketdata/   # Market data (port 8050)
│   │   ├── portfolio/    # Portfolio tracking (port 8100)
│   │   ├── risk/         # Risk management (port 8150)
│   │   ├── execution/    # Order execution (port 8010)
│   │   ├── positions/    # Position tracking (port 8020)
│   │   ├── analytics/    # Analytics engine (port 8030)
│   │   ├── gateway/      # Market data gateway (port 8080)
│   │   ├── live_gateway/ # Live trading gateway (port 8200)
│   │   ├── accounting/   # P&L accounting (port 8040)
│   │   ├── fills/        # Fill management (port 8060)
│   │   ├── instruments/  # Instrument database (port 8070)
│   │   ├── auth/         # Authentication (port 8300)
│   │   ├── reference/    # Reference data (port 8310)
│   │   ├── compliance/   # Compliance checks (port 8320)
│   │   └── reports/      # Report generation (port 8330)
│   └── core/             # Shared libraries
├── library/              # ML pipelines
│   ├── service/          # Library registry service (port 8350)
│   ├── pipelines/
│   │   ├── default_ml/   # XGBoost ML pipeline
│   │   └── prism/        # Physics-based simulation
│   └── registry/         # Strategy registry
├── prism/                # PRISM Physics Engine
│   ├── agents/           # 40 trading agents
│   ├── core/             # Order book, matching engine
│   ├── analytics/        # Market analytics
│   └── tests/            # Integration tests
├── infrastructure/
│   ├── docker/           # Docker Compose files
│   │   ├── docker-compose.core.yml        # 8 infrastructure services
│   │   ├── docker-compose.apps.yml        # 16 application services
│   │   ├── docker-compose.frontend.yml    # Nginx + React
│   │   └── docker-compose.library-db.yml  # PostgreSQL for ML Library
│   └── configs/          # Configuration files
├── data/                 # All persistent data
│   ├── nats/            # NATS JetStream data
│   ├── valkey/          # Valkey cache snapshots
│   ├── questdb/         # Time-series data (hot)
│   ├── clickhouse/      # Analytics data (warm/cold)
│   ├── seaweedfs/       # Object storage
│   ├── opensearch/      # Search indices
│   ├── postgres/        # SQL database
│   └── opa/             # Policy bundles
├── docs/                 # Documentation
│   ├── system_overview/  # This documentation
│   └── appendices/       # Phase appendices
└── archive/              # Old documentation (archived 2025-10-20)
```

**Network Architecture** (CPGS v1.0):

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network: frontend                  │
│                     (Public-facing services)                 │
│                                                              │
│  ┌──────────┐           ┌────────────────┐                 │
│  │  Nginx   │◄──────────│  React App     │                 │
│  │  :80     │           │  (build)       │                 │
│  └────┬─────┘           └────────────────┘                 │
│       │                                                     │
└───────┼─────────────────────────────────────────────────────┘
        │
        │ Reverse Proxy
        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Docker Network: lowlatency                  │
│                 (Latency-critical services: 8000-8199)       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Order   │  │  Market  │  │Portfolio │  │   Risk   │   │
│  │  :8000   │  │  Data    │  │  :8100   │  │  :8150   │   │
│  │          │  │  :8050   │  │          │  │          │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │Execution │  │ Gateway  │  │Positions │  │Analytics │   │
│  │  :8010   │  │  :8080   │  │  :8020   │  │  :8030   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Accounting│  │  Fills   │  │Instruments│ │   Live   │   │
│  │  :8040   │  │  :8060   │  │  :8070   │  │ Gateway  │   │
│  │          │  │          │  │          │  │  :8200   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
└───────┼──────────────────────────────────────────────────────┘
        │
        │ Backend Communication
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Docker Network: backend                    │
│                  (Backend services: 8300-8499)               │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │Reference │  │Compliance│  │ Reports  │   │
│  │  :8300   │  │  :8310   │  │  :8320   │  │  :8330   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐                                               │
│  │ Library  │  (ML Strategy Library)                        │
│  │  :8350   │                                               │
│  └──────────┘                                               │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Infrastructure Services (All Networks)         │ │
│  │                                                        │ │
│  │  NATS :4222         Valkey :6379     QuestDB :9000   │ │
│  │  ClickHouse :8123   SeaweedFS :8333  OpenSearch :9200│ │
│  │  PostgreSQL :5432   OPA :8181                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Native Python Process                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │             PRISM Physics Engine                   │    │
│  │  • 40 trading agents                              │    │
│  │  • Order book simulation                          │    │
│  │  • Price discovery                                │    │
│  │  • Dual persistence (QuestDB + ClickHouse)       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Deployment Model**:
- **Infrastructure**: Docker Compose (25 containers)
- **PRISM**: Native Python process (not containerized)
- **Data Persistence**: Docker-managed volumes
- **Configuration**: Environment variables via .env file

**Port Allocation** (CPGS v1.0):
- **Frontend**: 80, 443 (Nginx)
- **Low-latency**: 8000-8199 (order flow, market data, execution)
- **Backend**: 8300-8499 (auth, compliance, reporting, ML library)
- **Infrastructure**: Various (NATS 4222, QuestDB 9000, ClickHouse 8123, etc.)

---

### WHY - Purpose & Rationale

**Primary Goal**: Create a unified, production-ready algorithmic trading platform that consolidates:
- Backend microservices (previously Trade2025 at C:\Trade2025\)
- Frontend UI (previously GUI at C:\GUI\)
- ML pipelines (newly developed)

**Business Drivers**:
1. **Consolidation**: Eliminate duplication between backend and frontend projects
2. **Integration**: Connect real backend APIs to frontend (remove mock data)
3. **Scalability**: Containerized microservices architecture
4. **ML-First**: Built-in strategy library and ML pipelines
5. **Production-Ready**: Robust infrastructure with monitoring and health checks

**Technical Rationale**:

**Why Docker?**
- Consistent deployment across environments
- Easy scaling and orchestration
- Isolated service dependencies
- Simplified CI/CD

**Why Microservices?**
- Independent scaling of services
- Fault isolation
- Technology flexibility per service
- Easier to maintain and update

**Why Multiple Databases?**
- **QuestDB**: Fast time-series ingestion (hot data, low latency)
- **ClickHouse**: Analytics queries on warm/cold data
- **PostgreSQL**: Relational data for ML Library metadata
- **Valkey**: In-memory caching for ultra-low latency
- **OpenSearch**: Full-text search and log aggregation
- **SeaweedFS**: Object storage for large files

**Why NATS?**
- Ultra-low latency messaging (microseconds)
- Built-in persistence (JetStream)
- Pub/sub and request/reply patterns
- Clustering support for HA

**Why PRISM Physics Engine?**
- Realistic market simulation with order book dynamics
- Multi-agent backtesting environment
- Price discovery modeling
- Test strategies before live trading

**Why IBKR?**
- User's primary broker
- Professional-grade API (TWS/Gateway)
- Direct market access
- Wide range of instruments

**Risk Management Philosophy**:
- **SHADOW Mode First**: Log all orders, send none to broker
- **CANARY Testing**: Gradually increase live order percentage
- **Multi-Layer Validation**: Pre-trade risk checks, compliance, OPA policies
- **Comprehensive Monitoring**: Health endpoints, metrics, alerting

---

## System Components Overview

### 1. Infrastructure Layer (8 Services)

**Purpose**: Provide foundational services for message streaming, data storage, caching, and search.

| Service | Type | Port | Purpose | Health Status |
|---------|------|------|---------|---------------|
| NATS | Message Broker | 4222 | Ultra-low latency messaging, JetStream persistence | ✅ 100% |
| Valkey | Cache | 6379 | In-memory caching (Redis alternative) | ✅ 100% |
| QuestDB | Time-Series DB | 9000 | Hot data, sub-millisecond ingestion | ✅ 100% |
| ClickHouse | OLAP DB | 8123 | Warm/cold analytics data | ✅ 100% |
| SeaweedFS | Object Storage | 8333 | S3-compatible large file storage | ✅ 100% |
| OpenSearch | Search Engine | 9200 | Full-text search, log aggregation | ✅ 100% |
| PostgreSQL | SQL Database | 5432 | ML Library metadata | ✅ 100% |
| OPA | Policy Engine | 8181 | Authorization and compliance policies | ⚠️ Warning |

**Details**: See [Appendix A: Infrastructure Components](#appendix-a-infrastructure-components)

---

### 2. Application Layer (16 Services)

**Purpose**: Core trading functionality - order management, market data, portfolio, risk, execution.

**Low-Latency Services** (8000-8199):

| Service | Port | Purpose | Health Status |
|---------|------|---------|---------------|
| Order | 8000 | Order management, validation, routing | ✅ Healthy |
| Execution | 8010 | Order execution, smart routing | ✅ Healthy |
| Positions | 8020 | Real-time position tracking | ✅ Healthy |
| Analytics | 8030 | Real-time market analytics | ✅ Healthy |
| Accounting | 8040 | P&L accounting, trade booking | ✅ Healthy |
| Market Data | 8050 | Market data ingestion, distribution | ✅ Healthy |
| Fills | 8060 | Fill management, matching | ✅ Healthy |
| Instruments | 8070 | Instrument reference database | ✅ Healthy |
| Gateway | 8080 | Market data gateway (Binance mock) | ✅ Healthy |
| Live Gateway | 8200 | Live trading gateway (IBKR SHADOW) | ✅ Healthy |

**Backend Services** (8300-8499):

| Service | Port | Purpose | Health Status |
|---------|------|---------|---------------|
| Auth | 8300 | Authentication, JWT tokens | ✅ Healthy |
| Reference | 8310 | Reference data management | ✅ Healthy |
| Compliance | 8320 | Pre-trade compliance checks | ✅ Healthy |
| Reports | 8330 | Report generation, scheduling | ✅ Healthy |
| Library | 8350 | ML strategy library registry | ✅ Healthy |

**Details**: See [Appendix B: Backend Services](#appendix-b-backend-services)

---

### 3. Frontend Layer

**Purpose**: User interface for monitoring, trading, and strategy management.

| Component | Technology | Purpose | Status |
|-----------|-----------|---------|--------|
| React App | TypeScript + React | 50+ pages, real-time dashboard | ✅ Operational |
| Nginx | Reverse Proxy | Serving on port 80, API routing | ✅ Operational |

**Key Features**:
- Real-time order monitoring
- Portfolio and position tracking
- Risk dashboard
- Strategy management UI
- Market data visualization
- P&L reporting

**Details**: See [Appendix C: Frontend Application](#appendix-c-frontend-application)

---

### 4. ML Library (Strategy & ML Pipelines)

**Purpose**: Central registry for trading strategies with ML-based alpha generation.

| Component | Technology | Purpose | Status |
|-----------|-----------|---------|--------|
| Library Service | FastAPI + PostgreSQL | Strategy registry, CRUD API | ✅ Operational |
| Default ML Pipeline | XGBoost + Feast | ML-based alpha signals | ✅ Operational |
| Feature Store | Feast | Feature engineering, materialization | ✅ Operational |

**Details**: See [Appendix D: ML Library](#appendix-d-ml-library)

---

### 5. PRISM Physics Engine

**Purpose**: Physics-based market simulation for realistic backtesting.

| Component | Purpose | Status |
|-----------|---------|--------|
| 40 Trading Agents | Market participants with diverse strategies | ✅ Running |
| Order Book Engine | Central limit order book with matching | ✅ Operational |
| Price Discovery | Market microstructure simulation | ✅ Operational |
| Dual Persistence | QuestDB (time-series) + ClickHouse (analytics) | ✅ Operational |

**Details**: See [Appendix E: PRISM Physics Engine](#appendix-e-prism-physics-engine)

---

## Detailed Appendices

Comprehensive technical documentation for each system component:

1. **[Appendix A: Infrastructure Components](./appendix_A_infrastructure.md)**
   - NATS JetStream configuration
   - Valkey caching strategies
   - QuestDB schema and ILP protocol
   - ClickHouse table design
   - SeaweedFS volume management
   - OpenSearch index mappings
   - PostgreSQL schema
   - OPA policy bundles

2. **[Appendix B: Backend Services](./appendix_B_backend_services.md)**
   - Service-by-service detailed documentation
   - API specifications (REST, gRPC)
   - Configuration files
   - Health check implementations
   - Docker build configurations

3. **[Appendix C: Frontend Application](./appendix_C_frontend.md)**
   - React component tree
   - Page routing
   - API client implementations
   - Nginx configuration
   - Build and deployment process

4. **[Appendix D: ML Library](./appendix_D_ml_library.md)**
   - Library service API
   - Default ML Pipeline architecture
   - Feast feature store configuration
   - Strategy registration process
   - Model training and deployment

5. **[Appendix E: PRISM Physics Engine](./appendix_E_prism.md)**
   - Agent architecture
   - Order book implementation
   - Market simulation algorithm
   - Persistence layer
   - Performance optimization

6. **[Appendix F: System Tree Maps](./appendix_F_tree_maps.md)**
   - Complete directory structure
   - Service dependency graph
   - Data flow diagrams
   - Network topology

7. **[Appendix G: Data Flow & Integration](./appendix_G_data_flow.md)**
   - Order flow lifecycle
   - Market data pipeline
   - Portfolio update flow
   - Risk calculation flow
   - Analytics pipeline

8. **[Appendix H: Network Topology](./appendix_H_network.md)**
   - Docker network configuration
   - Port allocation (CPGS v1.0)
   - Service discovery
   - DNS resolution

9. **[Appendix I: Deployment Guide](./appendix_I_deployment.md)**
   - Docker Compose orchestration
   - Environment variable configuration
   - Startup sequence
   - Health check validation
   - Troubleshooting

10. **[Appendix J: External Venues](./appendix_J_external_venues.md)**
    - IBKR TWS/Gateway setup
    - Market data configuration
    - Trading mode progression (SHADOW → CANARY → LIVE)
    - Symbol/contract configuration

---

## Quick Reference

### System Access

**Frontend**: http://localhost

**Key Services**:
- Order Service: http://localhost:8000/health
- Market Data: http://localhost:8050/health
- Portfolio: http://localhost:8100/health
- Risk: http://localhost:8150/health
- Library: http://localhost:8350/api/v1/health

**Infrastructure Consoles**:
- QuestDB: http://localhost:9000
- ClickHouse: http://localhost:8123
- NATS Monitoring: http://localhost:8222
- OpenSearch: http://localhost:9200

### System Control

**Start All Services**:
```bash
cd C:\claudedesktop_projects\trade2026
docker-compose -f infrastructure/docker/docker-compose.core.yml up -d
docker-compose -f infrastructure/docker/docker-compose.apps.yml up -d
docker-compose -f infrastructure/docker/docker-compose.frontend.yml up -d
docker-compose -f infrastructure/docker/docker-compose.library-db.yml up -d
python -m prism.main
```

**Check Health**:
```bash
docker ps                              # All containers
curl http://localhost/                 # Frontend
curl http://localhost:8000/health      # Order service
```

**View Logs**:
```bash
docker logs -f [container-name]        # Container logs
tail -f prism.log                      # PRISM logs
```

### System Stats

- **Total Services**: 26 (25 Docker + 1 Python)
- **Infrastructure Health**: 8/8 (100%)
- **Application Health**: 15/16 (94%)
- **System Uptime**: 13+ hours continuous
- **Completion**: 85% (Phases 1-5 complete)

---

## Document Navigation

**Main Documents**:
- **This Document**: Complete 5W overview
- **MASTER_PLAN.md**: 8-phase integration roadmap
- **README.md**: Project readme
- **SYSTEM_STATUS_2025-10-20.md**: Latest system audit

**Appendices**: Detailed technical documentation (see links above)

**Historical**: See `archive/` folder for old documentation

---

**Status**: ✅ OPERATIONAL (85% complete)
**Last Validated**: 2025-10-20
**Next Steps**: Phase 7 (Load Testing) + Phase 8 (Documentation Polish)

---
