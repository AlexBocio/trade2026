# Task 05: Validate Core Services

**Phase**: 1 - Foundation
**Priority**: P0-Critical
**Estimated Time**: 1 hour
**Dependencies**: Task 01-04 (All previous foundation tasks)
**Created**: 2025-10-14
**Assigned To**: Claude Code

---

# 🛑 STOP - READ THIS FIRST 🛑

## MANDATORY READING BEFORE ANY CODE EXECUTION

**Claude Code**: You MUST read these files IN FULL before starting any work. This is NON-NEGOTIABLE.

### 1. MASTER_GUIDELINES.md (CRITICAL - READ FIRST)
**Location**: `C:\ClaudeDesktop_Projects\ClaudeKnowledge\MASTER_GUIDELINES.md`

**YOU MUST READ THESE SECTIONS** (use file_read tool):
- [ ] **New Session Startup Protocol** - How to begin ANY session
- [ ] **Core Development Rules** - Component Isolation, Read Before Write, Backup Critical Files
- [ ] **Testing & Validation Rules** - CRITICAL for this validation task
- [ ] **6-Phase Mandatory Workflow** - EVERY task follows this workflow
- [ ] **Documentation Standards** - How to document validation results
- [ ] **Error Handling** - What to do when validation fails

**Why This Matters**: This is the final validation task for Phase 1. The guidelines tell you:
- ✅ How to comprehensively test services
- ✅ What tests are required
- ✅ How to document test results
- ✅ When tests pass vs fail
- ✅ What to do if validation fails

**Estimated Time**: 10 minutes to read the relevant sections

### 2. Project Context (MUST READ AFTER GUIDELINES)
**Location**: `C:\ClaudeDesktop_Projects\Trade2026\docs\deployment\DOCKER_COMPOSE_GUIDE.md`
- [ ] Read Docker Compose usage guide (created in Task 04)

**Estimated Time**: 5 minutes

---

## ⚠️ CONSEQUENCES OF NOT READING GUIDELINES

If you skip reading MASTER_GUIDELINES.md, you will:
- ❌ Not know what tests are required
- ❌ Skip critical validation steps
- ❌ Not document results properly
- ❌ Miss failing services
- ❌ Pass Phase 1 with broken infrastructure

**The guidelines exist to prevent failures. READ THEM FIRST.**

---

## ✅ CHECKLIST BEFORE PROCEEDING

**I confirm I have read and understood**:
- [ ] MASTER_GUIDELINES.md - New Session Startup Protocol
- [ ] MASTER_GUIDELINES.md - Core Development Rules
- [ ] MASTER_GUIDELINES.md - Testing & Validation Rules
- [ ] MASTER_GUIDELINES.md - 6-Phase Mandatory Workflow
- [ ] MASTER_GUIDELINES.md - Documentation Standards
- [ ] MASTER_GUIDELINES.md - Error Handling
- [ ] DOCKER_COMPOSE_GUIDE.md - How to operate services

**Total Reading Time**: ~15 minutes

**Only proceed to next section after completing this checklist.**

---

# 🚦 VALIDATION GATE - VERIFY TASKS 01-04

## MANDATORY: Validate ALL Previous Tasks Before Starting

**STOP**: Before starting Task 05 (Final Validation), you MUST verify Tasks 01-04 are complete and working.

### Prerequisites Validation

#### Complete Platform Check
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

echo "===========================================" 
echo "PHASE 1 COMPLETE VALIDATION"
echo "===========================================\n"

echo "Task 01: Directory Structure"
test -d frontend && echo "✅ frontend/" || echo "❌ MISSING"
test -d backend && echo "✅ backend/" || echo "❌ MISSING"
test -d library && echo "✅ library/" || echo "❌ MISSING"
test -d infrastructure && echo "✅ infrastructure/" || echo "❌ MISSING"
test -d data && echo "✅ data/" || echo "❌ MISSING"
test -d config && echo "✅ config/" || echo "❌ MISSING"
test -d secrets && echo "✅ secrets/" || echo "❌ MISSING"
test -d docs && echo "✅ docs/" || echo "❌ MISSING"
test -d tests && echo "✅ tests/" || echo "❌ MISSING"
test -d scripts && echo "✅ scripts/" || echo "❌ MISSING"

