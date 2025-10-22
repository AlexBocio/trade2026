# PHASE 2A PROMPT - Critical Trading Core Migration

**For**: Claude Code  
**Phase**: 2A - Backend Migration (Critical Trading Core)  
**Services**: risk, oms, exeq  
**Estimated Time**: 20 hours  
**Status**: Ready to Execute

---

## 🎯 OBJECTIVE

Migrate and deploy the critical trading core services (risk, oms, exeq) following the comprehensive test-integrate-validate methodology.

---

## 📋 SERVICES TO MIGRATE

### Group 1: Risk Service (6 hours)
- **Service**: risk (Risk Management)
- **Port**: 8103
- **Priority**: P3 (CRITICAL)
- **SLA**: P50 ≤ 1.5ms latency
- **Source**: C:\Trade2025\trading\apps\risk\
- **Target**: C:\ClaudeDesktop_Projects\trade2026\backend\apps\risk\

### Group 2: OMS Service (8 hours)
- **Service**: oms (Order Management System)
- **Port**: 8099
- **Priority**: P3 (CRITICAL)
- **SLA**: P50 ≤ 10ms, P99 ≤ 50ms
- **Source**: C:\Trade2025\trading\apps\oms\
- **Target**: C:\ClaudeDesktop_Projects\trade2026\backend\apps\oms\
- **Depends On**: risk service

### Group 3: EXEQ Service (6 hours)
- **Service**: exeq (Execution & Queueing)
- **Port**: 8095
- **Priority**: P1 (High)
- **Source**: C:\Trade2025\trading\apps\exeq\
- **Target**: C:\ClaudeDesktop_Projects\trade2026\backend\apps\exeq\
- **Depends On**: oms service

---

## 🔄 UNIVERSAL MIGRATION PATTERN

For EACH service, follow these 10 steps:

### Step 1: Survey Service
```
1. Check if code already exists in backend/apps/{service}/
2. If exists: Review and document
3. If missing: Copy from Trade2025
4. Document dependencies, ports, networks
```

### Step 2: Create Configuration
```
1. Create config/backend/{service}/config.yaml
2. Set correct ports (match docker-compose.apps.yml)
3. Update all URLs (localhost → Docker service names)
4. Configure dependencies (NATS, Valkey, QuestDB, etc.)
```

### Step 3: Verify/Update Code
```
1. Check all localhost references → replace with service names
2. Verify configuration loading (path: /app/config/config.yaml)
3. Check secrets loading if needed
4. Ensure health check endpoint exists
```

### Step 4: Verify Dockerfile
```
1. Check Dockerfile exists
2. Verify health check uses correct port
3. Verify EXPOSE statements correct
4. Check requirements.txt complete
```

### Step 5: Build Docker Image
```bash
cd backend/apps/{service}
docker build -t localhost/{service}:latest .
docker images | grep {service}
```

### Step 6: Verify docker-compose Entry
```
1. Check service defined in docker-compose.apps.yml
2. Verify ports match
3. Verify networks correct (frontend/lowlatency/backend)
4. Verify dependencies listed
5. Verify health check configured
```

### Step 7: Start Service
```bash
cd infrastructure/docker
docker-compose -f docker-compose.apps.yml up -d {service}
docker logs {service} --tail 50
```

### Step 8: Component Testing
```
Test 1: Container starts
- docker ps --filter "name={service}"
- Check status: "Up" or "healthy"

Test 2: Health check passes
- curl http://localhost:{port}/health
- Expected: {"status":"healthy"}

Test 3: Service logs clean
- docker logs {service} --tail 100
- Look for: "Started", "Connected", no errors
```

### Step 9: Integration Testing
```
Test 1: NATS connectivity
- Check logs for "Connected to NATS"
- docker exec -it nats nats sub '{service}.>'

Test 2: Redis/Valkey connectivity
- Check logs for "Connected to Redis"

Test 3: Database connectivity (if applicable)
- Check logs for QuestDB/ClickHouse connections

Test 4: Service-to-service communication
- For risk: Test pre-trade risk check
- For oms: Test order submission
- For exeq: Test order queueing
```

