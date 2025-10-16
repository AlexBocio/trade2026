# Phase 2 Next Tasks - Quick Reference

**Current Status**: Task 02 (P1 Services) in progress with Claude Code  
**Created**: 2025-10-14  
**Purpose**: Quick reference for remaining Phase 2 tasks

---

## 📋 PHASE 2 TASK SEQUENCE

### ✅ Task 01: Survey (COMPLETE)
**Time**: 2 hours  
**Status**: ✅ Done  
**Result**: 18 services documented, priorities established

---

### ⏳ Task 02: P1 Services (IN PROGRESS)
**File**: `PHASE2_02_MIGRATE_P1_SERVICES.md`  
**Services**: normalizer, sink-ticks, sink-alt  
**Time**: 8 hours  
**Status**: ⏳ Claude Code is implementing this now  
**Next**: Wait for completion and validation

---

### ⏸️ Task 03: P2 Services (NEXT)
**Services**: gateway (6h), live-gateway (5h)  
**Time**: 11 hours  
**Dependencies**: Task 02 must pass validation  
**Priority**: Data ingestion services

**What to do**:
1. Wait for Task 02 validation to pass
2. Follow the same 10-step pattern as Task 02:
   - Copy source code from Trade2025
   - Create config files
   - Update URLs (localhost → Docker names)
   - Build Docker images  
   - Test component
   - Test integration
   - Validate performance
   - Pass validation gate

**Key Differences from Task 02**:
- **Needs API keys**: Exchange API keys required (or paper trading)
- **External dependencies**: CCXT, exchange APIs
- **Security critical**: Secrets must be managed properly
- **Paper trading first**: ALWAYS test in paper mode first

**Critical Files to Create**:
```
config/backend/gateway/config.yaml
config/backend/live_gateway/config.yaml
secrets/gateway.env (API keys)
secrets/live_gateway.env (API keys)
```

**docker-compose.apps.yml**: Already has entries for both services ✅

**Validation Gate After Task 03**:
- [ ] Both services running and healthy
- [ ] Gateway fetching market data from exchanges
- [ ] Live-gateway can execute paper trading orders
- [ ] Market data flowing: Exchange → Gateway → NATS → Normalizer
- [ ] Order flow working: Order → Live-gateway → Paper execution → Fill

---

### ⏸️ Task 04: P3 Services (CRITICAL)
**Services**: risk (6h), oms (8h)  
**Time**: 14 hours  
**Dependencies**: Tasks 02-03 must pass validation  
**Priority**: **CRITICAL** - Core trading functionality

**What to do**:
1. Wait for Task 03 validation to pass
2. Follow same 10-step pattern
3. **EXTRA TESTING REQUIRED** - These are mission-critical services

**Why Critical**:
- **risk**: Pre-trade risk checks, must be < 1.5ms latency
- **oms**: Central hub for all trading, complex state management
- **High risk**: Trading disruption if these fail

**Critical Requirements**:
- **Risk service**: P50 latency ≤ 1.5ms (NON-NEGOTIABLE)
- **OMS**: P50 ≤ 10ms, P99 ≤ 50ms
- **Load testing**: Must sustain 1000 orders/sec

**CRITICAL VALIDATION GATE After Task 04**:
```
FULL TRADING FLOW TEST (MANDATORY):

1. Submit test order via OMS
2. Risk check (must be < 1.5ms)
3. Order routed to live-gateway  
4. Order status updates
5. Position tracking works
6. Fill processing works
7. Data persisted to QuestDB

LOAD TEST (MANDATORY):
- Sustain 1000 orders/sec for 5 minutes
- Risk: P50 < 1.5ms
- OMS: P50 < 10ms, P99 < 50ms
- No errors or crashes

ONLY PROCEED TO TASK 05 IF ALL PASS
```

---

### ⏸️ Task 05: P4 Services (SUPPORTING)
**Services**: ptrc (4h), feast-pipeline (2h), + 4 others (7h)  
**Time**: 13 hours  
**Dependencies**: Tasks 02-04 must pass validation  
**Priority**: Supporting services, non-critical

**What to do**:
1. Wait for Task 04 CRITICAL validation to pass
2. Follow same 10-step pattern
3. These are lower risk, can work faster

