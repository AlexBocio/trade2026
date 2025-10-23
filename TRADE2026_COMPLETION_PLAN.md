# Trade2026 Platform - Comprehensive Completion Plan
**Created**: 2025-10-23
**Status**: DRAFT - Awaiting Approval
**Current Completion**: 90% (Phases 1-6.6 complete)
**Target**: 100% - Full Quantitative Trading & Research Platform
**Estimated Time**: 94-146 hours (12-18 weeks at 8 hours/week)

---

## 🎯 EXECUTIVE SUMMARY

### Current State
- **Operational**: 27/34 containers running, core trading functionality working
- **Traefik**: Deployed, 1/8 backend services registered (warming up)
- **Completed Phases**: 1 (Foundation), 2 (Backend), 3 (Frontend), 4 (ML Library), 5 (PRISM), 6.5 (Backend Services), 6.6 (Traefik)
- **Gap Analysis**: 27 services from Trade2025 not yet migrated (59% of backend)

### Vision
Transform Trade2026 from a **trading platform** into a **complete quantitative research and trading platform** by integrating:
- MLOps infrastructure (experiment tracking, feature store, model serving)
- SRE stack (monitoring, alerting, observability)
- Research environment (JupyterLab, hyperparameter tuning)
- Enhanced analytics (execution quality, treasury, advanced P&L)
- Operational tooling (trading console, profiling)

### Strategic Approach
**Phased migration from Trade2025** with validation gates at each step, following CPGS v1.0 architecture and existing quality standards.

---

## 📋 PHASE-BY-PHASE BREAKDOWN

### **Phase 6.7: System Stabilization** - P0 (CRITICAL)
**Timeline**: Week 1 (3-5 hours)
**Priority**: CRITICAL - Must complete before proceeding
**Dependencies**: None (can start immediately)

#### Objectives
1. Stabilize all 34 containers to healthy state
2. Complete Traefik integration (8/8 backend services registered)
3. Verify end-to-end data flow

#### Tasks

**Task 6.7.1: Service Health Stabilization** (1-2 hours)
```bash
# Current: 13/27 healthy, 11/27 unhealthy (warming up)
# Target: 28/34 healthy (excluding stopped services)

Actions:
□ Monitor healthcheck progression (services up 20+ min)
□ Investigate services failing healthchecks after 40+ min
□ Fix healthcheck configurations if needed
□ Verify internal service ports vs healthcheck ports

Deliverable: All running services show (healthy) status
```

**Task 6.7.2: Restart Missing Services** (1-2 hours)
```bash
# 7 services stopped from previous crash

Services to restart:
□ feast-pipeline (port 8113)
□ execution-quality (port 8092)
□ hot_cache (port 8088)
□ questdb_writer (port 8090)
□ pnl (port 8100)
□ exeq (port 8095)
□ nginx (port 5173) - OR integrate with Traefik

Actions:
□ Check config files exist for each service
□ Copy configs from source if missing (like live-gateway fix)
□ Start services via docker-compose
□ Monitor startup and healthchecks
□ Verify NATS connectivity

Deliverable: 34/34 containers running
```

**Task 6.7.3: Traefik Service Registration** (0.5-1 hour)
```bash
# Current: 1/8 backend services registered
# Blocker: Services marked unhealthy, Traefik won't register

Once Task 6.7.1 complete:
□ Verify Traefik auto-discovers all healthy backend services
□ Check dashboard: http://localhost:8080/dashboard/
□ Confirm all 8 routes appear in Traefik API

Expected routes:
✓ /api/portfolio → portfolio-optimizer:5000
✓ /api/rl → rl-trading:5000
✓ /api/backtest → advanced-backtest:5000
✓ /api/factors → factor-models:5000
✓ /api/simulation → simulation-engine:5000
✓ /api/fracdiff → fractional-diff:5000
✓ /api/metalabel → meta-labeling:5000
✓ /api/screener → stock-screener:5000

Deliverable: 8/8 backend services accessible via Traefik
```

**Task 6.7.4: End-to-End Testing** (1-2 hours)
```bash
Test Scenarios:
□ Test all backend service health endpoints via Traefik
  - curl -k https://localhost/api/portfolio/health
  - curl -k https://localhost/api/screener/health
  - (repeat for all 8 services)

□ Test functional endpoints
  - Stock screener scan
  - Portfolio optimization
  - RL agent listing

□ Test OMS order flow
  - Submit test order
  - Verify NATS message
  - Check risk validation
  - Confirm persistence to QuestDB

□ Test frontend connectivity
  - Access http://localhost:5173 OR http://localhost
  - Verify API calls reach backend through Traefik
  - Check WebSocket connections

Deliverable: All critical paths validated
```

#### Exit Criteria
- ✅ 34/34 containers running
- ✅ 28+ containers healthy (82%+)
- ✅ Traefik registering 8/8 backend services
- ✅ All health endpoints responding via gateway
- ✅ End-to-end order flow working
- ✅ Frontend accessible and connected

#### Risk Mitigation
- **Risk**: Healthchecks continue failing
- **Mitigation**: Adjust healthcheck intervals/retries or disable for non-critical services
- **Risk**: Port conflicts prevent service startup
- **Mitigation**: Document port allocation, use dynamic ports where possible

---

### **Phase 7: Testing & Validation** - P0 (CRITICAL)
**Timeline**: Week 2-3 (10-15 hours)
**Priority**: CRITICAL - Cannot deploy to production without this
**Dependencies**: Phase 6.7 complete

#### Objectives
1. Validate system performance under load
2. Test all integration points
3. Establish performance baselines
4. Document known issues and limitations

#### Tasks

**Task 7.1: Load Testing** (4-6 hours)
```bash
Target: 1000 orders/sec sustained throughput

Setup:
□ Install k6 or Locust on host machine
□ Create test scenarios:
  - Order submission (POST /api/orders)
  - Market data queries (GET /api/market/quote)
  - Portfolio calculations (POST /api/portfolio/optimize)
  - Stock screening (GET /api/screener/scan)

Test Levels:
1. Baseline (10 req/s) - Validate correctness
2. Normal (100 req/s) - Typical production load
3. Peak (500 req/s) - High activity periods
4. Stress (1000+ req/s) - Maximum capacity
5. Spike (0→1000→0) - Sudden traffic surge
6. Soak (100 req/s for 4 hours) - Sustained load

Metrics to collect:
- Response times (p50, p95, p99)
- Error rates
- Throughput
- Resource utilization (CPU, memory)
- Database connections
- NATS message rates

Deliverable: Load test report with performance baselines
```

