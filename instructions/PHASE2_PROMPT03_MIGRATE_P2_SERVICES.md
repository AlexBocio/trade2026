# Phase 2 Task 03: Migrate Priority 2 Services (Data Ingestion)

**Task**: 03 of 6  
**Services**: gateway, live-gateway  
**Priority**: P2 (Data Ingestion)  
**Estimated Time**: 11 hours  
**Dependencies**: Task 02 (P1) must be complete  
**Status**: ⏸️ Ready to start after Task 02 validation passes

---

## 🛑 MANDATORY VALIDATION GATE

### Prerequisites Check

Before starting Task 03, **MUST verify Task 02 complete**:

- [ ] **Task 02 Validation Passed**
  - [ ] normalizer running and healthy
  - [ ] sink-ticks running and healthy
  - [ ] sink-alt running and healthy
  - [ ] All P1 integration tests passed
  - [ ] All P1 performance benchmarks met
  - [ ] No errors in logs

- [ ] **Core Infrastructure Still Healthy**
  - [ ] NATS running on port 4222
  - [ ] Valkey running on port 6379
  - [ ] QuestDB running on port 9000
  - [ ] SeaweedFS running on port 8333
  - [ ] OpenSearch running on port 9200

**Decision**: All prerequisites met? ✅ YES → Proceed | ❌ NO → Fix Task 02 first

---

## 📋 TASK OVERVIEW

### Services to Migrate

| Service | Port | Est. Time | Complexity | Dependencies |
|---------|------|-----------|------------|--------------|
| gateway | 8080 | 6h | Complex | NATS, Valkey (optional) |
| live-gateway | 8200 | 5h | Complex | NATS |

**Total**: 11 hours

### Why Priority 2?

- Depend on P1 services operational
- External API dependencies (CCXT)
- Need exchange API keys
- Critical for market data flow

---

# 🔧 SERVICE 1: GATEWAY (Market Data Ingestion)

## Service Information

**Purpose**: Fetch market data from exchanges and publish to NATS

**Source Location**: `C:\Trade2025\trading\apps\gateway\`

**Target Location**: `C:\ClaudeDesktop_Projects\Trade2026\backend\apps\gateway\`

**Port**: 8080

**Networks**: frontend, lowlatency, backend

**Dependencies**:
- NATS (ticks.* publishing)
- Valkey (optional - rate limiting)
- External: Binance API, Coinbase API, Kraken API (via CCXT)

---

## Step 1: Copy Service Code

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Create service directory
mkdir -p backend\apps\gateway

# MANUAL: Copy all files from C:\Trade2025\trading\apps\gateway\
# to C:\ClaudeDesktop_Projects\Trade2026\backend\apps\gateway\
#
# Files to copy:
# - service.py (or main.py)
# - requirements.txt
# - Dockerfile (if exists)
# - config.yaml (if exists)
# - Any Python modules
# - tests/ directory
```

**Checklist**:
- [ ] Service directory created
- [ ] All source files copied
- [ ] requirements.txt copied
- [ ] Dockerfile copied/created
- [ ] Config files identified

---

## Step 2: Create Configuration

### Config File: config/backend/gateway/config.yaml

```yaml
# Gateway Configuration - Trade2026
service:
  name: "gateway"
  port: 8080
  log_level: "INFO"
  workers: 2

nats:
  url: "nats://nats:4222"
  publish_subject_prefix: "ticks"
  max_reconnect_attempts: 10
  reconnect_wait_sec: 2

valkey:
  url: "redis://valkey:6379"
  db: 2
  max_connections: 10
  # Rate limiting cache
  rate_limit_enabled: true

exchanges:
  # Enable exchanges (requires API keys in secrets)
  binance:
    enabled: true
    symbols:
      - "BTCUSDT"
      - "ETHUSDT"
      - "SOLUSDT"
    poll_interval_sec: 60
    websocket_enabled: true
    rate_limit_per_min: 1200
  
  coinbase:
    enabled: false  # Enable when API keys available
    symbols:
      - "BTC-USD"
      - "ETH-USD"
    poll_interval_sec: 60
    websocket_enabled: true
    rate_limit_per_min: 600
  
  kraken:
    enabled: false  # Enable when API keys available
    symbols:
      - "XBTUSD"
      - "ETHUSD"
    poll_interval_sec: 60
    websocket_enabled: false
    rate_limit_per_min: 300

rate_limiting:
  window_sec: 60
  max_requests_per_window: 1000
  use_valkey_cache: true

performance:
  max_ticks_per_sec: 10000
  buffer_size: 5000
  flush_interval_sec: 1

monitoring:
  health_check_interval_sec: 30
  metrics_port: 9080
```

