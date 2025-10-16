# Trade2026 - Complete Platform Integration Master Plan

**Created**: 2025-10-14
**Project**: Unify Backend (Trade2025) + Frontend (GUI) + ML Pipelines (PRISM + Strategy Library)
**Target**: Single containerized platform in C:\ClaudeDesktop_Projects\Trade2026\
**Timeline**: 6-8 weeks

---

## 🎯 EXECUTIVE SUMMARY

### What We're Building

**Trade2026** is the complete unification of THREE major systems:

1. **Trade2025 Backend** (C:\Trade2025\)
   - 20+ microservices
   - NATS, Valkey, QuestDB, ClickHouse, SeaweedFS
   - OMS, Risk, PTRC, ML Training, Model Serving
   - 89% operational, production-ready

2. **GUI Frontend** (C:\GUI\)
   - React 18.2 + TypeScript + Vite
   - 50+ pages, 41 routes, 15 Zustand stores
   - 12 alpha scanners, portfolio optimization
   - 100% complete, production-ready

3. **ML Pipelines** (Strategy & ML Library + PRISM Physics)
   - Default ML Pipeline (XGBoost, proven)
   - PRISM Physics Pipeline (experimental)
   - Hybrid Pipeline (ML + Physics)
   - 0% built (comprehensive design complete)

### The Integration Challenge