**Task 7.2: Integration Testing** (3-4 hours)
```bash
Test all service interactions:

□ Order Flow Integration
  1. UI → Traefik → OMS → Risk → NATS → Live Gateway
  2. Verify each hop
  3. Test success and failure paths

□ Market Data Flow
  1. IBKR → Market Data Gateway → NATS → Normalizer → QuestDB
  2. Verify real-time updates
  3. Test reconnection logic

□ Analytics Flow
  1. QuestDB → Backend Service → Calculation → Response
  2. Test with real historical data
  3. Verify caching behavior

□ ML Pipeline Flow
  1. Data → Feature Engineering → Model Training → Serving
  2. Test model versioning
  3. Verify feature store integration

Deliverable: Integration test suite with 90%+ pass rate
```

**Task 7.3: Frontend Integration Testing** (2-3 hours)
```bash
Test all 85 pages and 17 API integrations:

Critical Pages:
□ Trading page - Order submission
□ Portfolio page - Position display
□ Risk page - Real-time metrics
□ Analytics page - Charts and data
□ Screener pages (16 pages) - All filters

API Integration Verification:
□ All 17 API modules connecting
□ Real-time WebSocket updates
□ Error handling and retry logic
□ Loading states and timeouts

Browser Testing:
□ Chrome
□ Firefox
□ Edge

Deliverable: Frontend integration report
```

**Task 7.4: Performance Profiling** (1-2 hours)
```bash
Identify bottlenecks:

□ Critical Path Latency
  - Order submission: <50ms target
  - Market data update: <20ms target
  - Risk check: <30ms target

□ Database Performance
  - QuestDB write throughput
  - ClickHouse query performance
  - Valkey cache hit rate
  - PostgreSQL connection pooling

□ Service Resource Usage
  - Memory leaks
  - CPU spikes
  - Network saturation
  - Disk I/O bottlenecks

Tools:
- Docker stats
- Prometheus (once Phase 9 complete)
- Service-specific metrics endpoints

Deliverable: Performance profile with optimization recommendations
```

#### Exit Criteria
- ✅ System handles 500+ orders/sec sustained
- ✅ p95 latency <100ms for critical path
- ✅ No memory leaks during 4-hour soak test
- ✅ 99.9% uptime during testing
- ✅ All integration tests passing
- ✅ Frontend fully functional across browsers
- ✅ Performance baseline documented

---

### **Phase 8: Documentation Polish** - P1 (HIGH)
**Timeline**: Week 3-4 (5-8 hours)
**Priority**: HIGH - Critical for maintainability
**Dependencies**: Phase 7 complete

#### Objectives
1. Document system architecture comprehensively
2. Create operational runbooks
3. Write user guides
4. Generate API documentation

#### Tasks

**Task 8.1: API Documentation** (2-3 hours)
```bash
Generate OpenAPI/Swagger specs:

□ Backend Services (8 services)
  - Portfolio Optimizer endpoints
  - Stock Screener endpoints
  - RL Trading endpoints
  - Advanced Backtest endpoints
  - Factor Models endpoints
  - Simulation Engine endpoints
  - Fractional Diff endpoints
  - Meta-Labeling endpoints

□ Application Services (16 services)
  - OMS API
  - Risk API
  - P&L API
  - Market Data API
  - Data Ingestion API

Format:
- OpenAPI 3.0 YAML files
- Postman collections
- Example requests/responses
- Error codes and handling

Tools:
- Generate from code annotations
- Host on http://localhost/api/docs

Deliverable: Complete API documentation accessible via Swagger UI
```

**Task 8.2: Architecture Documentation** (1-2 hours)
```bash
Create comprehensive diagrams:

□ System Architecture Diagram
  - All 34+ services
  - Network topology (CPGS v1.0)
  - Data flow paths
  - Integration points

□ Data Flow Diagrams
  - Order flow (UI → Exchange)
  - Market data flow (Exchange → UI)
  - Analytics flow (Storage → Calculation → Display)
  - ML pipeline flow (Training → Serving)

□ Deployment Architecture
  - Docker Compose structure
  - Volume mounts
  - Network configuration
  - Port allocation

□ Database Schema
  - QuestDB tables
  - ClickHouse tables
  - PostgreSQL schema
  - Valkey key patterns

Tools:
- Mermaid diagrams
- Draw.io
- PlantUML

Deliverable: docs/architecture/ folder with all diagrams
```

**Task 8.3: User Guides** (1-2 hours)
```bash
Write step-by-step guides:

□ Getting Started Guide
  - System requirements
  - Installation steps
  - First-time setup
  - Running your first backtest

□ Trading Guide
  - How to submit orders
  - Risk management
  - Position monitoring
  - P&L tracking

□ Strategy Development Guide
  - Using JupyterLab (after Phase 10)
  - Data access
  - Backtesting workflow
  - Deployment process

□ Portfolio Management Guide
  - Optimization techniques
  - Risk analysis
  - Rebalancing
  - Reporting

Deliverable: docs/guides/ folder with user documentation
```

**Task 8.4: Operational Runbooks** (1-2 hours)
```bash
Document operational procedures:

□ Deployment Procedures
  - How to deploy updates
  - Rolling restart process
  - Rollback procedures
  - Configuration changes

□ Monitoring & Alerting
  - Key metrics to watch
  - Alert response procedures
  - Escalation paths

□ Troubleshooting Guide
  - Common issues and solutions
  - Log locations
  - Debug procedures
  - Health check failures

□ Disaster Recovery
  - Backup procedures
  - Restore procedures
  - Failover process
  - Data recovery

□ Maintenance Procedures
  - Database cleanup
  - Log rotation
  - Certificate renewal
  - Dependency updates

Deliverable: docs/operations/ folder with runbooks
```

#### Exit Criteria
- ✅ All APIs documented in OpenAPI format
- ✅ Architecture diagrams complete and accurate
- ✅ User guides cover all major workflows
- ✅ Operational runbooks address common scenarios
- ✅ Documentation accessible from main README