**Checklist**:
- [ ] Config file created
- [ ] All URLs use Docker service names
- [ ] Exchange settings configured
- [ ] Rate limiting configured

---

## Step 3: Create Secrets File

### Secrets File: secrets/gateway.env

```bash
# Gateway Exchange API Keys - Trade2026
# NEVER COMMIT THIS FILE TO GIT

# Binance API Keys
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here

# Coinbase API Keys (optional)
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_SECRET=your_coinbase_secret_here

# Kraken API Keys (optional)
KRAKEN_API_KEY=your_kraken_api_key_here
KRAKEN_SECRET=your_kraken_secret_here
```

**CRITICAL SECURITY**:
- [ ] secrets/gateway.env created
- [ ] secrets/.gitignore includes *.env
- [ ] **NEVER commit secrets to git**
- [ ] Use real API keys or test/paper trading keys

**If you don't have API keys**:
- Use paper trading mode
- Or use public endpoints (read-only)
- Or mock exchange data for testing

---

## Step 4: Update Service Code

### Critical Changes Required

**1. Configuration Path Updates**

```python
# OLD (Trade2025)
config_path = "config.yaml"
config_path = "C:/Trade2025/trading/apps/gateway/config.yaml"

# NEW (Trade2026)
config_path = "/app/config/config.yaml"
```

**2. URL Updates (CRITICAL)**

```python
# OLD - WRONG
nats_url = "nats://localhost:4222"
valkey_url = "redis://localhost:6379"

# NEW - CORRECT
nats_url = "nats://nats:4222"
valkey_url = "redis://valkey:6379"
```

**3. Secrets Loading**

```python
# Load secrets from environment or file
import os

binance_key = os.getenv('BINANCE_API_KEY')
binance_secret = os.getenv('BINANCE_SECRET')

# Or load from /secrets/gateway.env
```

**4. Error Handling for External APIs**

```python
# Add retry logic for exchange API calls
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def fetch_ticker(exchange, symbol):
    # CCXT API call with retry
    pass
```

**Checklist**:
- [ ] All localhost replaced with service names
- [ ] Configuration loading updated
- [ ] Secrets loaded from environment
- [ ] Retry logic added for external APIs
- [ ] Logging configured

---

## Step 5: Create/Update Dockerfile

### Dockerfile: backend/apps/gateway/Dockerfile

```dockerfile
# Gateway Service - Trade2026
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install CCXT for exchange connectivity
RUN pip install --no-cache-dir \
    ccxt==4.0.0 \
    aiohttp==3.9.0 \
    websockets==12.0

# Copy service code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose ports
EXPOSE 8080 9080

# Run service
CMD ["python", "service.py"]
```

**Checklist**:
- [ ] Dockerfile created/updated
- [ ] CCXT dependency added
- [ ] Health check configured
- [ ] Ports exposed

---

## Step 6: Verify docker-compose.apps.yml Entry

The entry should already exist from our complete compose file. Verify it looks correct:

```yaml
  gateway:
    image: localhost/gateway:latest
    container_name: gateway
    build:
      context: ../../backend/apps/gateway
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
      - "9080:9080"
    volumes:
      - ../../config/backend/gateway:/app/config:ro
      - ../../secrets:/secrets:ro
    networks:
      - frontend
      - lowlatency
      - backend
    environment:
      - CONFIG_PATH=/app/config/config.yaml
      - BINANCE_API_KEY=${BINANCE_API_KEY}
      - BINANCE_SECRET=${BINANCE_SECRET}
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
    env_file:
      - ../../secrets/gateway.env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    depends_on:
      nats:
        condition: service_healthy
    labels:
      - "com.trade2026.service=gateway"
      - "com.trade2026.priority=P2"
```

**Checklist**:
- [ ] Entry exists in docker-compose.apps.yml
- [ ] Secrets mounted
- [ ] Networks correct (frontend, lowlatency, backend)
- [ ] Environment variables configured

---

## Step 7: Build Docker Image

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\backend\apps\gateway

# Build image
docker build -t localhost/gateway:latest .

# Verify build
docker images | grep gateway
```

**Expected Output**:
```
localhost/gateway   latest   abc123def456   2 minutes ago   400MB
```

**Checklist**:
- [ ] Image builds successfully
- [ ] No build errors
- [ ] Image tagged correctly

---

## Step 8: Component Testing

### Test 1: Service Starts

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Start gateway only
docker-compose -f docker-compose.apps.yml up -d gateway

# Check logs
docker logs gateway --tail 50

# Expected: Service starts, connects to NATS
```

