# Phase 2 Task 02: Migrate Priority 1 Services

**Task**: 02 of 6
**Services**: normalizer, sink-ticks, sink-alt
**Priority**: P1 (Foundation - No Dependencies)
**Estimated Time**: 8 hours
**Status**: ⏳ IN PROGRESS

---

# 🛑 MANDATORY VALIDATION GATE

## Prerequisites Check

Before starting, verify:

- [x] Phase 1 complete (all infrastructure services running)
- [x] Phase 2 Task 01 complete (services surveyed)
- [x] BACKEND_SERVICES_INVENTORY.md reviewed
- [x] Core infrastructure healthy:
  - [x] NATS running on port 4222
  - [x] Valkey running on port 6379
  - [x] QuestDB running on port 9000
  - [x] SeaweedFS running on port 8333
  - [x] OpenSearch running on port 9200

**Decision**: All prerequisites met? ✅ YES → Proceed

---

# 📋 TASK OVERVIEW

## Services to Migrate

| Service | Port | Est. Time | Complexity | Dependencies |
|---------|------|-----------|------------|--------------|
| normalizer | 8081 | 2h | Simple | NATS, Valkey, QuestDB |
| sink-ticks | 8111 | 3h | Medium | NATS, SeaweedFS |
| sink-alt | 8112 | 3h | Medium | NATS, SeaweedFS, OpenSearch |

**Total**: 8 hours

## Why Priority 1?

- No dependencies on other application services
- Only depend on core infrastructure (already migrated)
- Foundation for entire data pipeline
- Can be migrated in parallel
- Lowest risk services

---

# 🔧 SERVICE 1: NORMALIZER

## Service Information

**Purpose**: Convert raw ticks → OHLCV bars (1m, 5m, 15m, 1h, 1d)

**Source Location**: `C:\Trade2025\trading\apps\normalizer\`

**Target Location**: `C:\ClaudeDesktop_Projects\Trade2026\backend\apps\normalizer\`

**Port**: 8081

**Networks**: lowlatency, backend

**Dependencies**:
- NATS (ticks.> subscription, ohlcv.* publishing)
- Valkey (bar caching)
- QuestDB (bar persistence)

---

## Step 1: Copy Service Code

### Actions

```bash
# Navigate to Trade2026
cd C:\ClaudeDesktop_Projects\Trade2026

# Create service directory
mkdir -p backend\apps\normalizer

# Copy all source code from Trade2025
# MANUAL STEP: Copy the following from C:\Trade2025\trading\apps\normalizer\
# to C:\ClaudeDesktop_Projects\Trade2026\backend\apps\normalizer\
#
# Files to copy:
# - service.py (or main.py)
# - requirements.txt
# - Dockerfile
# - config.yaml (if exists)
# - Any other Python files
# - tests/ directory (if exists)
```

**Checklist**:
- [ ] Service directory created
- [ ] All Python source files copied
- [ ] requirements.txt copied
- [ ] Dockerfile copied
- [ ] Config files identified

---

## Step 2: Create Configuration

### Config File: config/backend/normalizer/config.yaml

```yaml
# Normalizer Configuration - Trade2026
service:
  name: "normalizer"
  port: 8081
  log_level: "INFO"
  workers: 1

nats:
  url: "nats://nats:4222"
  subscribe_subjects:
    - "ticks.>"
  publish_subject_prefix: "ohlcv"
  max_reconnect_attempts: 10
  reconnect_wait_sec: 2

valkey:
  url: "redis://valkey:6379"
  db: 1
  max_connections: 10
  cache_ttl_sec: 3600

questdb:
  http_url: "http://questdb:9000"
  pg_url: "postgresql://admin:quest@questdb:8812/qdb"
  batch_size: 1000
  flush_interval_sec: 10

intervals:
  - "1m"
  - "5m"
  - "15m"
  - "1h"
  - "1d"

aggregation:
  flush_on_close: true
  bar_timeout_sec: 60
  
performance:
  max_ticks_per_sec: 100000
  batch_size: 5000
```

**Checklist**:
- [ ] Config file created
- [ ] All URLs use Docker service names (NOT localhost)
- [ ] All settings appropriate for Trade2026

---

## Step 3: Update Service Code

### Critical Changes Required

**1. Configuration Path Updates**

```python
# OLD (Trade2025)
config_path = "config.yaml"
config_path = "C:/Trade2025/trading/apps/normalizer/config.yaml"