---

### **Phase 9: SRE & Observability Stack** - P0 (CRITICAL)
**Timeline**: Week 4-5 (12-20 hours)
**Priority**: CRITICAL - Cannot operate production blind
**Dependencies**: Phase 6.7 complete (Phase 7-8 can run parallel)

#### Objectives
1. Deploy complete monitoring stack
2. Establish alerting rules
3. Create operational dashboards
4. Enable proactive issue detection

#### Tasks

**Task 9.1: Prometheus Deployment** (4-6 hours)
```bash
Source: C:\trade2025\docker-compose.sre.yml

Setup:
□ Copy Prometheus configuration from Trade2025
□ Update network names (trade2025 → trade2026)
□ Create docker-compose.monitoring.yml

Configuration:
□ Scrape configs for all services:
  - Infrastructure (NATS, Valkey, QuestDB, ClickHouse, etc.)
  - Applications (OMS, Risk, Gateway, etc.)
  - Backend Services (Portfolio, Screener, etc.)
  - Traefik metrics

□ Define recording rules:
  - Request rate by service
  - Error rate by service
  - Latency percentiles
  - Resource utilization

□ Storage configuration:
  - Retention: 30 days
  - Volume mount: data/prometheus/

Service Definition:
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: trade2026-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ../prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ../../data/prometheus:/prometheus
    networks:
      - backend
      - lowlatency
      - frontend
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'

Deliverable: Prometheus collecting metrics from all services
```

**Task 9.2: Grafana Deployment** (4-6 hours)
```bash
Source: C:\trade2025\docker-compose.sre.yml

Setup:
□ Copy Grafana configuration from Trade2025
□ Create docker-compose entry
□ Configure Prometheus data source

Dashboards to create:
□ System Overview
  - Container health
  - Resource utilization
  - Service status
  - Request rates

□ Trading Performance
  - Order rate
  - Fill rate
  - Latency distribution
  - Error rates
  - P&L tracking

□ Infrastructure Health
  - NATS metrics
  - Database performance
  - Cache hit rates
  - Network throughput

□ Backend Services
  - Request volume by endpoint
  - Response times
  - Error rates
  - Queue depths

□ Market Data
  - Tick rate
  - Update latency
  - Gap detection
  - Symbol coverage

Service Definition:
services:
  grafana:
    image: grafana/grafana:latest
    container_name: trade2026-grafana
    ports:
      - "3000:3000"
    volumes:
      - ../grafana/provisioning:/etc/grafana/provisioning:ro
      - ../../data/grafana:/var/lib/grafana
    networks:
      - backend
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=
    depends_on:
      - prometheus

Deliverable: Grafana with 5+ operational dashboards
```

**Task 9.3: Alertmanager Deployment** (2-3 hours)
```bash
Source: C:\trade2025\docker-compose.sre.yml

Setup:
□ Copy Alertmanager config from Trade2025
□ Configure notification channels (email, Slack, PagerDuty)
□ Define alert routing rules

Alert Rules:
□ Critical Alerts (page immediately)
  - Service down
  - High error rate (>5%)
  - Database unreachable
  - Disk space critical (<10%)
  - Memory critical (>90%)

□ Warning Alerts (notify, don't page)
  - High latency (p95 >200ms)
  - Elevated error rate (>1%)
  - Database slow queries
  - Cache miss rate high
  - Disk space low (<20%)

□ Info Alerts (log only)
  - Service restart
  - Configuration change
  - Deployment complete

Service Definition:
services:
  alertmanager:
    image: prom/alertmanager:latest
    container_name: trade2026-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ../alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
    networks:
      - backend
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'

Deliverable: Alerting system with defined rules and routing
```

**Task 9.4: Status Dashboard** (2-3 hours)
```bash
Source: C:\trade2025\docker-compose.sre.yml

Deploy status page:
□ Status API (backend)
□ Status Web (frontend)
□ Incident tracking

Features:
- Public status page (optional)
- Component status indicators
- Incident history
- Scheduled maintenance notices
- Uptime metrics

Deliverable: Status dashboard accessible
```

**Task 9.5: Load Testing Integration** (1-2 hours)
```bash
Source: C:\trade2025\docker-compose.sre.yml

Deploy k6:
□ Container for running load tests
□ Test scenario library
□ CI/CD integration

Service Definition:
services:
  k6:
    image: grafana/k6:latest
    container_name: trade2026-k6
    volumes:
      - ../k6/scripts:/scripts
    networks:
      - frontend
    command: run /scripts/load-test.js

Deliverable: Containerized load testing capability
```

#### Exit Criteria
- ✅ Prometheus collecting metrics from all services
- ✅ Grafana displaying 5+ dashboards
- ✅ Alertmanager configured with routing rules
- ✅ Critical alerts tested and firing correctly
- ✅ Status dashboard operational
- ✅ k6 load testing integrated
- ✅ 7-day retention verified

---

### **Phase 10: Research & Analytics Environment** - P1 (HIGH)
**Timeline**: Week 5-6 (8-12 hours)
**Priority**: HIGH - Needed for strategy development
**Dependencies**: Phase 9 complete (for monitoring)

#### Objectives
1. Deploy interactive research environment
2. Enable strategy development workflow
3. Integrate hyperparameter tuning
4. Automate report generation

#### Tasks

**Task 10.1: JupyterLab Deployment** (4-6 hours)
```bash
Source: C:\trade2025\infra\research\docker-compose.research.yml

Setup:
□ Copy JupyterLab configuration from Trade2025
□ Configure data source connections
□ Install required Python packages

Configuration:
□ Connect to all databases:
  - QuestDB (market data)
  - ClickHouse (analytics)
  - PostgreSQL (ML models)
  - Valkey (cache)

□ Connect to services:
  - NATS (event streaming)
  - Backend services APIs
  - Traefik gateway

□ Install Python packages:
  - pandas, numpy, scipy
  - scikit-learn, xgboost, lightgbm
  - matplotlib, seaborn, plotly
  - backtrader, zipline, pyfolio
  - tensorflow, pytorch (optional)
  - vectorbt, ta-lib
  - ib_insync (IBKR)

Service Definition:
services:
  jupyterlab:
    image: jupyter/scipy-notebook:latest
    container_name: trade2026-jupyterlab
    ports:
      - "8888:8888"
    volumes:
      - ../../notebooks:/home/jovyan/work
      - ../jupyterlab/config:/home/jovyan/.jupyter:ro
    networks:
      - frontend
      - backend
      - lowlatency
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - GRANT_SUDO=yes
    command: start-notebook.sh --NotebookApp.token='' --NotebookApp.password=''

Security Note: Disable authentication only in dev environment

Deliverable: JupyterLab accessible at http://localhost:8888
```

