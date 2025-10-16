# Phase 2 - Prompt 04: Migrate Priority 3 Services (CRITICAL)

**Phase**: 2 - Backend Migration  
**Prompt**: 04 of 06  
**Services**: risk (6h), oms (8h)  
**Priority**: P3 (CRITICAL - Core Trading Functionality)  
**Estimated Time**: 14 hours  
**Dependencies**: Prompts 02 and 03 must be complete and validated  
**Status**: ⏸️ Ready to start after Prompt 03 validation passes

---

## 🛑 MANDATORY VALIDATION GATE

### Prerequisites Check

Before starting Prompt 04, **MUST verify Prompts 02-03 complete**:

- [ ] **Prompt 02 (P1) Validated**
  - [ ] normalizer, sink-ticks, sink-alt all healthy
  - [ ] Data flow working: ticks → normalizer → QuestDB/S3

- [ ] **Prompt 03 (P2) Validated**
  - [ ] gateway, live-gateway both healthy
  - [ ] Market data flowing: Exchange → Gateway → NATS
  - [ ] Paper trading orders executing

- [ ] **All Core Infrastructure Healthy**
  - [ ] NATS, Valkey, QuestDB, ClickHouse, SeaweedFS, OpenSearch
  - [ ] All P1 + P2 services (5 services total) healthy

**Decision**: All prerequisites met? ✅ YES → Proceed | ❌ NO → Fix first

---

## ⚠️ CRITICAL TASK WARNING

**This is the MOST CRITICAL task in Phase 2**

**Why Critical**:
- **risk**: All trading must pass through risk checks
- **oms**: Central hub for all order flow
- **High Risk**: Trading disruption if either fails
- **Performance Critical**: risk must be < 1.5ms latency
- **Complex State**: oms manages positions, orders, fills

**Extra Requirements**:
- ✅ Extensive testing (component + integration + load)
- ✅ Performance profiling and optimization
- ✅ Comprehensive validation gate after both services
- ✅ Keep Trade2025 running as backup
- ✅ Full trading flow test required

---

## 📋 TASK OVERVIEW

### Services to Migrate

| Service | Port | Est. Time | Complexity | SLA |
|---------|------|-----------|------------|-----|
| risk | 8103 | 6h | Complex | P50 ≤ 1.5ms |
| oms | 8099 | 8h | Very Complex | P50 ≤ 10ms, P99 ≤ 50ms |

**Total**: 14 hours

**Migration Order**: risk FIRST (oms depends on it)

---

# 🔧 SERVICE 1: RISK (Pre-Trade Risk Checks)

## Service Information

**Purpose**: Real-time risk validation before order submission

**Source Location**: `C:\Trade2025\trading\apps\risk\`

**Target Location**: `C:\ClaudeDesktop_Projects\Trade2026\backend\apps\risk\`

**Port**: 8103

**Networks**: frontend, lowlatency, backend

**Dependencies**:
- Valkey (position cache) - CRITICAL
- QuestDB (historical data for VaR)
- Called by: oms (every order)

**Performance SLA**: P50 ≤ 1.5ms (NON-NEGOTIABLE)

---

## Step 1: Copy Service Code

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

mkdir -p backend\apps\risk

# MANUAL: Copy from C:\Trade2025\trading\apps\risk\
```

**Checklist**:
- [ ] Directory created
- [ ] All source files copied
- [ ] requirements.txt copied
- [ ] Dockerfile copied

---

## Step 2: Create Configuration

### Config File: config/backend/risk/config.yaml