echo "\nTask 02: Docker Networks"
docker network ls | grep trade2026-frontend > /dev/null && echo "✅ frontend network" || echo "❌ MISSING"
docker network ls | grep trade2026-lowlatency > /dev/null && echo "✅ lowlatency network" || echo "❌ MISSING"
docker network ls | grep trade2026-backend > /dev/null && echo "✅ backend network" || echo "❌ MISSING"

echo "\nTask 03: Core Services"
HEALTHY_COUNT=$(docker ps --format '{{.Names}}\t{{.Status}}' | grep -E 'nats|valkey|questdb|clickhouse|seaweedfs|opensearch|authn|opa' | grep -i 'up' | wc -l)
if [ "$HEALTHY_COUNT" -eq 8 ]; then
    echo "✅ All 8 core services running"
else
    echo "❌ Only $HEALTHY_COUNT/8 services running - FAILED"
    exit 1
fi

echo "\nTask 04: Docker Compose & Scripts"
test -f infrastructure/docker/docker-compose.yml && echo "✅ Master compose file" || echo "❌ MISSING"
test -f infrastructure/docker/.env && echo "✅ Environment file" || echo "❌ MISSING"
test -f scripts/up.sh && echo "✅ up.sh script" || echo "❌ MISSING"
test -f scripts/down.sh && echo "✅ down.sh script" || echo "❌ MISSING"
test -f scripts/logs.sh && echo "✅ logs.sh script" || echo "❌ MISSING"
test -f scripts/status.sh && echo "✅ status.sh script" || echo "❌ MISSING"
test -f docs/deployment/DOCKER_COMPOSE_GUIDE.md && echo "✅ Compose guide" || echo "❌ MISSING"

echo "\n===========================================" 
echo "VALIDATION COMPLETE"
echo "===========================================" 
```

#### Integration Test: Complete Platform Operational
```bash
echo "\nTesting complete platform integration..."

cd C:\ClaudeDesktop_Projects\Trade2026

# Test helper scripts work
echo "Testing helper scripts..."

# Test status script
bash scripts/status.sh > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ status.sh works"
else
    echo "❌ status.sh failed"
    exit 1
fi

# Test compose can manage platform
cd infrastructure/docker

echo "\nTesting compose platform management..."

# Test compose config validates
docker-compose config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Compose config valid"
else
    echo "❌ Compose config invalid"
    exit 1
fi

# Test compose ps works
docker-compose ps > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Compose can query all services"
else
    echo "❌ Compose cannot query services"
    exit 1
fi

# Quick health checks
echo "\nQuick health checks..."
curl -s http://localhost:8222/healthz > /dev/null && echo "✅ NATS" || echo "❌ NATS"
docker exec valkey valkey-cli ping > /dev/null 2>&1 && echo "✅ Valkey" || echo "❌ Valkey"
curl -s http://localhost:9000/ > /dev/null && echo "✅ QuestDB" || echo "❌ QuestDB"
curl -s http://localhost:8123/ping > /dev/null && echo "✅ ClickHouse" || echo "❌ ClickHouse"
curl -s http://localhost:9333/cluster/status > /dev/null && echo "✅ SeaweedFS" || echo "❌ SeaweedFS"
curl -s http://localhost:9200/_cluster/health > /dev/null && echo "✅ OpenSearch" || echo "❌ OpenSearch"
curl -s http://localhost:8114/health > /dev/null && echo "✅ authn" || echo "❌ authn"
curl -s http://localhost:8181/health > /dev/null && echo "✅ OPA" || echo "❌ OPA"