# NEW (Trade2026)
config_path = "/app/config/config.yaml"
# Will be mounted from: C:\ClaudeDesktop_Projects\Trade2026\config\backend\normalizer\config.yaml
```

**2. URL Updates (CRITICAL)**

```python
# OLD (Trade2025) - WRONG
nats_url = "nats://localhost:4222"
valkey_url = "redis://localhost:6379"
questdb_url = "http://localhost:9000"

# NEW (Trade2026) - CORRECT
nats_url = "nats://nats:4222"
valkey_url = "redis://valkey:6379"
questdb_url = "http://questdb:9000"
```

**3. Logging Configuration**

```python
# Ensure structured logging
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
```

**Checklist**:
- [ ] All localhost references replaced with service names
- [ ] Configuration loading updated
- [ ] Logging configured
- [ ] Code review complete

---

## Step 4: Create/Update Dockerfile

### Dockerfile: backend/apps/normalizer/Dockerfile

```dockerfile
# Normalizer Service - Trade2026
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8081/health || exit 1

# Expose port
EXPOSE 8081

# Run service
CMD ["python", "service.py"]
```

**Checklist**:
- [ ] Dockerfile created/updated
- [ ] Base image appropriate (python:3.11-slim)
- [ ] Health check configured
- [ ] Port exposed

---

## Step 5: Build Docker Image

### Build Command

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\backend\apps\normalizer

# Build image
docker build -t localhost/normalizer:latest .

# Verify build
docker images | grep normalizer
```

**Expected Output**:
```
localhost/normalizer   latest   abc123def456   2 minutes ago   350MB
```

**Checklist**:
- [ ] Image builds successfully
- [ ] No build errors
- [ ] Image tagged correctly
- [ ] Image size reasonable (<500MB)

---

## Step 6: Add to Docker Compose

### File: infrastructure/docker/docker-compose.apps.yml

```yaml
version: '3.8'

# Trade2026 Application Services
# Phase 2: Backend Migration

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
  # ============================================
  # Normalizer - Data Normalization Service
  # Priority 1 - Foundation Service
  # ============================================
  normalizer:
    image: localhost/normalizer:latest
    container_name: normalizer
    build:
      context: ../../backend/apps/normalizer
      dockerfile: Dockerfile
    ports:
      - "8081:8081"
    volumes:
      - ../../config/backend/normalizer:/app/config:ro
    networks:
      - lowlatency
      - backend
    environment:
      - CONFIG_PATH=/app/config/config.yaml
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    depends_on:
      - nats
      - valkey
      - questdb
    labels:
      - "com.trade2026.service=normalizer"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=application"
      - "com.trade2026.priority=P1"
      - "com.trade2026.network.lane=lowlatency,backend"
```

**Checklist**:
- [ ] Service added to docker-compose.apps.yml
- [ ] Networks configured (lowlatency, backend)
- [ ] Volumes mounted correctly
- [ ] Health check configured
- [ ] Dependencies declared
- [ ] Labels applied

---

## Step 7: Component Testing

### Test 1: Service Starts Successfully

```bash
# Start just normalizer (with dependencies)
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker
docker-compose -f docker-compose.apps.yml up -d normalizer

# Check logs
docker logs normalizer --tail 50

# Expected: Service starts, connects to NATS/Valkey/QuestDB
```

**Success Criteria**:
- [ ] Container starts
- [ ] No crash loops
- [ ] Health check passes
- [ ] Logs show successful connections

### Test 2: Mock Tick Processing

```python
# Test script: backend/apps/normalizer/tests/test_component.py
import asyncio
import json
from nats.aio.client import Client as NATS

async def test_normalizer():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    # Publish mock tick
    tick = {
        "timestamp": 1697292000000,
        "exchange": "binance",
        "symbol": "BTCUSDT",
        "price": 45000.0,
        "qty": 0.5,
        "side": "buy",
        "trade_id": 123456
    }
    
    await nc.publish("ticks.binance.BTCUSDT", json.dumps(tick).encode())
    
    # Subscribe to bar output
    async def bar_handler(msg):
        bar = json.loads(msg.data)
        print(f"Received bar: {bar}")
    
    await nc.subscribe("ohlcv.1m.BTCUSDT", cb=bar_handler)
    
    await asyncio.sleep(65)  # Wait for bar close
    await nc.close()

# Run test
asyncio.run(test_normalizer())
```