```yaml
# Risk Service Configuration - Trade2026
service:
  name: "risk"
  port: 8103
  log_level: "INFO"
  workers: 4  # Multiple workers for high throughput

valkey:
  url: "redis://valkey:6379"
  db: 4
  max_connections: 20
  # Position cache - CRITICAL for performance
  position_cache_ttl_sec: 300

questdb:
  http_url: "http://questdb:9000"
  pg_url: "postgresql://admin:quest@questdb:8812/qdb"
  # Historical data for VaR calculations

risk_checks:
  enabled:
    - "position_limit"
    - "order_size_limit"
    - "buying_power"
    - "var_limit"
    - "concentration_limit"
    - "short_restriction"
  
  # Order size limits
  max_order_size_usd: 100000
  max_order_size_shares: 10000
  
  # Position limits
  max_position_size_usd: 1000000
  max_concentration_pct: 25.0  # Max 25% in single position
  
  # Portfolio limits
  max_portfolio_var_usd: 50000
  var_confidence_level: 0.99
  var_lookback_days: 30
  
  # Buying power
  initial_buying_power_usd: 100000
  margin_requirement_pct: 50.0

performance:
  latency_sla_ms: 1.5  # CRITICAL: P50 must be ≤ 1.5ms
  cache_positions: true
  cache_limits: true
  async_var_calculation: false  # VaR must be synchronous

monitoring:
  health_check_interval_sec: 10
  latency_alert_threshold_ms: 2.0
  metrics_port: 9103
```

**Checklist**:
- [ ] Config created
- [ ] SLA defined (1.5ms)
- [ ] Risk checks configured
- [ ] Limits set

---

## Step 3: Update Service Code

### Critical Changes

**1. URLs**
```python
# OLD - WRONG
valkey_url = "redis://localhost:6379"
questdb_url = "http://localhost:9000"

# NEW - CORRECT
valkey_url = "redis://valkey:6379"
questdb_url = "http://questdb:9000"
```

**2. Performance Optimizations**

```python
# Use connection pooling
from redis import ConnectionPool
pool = ConnectionPool(host='valkey', port=6379, db=4, max_connections=20)
redis_client = redis.Redis(connection_pool=pool)

# Cache everything possible
@lru_cache(maxsize=10000)
def get_position_limits(account):
    # Cached in memory
    pass

# Async I/O for non-critical paths
async def calculate_var_async(positions):
    # VaR can be slightly delayed
    pass

# Fast path for critical checks
def check_position_limit(account, symbol, qty):
    # Direct Valkey lookup, <1ms
    position = redis_client.hget(f'position:{account}', symbol)
    # ... fast check logic
```

**3. Instrumentation**

```python
import time

def risk_check(order):
    start = time.perf_counter()
    
    try:
        # Run all risk checks
        result = run_all_checks(order)
        
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        # Log if exceeds SLA
        if elapsed_ms > 1.5:
            logger.warning(f"Risk check exceeded SLA: {elapsed_ms:.2f}ms")
        
        # Emit metric
        metrics.histogram('risk.check.latency_ms', elapsed_ms)
        
        return result
    except Exception as e:
        logger.error(f"Risk check failed: {e}")
        # FAIL CLOSED: Reject if risk check errors
        return {"approved": False, "reason": "risk_check_error"}
```

**Checklist**:
- [ ] URLs updated
- [ ] Connection pooling added
- [ ] Caching optimized
- [ ] Instrumentation added
- [ ] Fail-closed error handling

---

## Step 4: Create Dockerfile

```dockerfile
# Risk Service - Trade2026
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y gcc curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Performance libraries
RUN pip install --no-cache-dir \
    redis==5.0.0 \
    hiredis==2.2.0 \
    uvloop==0.19.0

COPY . .

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8103/health || exit 1

EXPOSE 8103 9103

# Use uvloop for performance
CMD ["python", "-u", "service.py"]
```

**Checklist**:
- [ ] Dockerfile created
- [ ] Performance libs installed
- [ ] Health check frequent (10s)

---

## Step 5: Build and Verify

```bash
cd backend\apps\risk
docker build -t localhost/risk:latest .

# Verify entry in docker-compose.apps.yml exists
```

**Checklist**:
- [ ] Image built successfully
- [ ] docker-compose entry verified

---

## Step 6: Component Testing

### Test 1: Service Starts

```bash
cd infrastructure\docker
docker-compose -f docker-compose.apps.yml up -d risk

docker logs risk --tail 50
```

**Success Criteria**:
- [ ] Service starts
- [ ] Connects to Valkey
- [ ] Connects to QuestDB
- [ ] Health check passes

---

### Test 2: Risk Check Latency