**Task 10.2: Example Notebooks** (2-3 hours)
```bash
Create template notebooks:

□ Data Access
  - Connecting to QuestDB
  - Querying ClickHouse
  - Using backend service APIs
  - Real-time data streaming via NATS

□ Backtesting
  - Loading historical data
  - Implementing strategy logic
  - Running backtest
  - Analyzing results

□ Portfolio Optimization
  - Fetching portfolio data
  - Running optimization algorithms
  - Visualizing efficient frontier
  - Risk analysis

□ Feature Engineering
  - Creating technical indicators
  - Fundamental data integration
  - Alternative data sources
  - Feature store integration

□ Model Training
  - Data preparation
  - Model training
  - Hyperparameter tuning
  - Model evaluation
  - Deployment to serving

Deliverable: notebooks/ folder with 5+ examples
```

**Task 10.3: Optuna Dashboard** (2-3 hours)
```bash
Source: C:\trade2025\infra\research\docker-compose.research.yml

Deploy hyperparameter tuning:
□ Optuna dashboard
□ PostgreSQL backend for study storage
□ Example optimization scripts

Service Definition:
services:
  optuna-dashboard:
    image: ghcr.io/optuna/optuna-dashboard:latest
    container_name: trade2026-optuna-dashboard
    ports:
      - "8080:8080"
    networks:
      - backend
    environment:
      - OPTUNA_DB_URL=postgresql://postgres:password@postgres:5432/optuna
    depends_on:
      - postgres-optuna

  postgres-optuna:
    image: postgres:15-alpine
    container_name: trade2026-postgres-optuna
    volumes:
      - ../../data/postgres-optuna:/var/lib/postgresql/data
    networks:
      - backend
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=optuna

Use Cases:
- Strategy parameter optimization
- Model hyperparameter tuning
- Portfolio weight optimization
- Risk parameter calibration

Deliverable: Optuna dashboard with example studies
```

**Task 10.4: Papermill Integration** (1-2 hours)
```bash
Source: C:\trade2025\infra\research\docker-compose.research.yml

Automate notebook execution:

Setup:
□ Install papermill in JupyterLab container
□ Create scheduled execution scripts
□ Configure output destinations

Use Cases:
- Daily P&L reports
- Weekly performance analysis
- Monthly risk reports
- Automated model retraining

Example automation:
# Daily report at 4pm
papermill daily_pnl_report.ipynb \
  output/pnl_$(date +%Y%m%d).ipynb \
  -p date "$(date +%Y-%m-%d)"

Deliverable: Automated report generation working
```

#### Exit Criteria
- ✅ JupyterLab accessible and functional
- ✅ All data sources connectable from notebooks
- ✅ 5+ example notebooks working
- ✅ Optuna dashboard operational
- ✅ Papermill automation configured
- ✅ Documentation for research workflow

---

### **Phase 11: MLOps Infrastructure** - P0 (CRITICAL)
**Timeline**: Week 6-9 (24-33 hours)
**Priority**: CRITICAL - Cannot deploy ML models without this
**Dependencies**: Phase 10 complete

#### Objectives
1. Enable ML experiment tracking
2. Deploy feature store for ML features
3. Setup model serving infrastructure
4. Establish model governance

#### Tasks

**Task 11.1: MLflow Deployment** (8 hours)
```bash
Source: C:\trade2025\infra\modelops\docker-compose.modelops.yml

Deploy experiment tracking platform:

Components:
□ MLflow Tracking Server
□ PostgreSQL backend store
□ S3-compatible artifact store (SeaweedFS)
□ Model registry

Service Definition:
services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    container_name: trade2026-mlflow
    ports:
      - "5000:5000"
    volumes:
      - ../mlflow/config:/mlflow/config:ro
    networks:
      - backend
    environment:
      - MLFLOW_BACKEND_STORE_URI=postgresql://postgres:password@postgres-mlflow:5432/mlflow
      - MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://mlflow-artifacts/
      - AWS_ACCESS_KEY_ID=admin
      - AWS_SECRET_ACCESS_KEY=admin
      - MLFLOW_S3_ENDPOINT_URL=http://seaweedfs:8333
    command:
      - mlflow
      - server
      - --host=0.0.0.0
      - --port=5000
      - --backend-store-uri=postgresql://postgres:password@postgres-mlflow:5432/mlflow
      - --default-artifact-root=s3://mlflow-artifacts/
    depends_on:
      - postgres-mlflow
      - seaweedfs

  postgres-mlflow:
    image: postgres:15-alpine
    container_name: trade2026-postgres-mlflow
    volumes:
      - ../../data/postgres-mlflow:/var/lib/postgresql/data
    networks:
      - backend
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mlflow

Configuration:
□ Create S3 bucket in SeaweedFS for artifacts
□ Configure experiment structure
□ Setup model registry
□ Define model stages (Staging, Production)

Integration:
□ Update JupyterLab to use MLflow tracking
□ Configure auto-logging for frameworks
□ Setup model comparison UI

Use Cases:
- Track all model training runs
- Compare model performance
- Version model artifacts
- Manage model lifecycle (dev → staging → production)
- A/B test models

Deliverable: MLflow UI accessible at http://localhost:5000
```