**Success Criteria**:
- [ ] Tick is consumed
- [ ] Bar is generated after 1 minute
- [ ] Bar published to NATS
- [ ] Bar contains OHLCV data

### Test 3: Database Writes

```sql
-- Check QuestDB for bars
SELECT * FROM ohlcv_1m 
WHERE symbol = 'BTCUSDT' 
ORDER BY timestamp DESC 
LIMIT 10;
```

**Success Criteria**:
- [ ] Bars written to QuestDB
- [ ] Timestamp correct
- [ ] OHLCV values correct

### Test 4: Cache Verification

```bash
# Check Valkey cache
docker exec -it valkey valkey-cli

# In valkey-cli:
SELECT 1
KEYS bars:1m:*
GET bars:1m:BTCUSDT
```

**Success Criteria**:
- [ ] Bars cached in Valkey
- [ ] Cache contains recent bars
- [ ] TTL configured correctly

---

## Step 8: Integration Testing

### Test 1: End-to-End Flow

```bash
# Ensure all dependencies running
docker-compose -f docker-compose.core.yml ps
docker-compose -f docker-compose.apps.yml ps

# All should be healthy
```

### Test 2: Performance Test

```python
# Load test: backend/apps/normalizer/tests/test_performance.py
import asyncio
import json
import time
from nats.aio.client import Client as NATS

async def load_test():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    start = time.time()
    count = 100000  # 100k ticks
    
    for i in range(count):
        tick = {
            "timestamp": int(time.time() * 1000),
            "exchange": "binance",
            "symbol": "BTCUSDT",
            "price": 45000.0 + (i % 100),
            "qty": 0.5,
            "side": "buy" if i % 2 == 0 else "sell",
            "trade_id": i
        }
        await nc.publish("ticks.binance.BTCUSDT", json.dumps(tick).encode())
    
    elapsed = time.time() - start
    print(f"Published {count} ticks in {elapsed:.2f}s")
    print(f"Throughput: {count/elapsed:.0f} ticks/sec")
    
    await nc.close()

asyncio.run(load_test())
```

**Success Criteria**:
- [ ] Processes 100k ticks successfully
- [ ] Throughput ≥ 100k ticks/sec (target)
- [ ] P50 latency < 5ms
- [ ] No errors or crashes
- [ ] Memory usage stable

---

## Step 9: Validation

### Validation Checklist

**Functionality**:
- [ ] Service starts successfully
- [ ] Connects to NATS, Valkey, QuestDB
- [ ] Consumes ticks from NATS
- [ ] Generates 1m, 5m, 15m, 1h, 1d bars
- [ ] Publishes bars to NATS
- [ ] Writes bars to QuestDB
- [ ] Caches bars in Valkey

**Performance**:
- [ ] Throughput: ≥ 100k ticks/sec
- [ ] Latency: P50 < 5ms, P99 < 20ms
- [ ] Memory: < 500MB
- [ ] CPU: < 50% (single core)

**Reliability**:
- [ ] No crashes during load test
- [ ] Handles NATS reconnections
- [ ] Handles QuestDB write failures
- [ ] Graceful shutdown

**Monitoring**:
- [ ] Health endpoint responds
- [ ] Logs are structured
- [ ] Metrics exposed (if applicable)

### Validation Result: ⏸️ PENDING

---

## Step 10: Documentation

### Update Files

**1. COMPLETION_TRACKER.md**
- [ ] Mark normalizer as complete
- [ ] Update Phase 2 progress

**2. SERVICE_STATUS.md** (create if needed)
- [ ] Document normalizer status
- [ ] Record any issues encountered
- [ ] Note performance metrics

---

# 🔧 SERVICE 2: SINK-TICKS

## Service Information

**Purpose**: Write ticks to Delta Lake on S3 for long-term storage