```python
# Test latency under load
import requests
import time
import statistics

def test_risk_latency():
    latencies = []
    
    for i in range(10000):
        order = {
            "account": "test_account",
            "symbol": "BTCUSDT",
            "side": "buy",
            "quantity": 0.1,
            "price": 45000.0
        }
        
        start = time.perf_counter()
        response = requests.post('http://localhost:8103/check', json=order)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        latencies.append(elapsed_ms)
        
        if i % 1000 == 0:
            p50 = statistics.median(latencies)
            p99 = statistics.quantiles(latencies, n=100)[98]
            print(f"Iteration {i}: P50={p50:.2f}ms, P99={p99:.2f}ms")
    
    p50 = statistics.median(latencies)
    p99 = statistics.quantiles(latencies, n=100)[98]
    
    print(f"\nFinal Results:")
    print(f"P50: {p50:.2f}ms (SLA: ≤1.5ms)")
    print(f"P99: {p99:.2f}ms")
    print(f"Min: {min(latencies):.2f}ms")
    print(f"Max: {max(latencies):.2f}ms")
    
    assert p50 <= 1.5, f"P50 latency {p50:.2f}ms exceeds SLA of 1.5ms"

test_risk_latency()
```

**Success Criteria**:
- [ ] **P50 ≤ 1.5ms** (MANDATORY)
- [ ] P99 ≤ 5ms
- [ ] No timeouts
- [ ] No errors

**If SLA not met**: Optimize before proceeding

---

### Test 3: Load Test

```python
# Load test: 10k checks/sec
import asyncio
import aiohttp

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for i in range(10000):
            order = {
                "account": f"test_account_{i % 100}",
                "symbol": "BTCUSDT",
                "side": "buy",
                "quantity": 0.1,
                "price": 45000.0
            }
            
            task = session.post('http://localhost:8103/check', json=order)
            tasks.append(task)
        
        start = time.time()
        responses = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        
        print(f"Completed 10k checks in {elapsed:.2f}s")
        print(f"Throughput: {10000/elapsed:.0f} checks/sec")
        
        # Check all succeeded
        successes = sum(1 for r in responses if r.status == 200)
        print(f"Success rate: {successes/10000*100:.1f}%")

asyncio.run(load_test())
```

**Success Criteria**:
- [ ] Sustains 10k checks/sec
- [ ] No errors
- [ ] Memory stable
- [ ] CPU < 80%

---

## Step 7: Integration Testing

### Test: With OMS (When Ready)

```python
# Test risk check called by OMS
# Submit order via OMS → Should call risk → Get approval

order = {
    "account": "test_account",
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 0.1,
    "price": 45000.0
}

# Submit via OMS
response = requests.post('http://localhost:8099/orders', json=order)

# Check logs
# docker logs oms | grep "risk check"
# docker logs risk | grep "check request"

# Should see:
# - OMS calls risk service
# - Risk check completes < 1.5ms
# - Order approved/rejected
```

**Success Criteria**:
- [ ] OMS → risk integration works
- [ ] Latency still < 1.5ms
- [ ] Risk checks enforced

---

## Step 8: Validation

### Risk Service Validation Checklist

**Functionality**:
- [ ] Service starts and stays healthy
- [ ] All risk checks work
- [ ] Position limits enforced
- [ ] Order size limits enforced
- [ ] Buying power checked
- [ ] VaR calculated
- [ ] Concentration limits enforced

**Performance** (CRITICAL):
- [ ] **P50 ≤ 1.5ms** (MANDATORY)
- [ ] P99 ≤ 5ms
- [ ] Sustains 10k checks/sec
- [ ] Memory < 1GB
- [ ] CPU < 80%

**Reliability**:
- [ ] No crashes during load test
- [ ] Handles Valkey disconnections
- [ ] Fail-closed on errors
- [ ] Position cache working

### Validation Result: ⏸️ PENDING

**CRITICAL**: Do not proceed to OMS until risk service validated

---

# 🔧 SERVICE 2: OMS (Order Management System)

## Service Information

**Purpose**: Central hub for order routing, position tracking, fill management

