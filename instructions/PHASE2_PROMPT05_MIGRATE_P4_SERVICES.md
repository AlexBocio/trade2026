# Phase 2 - Prompt 05: Migrate Priority 4 Services (Supporting)

**Phase**: 2 - Backend Migration  
**Prompt**: 05 of 06  
**Services**: ptrc, feast-pipeline, execution-quality, compliance-scanner, logger, monitoring  
**Priority**: P4 (Supporting Services - Non-Critical)  
**Estimated Time**: 13 hours  
**Dependencies**: Prompts 02-04 complete and CRITICAL validation passed  
**Status**: ⏸️ Ready after Prompt 04 CRITICAL validation

---

## 🛑 MANDATORY VALIDATION GATE

### Prerequisites Check

Before starting Prompt 05, **MUST verify Prompt 04 CRITICAL validation passed**:

- [ ] **Prompt 04 CRITICAL Validation Complete**
  - [ ] Full trading flow working
  - [ ] Load test passed (1000 orders/sec, 5 min)
  - [ ] Risk: P50 ≤ 1.5ms
  - [ ] OMS: P50 ≤ 10ms, P99 ≤ 50ms
  - [ ] All 7 services healthy (normalizer, sink-ticks, sink-alt, gateway, live-gateway, risk, oms)

- [ ] **Core Infrastructure Healthy**
  - [ ] NATS, Valkey, QuestDB, ClickHouse, SeaweedFS, OpenSearch all running

**Decision**: All prerequisites met? ✅ YES → Proceed | ❌ NO → Fix Prompt 04 first

---

## 📋 TASK OVERVIEW

### Services to Migrate

| Service | Port | Est. Time | Complexity | Purpose |
|---------|------|-----------|------------|---------|
| ptrc | 8109 | 4h | Medium | P&L, Tax, Risk, Compliance reporting |
| feast-pipeline | N/A | 2h | Simple | Feature store materialization |
| execution-quality | TBD | 3h | Medium | Execution quality monitoring |
| compliance-scanner | TBD | 2h | Simple | Wash trading / spoofing detection |
| logger | TBD | 2h | Simple | Centralized logging |
| monitoring | TBD | 2h | Simple | System monitoring |

**Total**: 13 hours

**Note**: These are supporting services, not critical for core trading.

**Migration Strategy**: Follow same 10-step pattern, can parallelize some services

---

# 🔧 SERVICE 1: PTRC (P&L, Tax, Risk, Compliance)

## Service Information

**Purpose**: Multi-function service for reporting and compliance

**Port**: 8109  
**Networks**: frontend, backend  
**Dependencies**: ClickHouse, QuestDB, SeaweedFS

**Modules**:
- P&L calculation (FIFO, LIFO, AVG methods)
- Tax reporting (1099, wash sales)
- Risk reports (VaR, stress testing)
- Compliance surveillance (wash trading, spoofing)

---

## Quick Migration Steps

### 1. Copy and Configure

```bash
mkdir -p backend/apps/ptrc
# Copy from Trade2025

# Create config
cat > config/backend/ptrc/config.yaml << 'EOF'
service:
  name: "ptrc"
  port: 8109
  log_level: "INFO"

clickhouse:
  http_url: "http://clickhouse:8123"
  database: "trade2026"

questdb:
  http_url: "http://questdb:9000"
  pg_url: "postgresql://admin:quest@questdb:8812/qdb"

seaweedfs:
  s3_endpoint: "http://seaweedfs:8333"
  bucket: "trader2026"
  prefix: "reports/"

modules:
  pnl:
    enabled: true
    default_method: "FIFO"
  tax:
    enabled: true
    wash_sale_window_days: 30
  risk:
    enabled: true
    var_confidence: 0.99
  compliance:
    enabled: true
    surveillance_enabled: true
EOF
```

### 2. Update URLs

```python
# Replace localhost with Docker service names
clickhouse_url = "http://clickhouse:8123"
questdb_url = "http://questdb:9000"
s3_endpoint = "http://seaweedfs:8333"
```

### 3. Build and Test