**Source Location**: `C:\Trade2025\trading\apps\sink_ticks\`

**Target Location**: `C:\ClaudeDesktop_Projects\Trade2026\backend\apps\sink_ticks\`

**Port**: 8111 (health), 9111 (metrics)

**Networks**: lowlatency, backend

**Dependencies**:
- NATS (ticks.> subscription)
- SeaweedFS (S3-compatible storage)

---

## Step 1: Copy Service Code

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

mkdir -p backend\apps\sink_ticks

# MANUAL: Copy all files from C:\Trade2025\trading\apps\sink_ticks\
# to C:\ClaudeDesktop_Projects\Trade2026\backend\apps\sink_ticks\
```

**Checklist**:
- [ ] Service directory created
- [ ] All source files copied
- [ ] requirements.txt copied
- [ ] Dockerfile copied

---

## Step 2: Create Configuration

### Config File: config/backend/sink_ticks/config.yaml

```yaml
# Sink-Ticks Configuration - Trade2026
service:
  name: "sink-ticks"
  port: 8111
  metrics_port: 9111
  log_level: "INFO"

nats:
  url: "nats://nats:4222"
  subscribe_subject: "ticks.>"
  queue_group: "sink-ticks-workers"
  max_reconnect_attempts: 10

s3:
  endpoint_url: "http://seaweedfs:8333"
  access_key: "test"
  secret_key: "test"
  bucket: "trader2026"
  prefix: "lake/ticks/"
  region: "us-east-1"

delta_lake:
  partition_by: "dt"  # Date partition (YYYY-MM-DD)
  schema:
    - name: "timestamp"
      type: "timestamp"
    - name: "exchange"
      type: "string"
    - name: "symbol"
      type: "string"
    - name: "price"
      type: "double"
    - name: "qty"
      type: "double"
    - name: "side"
      type: "string"
    - name: "trade_id"
      type: "long"
    - name: "dt"
      type: "string"

batching:
  batch_seconds: 10
  max_batch_size: 5000
  flush_on_shutdown: true

performance:
  max_memory_mb: 1024
  compression: "snappy"
```

**Checklist**:
- [ ] Config file created
- [ ] S3 endpoint uses SeaweedFS service name
- [ ] Delta Lake schema defined
- [ ] Batching configured

---

## Step 3: Update Service Code

### Critical Changes

```python
# OLD
s3_endpoint = "http://localhost:8333"
nats_url = "nats://localhost:4222"

# NEW
s3_endpoint = "http://seaweedfs:8333"
nats_url = "nats://nats:4222"
```

**Checklist**:
- [ ] All URLs updated
- [ ] Configuration loading updated
- [ ] Logging configured

---

## Step 4: Create/Update Dockerfile

### Dockerfile: backend/apps/sink_ticks/Dockerfile

```dockerfile
# Sink-Ticks Service - Trade2026
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Delta Lake dependencies
RUN pip install --no-cache-dir \
    delta-spark==2.4.0 \
    pyspark==3.4.0 \
    boto3==1.28.0

# Copy service code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8111/health || exit 1

# Expose ports
EXPOSE 8111 9111

# Run service
CMD ["python", "service.py"]
```

**Checklist**:
- [ ] Dockerfile created
- [ ] Delta Lake dependencies included
- [ ] Health check configured

---

## Step 5: Build Docker Image

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\backend\apps\sink_ticks

docker build -t localhost/sink-ticks:latest .

docker images | grep sink-ticks
```

**Checklist**:
- [ ] Image builds successfully
- [ ] No errors

---

## Step 6: Add to Docker Compose

### Update: infrastructure/docker/docker-compose.apps.yml

```yaml
  # ============================================
  # Sink-Ticks - Data Lake Sink (Ticks)
  # Priority 1 - Foundation Service
  # ============================================
  sink-ticks:
    image: localhost/sink-ticks:latest
    container_name: sink-ticks
    build:
      context: ../../backend/apps/sink_ticks
      dockerfile: Dockerfile
    ports:
      - "8111:8111"
      - "9111:9111"
    volumes:
      - ../../config/backend/sink_ticks:/app/config:ro
    networks:
      - lowlatency
      - backend
    environment:
      - CONFIG_PATH=/app/config/config.yaml
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8111/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    depends_on:
      - nats
      - seaweedfs
    labels:
      - "com.trade2026.service=sink-ticks"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=application"
      - "com.trade2026.priority=P1"
      - "com.trade2026.network.lane=lowlatency,backend"