**Source Location**: `C:\Trade2025\trading\apps\oms\`

**Target Location**: `C:\ClaudeDesktop_Projects\Trade2026\backend\apps\oms\`

**Port**: 8099

**Networks**: frontend, lowlatency, backend

**Dependencies**:
- NATS (orders.*, fills.* pub/sub)
- QuestDB (fill persistence)
- Valkey (position cache)
- **risk service** (pre-trade checks) - REQUIRED

**Performance SLA**: P50 ≤ 10ms, P99 ≤ 50ms

---

## Step 1: Copy Service Code

```bash
mkdir -p backend\apps\oms

# MANUAL: Copy from C:\Trade2025\trading\apps\oms\
```

**Checklist**:
- [ ] Directory created
- [ ] All files copied

---

## Step 2: Create Configuration

### Config File: config/backend/oms/config.yaml

```yaml
# OMS Configuration - Trade2026
service:
  name: "oms"
  port: 8099
  log_level: "INFO"
  workers: 4

nats:
  url: "nats://nats:4222"
  # Subscribe to fills from live-gateway
  fill_subject: "fills.>"
  # Publish orders to live-gateway
  order_subject_prefix: "orders"
  # Publish position updates
  position_subject_prefix: "positions"

valkey:
  url: "redis://valkey:6379"
  db: 5
  max_connections: 20
  # Position cache
  position_ttl_sec: 3600

questdb:
  http_url: "http://questdb:9000"
  pg_url: "postgresql://admin:quest@questdb:8812/qdb"
  # Fill persistence
  batch_size: 1000
  flush_interval_sec: 10

risk_service:
  url: "http://risk:8103"
  timeout_sec: 0.005  # 5ms timeout (allow for network)
  check_endpoint: "/check"
  enabled: true
  fail_closed: true  # Reject if risk service unavailable

order_management:
  supported_order_types:
    - "market"
    - "limit"
    - "stop"
    - "stop_limit"
  
  max_open_orders_per_account: 1000
  order_timeout_sec: 300
  
  # Position tracking
  update_positions_realtime: true
  reconcile_positions_interval_sec: 60

performance:
  latency_sla_ms: 10  # P50 target
  max_latency_ms: 50  # P99 target
  
monitoring:
  health_check_interval_sec: 30
  metrics_port: 9099
```

**Checklist**:
- [ ] Config created
- [ ] Risk service URL configured
- [ ] SLAs defined

---

## Step 3: Update Service Code

### Critical Changes

**1. URLs**
```python
# Update all service URLs
nats_url = "nats://nats:4222"
valkey_url = "redis://valkey:6379"
questdb_url = "http://questdb:9000"
risk_service_url = "http://risk:8103"  # CRITICAL
```

**2. Risk Service Integration**

```python
import requests
from functools import lru_cache

async def submit_order(order):
    start = time.perf_counter()
    
    # Step 1: Pre-trade risk check (CRITICAL)
    try:
        risk_response = requests.post(
            f"{config['risk_service']['url']}/check",
            json=order,
            timeout=config['risk_service']['timeout_sec']
        )
        
        if not risk_response.ok or not risk_response.json().get('approved'):
            reason = risk_response.json().get('reason', 'risk_check_failed')
            logger.warning(f"Order rejected by risk: {reason}")
            return {"status": "rejected", "reason": reason}
    
    except requests.Timeout:
        logger.error("Risk service timeout")
        if config['risk_service']['fail_closed']:
            return {"status": "rejected", "reason": "risk_timeout"}
    
    except Exception as e:
        logger.error(f"Risk service error: {e}")
        if config['risk_service']['fail_closed']:
            return {"status": "rejected", "reason": "risk_error"}
    
    # Step 2: Route to live-gateway
    await nats_client.publish(
        f"orders.{order['account']}.new",
        json.dumps(order).encode()
    )
    
    # Step 3: Update local order state
    save_order(order)
    
    elapsed_ms = (time.perf_counter() - start) * 1000
    metrics.histogram('oms.submit_order.latency_ms', elapsed_ms)
    
    return {"status": "submitted", "order_id": order['order_id']}