```bash
cd backend/apps/ptrc
docker build -t localhost/ptrc:latest .

# Start service
docker-compose -f infrastructure/docker/docker-compose.apps.yml up -d ptrc

# Test P&L calculation
curl -X POST http://localhost:8109/pnl/compute \
  -H "Content-Type: application/json" \
  -d '{"account": "test_account", "method": "FIFO"}'
```

**Success Criteria**:
- [ ] Service starts and healthy
- [ ] P&L calculations work
- [ ] Reports generate
- [ ] Data persists to S3

---

# 🔧 SERVICE 2: FEAST-PIPELINE (Feature Store)

## Service Information

**Purpose**: Materialize features from ClickHouse to Valkey for ML serving

**Port**: N/A (background job)  
**Networks**: backend  
**Dependencies**: ClickHouse (source), Valkey (online store)

---

## Quick Migration Steps

### 1. Copy and Configure

```bash
mkdir -p backend/apps/feast_pipeline
# Copy from Trade2025

# Create config
cat > config/backend/feast_pipeline/config.yaml << 'EOF'
feast:
  repo_path: "/app/feast"
  online_store:
    type: "redis"
    connection_string: "valkey:6379"
  offline_store:
    type: "clickhouse"
    host: "clickhouse"
    port: 8123
    database: "trade2026"

materialization:
  interval_minutes: 5
  features:
    - "market_features"
    - "order_features"
    - "position_features"
EOF
```

### 2. Create Feast Repository

```python
# feast_repo/feature_store.yaml
project: trade2026
provider: local
online_store:
  type: redis
  connection_string: "valkey:6379"
offline_store:
  type: clickhouse
  host: clickhouse
  port: 8123
  database: trade2026
```

### 3. Run Materialization

```bash
cd backend/apps/feast_pipeline

# Build image
docker build -t localhost/feast-pipeline:latest .

# Run materialization job
docker-compose -f infrastructure/docker/docker-compose.apps.yml up -d feast-pipeline

# Verify features in Valkey
docker exec -it valkey valkey-cli
# KEYS feast:*
```

**Success Criteria**:
- [ ] Materialization runs every 5 minutes
- [ ] Features written to Valkey
- [ ] Feature freshness < 5 minutes

---

# 🔧 SERVICES 3-6: Quick Implementation

## Execution Quality, Compliance Scanner, Logger, Monitoring

These services follow the same pattern. I'll provide a template approach:

### Template Migration (for each service)

```bash
# 1. Copy source
mkdir -p backend/apps/{service_name}
# Copy from C:\Trade2025\trading\apps\{service_name}\

# 2. Create config
cat > config/backend/{service_name}/config.yaml << 'EOF'
service:
  name: "{service_name}"
  port: {port}  # Assign from available range
  log_level: "INFO"

# Add service-specific config here
# Use Docker service names (not localhost)
EOF

# 3. Update code
# Replace all localhost with Docker service names

# 4. Build
cd backend/apps/{service_name}
docker build -t localhost/{service_name}:latest .

# 5. Start
docker-compose -f infrastructure/docker/docker-compose.apps.yml up -d {service_name}

# 6. Verify
docker logs {service_name} --tail 20
curl http://localhost:{port}/health
```

### Service-Specific Notes

**execution-quality** (Port: 8110):
- Monitors execution quality metrics
- Depends on: ClickHouse, QuestDB
- Measures: slippage, fill rate, time to fill

**compliance-scanner** (Port: 8111):
- Scans for wash trading, spoofing
- Depends on: ClickHouse
- Already part of PTRC, may be duplicate

**logger** (Port: 8112):
- Centralized logging aggregation
- Consider using existing infrastructure (Docker logs)
- May not need separate service

**monitoring** (Port: 8113):
- System monitoring and alerts
- Consider using Prometheus + Grafana
- May not need separate service

---

## ⚡ SIMPLIFIED APPROACH

### Option: Skip Logger and Monitoring

**Recommendation**: Skip logger and monitoring services if:
- Docker logs + ElasticSearch/OpenSearch already handle logging
- Prometheus + Grafana can be added later
- Focus on trading-critical services

**If skipping**:
- Reduces from 6 to 4 services
- Saves ~4 hours
- Still achieves MVP functionality