**Current State**: Three separate codebases in different directories
**Target State**: Single unified platform under `C:\ClaudeDesktop_Projects\Trade2026\`

**Key Integration Points**:
- Frontend needs backend APIs (currently mocked)
- ML pipelines need market data from backend
- Backend needs frontend for user interaction
- All need unified deployment & configuration

### Success Criteria

✅ **All services** containerized and running in single docker-compose
✅ **Frontend connected** to real backend APIs (no mocks)
✅ **ML pipelines operational** (at minimum, Default ML + Feature Store)
✅ **Single-command deployment**: `docker-compose up`
✅ **Unified documentation** and configuration
✅ **All data** in one place (C:\ClaudeDesktop_Projects\Trade2026\data\)

---

## 📊 ASSESSMENT OF CURRENT STATE

### Trade2025 Backend Analysis

**Location**: C:\Trade2025\
**Status**: ✅ 89% Operational (16/18 services healthy)

**Core Infrastructure** (8 services - ALL HEALTHY):
- ✅ NATS (message bus)
- ✅ Valkey (cache)
- ✅ QuestDB (time-series)
- ✅ ClickHouse (analytics)
- ✅ SeaweedFS (storage)
- ✅ OpenSearch (search)
- ✅ authn (authentication)
- ✅ OPA (authorization)

**Application Services** (12 services - 10 FUNCTIONAL):
- ✅ normalizer (data normalization)
- ✅ sink-ticks, sink-alt (data lake)
- ✅ oms (order management)
- ✅ live-gateway (exchange connectivity)
- ✅ risk (risk management)
- ✅ ptrc (P&L, tax, compliance)
- ✅ serving (ML inference)
- ✅ bt-orchestrator (backtesting)
- ⚠️ gateway (external API issue, not platform)
- ⚠️ opa (cosmetic healthcheck)

**ML Infrastructure** (5 services - OPERATIONAL):
- ✅ ml_training (Ray, MLflow, XGBoost)
- ✅ model_serving (BentoML, Feast)
- ✅ marketplace (strategy hosting)
- ✅ feast (feature store)
- ✅ modelops (governance)

**Architecture**: CPGS v1.0 (3-lane network: frontend, low-latency, backend)

**Verdict**: **PRODUCTION-READY**, just needs frontend integration

---

### GUI Frontend Analysis

**Location**: C:\GUI\trade2025-frontend\
**Status**: ✅ 100% Complete (Production-ready)

**Frontend Stack**:
- React 18.2 + TypeScript 5.3
- Vite 5.4 (build tool)
- Zustand (state management)
- TailwindCSS (styling)
- Plotly.js + AG Grid + Recharts (visualization)

**Features Built**:
- ✅ 50+ page components
- ✅ 41 configured routes
- ✅ 15 Zustand stores
- ✅ 10 API clients (ready for backend)
- ✅ 40+ reusable components
- ✅ 12 alpha scanners
- ✅ Portfolio optimization UI
- ✅ Trading interface
- ✅ Risk analytics
- ✅ Backtesting UI

**Current Limitation**: **API clients use MOCK DATA**
- All API calls return hardcoded responses
- No real backend connection yet
- Full API client structure ready for integration

**Verdict**: **READY FOR BACKEND INTEGRATION**

---

### ML Pipelines Analysis

**Location**: C:\ClaudeDesktop_Projects\ML_Pipelines\Physics_Pipeline\
**Status**: 📋 Design Complete (0% Built)

**What's Designed**:
- ✅ PRISM Physics Pipeline (comprehensive 200-page plan)
- ✅ Default ML Pipeline (XGBoost strategy)
- ✅ Hybrid Pipeline (ML + Physics)
- ✅ Strategy & ML Library (registry, hot-swap)
- ✅ 14-task implementation sequence

**What's Missing**:
- ❌ No code implemented yet
- ❌ No services running
- ❌ Integration with backend not done

**Integration Requirements**:
- Needs NATS (from backend)
- Needs QuestDB + ClickHouse (from backend)
- Needs feature store (Feast)
- Needs ML infrastructure (MLflow, BentoML, Ray)

**Verdict**: **NEEDS IMPLEMENTATION** (but plan is excellent)

---

## 🏗️ INTEGRATION ARCHITECTURE

### Unified Platform Structure

```
Trade2026/
├── frontend/              # React app (from C:\GUI\)
│   ├── src/
│   ├── public/
│   ├── vite.config.ts
│   └── package.json
│
├── backend/               # Microservices (from C:\Trade2025\)
│   ├── apps/
│   │   ├── gateway/       # Market data
│   │   ├── normalizer/    # Data normalization
│   │   ├── oms/           # Order management
│   │   ├── risk/          # Risk management
│   │   ├── ptrc/          # P&L, tax, compliance
│   │   ├── serving/       # ML inference
│   │   ├── ml_training/   # Model training
│   │   ├── marketplace/   # Strategy hosting
│   │   └── ... (all services)
│   └── shared/            # Shared utilities
│
├── library/               # Strategy & ML Library (NEW)
│   ├── apps/
│   │   └── library/       # Registry service
│   ├── pipelines/
│   │   ├── default_ml/    # XGBoost strategy
│   │   ├── prism_physics/ # Physics-based
│   │   └── hybrid/        # Combined
│   └── strategies/
│
├── infrastructure/        # Docker, Kubernetes, configs
│   ├── docker/
│   │   ├── docker-compose.yml         # MAIN COMPOSE FILE
│   │   ├── docker-compose.core.yml    # Infrastructure
│   │   ├── docker-compose.apps.yml    # Applications
│   │   ├── docker-compose.frontend.yml # Frontend
│   │   ├── docker-compose.library.yml  # ML Library
│   │   └── Dockerfiles/               # All Dockerfiles
│   ├── k8s/               # Kubernetes manifests
│   └── nginx/             # Nginx configs
│
├── data/                  # ALL platform data
│   ├── nats/              # Message bus persistence
│   ├── valkey/            # Cache data
│   ├── questdb/           # Time-series data
│   ├── clickhouse/        # Analytics data
│   ├── seaweed/           # Object storage
│   ├── opensearch/        # Search index
│   ├── postgres/          # Relational data
│   └── mlflow/            # ML tracking
│
├── config/                # Configuration files
│   ├── backend/           # Service configs
│   ├── frontend/          # Frontend configs
│   └── library/           # ML pipeline configs
│
├── secrets/               # Secrets (NOT in Git)
│   ├── api_keys.env
│   ├── jwt_keys/
│   └── certificates/
│
├── docs/                  # Documentation
│   ├── architecture/
│   ├── api/
│   ├── deployment/
│   └── user_guides/
│
├── tests/                 # All tests
│   ├── integration/
│   ├── e2e/
│   └── performance/
│
└── scripts/               # Helper scripts
    ├── setup.sh           # Initial setup
    ├── migrate.sh         # Data migration
    ├── deploy.sh          # Deployment
    └── cleanup.sh         # Cleanup