echo "\n✅ Integration validated: Complete platform operational"
```

### Validation Checklist

**Task 01 - Directory Structure**:
- [ ] All 10 top-level directories exist
- [ ] All subdirectories exist
- [ ] DIRECTORY_STRUCTURE.md exists

**Task 02 - Docker Networks**:
- [ ] 3 networks exist (frontend, lowlatency, backend)
- [ ] Correct subnets configured

**Task 03 - Core Services**:
- [ ] docker-compose.core.yml exists
- [ ] 8/8 services running
- [ ] All services healthy

**Task 04 - Docker Compose**:
- [ ] Master compose file exists
- [ ] .env file exists
- [ ] All 4 helper scripts exist (up, down, logs, status)
- [ ] Documentation exists

**Integration - Complete Platform**:
- [ ] Helper scripts work
- [ ] Compose config validates
- [ ] Compose can manage all services
- [ ] All 8 services passing quick health checks
- [ ] No errors in any validation

### Proceed/Stop Decision

**Run the validation scripts above and answer**:

1. Did ALL Task 01 validations pass? (YES/NO): _____
2. Did ALL Task 02 validations pass? (YES/NO): _____
3. Did ALL Task 03 validations pass? (YES/NO): _____
4. Did ALL Task 04 validations pass? (YES/NO): _____
5. Did integration test pass? (YES/NO): _____
6. Are there ANY error messages? (YES/NO): _____

**Can I proceed to Task 05?**
- ✅ **YES** - All validations passed, no errors → Continue to CRITICAL RULES section
- ❌ **NO** - Something failed → STOP, fix issues, re-run validations

**If ANY validation fails**:
1. ❌ **STOP** - Do NOT proceed with Task 05
2. Review error messages from validation scripts
3. Go back to failed task (01, 02, 03, or 04)
4. Fix the issue
5. Re-run validation scripts
6. Only proceed when ALL validations pass

---

**⚠️ CRITICAL**: Do NOT proceed past this point unless all validations above are complete and passing.

---

---

## ⚠️ CRITICAL RULES FOR THIS TASK

### Rule 1: Test Everything
Every service must pass health checks before Phase 1 is complete.

### Rule 2: Document Results
Record all validation results for future reference.

### Rule 3: Fix Before Proceeding
If any service fails, fix it before moving to Phase 2.

### Rule 4: COMPREHENSIVE TESTING - NO SHORTCUTS

**⚠️ MANDATORY**: All testing must be COMPLETE and COMPREHENSIVE. This is the final Phase 1 validation - no shortcuts allowed.

#### What This Means:

**✅ DO** - Complete Testing:
- Test ALL 8 services (not just critical ones)
- Run ALL test types (component, integration, performance, persistence, network)
- Document ALL results (not just pass/fail)
- Validate ALL acceptance criteria (not just key points)
- Create COMPLETE validation report (not summary)

**❌ DON'T** - Shortcuts/Abbreviated:
- "Quick" health checks that skip details
- "Basic" testing that skips edge cases
- "Simple" validation that skips comprehensive checks
- "Brief" documentation that skips test details
- "Fast" testing to save time

#### Specific Requirements:

**Service Testing** (For Each of 8 Services):
1. Component Test: Service works individually
2. Integration Test: Service works with dependencies
3. Performance Test: Latency/throughput acceptable
4. Persistence Test: Data survives restart
5. Network Test: Can communicate with other services

**Platform Testing** (Complete System):
1. All services running simultaneously
2. Cross-service communication working
3. Docker DNS resolution working
4. Compose can manage all services
5. Helper scripts all functional

**Documentation**:
- Complete PHASE1_VALIDATION_REPORT.md
- All test results with specific values
- All services with detailed status
- All issues encountered (if any)
- Recommendations for Phase 2

**Acceptance**:
- Every acceptance criterion validated
- Every checkbox confirmed
- Every service confirmed healthy
- No errors or warnings
- Complete confidence in foundation

---

## 📋 OBJECTIVE

Comprehensively validate that all 8 core infrastructure services are:
1. Running correctly
2. Healthy and responding
3. Communicating properly
4. Ready for application services

**Why This Matters**: Phase 2 (backend services) depends on solid infrastructure. Problems now cascade later.

---

## 🎯 CONTEXT

### What We're Validating

| Service | Key Tests | Expected Result |
|---------|-----------|-----------------|
| NATS | Pub/sub, JetStream | Messages flow, persistence works |
| Valkey | Read/write, persistence | Data stored and retrieved |
| QuestDB | SQL queries, ingestion | Time-series data works |
| ClickHouse | SQL queries, tables | Analytics queries work |
| SeaweedFS | S3 operations | Object storage works |
| OpenSearch | Index, search | Full-text search works |
| authn | JWT generation | Token issuance works |
| OPA | Policy evaluation | Authorization works |

---

## ✅ REQUIREMENTS

### Functional Requirements
1. All services respond to health checks
2. All services perform basic operations
3. Services can communicate with each other
4. Data persists across restarts

### Non-Functional Requirements
- **Completeness**: Test all critical functions
- **Reliability**: Tests are repeatable
- **Documentation**: Results recorded

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: Environment Check
**Goal**: Verify all services are running

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Check service status
bash scripts/status.sh

# Should show 8/8 healthy services
```