**Success Criteria**:
- [ ] Container starts
- [ ] No crash loops
- [ ] Health check passes
- [ ] Connected to NATS

### Test 2: Exchange Connectivity (Mock or Real)

**Option A: With Real API Keys**
```python
# Test script: backend/apps/gateway/tests/test_exchange.py
import ccxt

# Test Binance connection
exchange = ccxt.binance({
    'apiKey': 'YOUR_KEY',
    'secret': 'YOUR_SECRET',
})

# Fetch ticker
ticker = exchange.fetch_ticker('BTC/USDT')
print(f"BTC/USDT Price: ${ticker['last']}")
```

**Option B: With Mock Data**
```python
# Mock exchange data for testing
mock_ticker = {
    'timestamp': int(time.time() * 1000),
    'symbol': 'BTCUSDT',
    'last': 45000.0,
    'bid': 44999.0,
    'ask': 45001.0,
    'volume': 123456.78
}
```

**Success Criteria**:
- [ ] Can connect to exchange (or mock works)
- [ ] Can fetch ticker data
- [ ] No API errors

### Test 3: NATS Publishing

```bash
# Subscribe to ticks topic
docker exec -it nats nats sub 'ticks.>'

# Expected: See tick messages published by gateway
```

**Success Criteria**:
- [ ] Ticks published to NATS
- [ ] Subject format correct: `ticks.{exchange}.{symbol}`
- [ ] Tick data structure valid

### Test 4: Rate Limiting

```python
# Test rate limiting works
import time
import requests

start = time.time()
for i in range(1500):  # Exceed rate limit
    requests.get('http://localhost:8080/ticker/BTCUSDT')
    if i % 100 == 0:
        print(f"Sent {i} requests")

elapsed = time.time() - start
print(f"Time: {elapsed}s, Rate: {1500/elapsed:.0f} req/sec")

# Should see rate limiting kick in
```

**Success Criteria**:
- [ ] Rate limiting prevents excessive requests
- [ ] No 429 errors from exchange
- [ ] Valkey caching working (if enabled)

---

## Step 9: Integration Testing

### Test 1: End-to-End Data Flow

```
Exchange API → Gateway → NATS → Normalizer → QuestDB
```

**Verify**:
```bash
# 1. Gateway fetching data
docker logs gateway --tail 20

# 2. Ticks in NATS
docker exec -it nats nats sub 'ticks.binance.BTCUSDT'

# 3. Normalizer consuming ticks
docker logs normalizer --tail 20

# 4. Bars in QuestDB
# Query QuestDB
SELECT * FROM ohlcv_1m 
WHERE symbol = 'BTCUSDT' 
ORDER BY timestamp DESC 
LIMIT 10;
```

**Success Criteria**:
- [ ] Gateway fetching ticks from exchange
- [ ] Ticks published to NATS
- [ ] Normalizer consuming ticks
- [ ] Bars written to QuestDB
- [ ] No data loss

### Test 2: WebSocket Reconnection

```bash
# Restart NATS while gateway running
docker restart nats

# Watch gateway logs
docker logs gateway -f

# Expected: Gateway reconnects automatically
```

**Success Criteria**:
- [ ] Gateway detects disconnection
- [ ] Gateway reconnects to NATS
- [ ] No data loss during reconnection
- [ ] Backlog processed

---

## Step 10: Validation

### Validation Checklist

**Functionality**:
- [ ] Service starts successfully
- [ ] Connects to NATS
- [ ] Connects to exchanges (or mock works)
- [ ] Fetches ticker data
- [ ] Publishes to NATS (ticks.*)
- [ ] Rate limiting works
- [ ] Handles reconnections

**Performance**:
- [ ] Throughput: 1000+ ticks/sec
- [ ] Latency: < 100ms from fetch to publish
- [ ] Memory: < 500MB
- [ ] CPU: < 50%

**Reliability**:
- [ ] No crashes during load test
- [ ] Handles NATS reconnections
- [ ] Handles exchange API errors
- [ ] Rate limiting prevents bans

**Security**:
- [ ] API keys loaded from secrets
- [ ] secrets/.gitignore configured
- [ ] No keys in logs
- [ ] No keys in code

### Validation Result: ⏸️ PENDING

---

# 🔧 SERVICE 2: LIVE-GATEWAY (Exchange Connectivity)

## Service Information

**Purpose**: Execute orders on exchanges, receive fills