```

---

## 🎯 INTEGRATION PHASES

### Phase 1: Foundation Setup (Week 1)
**Goal**: Create unified directory structure and core infrastructure

**Tasks**:
1. Create Trade2026 directory structure
2. Migrate backend core infrastructure
3. Configure unified Docker networks
4. Setup unified docker-compose.yml
5. Test core services (NATS, Valkey, databases)

**Deliverables**:
- ✅ Complete directory structure
- ✅ docker-compose.core.yml running
- ✅ All core infrastructure healthy

---

### Phase 2: Backend Migration (Week 2-3)
**Goal**: Move all backend services to Trade2026

**Tasks**:
1. Copy backend services to Trade2026/backend/
2. Update all configuration files (use Trade2026 paths)
3. Update Docker Compose for all application services
4. Test each service individually
5. Test service-to-service communication

**Deliverables**:
- ✅ All backend services in Trade2026/backend/
- ✅ docker-compose.apps.yml running
- ✅ 18/18 services healthy
- ✅ NATS communication working

---

### Phase 3: Frontend Integration (Week 3-4)
**Goal**: Connect frontend to real backend APIs

**Tasks**:
1. Copy frontend to Trade2026/frontend/
2. Replace mock API clients with real API calls
3. Configure API base URL (environment variables)
4. Update Docker Compose for frontend
5. Setup Nginx reverse proxy
6. Test each API integration

**API Integration Checklist**:
- [ ] Alpha Scanner API → Port 5008
- [ ] Portfolio Optimizer API → Port 5001
- [ ] PBO Analysis API → Port 5002
- [ ] Simulation Engine API → Port 5003
- [ ] Meta-Label Service API → Port 5004
- [ ] Fractional Diff API → Port 5005
- [ ] Screener API → Port 5006
- [ ] Scanner API → Port 5007
- [ ] Covariance API → Port 5001
- [ ] Market Data API → Gateway

**Deliverables**:
- ✅ Frontend in Trade2026/frontend/
- ✅ docker-compose.frontend.yml running
- ✅ All API clients connected to real backends
- ✅ Nginx routing configured
- ✅ Frontend accessible at http://localhost

---

### Phase 4: Strategy & ML Library (Week 4-5)
**Goal**: Build unified Strategy & ML Library service

**Tasks**:
1. Create Trade2026/library/ structure
2. Implement Library service (from previous instructions)
3. Build Default ML Pipeline
4. Setup Feast feature store integration
5. Connect to ML infrastructure (MLflow, BentoML, Ray)

**Sub-phases**:

**4a. Library Service Foundation**:
- PostgreSQL registry database
- FastAPI service with CRUD API
- NATS integration
- Hot-swap engine

**4b. Default ML Pipeline**:
- Feature engineering (RSI, MACD, Bollinger Bands)
- XGBoost model training
- MLflow tracking integration
- BentoML serving integration

**4c. Feature Store Integration**:
- Feast feature views
- ClickHouse offline store
- Valkey online store
- Materialization pipeline

**Deliverables**:
- ✅ Library service running (port 8350)
- ✅ Default ML Pipeline operational
- ✅ Feast feature store working
- ✅ First alpha strategy deployed

---

### Phase 5: PRISM Physics Pipeline (Week 5-6)
**Goal**: Implement physics-based analysis (OPTIONAL - can skip if time constrained)

**Tasks**:
1. Build physics calculators (Entropy, Turbulence, Pressure)
2. Implement phase transition detection
3. Build percolation tracker
4. Create physics alpha strategy
5. Validate physics signals with backtests

**Decision Point**: Skip if Default ML is performing well

**Deliverables** (if built):
- ✅ Physics modules operational
- ✅ Physics alpha strategy deployed
- ✅ Backtest validation showing value

---

### Phase 6: Hybrid Pipeline (Week 6)
**Goal**: Combine ML and Physics (only if Phase 5 completed)

**Tasks**:
1. Build hybrid signal synthesis
2. Implement adaptive weighting
3. Deploy hybrid alpha strategy
4. Compare performance (ML vs Physics vs Hybrid)

**Deliverables**:
- ✅ Hybrid pipeline operational
- ✅ Performance comparison complete
- ✅ Best strategy identified

---

### Phase 7: Testing & Validation (Week 7)
**Goal**: Comprehensive testing of integrated platform

**Tasks**:
1. Unit tests for all new code
2. Integration tests (frontend ↔ backend)
3. E2E tests (user workflows)
4. Performance tests (load, stress)
5. Security tests (Trivy, ZAP)

**Test Coverage Goals**:
- Unit tests: > 80%
- Integration tests: All API endpoints
- E2E tests: All major user workflows
- Performance: Meet latency SLAs

**Deliverables**:
- ✅ All tests passing
- ✅ Performance benchmarks met
- ✅ Security vulnerabilities addressed

---

### Phase 8: Documentation & Deployment (Week 8)
**Goal**: Production-ready deployment and documentation

**Tasks**:
1. Write deployment guide
2. Create user documentation
3. Setup CI/CD pipeline
4. Production environment configuration
5. Monitoring & alerting setup

**Documentation**:
- Architecture diagrams
- API documentation
- User guides
- Deployment procedures
- Troubleshooting guides

**Deliverables**:
- ✅ Complete documentation
- ✅ CI/CD pipeline operational
- ✅ Production deployment successful
- ✅ Monitoring dashboards live

---

## 🚀 DETAILED TASK BREAKDOWN

### Task Group 1: Directory Structure & Setup

**Task 1.1**: Create Trade2026 directory structure
```bash
# Create main directories
mkdir -p C:\ClaudeDesktop_Projects\Trade2026\{frontend,backend,library,infrastructure,data,config,secrets,docs,tests,scripts}