**Task 11.2: Feast Feature Store - Offline** (5-7 hours)
```bash
Source: C:\trade2025\docker-compose.feast.yml

Deploy offline feature store for training:

Components:
□ Feast SDK
□ Offline store (Parquet files in SeaweedFS)
□ Feature registry (PostgreSQL)

Service Definition:
services:
  feast-offline:
    build:
      context: ../../backend/feast
      dockerfile: Dockerfile
    container_name: trade2026-feast-offline
    volumes:
      - ../feast/feature_repo:/feature_repo
      - ../../data/feast/offline:/data/offline
    networks:
      - backend
    environment:
      - FEAST_REGISTRY=s3://feast-registry/registry.db
      - OFFLINE_STORE_TYPE=file
      - OFFLINE_STORE_PATH=/data/offline

Feature Definitions:
□ Price features (OHLCV, returns)
□ Technical indicators (SMA, RSI, Bollinger)
□ Fundamental features (P/E, market cap)
□ Alternative data (sentiment, volume)
□ Derived features (spreads, ratios)

Feature Engineering Pipeline:
1. Extract raw data from QuestDB/ClickHouse
2. Transform to features
3. Store in Parquet format
4. Register in feature store
5. Enable point-in-time correct retrieval

Integration:
□ Materialize features from data sources
□ Query features for model training
□ Ensure no data leakage (point-in-time correctness)

Deliverable: Offline feature store with 20+ features defined
```

**Task 11.3: Feast Feature Store - Online** (5-8 hours)
```bash
Source: C:\trade2025\docker-compose.feast.yml

Deploy online feature store for serving:

Components:
□ Feast server
□ Online store (Redis/Valkey)
□ Feature serving API

Service Definition:
services:
  feast-online:
    build:
      context: ../../backend/feast
      dockerfile: Dockerfile
    container_name: trade2026-feast-online
    ports:
      - "6566:6566"
    volumes:
      - ../feast/feature_repo:/feature_repo
    networks:
      - backend
      - lowlatency
    environment:
      - FEAST_REGISTRY=s3://feast-registry/registry.db
      - ONLINE_STORE_TYPE=redis
      - ONLINE_STORE_HOST=valkey
      - ONLINE_STORE_PORT=6379
    command: serve -h 0.0.0.0

Materialization:
□ Setup scheduled materialization (offline → online)
□ Configure materialization frequency
□ Monitor data freshness

Online Serving:
□ Low-latency feature retrieval (<10ms)
□ Support for real-time inference
□ Feature versioning

Integration:
□ Model serving accesses online features
□ Trading strategies query latest features
□ Real-time feature updates

Use Cases:
- Serve features for real-time model inference
- Provide features to trading strategies
- Enable fast feature lookup during trading

Deliverable: Online feature store serving features <10ms
```

**Task 11.4: Model Serving (CPU)** (6-8 hours)
```bash
Source: C:\trade2025\docker-compose.apps.yml

Deploy model inference service:

Components:
□ Model serving API
□ Model loader (from MLflow)
□ Feature fetcher (from Feast online)
□ Prediction cache (Valkey)

Service Definition:
services:
  model-serving:
    build:
      context: ../../backend/serving
      dockerfile: Dockerfile
    container_name: trade2026-model-serving
    ports:
      - "8400:8400"
    volumes:
      - ../serving/config:/app/config:ro
    networks:
      - backend
      - lowlatency
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - FEAST_SERVING_URL=feast-online:6566
      - CACHE_BACKEND=redis://valkey:6379/1
    depends_on:
      - mlflow
      - feast-online
      - valkey

Capabilities:
□ Load models from MLflow registry
□ Fetch features from Feast online store
□ Run inference
□ Cache predictions
□ A/B testing support
□ Canary deployments
□ Model versioning

API Endpoints:
- POST /predict - Single prediction
- POST /predict/batch - Batch prediction
- GET /models - List loaded models
- POST /models/load - Load model from MLflow
- POST /models/unload - Unload model
- GET /health - Health check

Performance Targets:
- Inference latency: <50ms p95
- Throughput: 1000+ req/sec
- Model load time: <30 seconds

Integration:
□ Trading strategies call serving API
□ Backtest engine uses serving API
□ Portfolio optimizer integrates predictions

Deliverable: Model serving API operational with <50ms latency
```

**Task 11.5: Marquez (Data Lineage)** (4-6 hours)
```bash
Source: C:\trade2025\infra\modelops\docker-compose.modelops.yml

Deploy data lineage tracking:

Components:
□ Marquez API
□ Marquez Web UI
□ PostgreSQL backend

Service Definition:
services:
  marquez:
    image: marquezproject/marquez:latest
    container_name: trade2026-marquez
    ports:
      - "5001:5000"
      - "5002:5001"
    networks:
      - backend
    environment:
      - MARQUEZ_DB_HOST=postgres-marquez
      - MARQUEZ_DB_PORT=5432
      - MARQUEZ_DB_USER=postgres
      - MARQUEZ_DB_PASSWORD=password
      - MARQUEZ_DB_NAME=marquez
    depends_on:
      - postgres-marquez

  postgres-marquez:
    image: postgres:15-alpine
    container_name: trade2026-postgres-marquez
    volumes:
      - ../../data/postgres-marquez:/var/lib/postgresql/data
    networks:
      - backend
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=marquez

Integration:
□ Instrument data pipelines with OpenLineage
□ Track data transformations
□ Visualize data lineage

Use Cases:
- Understand data provenance
- Debug data quality issues
- Compliance and auditing
- Impact analysis (what breaks if I change X?)

Deliverable: Marquez UI showing data lineage
```

**Task 11.6: Model Governance API** (4-6 hours)
```bash
Source: C:\trade2025\infra\modelops\docker-compose.modelops.yml

Deploy model approval workflow:

Components:
□ Governance API
□ Approval workflow engine
□ Audit log

Service Definition:
services:
  model-governance:
    build:
      context: ../../backend/governance
      dockerfile: Dockerfile
    container_name: trade2026-model-governance
    ports:
      - "8401:8401"
    volumes:
      - ../governance/config:/app/config:ro
    networks:
      - backend
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - DATABASE_URL=postgresql://postgres:password@postgres-governance:5432/governance
    depends_on:
      - mlflow
      - postgres-governance

  postgres-governance:
    image: postgres:15-alpine
    container_name: trade2026-postgres-governance
    volumes:
      - ../../data/postgres-governance:/var/lib/postgresql/data
    networks:
      - backend
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=governance

Governance Workflow:
1. Model trained and logged to MLflow
2. Model performance exceeds threshold
3. Governance API creates approval request
4. Human reviews model:
   - Performance metrics
   - Validation results
   - Risk assessment
   - Business impact
5. Approved models move to Production stage
6. Rejected models stay in Staging

Features:
□ Approval workflows
□ Model validation rules
□ Performance thresholds
□ Risk assessment
□ Audit trail
□ Compliance reporting

Deliverable: Model governance workflow operational
```