**If Any Service Unhealthy**:
```bash
# Check logs
bash scripts/logs.sh <service_name>

# Fix issue before proceeding
# Common fixes:
# - Wait 30-60 seconds (some services slow to start)
# - Restart service: docker-compose restart <service_name>
# - Check ports: netstat -ano | findstr :<port>
```

**Checklist**:
- [ ] All 8 services running
- [ ] All health checks passing
- [ ] No error messages in logs
- [ ] **Phase 1 complete: Environment ready** ✅

---

### Step 2: Validate NATS (Message Bus)
**Goal**: Test pub/sub and JetStream persistence

**Test 1: Basic Connectivity**
```bash
# Check NATS server info
curl http://localhost:8222/varz | jq .

# Should show server info, version, connections
```

**Test 2: Publish/Subscribe**
```bash
# Install nats CLI (if not already)
# Download from: https://github.com/nats-io/natscli/releases

# Subscribe to test subject (in one terminal)
nats sub test.subject

# Publish message (in another terminal)
nats pub test.subject "Hello Trade2026"

# Expected: Message received by subscriber
```

**Test 3: JetStream Persistence**
```bash
# Check JetStream status
curl http://localhost:8222/jsz | jq .

# Expected: JetStream enabled, storage path configured
# Look for: "config": { "store_dir": "/data" }
```

**Test 4: Create Stream**
```bash
# Create test stream
nats stream add TEST_STREAM \
  --subjects "test.>" \
  --storage file \
  --retention limits \
  --max-msgs 1000

# Publish to stream
nats pub test.example "Test message 1"
nats pub test.example "Test message 2"

# Verify messages stored
nats stream info TEST_STREAM

# Expected: Shows 2 messages stored

# Cleanup
nats stream rm TEST_STREAM -f
```

**Validation Checklist**:
- [ ] NATS server responding
- [ ] Pub/sub working
- [ ] JetStream enabled
- [ ] Stream persistence working
- [ ] **Phase 2 complete: NATS validated** ✅

---

### Step 3: Validate Valkey (Cache)
**Goal**: Test read/write operations and persistence

**Test 1: Basic Operations**
```bash
# Set value
docker exec valkey valkey-cli set trade2026:test "validation_value"

# Get value
docker exec valkey valkey-cli get trade2026:test
# Expected: "validation_value"

# Delete value
docker exec valkey valkey-cli del trade2026:test
```

**Test 2: Data Types**
```bash
# String
docker exec valkey valkey-cli set mykey "Hello"

# Hash
docker exec valkey valkey-cli hset user:1 name "Alice" age 30

# List
docker exec valkey valkey-cli lpush mylist "item1" "item2"

# Set
docker exec valkey valkey-cli sadd myset "member1" "member2"

# Retrieve
docker exec valkey valkey-cli get mykey
docker exec valkey valkey-cli hgetall user:1
docker exec valkey valkey-cli lrange mylist 0 -1
docker exec valkey valkey-cli smembers myset
```

**Test 3: Persistence**
```bash
# Set value
docker exec valkey valkey-cli set persist:test "persistent_data"

# Check AOF is enabled
docker exec valkey valkey-cli config get appendonly
# Expected: appendonly yes

# Restart container
docker restart valkey
sleep 10

# Check value persisted
docker exec valkey valkey-cli get persist:test
# Expected: "persistent_data"

# Cleanup
docker exec valkey valkey-cli del persist:test
```

