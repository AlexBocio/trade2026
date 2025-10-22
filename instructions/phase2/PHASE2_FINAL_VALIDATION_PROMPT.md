# PHASE 2 FINAL VALIDATION PROMPT

**For**: Claude Code  
**Phase**: 2 Final - Complete Backend Validation  
**Estimated Time**: 3 hours  
**Prerequisites**: Phase 2A + 2B complete  
**Status**: Execute after all services deployed

---

## 🎯 OBJECTIVE

Perform comprehensive validation of the entire Phase 2 backend system before proceeding to Phase 3 (Frontend Integration).

This is the **FINAL GATE** before frontend work begins.

---

## 📋 VALIDATION SCOPE

### Services to Validate (11-13 services)

**Phase 1 Infrastructure** (8 services):
- PostgreSQL, NATS, Valkey, QuestDB
- ClickHouse, SeaweedFS, OpenSearch, OPA

**Phase 2A - Critical Trading Core** (3 services):
- risk (8103)
- oms (8099)
- exeq (8095)

**Phase 2B - Supporting Services** (6 services):
- ptrc (8109)
- pnl (8100)
- hot_cache (8088)
- questdb_writer (8090)
- feast-pipeline (8104) - optional
- execution-quality (8096) - optional

**Phase 2 P1-P2** (5 services):
- normalizer (8081)
- sink-ticks (8111)
- sink-alt (8112)
- gateway (8080)
- live-gateway (8200)

**Total**: 11-13 application services + 8 infrastructure = 19-21 services

---

## 🔍 VALIDATION TESTS

### Test Suite 1: Service Health (30 minutes)

**Test 1.1: All Containers Running**
```bash
cd infrastructure/docker
docker-compose -f docker-compose.core.yml -f docker-compose.apps.yml ps

# Check for:
# - All services showing "Up" or "healthy"
# - No "Restarting" or "Exited" states
# - Uptime > 5 minutes
```

**Test 1.2: Health Check Endpoints**
```bash
# Infrastructure
curl http://localhost:9000/  # QuestDB
curl http://localhost:8123/ping  # ClickHouse
curl http://localhost:8333/status  # SeaweedFS
curl http://localhost:9200/  # OpenSearch

# Application Services
curl http://localhost:8103/health  # risk
curl http://localhost:8099/health  # oms
curl http://localhost:8095/health  # exeq
curl http://localhost:8109/health  # ptrc
curl http://localhost:8100/health  # pnl
curl http://localhost:8081/health  # normalizer
curl http://localhost:8080/health  # gateway
curl http://localhost:8200/health  # live-gateway

# All should return 200 OK with {"status":"healthy"}
```

**Success Criteria**:
- [ ] All containers running
- [ ] All health checks passing
- [ ] No services in error state
- [ ] Uptime stable (no restarts)

---

### Test Suite 2: Data Pipeline (45 minutes)

**Test 2.1: Market Data Flow**
```
Exchange → Gateway → NATS → Normalizer → QuestDB
                           → Sink-Ticks → Delta Lake (SeaweedFS)
```

**Validation Steps**:
```bash
# 1. Check gateway producing ticks
docker logs gateway --tail 100 | grep "Published tick"

# 2. Check NATS streams
docker exec -it nats nats stream ls
docker exec -it nats nats stream info MARKET_TICKS

# 3. Check normalizer consuming
docker logs normalizer --tail 100 | grep "Processed"

# 4. Check QuestDB has data
curl "http://localhost:9000/exec?query=SELECT COUNT(*) FROM ohlcv_1m WHERE timestamp > now() - interval '1 hour'"

# 5. Check Delta Lake
docker logs sink-ticks --tail 100 | grep "Written"
```

**Success Criteria**:
- [ ] Gateway publishing ticks to NATS
- [ ] NATS streams active and growing
- [ ] Normalizer consuming and processing
- [ ] QuestDB receiving bar data
- [ ] Delta Lake receiving tick data
- [ ] No data loss or errors

---

**Test 2.2: Trading Flow**
```
Order Submit → Risk Check → OMS → EXEQ → Live Gateway → Exchange
                                → PTRC → PNL
```

**Validation Steps**:
```bash
# 1. Submit test order
curl -X POST http://localhost:8099/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 0.001,
    "price": 45000,
    "type": "limit",
    "account": "test_account"
  }'

# Expected: Order accepted, returns order_id

# 2. Check risk service processed
docker logs risk --tail 50 | grep "Risk check"

# 3. Check OMS processed
curl http://localhost:8099/orders/{order_id}

# 4. Check PTRC tracking
curl http://localhost:8109/positions

# 5. Check PNL calculated
curl http://localhost:8100/pnl/realtime
```

**Success Criteria**:
- [ ] Order submission successful
- [ ] Risk check executed (< 1.5ms)
- [ ] OMS tracking order state
- [ ] PTRC recording position
- [ ] PNL calculating correctly
- [ ] Full flow end-to-end working

---

### Test Suite 3: Performance Benchmarks (60 minutes)