**Source Location**: `C:\Trade2025\trading\apps\live_gateway\`

**Target Location**: `C:\ClaudeDesktop_Projects\Trade2026\backend\apps\live_gateway\`

**Port**: 8200

**Networks**: frontend, lowlatency, backend

**Dependencies**:
- NATS (orders.*.new subscription, fills.* publishing)
- External: Exchange APIs (via CCXT)

---

## Step 1: Copy Service Code

```bash
mkdir -p backend\apps\live_gateway

# MANUAL: Copy from C:\Trade2025\trading\apps\live_gateway\
```

**Checklist**:
- [ ] Directory created
- [ ] All files copied

---

## Step 2: Create Configuration

### Config File: config/backend/live_gateway/config.yaml

```yaml
# Live Gateway Configuration - Trade2026
service:
  name: "live-gateway"
  port: 8200
  log_level: "INFO"
  mode: "paper"  # IMPORTANT: "paper" or "live"

nats:
  url: "nats://nats:4222"
  subscribe_subject: "orders.*.new"
  publish_subject_prefix: "orders"
  fill_subject_prefix: "fills"
  queue_group: "live-gateway-workers"

exchanges:
  binance:
    enabled: true
    mode: "paper"  # paper or live
    default_symbol: "BTCUSDT"
    order_timeout_sec: 30
  
  coinbase:
    enabled: false
    mode: "paper"
  
  kraken:
    enabled: false
    mode: "paper"

execution:
  max_retries: 3
  retry_delay_sec: 1
  timeout_sec: 30
  validate_orders: true

monitoring:
  health_check_interval_sec: 30
  metrics_port: 9200

# CRITICAL SAFETY SETTINGS
safety:
  paper_trading_only: true  # MUST be true initially
  max_order_size_usd: 1000
  max_position_size_usd: 10000
  require_manual_approval: false
```

**Checklist**:
- [ ] Config created
- [ ] **PAPER TRADING MODE ENABLED**
- [ ] Safety limits configured

---

## Step 3: Create Secrets File

### Secrets File: secrets/live_gateway.env

```bash
# Live Gateway Exchange API Keys - Trade2026
# NEVER COMMIT TO GIT

# Same keys as gateway
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here

# For paper trading, can use test API keys
# BINANCE_API_KEY=test_key
# BINANCE_SECRET=test_secret
```

**CRITICAL**:
- [ ] Secrets file created
- [ ] **Start with paper trading mode**
- [ ] Never commit secrets

---

## Step 4: Update Service Code

```python
# Update URLs
nats_url = "nats://nats:4222"  # NOT localhost

# Add safety checks
def validate_order(order):
    if config['safety']['paper_trading_only']:
        # Force paper trading
        order['paper_trading'] = True
    
    # Check limits
    if order['size_usd'] > config['safety']['max_order_size_usd']:
        raise ValueError(f"Order size {order['size_usd']} exceeds limit")
    
    return order

# Add comprehensive error handling
try:
    response = exchange.create_order(symbol, type, side, amount, price)
except ccxt.NetworkError as e:
    logger.error(f"Network error: {e}")
    # Retry logic
except ccxt.ExchangeError as e:
    logger.error(f"Exchange error: {e}")
    # Handle exchange-specific errors
```

**Checklist**:
- [ ] URLs updated
- [ ] Safety checks added
- [ ] Error handling comprehensive
- [ ] Paper trading enforced

---

## Step 5: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CCXT for exchange connectivity
RUN pip install --no-cache-dir ccxt==4.0.0

COPY . .

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8200/health || exit 1

EXPOSE 8200 9200

CMD ["python", "service.py"]
```

**Checklist**:
- [ ] Dockerfile created
- [ ] CCXT installed

---

## Step 6: Verify docker-compose Entry

```yaml
  live-gateway:
    image: localhost/live-gateway:latest
    container_name: live-gateway
    build:
      context: ../../backend/apps/live_gateway
      dockerfile: Dockerfile
    ports:
      - "8200:8200"
      - "9200:9200"
    volumes:
      - ../../config/backend/live_gateway:/app/config:ro
      - ../../secrets:/secrets:ro
    networks:
      - frontend
      - lowlatency
      - backend
    environment:
      - CONFIG_PATH=/app/config/config.yaml
      - LOG_LEVEL=INFO
    env_file:
      - ../../secrets/live_gateway.env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8200/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
    depends_on:
      nats:
        condition: service_healthy
    labels:
      - "com.trade2026.service=live-gateway"
      - "com.trade2026.priority=P2"
      - "com.trade2026.critical=true"
```