#### Exit Criteria
- ✅ MLflow tracking 100+ experiments
- ✅ Feast offline store with 20+ features
- ✅ Feast online store serving <10ms
- ✅ Model serving API handling 1000+ req/sec
- ✅ Marquez showing data lineage
- ✅ Governance workflow approving models
- ✅ End-to-end ML pipeline working (train → approve → deploy → serve)

---

### **Phase 12: Enhanced Financial Services** - P2 (MEDIUM)
**Timeline**: Week 9-10 (6-10 hours)
**Priority**: MEDIUM - Nice to have, not blocking
**Dependencies**: Phase 11 complete

#### Objectives
1. Enhanced P&L reporting
2. Execution quality analytics
3. Treasury and cash management
4. Advanced risk metrics

#### Tasks

**Task 12.1: Enhanced P&L Service** (3-4 hours)
```bash
Source: C:\trade2025\infra\pnl\docker-compose.pnl.yml

Deploy enhanced P&L tracking:

Note: Current PTRC service provides basic P&L. This adds:
- Multi-currency support
- Tax reporting
- Realized vs unrealized P&L
- Attribution analysis
- Custom reporting

Service Definition:
services:
  pnl-service:
    build:
      context: ../../backend/pnl_service
      dockerfile: Dockerfile
    container_name: trade2026-pnl-service
    ports:
      - "8410:8410"
    networks:
      - backend
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres-library:5432/trading
      - QUESTDB_URL=http://questdb:9000
      - CLICKHOUSE_URL=http://clickhouse:8123
    depends_on:
      - postgres-library
      - questdb
      - clickhouse

Features:
□ Multi-currency P&L
□ Tax lot tracking
□ Realized/unrealized P&L
□ Performance attribution
□ Custom date ranges
□ Export to CSV/Excel

Deliverable: Enhanced P&L API operational
```

**Task 12.2: Execution Quality Service (ExEq)** (2-3 hours)
```bash
Source: C:\trade2025\infra\exeq\docker-compose.exeq.yml

Deploy execution analytics:

Note: Current execution-quality service exists. This enhances it.

Additional Features:
□ Venue analysis (which broker/exchange performed best)
□ Slippage tracking
□ Fill quality metrics
□ Best execution compliance
□ Benchmarking (VWAP, TWAP)

Service Definition:
services:
  exeq-enhanced:
    build:
      context: ../../backend/exeq_enhanced
      dockerfile: Dockerfile
    container_name: trade2026-exeq-enhanced
    ports:
      - "8411:8411"
    networks:
      - backend
    environment:
      - QUESTDB_URL=http://questdb:9000
      - CLICKHOUSE_URL=http://clickhouse:8123

Reports:
- Daily execution summary
- Slippage analysis
- Venue comparison
- Best execution compliance

Deliverable: ExEq reports accessible via API
```

**Task 12.3: Treasury Service** (2-3 hours)
```bash
Source: C:\trade2025\infra\treasury\docker-compose.yaml

Deploy cash management:

Service Definition:
services:
  treasury:
    build:
      context: ../../backend/treasury
      dockerfile: Dockerfile
    container_name: trade2026-treasury
    ports:
      - "8412:8412"
    networks:
      - backend
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres-library:5432/trading

Features:
□ Cash position tracking
□ Margin monitoring
□ Collateral management
□ Cash forecasting
□ Sweep optimization

Use Cases:
- Monitor available cash
- Track margin requirements
- Optimize idle cash (sweep to money market)
- Alert on margin calls

Deliverable: Treasury dashboard operational
```

#### Exit Criteria
- ✅ Enhanced P&L service providing multi-currency reports
- ✅ ExEq service tracking execution quality
- ✅ Treasury service monitoring cash positions
- ✅ All services integrated with existing platform

---

### **Phase 13: Trading Console** - P2 (MEDIUM)
**Timeline**: Week 10-11 (8-12 hours)
**Priority**: MEDIUM - Useful for operators
**Dependencies**: Phase 9 complete (SRE stack)

#### Objectives
1. Operator control panel
2. System monitoring dashboard
3. Manual intervention tools
4. Alert management

#### Tasks

**Task 13.1: Console BFF (Backend for Frontend)** (4-6 hours)
```bash
Source: C:\trade2025\infra\console\docker-compose.console.yml

Deploy operator API:

Service Definition:
services:
  console-bff:
    build:
      context: ../../backend/console_bff
      dockerfile: Dockerfile
    container_name: trade2026-console-bff
    ports:
      - "8420:8420"
    networks:
      - frontend
      - backend
      - lowlatency
    environment:
      - PROMETHEUS_URL=http://prometheus:9090
      - GRAFANA_URL=http://grafana:3000
      - ALERTMANAGER_URL=http://alertmanager:9093
      - MLFLOW_URL=http://mlflow:5000

API Endpoints:
□ GET /system/health - Aggregate system health
□ GET /services/status - All service statuses
□ GET /alerts - Active alerts
□ POST /alerts/acknowledge - Acknowledge alert
□ POST /services/{id}/restart - Restart service
□ GET /metrics/live - Real-time metrics
□ POST /trading/halt - Emergency halt trading
□ POST /trading/resume - Resume trading

Deliverable: Console BFF API operational
```

**Task 13.2: Console Web UI** (4-6 hours)
```bash
Source: C:\trade2025\infra\console\docker-compose.console.yml

Deploy operator dashboard:

Service Definition:
services:
  console-web:
    build:
      context: ../../frontend/console
      dockerfile: Dockerfile
    container_name: trade2026-console-web
    ports:
      - "8421:80"
    networks:
      - frontend
    depends_on:
      - console-bff

Dashboard Sections:
□ System Overview
  - Service health grid
  - Resource utilization
  - Active alerts
  - Recent events

□ Trading Control
  - Emergency halt button
  - Trading mode (live, paper, replay)
  - Risk limit overrides
  - Manual order entry

□ Alert Management
  - Active alerts list
  - Alert history
  - Acknowledge/silence controls
  - Escalation status

□ Service Management
  - Start/stop/restart services
  - View logs
  - Configuration changes
  - Deployment controls

□ Monitoring
  - Live metrics charts
  - Performance graphs
  - Database status
  - Queue depths

Technology:
- React + TypeScript
- Real-time WebSocket updates
- Responsive design
- Dark mode

Deliverable: Console UI accessible at http://localhost:8421
```