**Test 3.1: Risk Service Latency**
```bash
# Run 1000 risk checks, measure latency
# Target: P50 ≤ 1.5ms, P99 ≤ 5ms

# Test script (create test-risk-latency.sh):
for i in {1..1000}; do
  time curl -X POST http://localhost:8103/check \
    -H "Content-Type: application/json" \
    -d '{"symbol":"BTCUSDT","quantity":0.1,"price":45000}'
done
```

**Success Criteria**:
- [ ] P50 latency ≤ 1.5ms
- [ ] P99 latency ≤ 5ms
- [ ] No timeouts
- [ ] No errors

---

**Test 3.2: OMS Throughput**
```bash
# Submit 1000 orders/sec for 1 minute
# Target: P50 ≤ 10ms, P99 ≤ 50ms, 0% error rate

# Use load testing tool or script
```

**Success Criteria**:
- [ ] Can handle 1000 orders/sec
- [ ] P50 latency ≤ 10ms
- [ ] P99 latency ≤ 50ms
- [ ] Error rate < 0.1%
- [ ] No crashes

---

**Test 3.3: Data Pipeline Throughput**
```bash
# Check normalizer throughput
docker logs normalizer --tail 1000 | grep "ticks/sec"

# Check sink-ticks throughput
docker logs sink-ticks --tail 1000 | grep "writes/sec"

# Target: 100k ticks/sec (normalizer), 50k writes/sec (sink-ticks)
```

**Success Criteria**:
- [ ] Normalizer: 100k+ ticks/sec
- [ ] Sink-ticks: 50k+ writes/sec
- [ ] No backlog building
- [ ] CPU usage < 80%

---

### Test Suite 4: Integration Tests (45 minutes)

**Test 4.1: Service Communication via NATS**
```bash
# Check NATS subscriptions
docker exec -it nats nats consumer ls MARKET_TICKS
docker exec -it nats nats sub 'risk.>'
docker exec -it nats nats sub 'orders.>'
docker exec -it nats nats sub 'fills.>'
docker exec -it nats nats sub 'positions.>'

# Verify all services subscribed
```

**Success Criteria**:
- [ ] All expected subscriptions present
- [ ] Messages flowing
- [ ] No subscription errors
- [ ] Pub/sub working correctly

---

**Test 4.2: Database Connectivity**
```bash
# QuestDB
curl "http://localhost:9000/exec?query=SELECT COUNT(*) FROM ohlcv_1m"
# Should have data

# ClickHouse
curl "http://localhost:8123/?query=SELECT COUNT(*) FROM trade2026.fills"
# Should have data (if any fills)

# Valkey
docker exec -it valkey redis-cli PING
# Should return PONG

# Check service connections
docker logs risk --tail 100 | grep "Connected to Redis"
docker logs oms --tail 100 | grep "Connected to"
```

**Success Criteria**:
- [ ] All databases accessible
- [ ] All services connected
- [ ] Data persisting correctly
- [ ] No connection errors

---

**Test 4.3: Cross-Service Data Flow**
```bash
# Submit order → verify in multiple services

# 1. Submit via OMS
ORDER_ID=$(curl -X POST http://localhost:8099/orders ... | jq -r '.order_id')

# 2. Check in risk logs
docker logs risk | grep $ORDER_ID

# 3. Check in OMS
curl http://localhost:8099/orders/$ORDER_ID

# 4. Check in PTRC
curl http://localhost:8109/orders/$ORDER_ID

# 5. Check in PNL (if filled)
curl http://localhost:8100/pnl/positions
```

**Success Criteria**:
- [ ] Order tracked across services
- [ ] Data consistency maintained
- [ ] No data loss
- [ ] Timing correct

---

### Test Suite 5: Resilience Tests (30 minutes)

**Test 5.1: Service Restart**
```bash
# Restart each critical service, verify recovery

# Risk service
docker restart risk
sleep 30
curl http://localhost:8103/health

# OMS service
docker restart oms
sleep 30
curl http://localhost:8099/health

# Verify all services reconnected
docker logs risk --tail 50 | grep "Connected"
docker logs oms --tail 50 | grep "Connected"
```

**Success Criteria**:
- [ ] Services restart cleanly
- [ ] Reconnect to dependencies
- [ ] Resume processing
- [ ] No data loss

---

**Test 5.2: NATS Failover**
```bash
# Restart NATS while services running
docker restart nats
sleep 10

# Check services reconnect
docker logs risk --tail 50 | grep "reconnect"
docker logs oms --tail 50 | grep "reconnect"

# Verify message flow resumes
docker exec -it nats nats sub 'ticks.>' --count 10
```

**Success Criteria**:
- [ ] Services detect NATS down
- [ ] Services reconnect automatically
- [ ] Message flow resumes
- [ ] No crashes

---

**Test 5.3: Database Failover**
```bash
# Restart Valkey
docker restart valkey
sleep 10

# Check services handle it
docker logs risk --tail 100
docker logs oms --tail 100

# Verify operations resume
curl http://localhost:8103/health
curl http://localhost:8099/health
```