**Services**:
- ptrc: P&L, tax, risk reports, compliance
- feast-pipeline: Feature store materialization
- execution-quality: Execution monitoring
- compliance-scanner: Wash trading detection  
- logger: Centralized logging
- monitoring: System monitoring

**Less Critical**: These support operations but don't block core trading

---

### ⏸️ Task 06: P5 Services (OPTIONAL)
**Services**: serving, bt-orchestrator, ml-training, marketplace, modelops  
**Time**: 22 hours  
**Dependencies**: Tasks 02-05 complete  
**Status**: **OPTIONAL - Recommend skipping for MVP**

**Recommendation**: **SKIP** and do in Phase 4 (ML Library)

**Why Skip**:
- ML services not required for core trading
- Phase 4 will build unified ML Library anyway
- Saves 22 hours
- Focus on getting MVP operational first

**If you decide to do it**:
- Same 10-step pattern
- Low risk (optional services)
- Can execute if time permits

---

## 🎯 NEXT PROMPT FOR CLAUDE CODE

### When Task 02 Complete

**Verify Task 02 first**:
```bash
# Check all P1 services healthy
docker-compose -f infrastructure/docker/docker-compose.apps.yml ps

# Should show:
# normalizer    running (healthy)
# sink-ticks    running (healthy)
# sink-alt      running (healthy)
```

**Then give Claude Code this prompt**:

```
Task 02 (P1 services) is complete and validated. 

Please proceed with Phase 2 Task 03: Migrate Priority 2 Services.

Services to migrate:
1. gateway (6 hours) - Market data ingestion from exchanges
2. live-gateway (5 hours) - Order execution on exchanges

Follow the same 10-step pattern as Task 02:
1. Copy source code from C:\Trade2025\trading\apps\{gateway|live_gateway}\
2. Create config files (config/backend/{service}/config.yaml)
3. Create secrets files (secrets/{service}.env) for exchange API keys
4. Update all URLs (localhost → Docker service names)
5. Build Docker images
6. Component testing
7. Integration testing
8. Performance validation
9. Validation gate
10. Update tracker

CRITICAL: 
- Start with paper trading mode ONLY
- Never use real API keys until fully validated
- Gateway needs exchange API keys (or mock mode)
- Live-gateway MUST use paper trading initially

The docker-compose.apps.yml already has entries for both services.

Begin with gateway service.
```

---

### When Task 03 Complete

**Then give this prompt**:

```
Task 03 (P2 services) is complete and validated.

Please proceed with Phase 2 Task 04: Migrate Priority 3 Services (CRITICAL TASK).

Services to migrate:
1. risk (6 hours) - Pre-trade risk checks (LATENCY CRITICAL: < 1.5ms)
2. oms (8 hours) - Order Management System (CENTRAL HUB)

This is a CRITICAL task. These services are core trading functionality.

After both services are migrated and tested, you MUST run the CRITICAL VALIDATION GATE:

FULL TRADING FLOW TEST:
1. Submit test order via OMS API
2. Verify risk check completes in < 1.5ms
3. Verify order routed to live-gateway
4. Verify position tracking
5. Verify fill processing
6. Verify data persistence

LOAD TEST:
- 1000 orders/sec sustained for 5 minutes
- Risk service: P50 < 1.5ms (NON-NEGOTIABLE)
- OMS: P50 < 10ms, P99 < 50ms

ONLY proceed to Task 05 if ALL validation passes.

Begin with risk service (it's required by OMS).
```

---

### When Task 04 Complete

**Then give this prompt**:

```
Task 04 (P3 services - CRITICAL) is complete and CRITICAL validation passed.

You can now choose:

OPTION A (RECOMMENDED): Proceed with Task 05 (P4 Supporting Services)
- 6 services: ptrc, feast-pipeline, execution-quality, compliance-scanner, logger, monitoring
- 13 hours total
- After this, Phase 2 MVP is complete (Tasks 01-05)

OPTION B: Skip to Phase 3 (Frontend Integration)
- Phase 2 MVP complete with P1-P4 services
- Can do Task 05 later if needed

OPTION C: Do Task 06 (P5 ML Services) - NOT RECOMMENDED
- 5 ML services, 22 hours
- Better to defer to Phase 4 (ML Library)

What would you like to do? (Recommend Option A)
```