### Step 10: Validation Gate
```
Checklist:
- [ ] Service healthy
- [ ] Health check passes
- [ ] NATS connected
- [ ] Redis connected
- [ ] Database connected (if applicable)
- [ ] Component tests pass
- [ ] Integration tests pass
- [ ] No errors in logs
- [ ] Performance acceptable

Decision: PASS ✓ → Next service | FAIL ✗ → Fix issues
```

---

## 🚀 EXECUTION ORDER

### Phase 2A-1: Risk Service (6 hours)

**Prerequisites**:
- [ ] NATS healthy
- [ ] Valkey healthy
- [ ] QuestDB healthy

**Execute**:
1. Follow 10-step pattern for risk service
2. Pay special attention to port configuration (8103 in compose vs 8097 in code)
3. **CRITICAL**: Fix port conflicts before building
4. Test risk check endpoint: POST to risk.check.order via NATS
5. Validate P50 latency < 1.5ms

**Validation**:
```bash
# Test risk check
curl http://localhost:8103/health
curl http://localhost:8103/stats
curl http://localhost:8103/risk/portfolio
curl http://localhost:8103/risk/limits
```

**Success Criteria**:
- [ ] Risk service healthy
- [ ] Risk checks responding
- [ ] Latency P50 < 1.5ms
- [ ] Portfolio risk calculation working
- [ ] Can block/unblock symbols

---

### Phase 2A-2: OMS Service (8 hours)

**Prerequisites**:
- [ ] Risk service healthy and validated
- [ ] All Phase 2A-1 tests passing

**Execute**:
1. Follow 10-step pattern for oms service
2. Configure RISK_SERVICE_URL=http://risk:8103
3. Test order submission flow
4. Validate order lifecycle management

**Validation**:
```bash
# Test OMS
curl http://localhost:8099/health
curl http://localhost:8099/stats

# Submit test order
curl -X POST http://localhost:8099/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 0.001,
    "price": 45000,
    "type": "limit"
  }'
```

**Success Criteria**:
- [ ] OMS service healthy
- [ ] Can submit orders
- [ ] Orders pass through risk checks
- [ ] Order state management working
- [ ] Latency P50 < 10ms, P99 < 50ms

---

### Phase 2A-3: EXEQ Service (6 hours)

**Prerequisites**:
- [ ] OMS service healthy and validated
- [ ] All Phase 2A-2 tests passing

**Execute**:
1. Follow 10-step pattern for exeq service
2. Configure order routing
3. Test execution queueing

**Validation**:
```bash
# Test EXEQ
curl http://localhost:8095/health
curl http://localhost:8095/stats
```

**Success Criteria**:
- [ ] EXEQ service healthy
- [ ] Order queueing working
- [ ] Smart routing logic functional

---

## 🔒 CRITICAL VALIDATION GATE

After ALL THREE services are deployed, run this comprehensive validation:

### Test 1: Full Trading Flow
```
Submit Order → Risk Check → OMS Accept → EXEQ Queue → Route to Exchange
```

### Test 2: Load Test
```
- Generate 1000 orders/sec
- Sustain for 5 minutes
- Monitor latencies
```

### Test 3: Performance Validation
```
- Risk P50 ≤ 1.5ms ✓
- OMS P50 ≤ 10ms ✓
- OMS P99 ≤ 50ms ✓
- No errors ✓
- No crashes ✓
```

### Test 4: Integration Validation
```
- All services communicating via NATS ✓
- Risk checks blocking invalid orders ✓
- OMS tracking order state correctly ✓
- EXEQ routing orders properly ✓
```

**CRITICAL**: Do NOT proceed to Phase 2B until ALL validation tests pass.

---

## 📊 SUCCESS METRICS

### Per-Service Success
- [ ] Service builds successfully
- [ ] Service starts and stays healthy
- [ ] Health check passes
- [ ] Integration tests pass
- [ ] Performance benchmarks met
- [ ] No errors in logs