**Checklist**:
- [ ] Entry exists
- [ ] Secrets mounted

---

## Step 7: Build Image

```bash
cd backend\apps\live_gateway
docker build -t localhost/live-gateway:latest .
```

**Checklist**:
- [ ] Build successful

---

## Step 8: Component Testing

### Test 1: Paper Trading Mode

```python
# Test order submission in paper mode
import json
import asyncio
from nats.aio.client import Client as NATS

async def test_paper_order():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    # Submit paper trading order
    order = {
        "account": "test_account",
        "symbol": "BTCUSDT",
        "side": "buy",
        "type": "limit",
        "quantity": 0.001,
        "price": 45000.0,
        "paper_trading": True
    }
    
    await nc.publish("orders.test_account.new", json.dumps(order).encode())
    
    # Listen for fill
    async def fill_handler(msg):
        fill = json.loads(msg.data)
        print(f"Fill received: {fill}")
    
    await nc.subscribe("fills.test_account", cb=fill_handler)
    
    await asyncio.sleep(10)
    await nc.close()

asyncio.run(test_paper_order())
```

**Success Criteria**:
- [ ] Order submitted
- [ ] Fill received
- [ ] **No real exchange order placed**
- [ ] Paper trading confirmed

### Test 2: Safety Limits

```python
# Test order size limit
large_order = {
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 100,  # Too large
    "price": 45000.0
}

# Should be rejected
```

**Success Criteria**:
- [ ] Large orders rejected
- [ ] Safety limits enforced
- [ ] Errors logged

---

## Step 9: Integration Testing

### Test: Order Flow

```
OMS → orders.*.new → Live Gateway → [Paper Trading] → fills.* → OMS
```

**Verify**:
```bash
# 1. Submit order (via OMS when ready, or directly to NATS)
# 2. Watch live-gateway logs
docker logs live-gateway -f

# 3. Verify fill published
docker exec -it nats nats sub 'fills.>'

# Expected: Fill message received
```

**Success Criteria**:
- [ ] Order consumed from NATS
- [ ] Order "executed" (paper)
- [ ] Fill published to NATS
- [ ] Order lifecycle complete

---

## Step 10: Validation

### Validation Checklist

**Functionality**:
- [ ] Service starts
- [ ] Connects to NATS
- [ ] Consumes orders
- [ ] Executes orders (paper mode)
- [ ] Publishes fills
- [ ] Safety limits enforced

**Performance**:
- [ ] Order execution < 1 second
- [ ] Memory < 500MB
- [ ] No crashes

**Reliability**:
- [ ] Handles NATS reconnections
- [ ] Handles exchange errors
- [ ] Order timeout handling

**Safety** (CRITICAL):
- [ ] **Paper trading mode enforced**
- [ ] Order size limits enforced
- [ ] Position limits enforced
- [ ] No real money at risk

### Validation Result: ⏸️ PENDING

---

# ✅ TASK 03 VALIDATION GATE

## Post-Migration Validation

After BOTH services migrated:

### Integration Validation

**Test 1: Both Services Running**
```bash
docker-compose -f docker-compose.apps.yml ps

# Expected: gateway, live-gateway, all P1 services "healthy"
```

**Test 2: Market Data Flow**
```
Exchange → Gateway → NATS → Normalizer → QuestDB
```

**Test 3: Order Flow (Paper Trading)**
```
Submit Order → Live Gateway → Paper Execution → Fill
```

### Performance

- [ ] Gateway: 1000+ ticks/sec
- [ ] Live-gateway: Order execution < 1s
- [ ] All services stable

### Decision Point

**All validation passed?**
- ✅ YES → Proceed to Task 04 (P3 - Trading Core)
- ❌ NO → Fix issues, re-validate

### Validation Result: ⏸️ PENDING

---

## 📊 TASK 03 COMPLETION CRITERIA

Task 03 complete when:

- [ ] Both services migrated
- [ ] Both services in docker-compose.apps.yml
- [ ] Both config files created
- [ ] Both Docker images built
- [ ] Both services start successfully
- [ ] Both health checks passing
- [ ] Component tests pass
- [ ] Integration tests pass
- [ ] **Paper trading validated**
- [ ] Performance benchmarks met
- [ ] Validation gate passed
- [ ] COMPLETION_TRACKER.md updated

---

**Task Status**: ⏸️ READY TO START (After Task 02 complete)

**Next Step**: Wait for Task 02 validation, then execute this task

**Critical Note**: **ALWAYS use paper trading mode** for live-gateway until full system validated