**Test 4: Memory & Performance**
```bash
# Check memory usage
docker exec valkey valkey-cli info memory | grep used_memory_human

# Check performance
docker exec valkey valkey-cli --latency
# Press Ctrl+C after a few seconds
# Expected: Latency < 1ms
```

**Validation Checklist**:
- [ ] Basic read/write working
- [ ] All data types supported
- [ ] Persistence working (survives restart)
- [ ] Latency acceptable (< 1ms)
- [ ] **Phase 3 complete: Valkey validated** ✅

---

### Step 4: Validate QuestDB (Time-Series)
**Goal**: Test SQL queries and data ingestion

**Test 1: HTTP API**
```bash
# Simple query
curl -G --data-urlencode "query=SELECT 1" http://localhost:9000/exec | jq .

# Expected: {"query":"SELECT 1","columns":[...],"dataset":[[1]],...}
```

**Test 2: Create Table**
```bash
# Create test table
curl -G --data-urlencode "query=CREATE TABLE test_ticks (
  timestamp TIMESTAMP,
  symbol SYMBOL,
  price DOUBLE,
  qty DOUBLE
) TIMESTAMP(timestamp) PARTITION BY DAY" http://localhost:9000/exec | jq .

# Expected: {"ddl":"OK"}
```

**Test 3: Insert Data**
```bash
# Insert test data
curl -G --data-urlencode "query=INSERT INTO test_ticks VALUES(
  systimestamp(),
  'BTCUSDT',
  45000.0,
  0.5
)" http://localhost:9000/exec | jq .

# Insert more data
curl -G --data-urlencode "query=INSERT INTO test_ticks VALUES(
  systimestamp(),
  'ETHUSDT',
  3000.0,
  1.2
)" http://localhost:9000/exec | jq .
```

**Test 4: Query Data**
```bash
# Query inserted data
curl -G --data-urlencode "query=SELECT * FROM test_ticks" http://localhost:9000/exec | jq .

# Expected: 2 rows returned

# Aggregation query
curl -G --data-urlencode "query=SELECT symbol, avg(price) as avg_price FROM test_ticks GROUP BY symbol" http://localhost:9000/exec | jq .
```

**Test 5: Performance**
```bash
# Insert 1000 rows for performance test
for i in {1..1000}; do
  curl -G --data-urlencode "query=INSERT INTO test_ticks VALUES(systimestamp(), 'TEST', $((45000 + RANDOM % 1000)), 0.1)" http://localhost:9000/exec > /dev/null 2>&1
done

# Query performance
time curl -G --data-urlencode "query=SELECT count(*) FROM test_ticks" http://localhost:9000/exec

# Expected: < 100ms
```

**Test 6: Cleanup**
```bash
# Drop test table
curl -G --data-urlencode "query=DROP TABLE test_ticks" http://localhost:9000/exec | jq .
```

**Validation Checklist**:
- [ ] HTTP API responding
- [ ] Can create tables
- [ ] Can insert data
- [ ] Can query data
- [ ] Aggregations work
- [ ] Performance acceptable
- [ ] **Phase 4 complete: QuestDB validated** ✅

---

### Step 5: Validate ClickHouse (Analytics)
**Goal**: Test SQL queries and OLAP operations

**Test 1: Basic Connectivity**
```bash
# Ping
curl http://localhost:8123/ping
# Expected: Ok.

# Version
echo "SELECT version()" | curl -s "http://localhost:8123/" --data-binary @-
# Expected: Version number (e.g., 24.9.1.1)
```

**Test 2: Create Database**
```bash
echo "CREATE DATABASE IF NOT EXISTS trade2026" | curl -s "http://localhost:8123/" --data-binary @-

# Verify
echo "SHOW DATABASES" | curl -s "http://localhost:8123/" --data-binary @-
# Expected: List includes trade2026
```