# Create subdirectories
mkdir -p C:\ClaudeDesktop_Projects\Trade2026\backend\apps
mkdir -p C:\ClaudeDesktop_Projects\Trade2026\library\{apps,pipelines,strategies}
mkdir -p C:\ClaudeDesktop_Projects\Trade2026\infrastructure\{docker,k8s,nginx}
mkdir -p C:\ClaudeDesktop_Projects\Trade2026\data\{nats,valkey,questdb,clickhouse,seaweed,opensearch,postgres,mlflow}
```

**Task 1.2**: Copy and configure core infrastructure
```bash
# Copy Docker Compose files
cp C:\Trade2025\docker-compose.core.yml C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker\

# Update paths in docker-compose files
# Change: C:/trade2025/trading/ → C:/ClaudeDesktop_Projects/Trade2026/
```

**Task 1.3**: Setup unified Docker networks
```yaml
# infrastructure/docker/docker-compose.networks.yml
version: '3.8'
networks:
  trade2026-frontend:
    name: trade2026-frontend
    driver: bridge
    ipam:
      config:
        - subnet: 172.23.0.0/16
  trade2026-lowlatency:
    name: trade2026-lowlatency
    driver: bridge
    ipam:
      config:
        - subnet: 172.22.0.0/16
  trade2026-backend:
    name: trade2026-backend
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16
```

---

### Task Group 2: Backend Migration

**Task 2.1**: Copy backend services
```bash
# Copy all apps
cp -r C:\Trade2025\trading\apps\* C:\ClaudeDesktop_Projects\Trade2026\backend\apps\