---

# ✅ PROMPT 05 VALIDATION GATE

## Post-Migration Validation

After migrating P4 services:

### Test 1: All Services Running

```bash
docker-compose -f docker-compose.apps.yml ps

# Expected: 11-13 services healthy (depending on what you migrated)
# P1: normalizer, sink-ticks, sink-alt
# P2: gateway, live-gateway
# P3: risk, oms
# P4: ptrc, feast-pipeline, execution-quality, (compliance-scanner), (logger), (monitoring)
```

**Success Criteria**:
- [ ] All migrated services healthy
- [ ] No crashes
- [ ] No errors in logs

---

### Test 2: Supporting Functions Work

```bash
# Test PTRC P&L calculation
curl -X POST http://localhost:8109/pnl/compute \
  -H "Content-Type: application/json" \
  -d '{"account": "test_account"}'

# Test Feast features
docker exec -it valkey valkey-cli
# GET feast:market_features:BTCUSDT

# Test execution quality (if implemented)
curl http://localhost:8110/metrics
```

**Success Criteria**:
- [ ] PTRC generates reports
- [ ] Feast features materialize
- [ ] Execution quality monitors orders
- [ ] All supporting functions operational

---

### Test 3: Core Trading Still Works

```bash
# Verify core trading not impacted by new services
# Submit test order
curl -X POST http://localhost:8099/orders \
  -H "Content-Type: application/json" \
  -d '{
    "account": "test_account",
    "symbol": "BTCUSDT",
    "side": "buy",
    "type": "limit",
    "quantity": 0.1,
    "price": 45000.0
  }'

# Should still work with same performance
```

**Success Criteria**:
- [ ] Core trading still works
- [ ] Performance not degraded
- [ ] Risk/OMS still meet SLAs

---

## 🎉 PHASE 2 MVP COMPLETE!

### If Prompt 05 Validation Passes

**Congratulations! Phase 2 MVP is complete.**

**What You Have**:
- ✅ All Priority 1-4 services (13 services)
- ✅ Complete data pipeline (ingestion → normalization → storage)
- ✅ Complete trading flow (API → OMS → Risk → Execution → Fills → Positions)
- ✅ Supporting services (reports, features, monitoring)
- ✅ Fully functional trading platform

**What Works**:
- ✅ Market data ingestion from exchanges
- ✅ Real-time data normalization
- ✅ Order submission and execution (paper trading)
- ✅ Risk checks (< 1.5ms)
- ✅ Position tracking
- ✅ P&L calculation
- ✅ Feature store for ML

---

## 🚦 DECISION POINT

### After Prompt 05 Complete

You have three options:

**OPTION A (RECOMMENDED)**: Move to Phase 3 (Frontend Integration)
- Connect React frontend to backend APIs
- Build unified user interface
- Production-ready platform in 1-2 weeks

**OPTION B**: Do Prompt 06 (P5 ML Services)
- 5 additional services
- 22 hours of work
- ML infrastructure (serving, training, backtesting)
- Can defer to Phase 4 (ML Library)

**OPTION C**: Stop and Deploy MVP
- Current platform is functional
- Can start paper trading
- Polish and optimize
- Add features later

**My Recommendation**: **Choose Option A** (Phase 3 - Frontend)

---

## 📊 PROMPT 05 COMPLETION CRITERIA

Prompt 05 complete when:

- [ ] All P4 services migrated (4-6 services)
- [ ] All services healthy
- [ ] PTRC generating reports
- [ ] Feast materializing features
- [ ] Supporting functions operational
- [ ] Core trading still works (not degraded)
- [ ] Validation gate passed
- [ ] COMPLETION_TRACKER.md updated

**Total Services After Prompt 05**: 11-13 services
**Phase 2 MVP Status**: ✅ COMPLETE

---

**Prompt Status**: ⏸️ READY (After Prompt 04 CRITICAL validation)

**Next Options**:
- **Prompt 06**: P5 ML Services (Optional, 22h)
- **Phase 3**: Frontend Integration (Recommended)
- **Deploy**: Production deployment

**Note**: Supporting services are lower priority, can implement quickly or skip some