```

**3. Position Tracking**

```python
async def process_fill(fill):
    """Process fill and update positions"""
    account = fill['account']
    symbol = fill['symbol']
    side = fill['side']
    quantity = fill['quantity']
    price = fill['price']
    
    # Update position in Valkey (fast)
    position_key = f"position:{account}:{symbol}"
    current = float(redis_client.hget(position_key, 'quantity') or 0)
    
    if side == 'buy':
        new_position = current + quantity
    else:  # sell
        new_position = current - quantity
    
    redis_client.hset(position_key, 'quantity', new_position)
    redis_client.hset(position_key, 'last_price', price)
    redis_client.expire(position_key, config['valkey']['position_ttl_sec'])
    
    # Persist fill to QuestDB (async)
    asyncio.create_task(persist_fill_to_questdb(fill))
    
    # Publish position update
    await nats_client.publish(
        f"positions.{account}",
        json.dumps({
            "account": account,
            "symbol": symbol,
            "quantity": new_position,
            "price": price,
            "timestamp": time.time()
        }).encode()
    )
    
    logger.info(f"Position updated: {account}/{symbol} = {new_position}")
```

**Checklist**:
- [ ] URLs updated
- [ ] Risk integration added
- [ ] Position tracking optimized
- [ ] Error handling comprehensive

---

## Step 4: Create Dockerfile

```dockerfile
# OMS Service - Trade2026
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Additional dependencies
RUN pip install --no-cache-dir \
    redis==5.0.0 \
    aiohttp==3.9.0 \
    requests==2.31.0

COPY . .

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8099/health || exit 1

EXPOSE 8099 9099

CMD ["python", "service.py"]
```

**Checklist**:
- [ ] Dockerfile created

---

## Step 5: Build and Verify

```bash
cd backend\apps\oms
docker build -t localhost/oms:latest .
```

**Checklist**:
- [ ] Build successful
- [ ] docker-compose entry verified

---

## Step 6: Component Testing

### Test 1: Service Starts

```bash
docker-compose -f docker-compose.apps.yml up -d oms

docker logs oms --tail 50
```

**Success Criteria**:
- [ ] Service starts
- [ ] Connects to NATS, Valkey, QuestDB
- [ ] Connects to risk service
- [ ] Health check passes

---

### Test 2: Order Submission

```python
# Test order submission
import requests

order = {
    "account": "test_account",
    "symbol": "BTCUSDT",
    "side": "buy",
    "type": "limit",
    "quantity": 0.1,
    "price": 45000.0
}

response = requests.post('http://localhost:8099/orders', json=order)
print(response.json())

# Expected: {"status": "submitted", "order_id": "..."}
```

**Success Criteria**:
- [ ] Order accepted
- [ ] Risk check called
- [ ] Order routed to NATS
- [ ] Order ID returned

---

### Test 3: Latency Test

```python
# Test OMS latency
import statistics
import time
import requests

latencies = []

for i in range(1000):
    order = {
        "account": "test_account",
        "symbol": "BTCUSDT",
        "side": "buy",
        "type": "limit",
        "quantity": 0.1,
        "price": 45000.0 + i
    }
    
    start = time.perf_counter()
    response = requests.post('http://localhost:8099/orders', json=order)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    latencies.append(elapsed_ms)

p50 = statistics.median(latencies)
p99 = statistics.quantiles(latencies, n=100)[98]

print(f"OMS Latency:")
print(f"P50: {p50:.2f}ms (SLA: ≤10ms)")
print(f"P99: {p99:.2f}ms (SLA: ≤50ms)")

assert p50 <= 10, f"P50 {p50:.2f}ms exceeds SLA"
assert p99 <= 50, f"P99 {p99:.2f}ms exceeds SLA"
```

**Success Criteria**:
- [ ] P50 ≤ 10ms
- [ ] P99 ≤ 50ms
- [ ] No timeouts

---

## Step 7: Integration Testing

### Test: Full Order Lifecycle

```python
# Test complete order flow
import asyncio
import json
from nats.aio.client import Client as NATS

