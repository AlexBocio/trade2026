# Trade2026 Service Optimization Guide
**Date**: 2025-10-17
**Purpose**: Document optimization opportunities and fixes for deployed services

---

## 🔧 IMMEDIATE FIXES REQUIRED

### 1. Health Check Repairs

#### PNL Service (Port 8100)
**Issue**: Service functional but health check returning unhealthy
**Root Cause**: Health endpoint likely not implemented or misconfigured
**Fix**:
```python
# Add to backend/apps/pnl/service.py
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pnl"}
```

#### SINK-TICKS Service (Port 8111)
**Issue**: Successfully writing data but health check returns 503
**Evidence**: Logs show "Wrote 6 ticks to Delta Lake"
**Fix**:
```python
# Update health check logic
@app.get("/health")
async def health_check():
    try:
        # Check NATS connection
        if not nats_client or not nats_client.is_connected:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "reason": "NATS disconnected"}
            )
        # Check Delta Lake accessibility
        if not delta_table_accessible():
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "reason": "Delta Lake unavailable"}
            )
        return {"status": "healthy", "service": "sink-ticks"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )
```

#### SINK-ALT Service (Port 8112)
**Issue**: Health check consistently returns 503
**Fix**: Similar to sink-ticks, ensure health check validates actual functionality

---

## 🚀 PERFORMANCE OPTIMIZATIONS

### 1. OMS Service Optimization (Current: ~250ms, Target: <10ms)

#### A. Connection Pooling
```python
# backend/apps/oms/service.py
from redis import ConnectionPool
import httpx

# Create connection pools
redis_pool = ConnectionPool(
    host='valkey',
    port=6379,
    max_connections=50,
    decode_responses=True
)
redis_client = redis.Redis(connection_pool=redis_pool)

# HTTP connection pool for risk service
http_client = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=100, max_keepalive=50)
)
```

#### B. Async Risk Checks
```python
# Make risk checks async
async def check_risk_async(order):
    try:
        response = await http_client.post(
            "http://risk:8103/check",
            json=order,
            timeout=0.005  # 5ms timeout
        )
        return response.json()
    except httpx.TimeoutException:
        # Fail open or closed based on config
        return {"approved": False, "reason": "timeout"}
```

#### C. Batch Processing
```python
# Process orders in batches
from asyncio import Queue, gather

order_queue = Queue(maxsize=1000)

async def batch_processor():
    while True:
        batch = []
        # Collect up to 10 orders or wait 10ms
        deadline = time.time() + 0.01
        while len(batch) < 10 and time.time() < deadline:
            try:
                order = await asyncio.wait_for(
                    order_queue.get(),
                    timeout=max(0, deadline - time.time())
                )
                batch.append(order)
            except asyncio.TimeoutError:
                break

        if batch:
            # Process batch in parallel
            results = await gather(*[process_order(o) for o in batch])
```

### 2. Risk Service Optimization (Current: >10ms, Target: <1.5ms)

#### A. In-Memory Caching
```python
from functools import lru_cache
import asyncio

# Cache risk limits
@lru_cache(maxsize=10000)
def get_cached_limit(symbol, limit_type):
    return limits.get(symbol, {}).get(limit_type)

# Cache position data with TTL
position_cache = {}
position_cache_ttl = {}

async def get_position(account, symbol):
    cache_key = f"{account}:{symbol}"
    if cache_key in position_cache:
        if time.time() < position_cache_ttl[cache_key]:
            return position_cache[cache_key]

    # Fetch from Redis
    position = await redis_client.hget(f"position:{account}", symbol)
    position_cache[cache_key] = position
    position_cache_ttl[cache_key] = time.time() + 1  # 1 second TTL
    return position
```

#### B. Pre-computed Risk Metrics
```python
# Pre-compute VaR and other metrics
async def precompute_risk_metrics():
    while True:
        # Calculate VaR, exposure, etc.
        metrics = await calculate_portfolio_metrics()

        # Store in Redis for fast lookup
        await redis_client.setex(
            "risk:metrics:current",
            60,  # 60 second expiry
            json.dumps(metrics)
        )

        await asyncio.sleep(30)  # Update every 30 seconds

# Start background task
asyncio.create_task(precompute_risk_metrics())
```

#### C. Fast Path for Common Checks
```python
async def fast_risk_check(order):
    # Quick reject for obvious violations
    if order['quantity'] > MAX_ORDER_SIZE:
        return {"approved": False, "reason": "size_limit"}

    if order['symbol'] in blocked_symbols:
        return {"approved": False, "reason": "symbol_blocked"}

    # Fast approve for small orders
    if order['quantity'] * order['price'] < 100:  # $100
        return {"approved": True, "fast_path": True}

    # Full check for others
    return await full_risk_check(order)
```

---

## 🔄 SERVICE CONFIGURATION OPTIMIZATIONS

### 1. Docker Compose Optimizations
```yaml
# infrastructure/docker/docker-compose.apps.yml

services:
  oms:
    image: localhost/oms:latest
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 512M
        reservations:
          cpus: '1'
          memory: 256M
    environment:
      - PYTHONUNBUFFERED=1
      - WORKERS=4
      - CONNECTION_POOL_SIZE=50
      - ASYNC_MODE=true

  risk:
    image: localhost/risk:latest
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 512M
    environment:
      - CACHE_ENABLED=true
      - CACHE_TTL=60
      - PRECOMPUTE_METRICS=true
      - FAST_PATH_ENABLED=true
```