**Test 3: Create Table**
```bash
echo "CREATE TABLE IF NOT EXISTS trade2026.test_ohlcv (
  timestamp DateTime,
  symbol String,
  open Float64,
  high Float64,
  low Float64,
  close Float64,
  volume Float64
) ENGINE = MergeTree()
ORDER BY (symbol, timestamp)" | curl -s "http://localhost:8123/" --data-binary @-
```

**Test 4: Insert Data**
```bash
echo "INSERT INTO trade2026.test_ohlcv VALUES 
('2025-10-14 10:00:00', 'BTCUSDT', 45000, 45100, 44900, 45050, 100.5),
('2025-10-14 10:01:00', 'BTCUSDT', 45050, 45150, 45000, 45100, 95.3),
('2025-10-14 10:00:00', 'ETHUSDT', 3000, 3010, 2990, 3005, 50.2)" | curl -s "http://localhost:8123/" --data-binary @-
```

**Test 5: Query Data**
```bash
# Simple query
echo "SELECT * FROM trade2026.test_ohlcv LIMIT 3" | curl -s "http://localhost:8123/" --data-binary @-

# Aggregation
echo "SELECT symbol, avg(close) as avg_price FROM trade2026.test_ohlcv GROUP BY symbol" | curl -s "http://localhost:8123/" --data-binary @-

# Time-series aggregation
echo "SELECT 
  symbol,
  max(high) as high,
  min(low) as low,
  last_value(close) as close
FROM trade2026.test_ohlcv 
GROUP BY symbol" | curl -s "http://localhost:8123/" --data-binary @-
```

**Test 6: Performance**
```bash
# Insert 10K rows
echo "INSERT INTO trade2026.test_ohlcv 
SELECT 
  now() - INTERVAL number SECOND as timestamp,
  'BTCUSDT' as symbol,
  45000 + (rand() % 1000) as open,
  45000 + (rand() % 1000) as high,
  45000 - (rand() % 1000) as low,
  45000 + (rand() % 500) as close,
  rand() % 100 as volume
FROM numbers(10000)" | curl -s "http://localhost:8123/" --data-binary @-

# Query performance
time echo "SELECT count(*) FROM trade2026.test_ohlcv" | curl -s "http://localhost:8123/" --data-binary @-
# Expected: < 100ms
```

**Test 7: Cleanup**
```bash
echo "DROP TABLE trade2026.test_ohlcv" | curl -s "http://localhost:8123/" --data-binary @-
```

**Validation Checklist**:
- [ ] ClickHouse responding
- [ ] Database created
- [ ] Tables created
- [ ] Data inserted
- [ ] Queries working
- [ ] Aggregations fast
- [ ] **Phase 5 complete: ClickHouse validated** ✅

---

### Step 6: Validate Remaining Services
**Goal**: Quick validation of SeaweedFS, OpenSearch, authn, OPA

**SeaweedFS (S3 Storage)**
```bash
# Check cluster status
curl http://localhost:9333/cluster/status | jq .
# Expected: Cluster healthy

# Note: Full S3 testing requires awscli
# Basic validation is cluster status
```

**OpenSearch (Search Engine)**
```bash
# Cluster health
curl http://localhost:9200/_cluster/health | jq .
# Expected: status "green" or "yellow"

# Create test index
curl -X PUT http://localhost:9200/test_index

# Index document
curl -X POST http://localhost:9200/test_index/_doc/1 \
  -H 'Content-Type: application/json' \
  -d '{"title": "Test Doc", "content": "Trade2026 validation"}'

# Search
curl "http://localhost:9200/test_index/_search?q=Trade2026" | jq .
# Expected: Document found

# Cleanup
curl -X DELETE http://localhost:9200/test_index
```

**authn (Authentication)**
```bash
# Health check
curl http://localhost:8114/health | jq .
# Expected: {"status": "healthy"}

# Get JWKS
curl http://localhost:8114/.well-known/jwks.json | jq .
# Expected: JSON with public keys

# Request token (requires client credentials in secrets)
# This may fail if secrets not configured - that's OK for Phase 1
```