#### Exit Criteria
- ✅ Console BFF API responding
- ✅ Console UI accessible
- ✅ Real-time updates working
- ✅ Emergency controls tested
- ✅ Alert management functional

---

### **Phase 14: Advanced Features (OPTIONAL)** - P3 (LOW)
**Timeline**: Week 11-13 (15-25 hours)
**Priority**: LOW - Nice to have
**Dependencies**: Phases 11-13 complete

#### Optional Tasks

**Task 14.1: Backtest Orchestrator** (8-12 hours)
```bash
Source: C:\trade2025\docker-compose.apps.yml

Multi-strategy backtest management:

Features:
□ Parallel backtest execution
□ Parameter sweep
□ Walk-forward optimization at scale
□ Result aggregation
□ Portfolio construction from multiple strategies

Use Cases:
- Run 100+ backtest variants in parallel
- Optimize strategy parameters across date ranges
- Compare multiple strategies
- Build meta-strategies

Deliverable: Orchestrator running 10+ backtests in parallel
```

**Task 14.2: Ray Cluster for Distributed Computing** (4-8 hours)
```bash
Source: C:\trade2025\docker-compose.gpu.yml

Distributed ML training and backtesting:

Components:
□ Ray head node
□ Ray worker nodes (CPU)
□ Ray dashboard

Use Cases:
- Distributed hyperparameter search
- Parallel model training
- Distributed backtesting
- Large-scale simulations

Deliverable: Ray cluster processing distributed workloads
```

**Task 14.3: GPU Model Serving** (3-5 hours)
```bash
Source: C:\trade2025\docker-compose.gpu.yml

Accelerated deep learning inference:

Note: Requires NVIDIA GPU

Components:
□ NVIDIA Docker runtime
□ TensorRT optimization
□ GPU-accelerated serving

Use Cases:
- Deep learning models (LSTM, Transformers)
- Real-time inference for complex models
- Image/text processing

Deliverable: GPU serving handling 10x throughput vs CPU
```

**Task 14.4: Parca Continuous Profiler** (2-4 hours)
```bash
Source: C:\trade2025\perf\prof\parca\docker-compose.parca.yml

Continuous performance profiling:

Components:
□ Parca server
□ Parca agent (on each service)
□ Profiling UI

Features:
- CPU profiling
- Memory profiling
- Flame graphs
- Historical comparison

Deliverable: Parca showing service profiles
```

**Task 14.5: Vector Store for Alternative Data** (4-8 hours)
```bash
Source: C:\trade2025\docker-compose.vector.yml

Semantic search over alternative data:

Components:
□ Qdrant vector database
□ Embedder service (sentence transformers)
□ Vector ingestion pipeline

Use Cases:
- News sentiment analysis
- Social media monitoring
- Research report search
- Similar company finding

Deliverable: Vector search operational
```

#### Exit Criteria
- ✅ Selected advanced features operational
- ✅ Documentation updated
- ✅ Integration tested

---

## 📊 TIME AND RESOURCE ESTIMATES

### Summary Table

| Phase | Name | Priority | Time (hrs) | Week |
|-------|------|----------|------------|------|
| 6.7 | System Stabilization | P0 | 3-5 | 1 |
| 7 | Testing & Validation | P0 | 10-15 | 2-3 |
| 8 | Documentation | P1 | 5-8 | 3-4 |
| 9 | SRE & Observability | P0 | 12-20 | 4-5 |
| 10 | Research Environment | P1 | 8-12 | 5-6 |
| 11 | MLOps Infrastructure | P0 | 24-33 | 6-9 |
| 12 | Enhanced Finance | P2 | 6-10 | 9-10 |
| 13 | Trading Console | P2 | 8-12 | 10-11 |
| 14 | Advanced Features | P3 | 15-25 | 11-13 |
| **TOTAL** | | | **94-146** | **13-18** |

### Effort Breakdown by Priority

**P0 (CRITICAL)**: 49-73 hours
- Must complete for production readiness
- Phases: 6.7, 7, 9, 11

**P1 (HIGH)**: 13-20 hours
- Important for full functionality
- Phases: 8, 10

**P2 (MEDIUM)**: 14-22 hours
- Nice to have enhancements
- Phases: 12, 13

**P3 (LOW)**: 15-25 hours
- Optional advanced features
- Phase: 14

### Resource Requirements

**Development Environment**:
- Windows 11 machine (current)
- Docker Desktop
- 16GB+ RAM (32GB recommended)
- 100GB+ free disk space
- Internet connection (for pulling images)

**External Services**:
- GitHub (for version control)
- IBKR account (for market data)
- FRED API key (for economic data)

**Skills Required**:
- Docker & Docker Compose
- Python (backend services)
- React/TypeScript (frontend)
- SQL (databases)
- System administration
- ML/AI (for Phases 10-11)

---

## 🎯 EXECUTION STRATEGY

### Recommended Approach

**Phase 1: Stabilize & Test** (Weeks 1-3)
```
Phase 6.7 → Phase 7 → Phase 8
= Quick wins, build confidence
= Result: Production-ready trading platform
```

**Phase 2: Observability** (Weeks 4-5)
```
Phase 9 (SRE Stack)
= Cannot operate production blind
= Result: Monitoring, alerting, dashboards
```

**Phase 3: Research & ML** (Weeks 5-9)
```
Phase 10 → Phase 11
= Enable strategy development & deployment
= Result: Full quant research platform
```

**Phase 4: Enhancements** (Weeks 9-11)
```
Phase 12 → Phase 13
= Better analytics and operations
= Result: Enterprise-grade platform
```

**Phase 5: Advanced (Optional)** (Weeks 11-13)
```
Phase 14
= Cutting-edge capabilities
= Result: Industry-leading platform
```

### Parallel Execution Opportunities

**Can Run in Parallel**:
- Phase 7 (Testing) + Phase 8 (Docs) - Different skill sets
- Phase 10 (Research) + Phase 12 (Finance) - Independent services
- Phase 13 (Console) + Phase 14 (Advanced) - Optional nice-to-haves