### 2. NATS Configuration
```yaml
# Add JetStream configuration for better performance
nats:
  jetstream:
    max_memory: 1G
    max_file_store: 10G
    store_dir: /data/jetstream
```

### 3. Redis/Valkey Optimization
```bash
# Add Redis configuration
docker exec -it valkey redis-cli CONFIG SET maxmemory 2gb
docker exec -it valkey redis-cli CONFIG SET maxmemory-policy allkeys-lru
docker exec -it valkey redis-cli CONFIG SET tcp-keepalive 60
docker exec -it valkey redis-cli CONFIG SET tcp-backlog 511
```

---

## 📊 MONITORING AND METRICS

### 1. Add Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
order_counter = Counter('oms_orders_total', 'Total orders processed')
order_latency = Histogram('oms_order_latency_seconds', 'Order processing latency')
active_orders = Gauge('oms_active_orders', 'Number of active orders')

# Use in code
@order_latency.time()
async def process_order(order):
    order_counter.inc()
    # ... process order
```

### 2. Health Check Improvements
```python
@app.get("/health/detailed")
async def detailed_health():
    checks = {
        "nats": check_nats_connection(),
        "redis": check_redis_connection(),
        "database": check_database_connection(),
        "latency_ms": get_p50_latency(),
        "memory_mb": get_memory_usage(),
        "active_connections": get_connection_count()
    }

    status = "healthy" if all(checks.values()) else "degraded"
    return {"status": status, "checks": checks}
```

---

## 🚦 LOAD BALANCING STRATEGY

### 1. Multiple OMS Instances
```bash
# Scale OMS horizontally
docker-compose -f docker-compose.apps.yml up -d --scale oms=3
```

### 2. NGINX Load Balancer
```nginx
upstream oms_backend {
    least_conn;
    server oms_1:8099 max_fails=3 fail_timeout=30s;
    server oms_2:8099 max_fails=3 fail_timeout=30s;
    server oms_3:8099 max_fails=3 fail_timeout=30s;
}

server {
    listen 8099;
    location / {
        proxy_pass http://oms_backend;
        proxy_next_upstream error timeout invalid_header http_500;
    }
}
```

---

## 🔍 DEBUGGING SLOW SERVICES

### 1. Profile Service Performance
```python
# Add profiling endpoint
import cProfile
import pstats
import io

@app.get("/debug/profile")
async def profile_endpoint():
    pr = cProfile.Profile()
    pr.enable()

    # Run sample workload
    for _ in range(100):
        await process_order(sample_order)

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)

    return {"profile": s.getvalue()}
```

### 2. Trace Request Flow
```python
import opentelemetry

# Add tracing
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

async def process_order(order):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order['order_id'])

        with tracer.start_span("risk_check"):
            risk_result = await check_risk(order)

        with tracer.start_span("persist_order"):
            await save_order(order)

        return result
```

---

## 📈 EXPECTED IMPROVEMENTS

After implementing these optimizations:

| Service | Current | Expected | Improvement |
|---------|---------|----------|-------------|
| OMS | 250ms | <10ms | 25x |
| Risk | >10ms | <1.5ms | 10x |
| Throughput | 4 ops/s | 100 ops/s | 25x |
| Memory | 4.5GB | 3.5GB | -22% |

---

## 🎯 IMPLEMENTATION PRIORITY

### Phase 1: Quick Fixes (2 hours)
1. Fix health check endpoints
2. Add connection pooling
3. Enable caching

### Phase 2: Core Optimizations (4 hours)
1. Implement async processing
2. Add batch processing
3. Create fast paths

### Phase 3: Advanced Optimizations (4 hours)
1. Add horizontal scaling
2. Implement load balancing
3. Add detailed monitoring

### Phase 4: Testing & Validation (2 hours)
1. Run load tests
2. Measure improvements
3. Fine-tune parameters

---

## 📝 TESTING OPTIMIZATIONS

### Load Test Script
```python
# test_optimized_performance.py
import asyncio
import aiohttp
import time
import statistics

async def load_test(num_requests=1000):
    async with aiohttp.ClientSession() as session:
        start = time.time()
        tasks = []

        for i in range(num_requests):
            order = {
                "symbol": "BTCUSDT",
                "side": "buy" if i % 2 else "sell",
                "quantity": 0.001,
                "price": 45000 + (i % 100),
                "order_type": "LIMIT"
            }
            task = session.post('http://localhost:8099/orders', json=order)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        duration = time.time() - start
        successful = sum(1 for r in responses if not isinstance(r, Exception))

        print(f"Requests: {num_requests}")
        print(f"Duration: {duration:.2f}s")
        print(f"Throughput: {num_requests/duration:.1f} req/s")
        print(f"Success rate: {successful/num_requests*100:.1f}%")

asyncio.run(load_test(1000))
```

---

## ✅ VALIDATION CHECKLIST

After optimizations:
- [ ] All services report healthy
- [ ] OMS latency < 10ms P50
- [ ] Risk latency < 1.5ms P50
- [ ] System handles 100+ orders/sec
- [ ] Memory usage < 4GB total
- [ ] CPU usage < 50% under load
- [ ] No errors in logs
- [ ] Data persistence working

---

**Created**: 2025-10-17
**Purpose**: Optimization guide for Trade2026 services
**Target**: 25x performance improvement