async def test_order_lifecycle():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    # Subscribe to fills
    fills_received = []
    
    async def fill_handler(msg):
        fill = json.loads(msg.data)
        fills_received.append(fill)
        print(f"Fill received: {fill}")
    
    await nc.subscribe("fills.test_account", cb=fill_handler)
    
    # Submit order via OMS
    order = {
        "account": "test_account",
        "symbol": "BTCUSDT",
        "side": "buy",
        "type": "market",
        "quantity": 0.1
    }
    
    response = requests.post('http://localhost:8099/orders', json=order)
    print(f"Order submitted: {response.json()}")
    
    # Wait for fill (from live-gateway paper trading)
    await asyncio.sleep(5)
    
    assert len(fills_received) > 0, "No fill received"
    
    # Check position updated
    positions = requests.get('http://localhost:8099/positions/test_account')
    print(f"Positions: {positions.json()}")
    
    await nc.close()

asyncio.run(test_order_lifecycle())
```

**Success Criteria**:
- [ ] Order submitted
- [ ] Risk check passed
- [ ] Order routed to live-gateway
- [ ] Fill received
- [ ] Position updated
- [ ] Fill persisted to QuestDB

---

## Step 8: Validation

### OMS Validation Checklist

**Functionality**:
- [ ] Order submission works
- [ ] All order types supported
- [ ] Risk checks enforced
- [ ] Orders routed to live-gateway
- [ ] Fills processed
- [ ] Positions tracked
- [ ] Fill persistence working

**Performance**:
- [ ] P50 ≤ 10ms
- [ ] P99 ≤ 50ms
- [ ] Memory < 2GB
- [ ] CPU < 80%

**Reliability**:
- [ ] No crashes
- [ ] Handles NATS reconnections
- [ ] Handles risk service failures
- [ ] Position reconciliation working

### Validation Result: ⏸️ PENDING

---

# ✅ PROMPT 04 CRITICAL VALIDATION GATE

## 🛑 MANDATORY FULL SYSTEM VALIDATION

**After both risk and oms migrated, you MUST run this comprehensive validation**

### Test 1: Full Trading Flow

```
API → OMS → Risk Check → Live Gateway → Paper Execution → Fill → Position Update
```

**Steps**:
```python
# 1. Submit order via OMS API
order = {
    "account": "test_account",
    "symbol": "BTCUSDT",
    "side": "buy",
    "type": "limit",
    "quantity": 0.1,
    "price": 45000.0
}

response = requests.post('http://localhost:8099/orders', json=order)
order_id = response.json()['order_id']

# 2. Verify risk check was called
# docker logs risk | grep {order_id}
# Should see risk check < 1.5ms

# 3. Verify order routed to live-gateway
# docker logs live-gateway | grep {order_id}
# Should see order received

# 4. Verify fill generated (paper trading)
# docker logs live-gateway | grep "fill"

# 5. Verify OMS processed fill
# docker logs oms | grep "fill"

# 6. Verify position updated
positions = requests.get('http://localhost:8099/positions/test_account')
assert positions.json()['BTCUSDT']['quantity'] == 0.1

# 7. Verify data persisted
# Query QuestDB fills table
```

**Success Criteria**:
- [ ] Complete flow works end-to-end
- [ ] Risk check < 1.5ms
- [ ] Order submission < 10ms
- [ ] Fill processed
- [ ] Position accurate
- [ ] Data persisted

---

### Test 2: Load Test (CRITICAL)

```python
# Sustained load test
import concurrent.futures
import time
import requests

def submit_order(i):
    order = {
        "account": f"test_account_{i % 10}",
        "symbol": "BTCUSDT",
        "side": "buy" if i % 2 == 0 else "sell",
        "type": "limit",
        "quantity": 0.01,
        "price": 45000.0 + (i % 100)
    }
    
    start = time.perf_counter()
    response = requests.post('http://localhost:8099/orders', json=order)
    elapsed = time.perf_counter() - start
    
    return {
        'elapsed': elapsed,
        'success': response.status_code == 200
    }

# Submit 1000 orders/sec for 5 minutes
print("Starting load test: 1000 orders/sec for 5 minutes")