**OPA (Authorization)**
```bash
# Health check
curl http://localhost:8181/health
# Expected: {}

# Test policy (should always allow for basic policy)
curl -X POST http://localhost:8181/v1/data/example/allow | jq .
# Expected: {"result": true}
```

**Validation Checklist**:
- [ ] SeaweedFS cluster healthy
- [ ] OpenSearch can index/search
- [ ] authn health check passes
- [ ] OPA policy evaluation works
- [ ] **Phase 6 complete: All services validated** ✅

---

### Step 7: Test Service Communication
**Goal**: Verify services can communicate via Docker DNS

**Test Inter-Service DNS**
```bash
# Test NATS → Valkey
docker exec nats ping -c 3 valkey
# Expected: 3 successful pings

# Test QuestDB → ClickHouse
docker exec questdb ping -c 3 clickhouse
# Expected: 3 successful pings

# Test authn → OPA
docker exec authn ping -c 3 opa
# Expected: 3 successful pings
```

**Test Cross-Network Communication**
```bash
# authn is on frontend + backend networks
# Should reach both valkey (backend) and opa (frontend)

docker exec authn ping -c 3 valkey
# Expected: Success

docker exec authn ping -c 3 opa
# Expected: Success
```

**Validation Checklist**:
- [ ] Services resolve each other by name
- [ ] Ping successful between services
- [ ] Cross-network communication works
- [ ] **Phase 7 complete: Communication validated** ✅

---

### Step 8: Document Validation Results
**Goal**: Record all validation results

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\docs

# Create validation report
cat > PHASE1_VALIDATION_REPORT.md << 'EOF'
# Phase 1 Validation Report

**Date**: 2025-10-14
**Phase**: 1 - Foundation
**Status**: ✅ Complete

---

## Services Validated

### Core Infrastructure (8/8)

| Service | Status | Health | Tests | Notes |
|---------|--------|--------|-------|-------|
| NATS | ✅ Pass | Healthy | Pub/sub, JetStream | All tests pass |
| Valkey | ✅ Pass | Healthy | Read/write, persistence | Latency < 1ms |
| QuestDB | ✅ Pass | Healthy | SQL, ingestion | Performance good |
| ClickHouse | ✅ Pass | Healthy | OLAP queries | Fast aggregations |
| SeaweedFS | ✅ Pass | Healthy | Cluster status | S3 API ready |
| OpenSearch | ✅ Pass | Healthy | Index, search | Full-text working |
| authn | ✅ Pass | Healthy | JWT generation | Token issuance OK |
| OPA | ✅ Pass | Healthy | Policy evaluation | Authorization OK |

---

## Test Results

### NATS
- ✅ Server responding on port 4222
- ✅ Monitoring API on port 8222
- ✅ JetStream enabled
- ✅ Pub/sub functional
- ✅ Stream persistence working

### Valkey
- ✅ Redis protocol on port 6379
- ✅ All data types supported
- ✅ AOF persistence enabled
- ✅ Data survives restart
- ✅ Latency < 1ms

### QuestDB
- ✅ HTTP API on port 9000
- ✅ Postgres wire on port 8812
- ✅ Table creation works
- ✅ Data ingestion works
- ✅ Queries performant

### ClickHouse
- ✅ HTTP API on port 8123
- ✅ Native TCP on port 9000
- ✅ Database created
- ✅ Tables created
- ✅ Aggregations fast

### SeaweedFS
- ✅ S3 API on port 8333
- ✅ Master on port 9333
- ✅ Cluster healthy
- ✅ Ready for object storage

### OpenSearch
- ✅ REST API on port 9200
- ✅ Cluster healthy
- ✅ Can create indices
- ✅ Can search documents

### authn
- ✅ API on port 8114
- ✅ Health endpoint OK
- ✅ JWKS endpoint OK
- ✅ Ready for authentication

### OPA
- ✅ API on port 8181
- ✅ Health endpoint OK
- ✅ Policy evaluation OK
- ✅ Ready for authorization

---

## Network Validation

### Networks Created
- ✅ trade2026-frontend (172.23.0.0/16)
- ✅ trade2026-lowlatency (172.22.0.0/16)
- ✅ trade2026-backend (172.21.0.0/16)

