# Phase 3 - Prompt 00: Validation Gate

**Phase**: 3 - Frontend Integration  
**Prompt**: 00 (Validation Gate)  
**Purpose**: Validate Phase 2 complete before starting Phase 3  
**Duration**: 10 minutes  
**Status**: ⏸️ Run before any Phase 3 work

---

## 🛑 MANDATORY PREREQUISITES

### Phase 2 Must Be Complete

Before starting Phase 3, you **MUST** verify Phase 2 is complete and operational.

---

## ✅ PHASE 2 VALIDATION CHECKLIST

### 1. All Backend Services Running

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Check all services
docker-compose -f docker-compose.base.yml -f docker-compose.apps.yml ps

# Expected: All services showing "healthy" status
```

**Required Services** (minimum for MVP):

**Core Infrastructure** (8 services):
- [ ] nats - running (healthy)
- [ ] valkey - running (healthy)
- [ ] questdb - running (healthy)
- [ ] clickhouse - running (healthy)
- [ ] seaweedfs - running (healthy)
- [ ] opensearch - running (healthy)
- [ ] authn - running (healthy)
- [ ] opa - running (healthy)

**Application Services** (minimum 7 services):
- [ ] normalizer - running (healthy)
- [ ] sink-ticks - running (healthy)
- [ ] sink-alt - running (healthy)
- [ ] gateway - running (healthy)
- [ ] live-gateway - running (healthy)
- [ ] risk - running (healthy)
- [ ] oms - running (healthy)

**Additional Services** (optional but recommended):
- [ ] ptrc - running (healthy)
- [ ] feast-pipeline - running (healthy)
- [ ] execution-quality - running (healthy)

---

### 2. Backend API Endpoints Accessible

Test that all backend services are responding:

```bash
# Test OMS API
curl -f http://localhost:8099/health
# Expected: {"status": "healthy"}

# Test Risk API
curl -f http://localhost:8103/health
# Expected: {"status": "healthy"}

# Test Gateway API
curl -f http://localhost:8080/health
# Expected: {"status": "healthy"}

# Test Live Gateway API
curl -f http://localhost:8200/health
# Expected: {"status": "healthy"}
```

**All health checks must return 200 OK**

- [ ] OMS health check passes (port 8099)
- [ ] Risk health check passes (port 8103)
- [ ] Gateway health check passes (port 8080)
- [ ] Live Gateway health check passes (port 8200)
- [ ] PTRC health check passes (port 8109) - optional

---

### 3. Data Pipeline Operational

Verify end-to-end data flow:

```bash
# Check NATS has data flowing
docker exec -it nats nats stream ls
# Expected: See streams

# Check QuestDB has data
curl "http://localhost:9000/exec?query=SELECT%20COUNT(*)%20FROM%20ohlcv_1m"
# Expected: Should have records

# Check ClickHouse has data
curl "http://localhost:8123/?query=SELECT%20COUNT(*)%20FROM%20trade2026.fills"
# Expected: Should have records (if any trades executed)
```

**Data Flow Checks**:
- [ ] NATS streams exist and active
- [ ] QuestDB has OHLCV data
- [ ] Market data flowing
- [ ] No errors in logs

---

### 4. Trading Flow Functional

Test core trading functionality:

```bash
# Submit test order via OMS
curl -X POST http://localhost:8099/orders \
  -H "Content-Type: application/json" \
  -d '{
    "account": "test_account",
    "symbol": "BTCUSDT",
    "side": "buy",
    "type": "limit",
    "quantity": 0.001,
    "price": 45000.0
  }'

# Expected: {"status": "submitted", "order_id": "..."}
```

**Trading Flow Checks**:
- [ ] Order submission works
- [ ] Risk checks executing (< 1.5ms)
- [ ] Orders routing to live-gateway
- [ ] Paper trading functional
- [ ] Position tracking working

---

### 5. Performance Benchmarks Met

Verify Phase 2 performance requirements:

```bash
# Check risk service latency
docker logs risk | grep "latency" | tail -20
# Expected: P50 < 1.5ms

# Check OMS latency
docker logs oms | grep "latency" | tail -20
# Expected: P50 < 10ms

# Check no errors
docker logs risk | grep "ERROR" | tail -20
docker logs oms | grep "ERROR" | tail -20
# Expected: No recent errors
```

**Performance Checks**:
- [ ] Risk service P50 ≤ 1.5ms
- [ ] OMS P50 ≤ 10ms
- [ ] No errors in logs
- [ ] Services stable (no restarts)

---

### 6. Docker Networks Configured

Verify CPGS v1.0 network configuration:

```bash
# Check networks exist
docker network ls | grep trade2026