with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    total_orders = 300000  # 1000/sec * 300 seconds
    
    futures = []
    start = time.time()
    
    for i in range(total_orders):
        future = executor.submit(submit_order, i)
        futures.append(future)
        
        # Rate limiting
        if i % 1000 == 0:
            elapsed = time.time() - start
            expected = i / 1000
            if elapsed < expected:
                time.sleep(expected - elapsed)
            
            print(f"Submitted {i} orders...")
    
    # Collect results
    results = [f.result() for f in futures]
    
    elapsed_total = time.time() - start
    print(f"\nLoad Test Complete:")
    print(f"Total orders: {total_orders}")
    print(f"Time: {elapsed_total:.1f}s")
    print(f"Rate: {total_orders/elapsed_total:.0f} orders/sec")
    
    successes = sum(1 for r in results if r['success'])
    print(f"Success rate: {successes/total_orders*100:.1f}%")
    
    latencies = [r['elapsed'] * 1000 for r in results]
    p50 = statistics.median(latencies)
    p99 = statistics.quantiles(latencies, n=100)[98]
    
    print(f"Latency P50: {p50:.2f}ms")
    print(f"Latency P99: {p99:.2f}ms")
    
    # Check SLAs
    assert successes / total_orders >= 0.99, "Success rate < 99%"
    assert p50 <= 10, f"P50 {p50:.2f}ms exceeds 10ms SLA"
    assert p99 <= 50, f"P99 {p99:.2f}ms exceeds 50ms SLA"

print("\n✅ LOAD TEST PASSED")
```

**Success Criteria** (ALL MUST PASS):
- [ ] Sustains 1000 orders/sec for 5 minutes
- [ ] Success rate ≥ 99%
- [ ] Risk service: P50 ≤ 1.5ms
- [ ] OMS: P50 ≤ 10ms, P99 ≤ 50ms
- [ ] No crashes
- [ ] No memory leaks
- [ ] All services stable

---

### Test 3: Service Health Check

```bash
# All services must be healthy
docker-compose -f docker-compose.apps.yml ps

# Expected output:
# normalizer    running (healthy)
# sink-ticks    running (healthy)
# sink-alt      running (healthy)
# gateway       running (healthy)
# live-gateway  running (healthy)
# risk          running (healthy)
# oms           running (healthy)
```

**Success Criteria**:
- [ ] All 7 services healthy
- [ ] No restarts
- [ ] No errors in logs

---

### Test 4: Data Persistence

```sql
-- Check fills in QuestDB
SELECT COUNT(*) as fill_count
FROM fills
WHERE timestamp > dateadd('m', -10, now());

-- Should see fills from load test

-- Check positions in Valkey
-- docker exec -it valkey valkey-cli
-- KEYS position:*
-- Should see position keys
```

**Success Criteria**:
- [ ] Fills persisted to QuestDB
- [ ] Positions cached in Valkey
- [ ] No data loss

---

## 🚦 DECISION POINT

### All Validation Passed?

**✅ YES** → Proceed to Prompt 05 (P4 Supporting Services)

**❌ NO** → STOP, Fix Issues, Re-validate

**Do NOT proceed until**:
- Full trading flow works
- Load test passes
- All SLAs met
- All services healthy

---

## 📊 PROMPT 04 COMPLETION CRITERIA

Prompt 04 complete when:

- [ ] Both services (risk, oms) migrated
- [ ] Both services healthy
- [ ] Full trading flow validated
- [ ] Load test passed (1000 orders/sec)
- [ ] All SLAs met:
  - [ ] Risk: P50 ≤ 1.5ms
  - [ ] OMS: P50 ≤ 10ms, P99 ≤ 50ms
- [ ] No crashes during 5-minute load test
- [ ] Data persistence verified
- [ ] **CRITICAL VALIDATION GATE PASSED**
- [ ] COMPLETION_TRACKER.md updated

---

**Prompt Status**: ⏸️ READY TO START (After Prompt 03 validated)

**Next Prompt**: Prompt 05 (P4 Supporting Services) - After CRITICAL validation passes

**Warning**: This is the most critical prompt. Take time to validate thoroughly.