**Success Criteria**:
- [ ] Services handle DB restart
- [ ] Reconnect automatically
- [ ] Operations resume
- [ ] No data corruption

---

### Test Suite 6: Error Handling (30 minutes)

**Test 6.1: Invalid Order**
```bash
# Submit invalid order
curl -X POST http://localhost:8099/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "INVALID",
    "side": "buy",
    "quantity": -1,
    "price": -100
  }'

# Should reject with clear error
```

**Success Criteria**:
- [ ] Invalid order rejected
- [ ] Clear error message
- [ ] No service crash
- [ ] Error logged properly

---

**Test 6.2: Risk Limit Breach**
```bash
# Submit order that exceeds risk limits
curl -X POST http://localhost:8099/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 1000,
    "price": 45000
  }'

# Should be rejected by risk service
```

**Success Criteria**:
- [ ] Order rejected by risk
- [ ] Clear rejection reason
- [ ] Logged in risk service
- [ ] OMS updated order status

---

## 📊 VALIDATION SCORECARD

### Critical Requirements (Must Pass All)
- [ ] All services healthy
- [ ] All health checks passing
- [ ] Data pipeline working end-to-end
- [ ] Trading flow working end-to-end
- [ ] Risk latency ≤ 1.5ms P50
- [ ] OMS latency ≤ 10ms P50
- [ ] No critical errors in logs

### Important Requirements (Must Pass 90%+)
- [ ] Performance benchmarks met
- [ ] Integration tests passing
- [ ] Resilience tests passing
- [ ] Error handling correct
- [ ] Data consistency verified
- [ ] Service communication working
- [ ] Database connectivity stable

### Nice-to-Have (Target 80%+)
- [ ] All optional services working
- [ ] Advanced analytics operational
- [ ] ML pipeline functional
- [ ] Complete monitoring data

---

## 🚦 DECISION CRITERIA

### PASS ✅ - Proceed to Phase 3
**Requirements**:
- All critical requirements met
- 90%+ important requirements met
- 80%+ nice-to-have met
- No blocking issues
- System stable for 1+ hour

**Action**: Proceed to Phase 3 (Frontend Integration)

---

### CONDITIONAL PASS ⚠️ - Proceed with Cautions
**Requirements**:
- All critical requirements met
- 80%+ important requirements met
- Known issues documented
- Workarounds identified

**Action**: Proceed to Phase 3 with caution list

---

### FAIL ❌ - Do Not Proceed
**If ANY of these**:
- Critical requirement failed
- < 80% important requirements
- Unstable services
- Data loss detected
- Performance way below targets

**Action**: Debug, fix, re-validate

---

## 📝 VALIDATION REPORT

Create a validation report with:

### 1. Executive Summary
- Overall status (PASS/CONDITIONAL/FAIL)
- Key metrics
- Critical issues (if any)
- Recommendation

### 2. Detailed Results
- Test suite results
- Performance metrics
- Integration test outcomes
- Error analysis

### 3. Service Inventory
- List of operational services
- Health status of each
- Performance of each
- Issues per service

### 4. Known Issues
- Non-blocking issues
- Workarounds
- Future improvements needed

### 5. Next Steps
- Proceed to Phase 3? Yes/No
- What needs fixing (if NO)
- Cautions for Phase 3 (if conditional)

---

## 🎯 DELIVERABLES

1. **Validation Report** - docs/PHASE2_VALIDATION_REPORT.md
2. **Performance Metrics** - docs/PHASE2_PERFORMANCE_METRICS.md
3. **Service Health Status** - docs/PHASE2_SERVICE_STATUS.md
4. **Updated Tracker** - COMPLETION_TRACKER.md
5. **Session Summary** - SESSION_SUMMARY_PHASE2_VALIDATION.md

---

## ⚠️ CRITICAL NOTES

### Do Not Skip
- This validation is MANDATORY
- Cannot proceed to Phase 3 without passing
- Phase 3 depends on stable backend

### Time Investment
- Allow full 3 hours for comprehensive testing
- Don't rush the validation
- Better to find issues now than in Phase 3

### If Tests Fail
- Stop immediately
- Debug thoroughly
- Fix all critical issues
- Re-run full validation

---

## 🚀 AFTER VALIDATION

### If PASS:
1. Update COMPLETION_TRACKER.md
2. Create validation report
3. Commit all changes
4. Proceed to Phase 3 Validation Gate
5. Begin Phase 3 execution

### If FAIL:
1. Document all failures
2. Prioritize fixes
3. Fix critical issues first
4. Re-run validation
5. Do NOT proceed until passing

---

**Prompt Status**: ✅ READY FOR CLAUDE CODE

**Execute After**: Phase 2A + 2B complete

**Execution Time**: 3 hours

**Complexity**: High (comprehensive validation)

**Critical**: MANDATORY gate before Phase 3

---

**Created By**: Claude (Sonnet 4.5)  
**Date**: 2025-10-16  
**For**: Claude Code Execution  
**Phase**: 2 Final Validation