# Copy infrastructure configs
cp -r C:\Trade2025\trading\infra\* C:\ClaudeDesktop_Projects\Trade2026\infrastructure\
```

**Task 2.2**: Update configuration files

For EACH service in `backend/apps/*/config.yaml`:
```yaml
# OLD (Trade2025):
nats_url: nats://nats:4222
data_path: C:/trade2025/trading/data
secrets_path: C:/trade2025/trading/secrets

# NEW (Trade2026):
nats_url: nats://nats:4222  # Same (Docker DNS)
data_path: C:/ClaudeDesktop_Projects/Trade2026/data
secrets_path: C:/ClaudeDesktop_Projects/Trade2026/secrets
```

**Task 2.3**: Update Docker Compose

Create `infrastructure/docker/docker-compose.apps.yml`:
```yaml
version: '3.8'

networks:
  frontend:
    external: true
    name: trade2026-frontend
  lowlatency:
    external: true
    name: trade2026-lowlatency
  backend:
    external: true
    name: trade2026-backend

services:
  gateway:
    image: localhost/gateway:latest
    build:
      context: ../../backend/apps/gateway
      dockerfile: Dockerfile
    volumes:
      - ../../config/backend/gateway:/app/config
      - ../../secrets:/secrets
    networks:
      - frontend
      - lowlatency
      - backend
    ports:
      - "8080:8080"
    # ... (continue for all services)
```

**Task 2.4**: Test each service individually

For each service:
```bash
# Build image
docker build -t localhost/gateway:latest C:\ClaudeDesktop_Projects\Trade2026\backend\apps\gateway

# Start service
docker compose -f infrastructure/docker/docker-compose.apps.yml up -d gateway

# Check health
curl http://localhost:8080/health

# Check logs
docker logs gateway --tail 50
```

---

### Task Group 3: Frontend Integration

**Task 3.1**: Copy frontend code
```bash
# Copy entire frontend
cp -r C:\GUI\trade2025-frontend\* C:\ClaudeDesktop_Projects\Trade2026\frontend\
```

**Task 3.2**: Replace API client mocks

Current frontend structure:
```typescript
// frontend/src/api/clients/alphaScanner.ts (CURRENT - MOCK)
export class AlphaScannerClient {
  async findMatches(request: FindMatchesRequest): Promise<FindMatchesResponse> {
    // Returns hardcoded mock data
    return {
      matches: [...MOCK_DATA]
    };
  }
}
```

New structure:
```typescript
// frontend/src/api/clients/alphaScanner.ts (NEW - REAL API)
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api';

export class AlphaScannerClient {
  async findMatches(request: FindMatchesRequest): Promise<FindMatchesResponse> {
    const response = await axios.post(
      `${API_BASE_URL}/alpha/time-machine/find-matches`,
      request
    );
    return response.data;
  }
}
```

**Task 3.3**: Create environment configuration

```typescript
// frontend/.env.development
VITE_API_BASE_URL=http://localhost:8080/api
VITE_WS_URL=ws://localhost:8080/ws

// frontend/.env.production
VITE_API_BASE_URL=https://trade2026.your-domain.com/api
VITE_WS_URL=wss://trade2026.your-domain.com/ws
```

**Task 3.4**: Setup Nginx reverse proxy

```nginx
# infrastructure/nginx/nginx.conf
http {
    upstream backend {
        server gateway:8080;
    }

    upstream alpha_scanner {
        server alpha-scanner:5008;
    }

    upstream portfolio_optimizer {
        server portfolio-optimizer:5001;
    }

    # ... (all backend services)

    server {
        listen 80;
        server_name localhost;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # API Gateway
        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Alpha Scanner
        location /api/alpha/ {
            proxy_pass http://alpha_scanner/;
        }

        # Portfolio Optimizer
        location /api/portfolio/ {
            proxy_pass http://portfolio_optimizer/;
        }

        # WebSocket
        location /ws {
            proxy_pass http://backend/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $websocket;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

**Task 3.5**: Build frontend Docker image

```dockerfile
# infrastructure/docker/Dockerfiles/frontend.Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm ci

# Copy source
COPY frontend/ ./

# Build
RUN npm run build

# Production image
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY infrastructure/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Task 3.6**: Add frontend to Docker Compose

```yaml
# infrastructure/docker/docker-compose.frontend.yml
services:
  frontend:
    image: localhost/trade2026-frontend:latest
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfiles/frontend.Dockerfile
    networks:
      - trade2026-frontend
    ports:
      - "80:80"
    depends_on:
      - gateway
      - alpha-scanner
      - portfolio-optimizer
    environment:
      - VITE_API_BASE_URL=http://localhost:8080/api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 10s
      timeout: 3s
      retries: 3
```

---

### Task Group 4: Strategy & ML Library Implementation

This follows the 14-task sequence from the previous ML Pipeline instructions, but adapted for Trade2026:

**Task 4.1**: Build Library service (from previous Task 01)
- Location: `C:\ClaudeDesktop_Projects\Trade2026\library\apps\library\`
- Port: 8350
- Database: PostgreSQL (new container)
- Integration: NATS (existing)

**Task 4.2**: Implement CRUD API (from previous Task 02)
- Entity management
- Deployment lifecycle
- Swap operations

**Task 4.3**: Build Default ML Pipeline (from previous Tasks 04-06)
- Feature engineering
- XGBoost training
- ML alpha strategy

**Task 4.4**: Setup Feast integration
- Feature views
- ClickHouse offline store
- Valkey online store

---

### Task Group 5: OPTIONAL - PRISM Physics Pipeline

Only proceed if:
1. Default ML Pipeline is working
2. Time permits (week 5 available)
3. User wants experimental physics approach

**Task 5.1-5.3**: Build physics modules (from previous Tasks 07-09)
- Entropy Engine
- Phase Transition Scanner
- Turbulence Monitor
- Physics Alpha Strategy

---

### Task Group 6: Testing & Validation

**Task 6.1**: Integration tests
```bash
# Test frontend → backend connection
npm run test:integration

# Test backend services communication
cd tests/integration
pytest test_service_communication.py
```

**Task 6.2**: E2E tests
```bash
# Run Playwright E2E tests
cd frontend
npm run test:e2e

# Should cover:
# - Login flow
# - Dashboard loading
# - Running alpha scanner
# - Portfolio optimization
# - Order submission
# - Risk analysis
```

**Task 6.3**: Performance tests
```bash
# Load test API endpoints
k6 run tests/performance/api_load_test.js

# Target:
# - API latency P50 < 50ms, P99 < 200ms
# - 1000 concurrent users
# - No errors
```

---

## 📋 MASTER DOCKER COMPOSE

The final unified docker-compose will orchestrate EVERYTHING:

```yaml
# infrastructure/docker/docker-compose.yml
version: '3.8'

# Include all compose files
include:
  - docker-compose.networks.yml
  - docker-compose.core.yml
  - docker-compose.apps.yml
  - docker-compose.frontend.yml
  - docker-compose.library.yml

# This allows single command: docker-compose up
```

**Usage**:
```bash
# Start everything
cd C:\ClaudeDesktop_Projects\Trade2026
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Check status
docker ps

# View logs
docker-compose -f infrastructure/docker/docker-compose.yml logs -f

# Stop everything
docker-compose -f infrastructure/docker/docker-compose.yml down
```

---

## 🎯 CRITICAL SUCCESS FACTORS

### 1. Configuration Management

**Problem**: Services reference different paths
**Solution**: Environment variables + config templates

```yaml
# config/backend/gateway/config.template.yaml
nats_url: ${NATS_URL}
data_path: ${DATA_PATH}
secrets_path: ${SECRETS_PATH}
```

### 2. Service Discovery

**Problem**: Services need to find each other
**Solution**: Docker DNS names (already implemented in Trade2025)

✅ Keep using: `nats:4222`, `valkey:6379`, `questdb:9000`
❌ Never use: `localhost`, `127.0.0.1`, hardcoded IPs

### 3. Data Persistence

**Problem**: Data scattered across multiple locations
**Solution**: Unified data directory

All data goes to: `C:\ClaudeDesktop_Projects\Trade2026\data\`

```yaml
volumes:
  - ../../data/nats:/var/lib/nats
  - ../../data/questdb:/var/lib/questdb
  - ../../data/clickhouse:/var/lib/clickhouse
```

### 4. Port Conflicts

**Problem**: Multiple services need same ports
**Solution**: CPGS v1.0 port ranges (already defined)

- Frontend: 80 (Nginx), 443 (HTTPS)
- Backend services: 8000-8499 (CPGS standard)
- Frontend dev: 5173 (Vite)

### 5. API Integration

**Problem**: Frontend expects specific API structure
**Solution**: Either:
- A) Backend implements frontend's expected API
- B) Frontend adapts to backend's API
- C) API adapter layer (Nginx rewrite rules)

**Recommendation**: Option C (least disruptive)

---

## 🔄 MIGRATION WORKFLOW

### Step-by-Step Migration Process

**1. Backup Everything**
```bash
# Backup current Trade2025
cp -r C:\Trade2025 C:\Trade2025_backup_$(date +%Y%m%d)

# Backup GUI
cp -r C:\GUI C:\GUI_backup_$(date +%Y%m%d)
```

**2. Create Trade2026 Structure**
```bash
# Run setup script
cd C:\ClaudeDesktop_Projects\Trade2026
bash scripts/setup.sh
```

**3. Migrate Infrastructure (Core Services)**
```bash
# Copy and configure
bash scripts/migrate_infrastructure.sh

# Test
docker-compose -f infrastructure/docker/docker-compose.core.yml up -d
docker ps  # Should show 8 healthy core services
```

**4. Migrate Backend Services**
```bash
# Copy and configure
bash scripts/migrate_backend.sh

# Test each service
bash scripts/test_backend.sh
```

**5. Migrate Frontend**
```bash
# Copy and configure
bash scripts/migrate_frontend.sh

# Build and test
cd frontend
npm install
npm run build
```

**6. Build ML Library**
```bash
# Follow 14-task instruction sequence
# Starting with Library service foundation
```

**7. Full Integration Test**
```bash
# Start everything
docker-compose up -d

# Run integration tests
bash scripts/test_integration.sh

# Run E2E tests
cd frontend
npm run test:e2e
```

---

## 📊 PROGRESS TRACKING

### Checklist for Each Phase

**Phase 1: Foundation**
- [ ] Directory structure created
- [ ] Docker networks configured
- [ ] Core infrastructure migrated
- [ ] All core services healthy
- [ ] Data directories setup

**Phase 2: Backend Migration**
- [ ] All services copied to Trade2026
- [ ] Configuration files updated
- [ ] Docker Compose files created
- [ ] Each service tested individually
- [ ] Service-to-service communication verified
- [ ] 18/18 services healthy

**Phase 3: Frontend Integration**
- [ ] Frontend code copied
- [ ] API clients updated (mocks → real APIs)
- [ ] Environment configuration setup
- [ ] Nginx reverse proxy configured
- [ ] Frontend Docker image built
- [ ] Frontend accessible at localhost
- [ ] All API integrations working

**Phase 4: ML Library**
- [ ] Library service running
- [ ] PostgreSQL registry operational
- [ ] CRUD API working
- [ ] NATS integration complete
- [ ] Default ML Pipeline built
- [ ] Feast feature store working
- [ ] First alpha strategy deployed

**Phase 5: PRISM Physics** (OPTIONAL)
- [ ] Physics modules built
- [ ] Physics strategy deployed
- [ ] Backtests showing value
- [ ] OR: Skipped (time/performance)

**Phase 6: Hybrid** (OPTIONAL)
- [ ] Hybrid pipeline built
- [ ] Performance comparison done
- [ ] Best strategy identified

**Phase 7: Testing**
- [ ] Unit tests > 80% coverage
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance benchmarks met
- [ ] Security scans clean

**Phase 8: Documentation**
- [ ] Architecture docs complete
- [ ] API docs complete
- [ ] User guides complete
- [ ] Deployment guide complete
- [ ] CI/CD pipeline operational

---

## 🚨 RISK MITIGATION

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Configuration drift | High | Use config templates + validation scripts |
| Port conflicts | Medium | CPGS v1.0 strict port allocation |
| Data loss during migration | Critical | Backups before each phase |
| Service dependencies break | High | Test each service individually first |
| Frontend API mismatch | High | API adapter layer (Nginx) |
| Physics pipeline doesn't work | Low | Make optional, skip if needed |

### Process Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Timeline slips | Medium | Phase-based approach, can stop after Phase 4 |
| Scope creep | Medium | Stick to MVP, defer enhancements |
| Parallel work conflicts | High | Sequential phases, one at a time |
| Testing inadequate | High | Mandatory testing phase (Phase 7) |

---

## 📝 INSTRUCTION GENERATION FOR CLAUDE CODE

Based on this master plan, I'll generate **detailed instructions** for Claude Code similar to the ML Pipeline instructions:

### Instruction Structure

**Foundation Instructions** (5 tasks):
1. `01_SETUP_DIRECTORY_STRUCTURE.md`
2. `02_MIGRATE_CORE_INFRASTRUCTURE.md`
3. `03_CONFIGURE_NETWORKS.md`
4. `04_TEST_CORE_SERVICES.md`
5. `05_SETUP_DATA_DIRECTORIES.md`

**Backend Migration Instructions** (10 tasks):
6. `06_COPY_BACKEND_SERVICES.md`
7. `07_UPDATE_CONFIGURATIONS.md`
8. `08_BUILD_DOCKER_IMAGES.md`
9. `09_CREATE_APP_COMPOSE.md`
10. `10_TEST_GATEWAY.md`
11. `11_TEST_NORMALIZER_OMS.md`
12. `12_TEST_RISK_PTRC.md`
13. `13_TEST_ML_SERVICES.md`
14. `14_VERIFY_BACKEND_HEALTH.md`
15. `15_BACKEND_INTEGRATION_TEST.md`

**Frontend Integration Instructions** (8 tasks):
16. `16_COPY_FRONTEND_CODE.md`
17. `17_UPDATE_API_CLIENTS.md`
18. `18_CONFIGURE_ENVIRONMENT.md`
19. `19_BUILD_FRONTEND_IMAGE.md`
20. `20_SETUP_NGINX.md`
21. `21_TEST_FRONTEND_BUILD.md`
22. `22_API_INTEGRATION_TEST.md`
23. `23_E2E_FRONTEND_TEST.md`

**ML Library Instructions** (14 tasks - from previous):
24-37. `24_LIBRARY_CORE_DATABASE.md` through `37_LIBRARY_DASHBOARD.md`

**Testing & Validation Instructions** (5 tasks):
38. `38_INTEGRATION_TEST_SUITE.md`
39. `39_E2E_TEST_SUITE.md`
40. `40_PERFORMANCE_TESTS.md`
41. `41_SECURITY_SCANS.md`
42. `42_FULL_PLATFORM_VALIDATION.md`

**Documentation Instructions** (3 tasks):
43. `43_ARCHITECTURE_DOCS.md`
44. `44_API_DOCUMENTATION.md`
45. `45_USER_GUIDES.md`

**Total**: 45 detailed instructions (similar format to previous ML Pipeline task)

---

## 🎉 FINAL DELIVERABLE

When complete, you'll have:

```
Trade2026/
├── Frontend: React app at http://localhost
├── Backend: 18+ microservices (all healthy)
├── ML Library: Strategy registry + pipelines
├── Data: Unified storage location
├── Docs: Complete documentation
└── Tests: Full test coverage

Single command deployment:
$ cd C:\ClaudeDesktop_Projects\Trade2026
$ docker-compose up -d

Result:
- ✅ Complete trading platform
- ✅ Real-time market data
- ✅ Order execution
- ✅ Risk management
- ✅ Portfolio optimization
- ✅ ML-powered alpha generation
- ✅ 12 alpha scanners
- ✅ Backtesting engine
- ✅ Full UI/UX
```

---

## 🚀 RECOMMENDED START SEQUENCE

**Week 1**: Foundation + Backend Migration
1. Create directory structure (Day 1)
2. Migrate core infrastructure (Day 2)
3. Migrate backend services (Day 3-5)

**Week 2**: Frontend Integration
1. Copy frontend (Day 1)
2. Update API clients (Day 2-3)
3. Setup Nginx (Day 4)
4. Test integration (Day 5)

**Week 3-4**: ML Library (Default ML only)
1. Library service (Week 3)
2. Default ML Pipeline (Week 3)
3. Feature store (Week 4)
4. Alpha strategy (Week 4)

**Week 5**: Testing
1. Integration tests
2. E2E tests
3. Performance tests

**Week 6**: Production Deployment
1. Documentation
2. CI/CD
3. Production environment
4. Monitoring

**OPTIONAL Week 7-8**: PRISM Physics (if desired)

---

**Status**: 📋 Plan Complete → Ready for Task Generation

**Next Step**: Generate 45 detailed instructions for Claude Code

**Last Updated**: 2025-10-14

---

*This is the master plan. Execute sequentially. Build it right.* 🎯