---

## 📚 UNIVERSAL PATTERN (ALL SERVICES)

### 10-Step Process

**Every service migration follows this pattern**:

```
1. COPY source from Trade2025
   └─ C:\Trade2025\trading\apps\{service}\ 
      → C:\ClaudeDesktop_Projects\Trade2026\backend\apps\{service}\

2. CREATE config file
   └─ config/backend/{service}/config.yaml
   └─ Use Docker service names (nats:4222, not localhost:4222)

3. UPDATE code
   └─ Replace all localhost with Docker service names
   └─ Update config paths to /app/config/config.yaml

4. BUILD Docker image
   └─ docker build -t localhost/{service}:latest .

5. ADD to docker-compose (ALREADY DONE ✅)
   └─ docker-compose.apps.yml has all services

6. TEST component (isolated)
   └─ docker-compose up -d {service}
   └─ docker logs {service}
   └─ Health check passes

7. TEST integration (with dependencies)
   └─ End-to-end data/order flow
   └─ NATS pub/sub working
   └─ Database writes persisting

8. VALIDATE performance
   └─ Latency benchmarks (P50, P99)
   └─ Throughput targets
   └─ Resource usage acceptable

9. VALIDATION GATE
   └─ All tests pass
   └─ Performance met
   └─ Ready for next service/task

10. UPDATE tracker
    └─ COMPLETION_TRACKER.md
    └─ Mark service/task complete
```

---

## 🔒 CRITICAL REMINDERS

### Never Use Localhost ❌

```yaml
# WRONG - Will not work in Docker
nats_url: "nats://localhost:4222"
valkey_url: "redis://localhost:6379"

# CORRECT - Docker service names
nats_url: "nats://nats:4222"
valkey_url: "redis://valkey:6379"
```

### Always Validate Before Proceeding ✅

- Each task has a validation gate
- Must pass before next task
- Task 04 has CRITICAL gate (trading flow)
- Never skip validation

### Paper Trading First 📋

- live-gateway MUST start in paper mode
- Test thoroughly before real money
- Validate order flow completely
- Only switch to live after full validation

### Risk Service Latency ⚡

- P50 ≤ 1.5ms (NON-NEGOTIABLE)
- This is a hard requirement
- Load test at 10k checks/sec
- Monitor continuously

---

## 📊 PHASE 2 PROGRESS TRACKER

```
Task 01: Survey                    ✅ COMPLETE (2h)
Task 02: P1 Services               ⏳ IN PROGRESS (8h)
├─ normalizer                      ⏳ In progress
├─ sink-ticks                      ⏸️ Pending
└─ sink-alt                        ⏸️ Pending

Task 03: P2 Services               ⏸️ READY (11h)
├─ gateway                         ⏸️ After Task 02
└─ live-gateway                    ⏸️ After Task 02

Task 04: P3 Services (CRITICAL)    ⏸️ READY (14h)
├─ risk                            ⏸️ After Task 03
└─ oms                             ⏸️ After Task 03
└─ CRITICAL VALIDATION GATE        ⏸️ After both complete

Task 05: P4 Services               ⏸️ READY (13h)
├─ ptrc                            ⏸️ After Task 04
├─ feast-pipeline                  ⏸️ After Task 04
└─ 4 other services                ⏸️ After Task 04

Task 06: P5 Services (OPTIONAL)    ⏸️ SKIP (22h)
└─ Defer to Phase 4 (ML Library)   📋 RECOMMENDED

MVP Complete: After Task 05 ✅
Total MVP Time: 2h + 8h + 11h + 14h + 13h = 48 hours
```

---

## ✅ SUMMARY

**Current Task**: Task 02 (P1) - In progress with Claude Code

**Next Task**: Task 03 (P2) - Wait for Task 02 validation

**Critical Task**: Task 04 (P3) - Full trading flow must work

**MVP Complete**: After Task 05 (P4) - Functional trading platform

**Optional**: Task 06 (P5) - Recommend skipping for MVP

**Estimated Time to MVP**: 46 hours (already spent 2h on Task 01)

---

**Last Updated**: 2025-10-14  
**Status**: Task 02 in progress, Tasks 03-06 ready  
**Next Action**: Wait for Task 02 completion, then prompt for Task 03