```

**Checklist**:
- [ ] Service added
- [ ] Networks configured
- [ ] Volumes mounted
- [ ] Dependencies declared

---

## Step 7: Component Testing

### Test 1: Service Starts

```bash
docker-compose -f docker-compose.apps.yml up -d sink-ticks

docker logs sink-ticks --tail 50
```

**Success Criteria**:
- [ ] Container starts
- [ ] Connects to NATS
- [ ] Connects to S3

### Test 2: Write to S3

```python
# Test: Verify tick written to S3
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:8333',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

# List objects
response = s3.list_objects_v2(
    Bucket='trader2026',
    Prefix='lake/ticks/'
)

print(f"Found {response.get('KeyCount', 0)} objects")
for obj in response.get('Contents', []):
    print(f"  {obj['Key']}")
```

**Success Criteria**:
- [ ] Parquet files created in S3
- [ ] Files partitioned by date
- [ ] Delta Lake metadata exists

---

## Step 8: Integration Testing

### Test: End-to-End

```bash
# Publish test ticks
# Verify written to S3
# Verify Delta Lake format
```

**Success Criteria**:
- [ ] Ticks → NATS → Sink → S3 working
- [ ] Batching works correctly
- [ ] Partitioning correct

---

## Step 9: Validation

### Validation Checklist

**Functionality**:
- [ ] Consumes ticks from NATS
- [ ] Batches ticks
- [ ] Writes to S3 as Parquet
- [ ] Creates Delta Lake metadata
- [ ] Partitions by date

**Performance**:
- [ ] Batch writes complete in < 10s
- [ ] Memory < 1GB
- [ ] No data loss

**Reliability**:
- [ ] Handles NATS reconnections
- [ ] Handles S3 failures gracefully
- [ ] Flushes on shutdown

### Validation Result: ⏸️ PENDING

---

# 🔧 SERVICE 3: SINK-ALT

## Service Information

**Purpose**: Write alternative data to Delta Lake + OpenSearch

**Source Location**: `C:\Trade2025\trading\apps\sink_alt\`

**Target Location**: `C:\ClaudeDesktop_Projects\Trade2026\backend\apps\sink_alt\`

**Port**: 8112 (health), 9112 (metrics)

**Networks**: lowlatency, backend

**Dependencies**:
- NATS (alt.norm.> subscription)
- SeaweedFS (S3)
- OpenSearch (dual write)
- Valkey (deduplication)

---

## Step 1: Copy Service Code

```bash
mkdir -p backend\apps\sink_alt

# MANUAL: Copy from C:\Trade2025\trading\apps\sink_alt\
```

**Checklist**:
- [ ] Service directory created
- [ ] Files copied

---

## Step 2: Create Configuration

### Config File: config/backend/sink_alt/config.yaml

```yaml
# Sink-Alt Configuration - Trade2026
service:
  name: "sink-alt"
  port: 8112
  metrics_port: 9112
  log_level: "INFO"

nats:
  url: "nats://nats:4222"
  subscribe_subject: "alt.norm.>"
  queue_group: "sink-alt-workers"

s3:
  endpoint_url: "http://seaweedfs:8333"
  access_key: "test"
  secret_key: "test"
  bucket: "trader2026"
  prefix: "lake/alt_docs/"

opensearch:
  url: "http://opensearch:9200"
  index: "alt_news"
  bulk_size: 100

valkey:
  url: "redis://valkey:6379"
  db: 3
  dedup_window_hours: 72

delta_lake:
  partition_by: 
    - "category"
    - "dt"
  schema:
    - name: "timestamp"
      type: "timestamp"
    - name: "category"
      type: "string"
    - name: "source"
      type: "string"
    - name: "title"
      type: "string"
    - name: "body"
      type: "string"
    - name: "url"
      type: "string"
    - name: "symbols"
      type: "array<string>"
    - name: "sentiment"
      type: "double"
    - name: "dt"
      type: "string"

batching:
  batch_seconds: 10
  max_batch_size: 1000