### Service Communication
- ✅ Docker DNS resolution working
- ✅ Intra-network communication OK
- ✅ Cross-network communication OK (multi-network services)

---

## Configuration Validation

### Docker Compose
- ✅ Master compose file created
- ✅ Modular files included
- ✅ All services start with single command
- ✅ Environment variables configured

### Helper Scripts
- ✅ up.sh works
- ✅ down.sh works
- ✅ logs.sh works
- ✅ status.sh works

---

## Data Persistence

### Volume Mounts
- ✅ data/nats/ - NATS JetStream
- ✅ data/valkey/ - Cache data
- ✅ data/questdb/ - Time-series data
- ✅ data/clickhouse/ - Analytics data
- ✅ data/seaweed/ - Object storage
- ✅ data/opensearch/ - Search index

### Persistence Tests
- ✅ Data survives container restart
- ✅ Data in correct directories
- ✅ No data loss observed

---

## Performance Metrics

| Service | Metric | Result |
|---------|--------|--------|
| Valkey | Latency | < 1ms |
| QuestDB | Query time | < 100ms |
| ClickHouse | Query time | < 100ms |
| NATS | Throughput | Not measured (baseline OK) |

---

## Issues Encountered

### None

All services started and validated successfully on first attempt.

---

## Recommendations

### For Phase 2 (Backend Migration)
1. Use same validation approach for each service
2. Test services individually before integration
3. Document any custom configurations

### For Production
1. Enable security (TLS, authentication)
2. Set resource limits (memory, CPU)
3. Configure monitoring (Prometheus, Grafana)
4. Setup backups for data volumes

---

## Sign-Off

**Phase 1 Status**: ✅ COMPLETE

**Ready for Phase 2**: ✅ YES

**Date Validated**: 2025-10-14

**Validated By**: Claude Code

---
EOF
```

**Checklist**:
- [ ] Validation report created
- [ ] All test results documented
- [ ] Issues noted (if any)
- [ ] Recommendations included
- [ ] **Phase 8 complete: Documentation done** ✅

---

## ✅ ACCEPTANCE CRITERIA

The task is complete when ALL of the following are true:

### All Services Validated
- [ ] NATS: Pub/sub + JetStream working
- [ ] Valkey: Read/write + persistence working
- [ ] QuestDB: SQL queries + ingestion working
- [ ] ClickHouse: OLAP queries working
- [ ] SeaweedFS: Cluster healthy
- [ ] OpenSearch: Index + search working
- [ ] authn: Health check passing
- [ ] OPA: Policy evaluation working

### Communication Validated
- [ ] Docker DNS resolution working
- [ ] Services can ping each other
- [ ] Cross-network communication OK

### Documentation Complete
- [ ] PHASE1_VALIDATION_REPORT.md created
- [ ] All test results recorded
- [ ] Issues documented (if any)

### Ready for Phase 2
- [ ] All 8/8 services healthy
- [ ] No blocking issues
- [ ] Confidence in foundation

---

## 🔄 ROLLBACK PLAN

Not applicable for validation task. If issues found, fix them before completing Phase 1.

---

## 📝 NOTES FOR CLAUDE CODE

### Key Points
- This is the final Phase 1 task
- Every service must pass validation
- Document everything
- Don't proceed to Phase 2 if anything fails

### Common Issues

**Issue 1: Services slow to start**
**Solution**: Wait 30-60 seconds for health checks, especially OpenSearch

**Issue 2: Can't connect to service**
**Solution**: Check service is running (`docker ps`), check logs

**Issue 3: DNS resolution fails**
**Solution**: Verify networks created, services on correct networks

### Time Estimate
- Optimistic: 30 minutes
- Realistic: 1 hour
- Pessimistic: 2 hours (if troubleshooting needed)

---

## 📊 SUCCESS METRICS

After completion:
- ✅ 8/8 services validated
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Phase 1 COMPLETE
- ✅ Ready for Phase 2 (Backend Migration)

---

**Status**: ⏳ Pending

**Next Phase**: Phase 2 - Backend Migration

**Last Updated**: 2025-10-14