# Expected:
# trade2026_frontend
# trade2026_lowlatency
# trade2026_backend
```

**Network Checks**:
- [ ] trade2026_frontend network exists
- [ ] trade2026_lowlatency network exists
- [ ] trade2026_backend network exists

---

### 7. Configuration Files Ready

Verify all backend configuration files exist:

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Check configs exist
ls -la config/backend/oms/config.yaml
ls -la config/backend/risk/config.yaml
ls -la config/backend/gateway/config.yaml
ls -la config/backend/live_gateway/config.yaml
```

**Config Checks**:
- [ ] All backend config files exist
- [ ] All configs use Docker service names (not localhost)
- [ ] Secrets properly configured

---

## 🚦 VALIDATION DECISION

### All Prerequisites Met?

**Count your checkmarks above**:

**✅ ALL CHECKS PASSED** (minimum 30+ checks)?
→ **PROCEED TO PHASE 3**

**❌ ANY CHECKS FAILED**?
→ **STOP - Fix Phase 2 first**

**Partial Success**?
→ **Review failures, determine if blocking**

---

## 🛑 STOP CONDITIONS

**DO NOT PROCEED to Phase 3 if**:

1. **Less than 7 app services running**
   - Minimum: normalizer, sink-ticks, sink-alt, gateway, live-gateway, risk, oms
   - Without these, frontend has nothing to connect to

2. **Core trading flow broken**
   - Must be able to submit orders
   - Must be able to get positions
   - Must be able to view market data

3. **Performance SLAs not met**
   - Risk service > 1.5ms consistently
   - OMS experiencing errors
   - Services crashing or restarting

4. **Data pipeline not working**
   - No market data flowing
   - Database writes failing
   - NATS not operational

---

## ✅ PROCEED CONDITIONS

**You can PROCEED to Phase 3 if**:

**Minimum Requirements** (MVP):
- [ ] 7+ app services healthy
- [ ] Core trading flow works
- [ ] Can submit orders via API
- [ ] Can query positions via API
- [ ] Market data accessible via API
- [ ] No critical errors

**Optimal Requirements** (Recommended):
- [ ] 11+ app services healthy (includes P4 services)
- [ ] All performance SLAs met
- [ ] All data flows operational
- [ ] Complete test suite passing

---

## 📋 PRE-PHASE 3 CHECKLIST

### Before Starting Phase 3

1. **Document Current State**
   ```bash
   # Save current service status
   docker-compose -f docker-compose.base.yml -f docker-compose.apps.yml ps > phase2_final_status.txt
   
   # Test all endpoints
   curl http://localhost:8099/health > oms_health.txt
   curl http://localhost:8103/health > risk_health.txt
   ```

2. **Backup Current Configuration**
   ```bash
   # Backup configs before Phase 3 changes
   cp -r config config_phase2_backup
   ```

3. **Review Phase 2 Completion Tracker**
   ```bash
   # Check completion status
   cat COMPLETION_TRACKER.md | grep "Phase 2"
   ```

4. **Identify API Endpoints for Frontend**
   - List all backend services the frontend will call
   - Document API endpoints and ports
   - Note authentication requirements

---

## 📊 VALIDATION SUMMARY

### Validation Complete

**Date**: _____________  
**Validator**: _____________

**Phase 2 Services Count**:
- Infrastructure: ____ / 8
- Applications: ____ / 7 (minimum)
- Applications: ____ / 11 (recommended)

**Core Functionality**:
- [ ] Order submission: Working / Failed
- [ ] Position tracking: Working / Failed
- [ ] Market data: Working / Failed
- [ ] Risk checks: Working / Failed

**Performance**:
- Risk P50: ______ ms (SLA: ≤ 1.5ms)
- OMS P50: ______ ms (SLA: ≤ 10ms)

**Decision**: 
- [ ] ✅ PROCEED TO PHASE 3
- [ ] ❌ FIX PHASE 2 ISSUES FIRST

---

## 🚀 READY FOR PHASE 3

If validation passed, you're ready to proceed!

**Next Prompt**: PHASE3_PROMPT01_SURVEY_FRONTEND_CODE.md

**What Phase 3 Will Do**:
1. Survey GUI frontend codebase
2. Copy frontend to Trade2026
3. Replace mock APIs with real backend calls
4. Setup Nginx reverse proxy
5. Build and deploy frontend
6. Test all integrations
7. Complete MVP platform

**Estimated Time**: 1-2 weeks (8 prompts)

---

**Validation Gate Status**: ⏸️ PENDING

**Phase 2 Required**: Yes - Must be complete

**Next Action**: Run this validation, then proceed to Prompt 01