```

**Checklist**:
- [ ] Config created
- [ ] Dual write configured (S3 + OpenSearch)
- [ ] Deduplication settings

---

## Step 3: Update Service Code

```python
# Update all service URLs
opensearch_url = "http://opensearch:9200"  # NOT localhost
nats_url = "nats://nats:4222"
s3_endpoint = "http://seaweedfs:8333"
valkey_url = "redis://valkey:6379"
```

**Checklist**:
- [ ] URLs updated
- [ ] Deduplication logic verified

---

## Step 4: Create Dockerfile

### Dockerfile: backend/apps/sink_alt/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Additional deps
RUN pip install --no-cache-dir \
    delta-spark==2.4.0 \
    opensearch-py==2.3.0 \
    redis==5.0.0

COPY . .

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8112/health || exit 1

EXPOSE 8112 9112

CMD ["python", "service.py"]
```

**Checklist**:
- [ ] Dockerfile created
- [ ] Dependencies included

---

## Step 5: Build Image

```bash
cd backend\apps\sink_alt
docker build -t localhost/sink-alt:latest .
```

**Checklist**:
- [ ] Build successful

---

## Step 6: Add to Docker Compose

```yaml
  # ============================================
  # Sink-Alt - Alternative Data Sink
  # Priority 1 - Foundation Service
  # ============================================
  sink-alt:
    image: localhost/sink-alt:latest
    container_name: sink-alt
    build:
      context: ../../backend/apps/sink_alt
      dockerfile: Dockerfile
    ports:
      - "8112:8112"
      - "9112:9112"
    volumes:
      - ../../config/backend/sink_alt:/app/config:ro
    networks:
      - lowlatency
      - backend
    environment:
      - CONFIG_PATH=/app/config/config.yaml
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8112/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
    depends_on:
      - nats
      - seaweedfs
      - opensearch
      - valkey
    labels:
      - "com.trade2026.service=sink-alt"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.priority=P1"
```

**Checklist**:
- [ ] Service added
- [ ] All dependencies declared

---

## Step 7: Component Testing

### Test: Dual Write

```python
# Verify writes to both S3 and OpenSearch
import requests

# Check OpenSearch
response = requests.get('http://localhost:9200/alt_news/_search')
print(f"OpenSearch docs: {response.json()['hits']['total']['value']}")

# Check S3
# (boto3 code to list objects)
```

**Success Criteria**:
- [ ] Writes to S3 (Delta Lake)
- [ ] Writes to OpenSearch
- [ ] Deduplication working

---

## Step 8: Integration Testing

**Success Criteria**:
- [ ] Alt data → NATS → Sink → S3 + OpenSearch
- [ ] No duplicates

---

## Step 9: Validation

### Validation Checklist

**Functionality**:
- [ ] Dual write works
- [ ] Deduplication prevents duplicates
- [ ] Partitioning correct

**Performance**:
- [ ] Batch writes < 10s
- [ ] Memory < 1GB

**Reliability**:
- [ ] Handles failures gracefully

### Validation Result: ⏸️ PENDING

---

# ✅ TASK 02 VALIDATION GATE

## Post-Migration Validation

After ALL 3 services migrated:

### Integration Validation

**Test 1: All Services Running**
```bash
docker-compose -f docker-compose.apps.yml ps

# Expected: normalizer, sink-ticks, sink-alt all "healthy"
```

**Test 2: End-to-End Data Flow**
```bash
# 1. Publish test tick
# 2. Verify normalizer generates bar
# 3. Verify sink-ticks writes to S3
# 4. Verify bars in QuestDB
```

**Test 3: Performance**
- [ ] Normalizer: 100k ticks/sec
- [ ] Sink-ticks: Batch writes complete
- [ ] Sink-alt: Dual writes complete

### Decision Point

**All validation passed?**
- ✅ YES → Proceed to Task 03
- ❌ NO → Fix issues, re-validate

### Validation Result: ⏸️ PENDING

---

# 📊 TASK 02 COMPLETION CRITERIA

Task 02 complete when:

- [ ] All 3 services migrated
- [ ] All services in docker-compose.apps.yml
- [ ] All config files created
- [ ] All Docker images built
- [ ] All services start successfully
- [ ] All health checks passing
- [ ] Component tests pass
- [ ] Integration tests pass
- [ ] Performance benchmarks met
- [ ] Validation gate passed
- [ ] COMPLETION_TRACKER.md updated

---

**Task Status**: ⏳ IN PROGRESS (Instructions Created)
**Next Step**: Execute migration following these instructions