**Must Run Sequential**:
- Phase 6.7 → Everything else (foundation)
- Phase 9 → Phase 13 (console needs metrics)
- Phase 10 → Phase 11 (MLflow needs JupyterLab)

### Risk Management

**High-Risk Areas**:
1. **Feast Feature Store** - Complex, many dependencies
2. **Model Serving** - Performance critical
3. **Distributed Systems** - Ray, Backtest Orchestrator

**Mitigation**:
- Allocate extra buffer time
- Test thoroughly before proceeding
- Have rollback plan
- Document issues and solutions

**Dependencies on External Services**:
- Trade2025 source code (must be accessible)
- Docker Hub (for image pulling)
- PyPI (for Python packages)
- npm (for JavaScript packages)

---

## 📋 QUALITY GATES

### Every Phase Must Pass

**Before Proceeding to Next Phase**:
1. ✅ All services deployed and healthy
2. ✅ Integration tests passing
3. ✅ Documentation updated
4. ✅ No critical bugs
5. ✅ Performance meets targets
6. ✅ Changes committed to GitHub

### Validation Checklist Per Phase

```bash
# Service Health
□ docker ps shows all containers healthy
□ No restart loops
□ Logs show no errors

# Functional Testing
□ Health endpoints responding
□ APIs returning expected data
□ Integration with existing services working

# Performance Testing
□ Response times within targets
□ No memory leaks
□ CPU usage acceptable
□ Database queries optimized

# Documentation
□ README updated
□ API docs generated
□ Architecture diagrams updated
□ Runbooks created

# Code Quality
□ All files committed
□ Commit messages descriptive
□ No sensitive data in repo
□ GitHub Actions passing (if configured)
```

---

## 🔄 ROLLBACK PROCEDURES

### If Phase Fails

**Immediate Actions**:
1. Stop new deployments
2. Document failure symptoms
3. Check logs for root cause
4. Assess impact on running services

**Rollback Steps**:
```bash
# Stop failed services
docker-compose -f docker-compose.{phase}.yml down

# Remove failed volumes (if needed)
docker volume rm {volume-name}

# Restore previous version
git checkout {previous-commit}

# Restart previous stable state
docker-compose up -d

# Verify system health
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Post-Mortem**:
- Document what went wrong
- Identify root cause
- Update plan if needed
- Add safeguards for next attempt

---

## 📚 MIGRATION SOURCES

### Files to Copy from Trade2025

```
C:\trade2025\
├── docker-compose.sre.yml → Phase 9
├── docker-compose.feast.yml → Phase 11
├── docker-compose.vector.yml → Phase 14
├── docker-compose.gpu.yml → Phase 14
├── infra/
│   ├── modelops/docker-compose.modelops.yml → Phase 11
│   ├── research/docker-compose.research.yml → Phase 10
│   ├── console/docker-compose.console.yml → Phase 13
│   ├── pnl/ → Phase 12
│   ├── exeq/ → Phase 12
│   ├── treasury/ → Phase 12
│   └── derivs/ → Phase 14 (optional)
├── traefik/ → Already done in Phase 6.6
├── prometheus/ → Phase 9
├── grafana/ → Phase 9
├── alertmanager/ → Phase 9
└── perf/prof/parca/ → Phase 14
```

### Configuration Files to Adapt

**For Each Service**:
1. Update network names: `trade2025-*` → `trade2026-*`
2. Update volume paths to Trade2026 structure
3. Update service dependencies
4. Update environment variables
5. Add Traefik labels if needed
6. Test before deploying

---

## 🎉 SUCCESS CRITERIA

### Platform Complete When:

**Functional Requirements**:
- ✅ All 50+ services deployed and healthy
- ✅ Trading flow working (UI → OMS → Exchange → Fill → UI)
- ✅ Market data streaming (IBKR → UI)
- ✅ Backtesting functional
- ✅ Portfolio optimization working
- ✅ ML model training & deployment working
- ✅ Research environment fully functional
- ✅ Monitoring and alerting operational

**Performance Requirements**:
- ✅ 1000+ orders/sec sustained
- ✅ <50ms p95 latency on critical path
- ✅ 99.9% uptime over 24 hours
- ✅ No memory leaks during soak test
- ✅ Model inference <50ms p95

**Operational Requirements**:
- ✅ All services monitored
- ✅ Critical alerts configured
- ✅ Dashboards showing key metrics
- ✅ Runbooks for common issues
- ✅ Backup/restore procedures tested

**Documentation Requirements**:
- ✅ Architecture fully documented
- ✅ All APIs documented
- ✅ User guides complete
- ✅ Operational runbooks written
- ✅ Troubleshooting guide available

**Code Quality**:
- ✅ All code committed to GitHub
- ✅ No secrets in repository
- ✅ README comprehensive
- ✅ CI/CD configured (optional)

---

## 📝 NEXT STEPS

### Immediate Actions (After Plan Approval)

1. **Review Plan**:
   - User reviews this plan
   - Discuss any concerns
   - Agree on priorities
   - Adjust timeline if needed

2. **Update Master Plan**:
   - Add Phases 6.7-14 to 01_MASTER_PLAN.md
   - Update completion percentages
   - Update timeline estimates
   - Update downstream documents

3. **Commit to GitHub**:
   - Commit this plan
   - Commit updated master plan
   - Commit updated tracker
   - Push to remote

4. **Start Phase 6.7**:
   - Begin system stabilization
   - Monitor service health
   - Complete Traefik integration
   - Run initial tests

---

## 🤔 QUESTIONS FOR USER

Before finalizing this plan:

1. **Timeline**: Is 12-18 weeks (at 8 hrs/week) acceptable?
2. **Priorities**: Agree with P0/P1/P2/P3 prioritization?
3. **Optional Features**: Which Phase 14 features interest you?
4. **Resources**: Any resource constraints I should know about?
5. **External Dependencies**: Any issues accessing Trade2025 source?
6. **Testing**: Comfortable with load testing approach?
7. **Documentation**: Documentation depth appropriate?

---

**Status**: DRAFT - Awaiting User Approval
**Created**: 2025-10-23
**Author**: Claude Code (Sonnet 4.5)

---

*This plan will be integrated into the master plan upon approval and all downstream documents will be updated accordingly.*