### Phase 2A Success
- [ ] All 3 services operational
- [ ] Full trading flow working
- [ ] Load test passed
- [ ] All latency SLAs met
- [ ] CRITICAL validation gate passed

---

## 🛠️ TOOLS & COMMANDS

### Build Image
```bash
docker build -t localhost/{service}:latest backend/apps/{service}
```

### Start Service
```bash
cd infrastructure/docker
docker-compose -f docker-compose.apps.yml up -d {service}
```

### Check Logs
```bash
docker logs {service} -f
```

### Check Health
```bash
curl http://localhost:{port}/health
```

### Restart Service
```bash
docker-compose -f docker-compose.apps.yml restart {service}
```

### Check All Services
```bash
docker-compose -f docker-compose.core.yml -f docker-compose.apps.yml ps
```

---

## 📁 REFERENCE FILES

**Instructions**:
- instructions/PHASE2_PROMPT04_MIGRATE_P3_SERVICES_CRITICAL.md

**Service Inventory**:
- docs/BACKEND_SERVICES_INVENTORY.md

**Docker Compose**:
- infrastructure/docker/docker-compose.apps.yml

**Progress Tracker**:
- COMPLETION_TRACKER.md

---

## ⚠️ CRITICAL NOTES

### Port Conflicts
- **Risk**: docker-compose uses 8103, but code may use 8097
- **Action**: Fix code to use 8103 before building

### Service Names
- Always use Docker service names (nats, valkey, questdb)
- NEVER use localhost in service code

### Configuration Paths
- All configs must be at /app/config/config.yaml
- Mount point: config/backend/{service}:/app/config:ro

### Health Checks
- Must respond on configured port
- Must return {"status":"healthy"}
- Must be reliable (no false negatives)

### Testing Order
- Component tests first (isolated)
- Integration tests second (with dependencies)
- Performance tests third (under load)
- Full validation last (end-to-end)

---

## 🎯 DELIVERABLES

When Phase 2A is complete, you should have:

1. **3 Services Running**:
   - risk (port 8103)
   - oms (port 8099)
   - exeq (port 8095)

2. **All Configs Created**:
   - config/backend/risk/config.yaml
   - config/backend/oms/config.yaml
   - config/backend/exeq/config.yaml

3. **All Tests Passing**:
   - Component tests ✓
   - Integration tests ✓
   - Performance tests ✓
   - Critical validation gate ✓

4. **Documentation Updated**:
   - COMPLETION_TRACKER.md updated
   - Session summary created

---

## 📝 EXECUTION CHECKLIST

Before starting:
- [ ] Read this entire prompt
- [ ] Verify Phase 1 infrastructure running
- [ ] Verify Phase 2 P1+P2 services running (5 services)
- [ ] Have Trade2025 source available (if needed)

During execution:
- [ ] Follow 10-step pattern for each service
- [ ] Test at every step (component → integration → performance)
- [ ] Document issues and solutions
- [ ] Update COMPLETION_TRACKER.md after each service

After completion:
- [ ] Run CRITICAL validation gate
- [ ] All tests must pass before proceeding
- [ ] Update documentation
- [ ] Create session summary

---

## 🚦 NEXT STEPS AFTER PHASE 2A

If CRITICAL validation gate passes:
→ Proceed to Phase 2B (ptrc + supporting services)

If validation fails:
→ Debug and fix issues
→ Re-run validation
→ Do NOT proceed until passing

---

**Prompt Status**: ✅ READY FOR CLAUDE CODE

**Execution Time**: 20 hours (6h + 8h + 6h)

**Complexity**: High (Critical trading core)

**Validation**: Mandatory CRITICAL gate

**Success Probability**: High (with comprehensive testing)

---

**Created By**: Claude (Sonnet 4.5)  
**Date**: 2025-10-16  
**For**: Claude Code Execution  
**Phase**: 2A - Critical Trading Core
