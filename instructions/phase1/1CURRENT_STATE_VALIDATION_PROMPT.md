# CURRENT STATE VALIDATION PROMPT

**For**: Claude Code  
**Purpose**: Validate current system state and recommend next steps  
**Duration**: 30 minutes  
**Priority**: CRITICAL - Run this FIRST before any other work  
**Status**: Ready to Execute

---

## 🎯 OBJECTIVE

Perform comprehensive validation of the current Trade2026 system state to determine:
1. What infrastructure is running
2. What application services are deployed
3. What's working vs broken
4. Which phase we're actually in
5. **What prompt to execute next**

**Output**: STATUS_REPORT.md with clear recommendation

---

## 📋 VALIDATION STEPS

### STEP 1: Check Docker Services (5 minutes)

Run these commands and document the output:

```bash
# Navigate to docker directory
cd C:\ClaudeDesktop_Projects\trade2026\infrastructure\docker

# Check what's actually running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check all containers (including stopped)
docker ps -a --format "table {{.Names}}\t{{.Status}}"

# Check Docker networks
docker network ls | grep trade2026

# Check Docker volumes
docker volume ls | grep trade2026
```

**Document**:
- [ ] Total containers running
- [ ] Container names and status
- [ ] Which networks exist
- [ ] Which volumes exist

---

### STEP 2: Test Infrastructure Health (5 minutes)

Test each infrastructure service health endpoint:

```bash
# NATS
curl -f http://localhost:8222/healthz 2>/dev/null && echo "✅ NATS healthy" || echo "❌ NATS not responding"

# Valkey (Redis)
docker exec valkey redis-cli PING 2>/dev/null && echo "✅ Valkey healthy" || echo "❌ Valkey not responding"

# QuestDB
curl -f http://localhost:9000/ 2>/dev/null && echo "✅ QuestDB healthy" || echo "❌ QuestDB not responding"

# ClickHouse
curl -f http://localhost:8123/ping 2>/dev/null && echo "✅ ClickHouse healthy" || echo "❌ ClickHouse not responding"

# SeaweedFS
curl -f http://localhost:8333/status 2>/dev/null && echo "✅ SeaweedFS healthy" || echo "❌ SeaweedFS not responding"

# OpenSearch
curl -f http://localhost:9200/ 2>/dev/null && echo "✅ OpenSearch healthy" || echo "❌ OpenSearch not responding"

# PostgreSQL (via docker exec)
docker exec postgres pg_isready -U trader 2>/dev/null && echo "✅ PostgreSQL healthy" || echo "❌ PostgreSQL not responding"

# OPA
curl -f http://localhost:8181/health 2>/dev/null && echo "✅ OPA healthy" || echo "❌ OPA not responding"
```

**Document**:
- [ ] NATS status
- [ ] Valkey status
- [ ] QuestDB status
- [ ] ClickHouse status
- [ ] SeaweedFS status
- [ ] OpenSearch status
- [ ] PostgreSQL status
- [ ] OPA status

**Infrastructure Score**: X/8 services healthy

---

### STEP 3: Test Application Services (10 minutes)

Test each application service if container is running:

```bash
# Check which app containers exist
docker ps --filter "name=normalizer" --filter "name=sink" --filter "name=gateway" --filter "name=risk" --filter "name=oms" --filter "name=exeq" --filter "name=ptrc" --filter "name=pnl"

# Test health endpoints for running services
echo "Testing application services..."

# Normalizer (8081)
curl -f http://localhost:8081/health 2>/dev/null && echo "✅ normalizer healthy" || echo "❌ normalizer not responding"

# Sink-ticks (8111)
curl -f http://localhost:8111/health 2>/dev/null && echo "✅ sink-ticks healthy" || echo "❌ sink-ticks not responding"

# Sink-alt (8112)
curl -f http://localhost:8112/health 2>/dev/null && echo "✅ sink-alt healthy" || echo "❌ sink-alt not responding"

# Gateway (8080)
curl -f http://localhost:8080/health 2>/dev/null && echo "✅ gateway healthy" || echo "❌ gateway not responding"

# Live Gateway (8200)
curl -f http://localhost:8200/health 2>/dev/null && echo "✅ live-gateway healthy" || echo "❌ live-gateway not responding"

# Risk (8103)
curl -f http://localhost:8103/health 2>/dev/null && echo "✅ risk healthy" || echo "❌ risk not responding"

# OMS (8099)
curl -f http://localhost:8099/health 2>/dev/null && echo "✅ oms healthy" || echo "❌ oms not responding"

# EXEQ (8095)
curl -f http://localhost:8095/health 2>/dev/null && echo "✅ exeq healthy" || echo "❌ exeq not responding"

# PTRC (8109)
curl -f http://localhost:8109/health 2>/dev/null && echo "✅ ptrc healthy" || echo "❌ ptrc not responding"

# PNL (8100)
curl -f http://localhost:8100/health 2>/dev/null && echo "✅ pnl healthy" || echo "❌ pnl not responding"

# Hot Cache (8088)
curl -f http://localhost:8088/health 2>/dev/null && echo "✅ hot_cache healthy" || echo "❌ hot_cache not responding"

# QuestDB Writer (8090)
curl -f http://localhost:8090/health 2>/dev/null && echo "✅ questdb_writer healthy" || echo "❌ questdb_writer not responding"
```

**Document**:
- [ ] normalizer status
- [ ] sink-ticks status
- [ ] sink-alt status
- [ ] gateway status
- [ ] live-gateway status
- [ ] risk status
- [ ] oms status
- [ ] exeq status
- [ ] ptrc status
- [ ] pnl status
- [ ] hot_cache status
- [ ] questdb_writer status

**Application Score**: X/14 services healthy

---

### STEP 4: Functional Tests (5 minutes)

Test key functionality if services are running:

```bash
# Test 1: NATS Streams (if NATS running)
docker exec nats nats stream ls 2>/dev/null && echo "✅ NATS streams exist" || echo "❌ NATS streams not configured"

# Test 2: QuestDB Data (if QuestDB running)
curl "http://localhost:9000/exec?query=SELECT%20COUNT(*)%20FROM%20ohlcv_1m" 2>/dev/null && echo "✅ QuestDB has data" || echo "❌ QuestDB no data or error"

# Test 3: Order Submission (if OMS running)
curl -X POST http://localhost:8099/orders \
  -H "Content-Type: application/json" \
  -d '{"account":"test","symbol":"BTCUSDT","side":"buy","type":"limit","quantity":0.001,"price":45000}' \
  2>/dev/null && echo "✅ OMS accepting orders" || echo "❌ OMS not accepting orders"

# Test 4: Risk Check (if Risk running)
curl -X POST http://localhost:8103/risk/check \
  -H "Content-Type: application/json" \
  -d '{"account":"test","symbol":"BTCUSDT","side":"buy","quantity":0.1,"price":45000}' \
  2>/dev/null && echo "✅ Risk checks working" || echo "❌ Risk checks not working"

# Test 5: Market Data (if Gateway running)
curl http://localhost:8080/tickers 2>/dev/null && echo "✅ Market data available" || echo "❌ Market data not available"
```

**Document**:
- [ ] NATS streams configured
- [ ] QuestDB has data
- [ ] OMS accepting orders
- [ ] Risk checks working
- [ ] Market data available

**Functional Score**: X/5 tests passing

---

### STEP 5: Create Status Report (5 minutes)

Create a comprehensive status report file.

**Create**: `STATUS_REPORT.md`

```markdown
# Trade2026 System Status Report

**Date**: {CURRENT_DATE}  
**Time**: {CURRENT_TIME}  
**Generated By**: Claude Code

---

## 📊 SUMMARY

**Infrastructure**: {X}/8 services healthy ({percentage}%)  
**Applications**: {X}/14 services healthy ({percentage}%)  
**Functionality**: {X}/5 tests passing ({percentage}%)  
**Overall Status**: {HEALTHY/DEGRADED/CRITICAL}

---

## 🔍 DETAILED STATUS

### Infrastructure Services (8 total)

| Service | Status | Port | Notes |
|---------|--------|------|-------|
| NATS | {✅/❌} | 4222 | {details} |
| Valkey | {✅/❌} | 6379 | {details} |
| QuestDB | {✅/❌} | 9000 | {details} |
| ClickHouse | {✅/❌} | 8123 | {details} |
| SeaweedFS | {✅/❌} | 8333 | {details} |
| OpenSearch | {✅/❌} | 9200 | {details} |
| PostgreSQL | {✅/❌} | 5432 | {details} |
| OPA | {✅/❌} | 8181 | {details} |

### Application Services (14 total)

| Service | Status | Port | Notes |
|---------|--------|------|-------|
| normalizer | {✅/❌/⚠️} | 8081 | {details} |
| sink-ticks | {✅/❌/⚠️} | 8111 | {details} |
| sink-alt | {✅/❌/⚠️} | 8112 | {details} |
| gateway | {✅/❌/⚠️} | 8080 | {details} |
| live-gateway | {✅/❌/⚠️} | 8200 | {details} |
| risk | {✅/❌/⚠️} | 8103 | {details} |
| oms | {✅/❌/⚠️} | 8099 | {details} |
| exeq | {✅/❌/⚠️} | 8095 | {details} |
| ptrc | {✅/❌/⚠️} | 8109 | {details} |
| pnl | {✅/❌/⚠️} | 8100 | {details} |
| hot_cache | {✅/❌/⚠️} | 8088 | {details} |
| questdb_writer | {✅/❌/⚠️} | 8090 | {details} |
| feast-pipeline | {✅/❌/⚠️} | 8104 | {details} |
| execution-quality | {✅/❌/⚠️} | 8096 | {details} |

**Legend**:
- ✅ Running and healthy
- ⚠️ Container exists but not responding
- ❌ Container not found

### Functional Tests (5 total)

| Test | Result | Details |
|------|--------|---------|
| NATS Streams | {✅/❌} | {details} |
| QuestDB Data | {✅/❌} | {details} |
| Order Submission | {✅/❌} | {details} |
| Risk Checks | {✅/❌} | {details} |
| Market Data | {✅/❌} | {details} |

---

## 🎯 PHASE DETERMINATION

Based on service status:

**Current Phase**: {Phase 1/Phase 2A/Phase 2B/Phase 3/Unknown}

**Evidence**:
- Infrastructure: {complete/partial/not started}
- Phase 2A services (risk, oms, exeq): {X}/3 deployed
- Phase 2B services (ptrc, pnl, etc): {X}/6 deployed
- Frontend: {deployed/not deployed}

---

## 🚦 RECOMMENDATION

### Scenario A: Infrastructure Only (Phase 1 Complete)
**If**: Infrastructure 100%, Applications 0%  
**Recommendation**: Execute **PHASE2A_PROMPT_COMPLETE.md**  
**Reason**: Backend services not deployed yet  
**Next Action**: Deploy risk, oms, exeq services

### Scenario B: Phase 2A In Progress
**If**: Infrastructure 100%, Phase 2A partial (1-2 services)  
**Recommendation**: Continue **PHASE2A_PROMPT_COMPLETE.md**  
**Reason**: Phase 2A not complete  
**Next Action**: Complete remaining Phase 2A services

### Scenario C: Phase 2A Complete
**If**: Infrastructure 100%, Phase 2A 100% (risk, oms, exeq healthy)  
**Recommendation**: Execute **PHASE2B_PROMPT_COMPLETE.md**  
**Reason**: Ready for supporting services  
**Next Action**: Deploy ptrc, pnl, hot_cache, etc.

### Scenario D: Phase 2 Complete
**If**: Infrastructure 100%, Applications >90%  
**Recommendation**: Execute **PHASE2_FINAL_VALIDATION_PROMPT.md**  
**Reason**: Backend complete, needs validation  
**Next Action**: Comprehensive validation

### Scenario E: Phase 2 Validated
**If**: All backend healthy and validated  
**Recommendation**: Execute **PHASE3_PROMPT00_VALIDATION_GATE.md**  
**Reason**: Ready for frontend integration  
**Next Action**: Begin Phase 3

### Scenario F: Infrastructure Broken
**If**: Infrastructure <80%  
**Recommendation**: **FIX INFRASTRUCTURE FIRST**  
**Reason**: Cannot proceed without stable infrastructure  
**Next Action**: Debug and repair infrastructure

---

## 🎯 SPECIFIC RECOMMENDATION

**Detected Scenario**: {A/B/C/D/E/F}

**Next Prompt to Execute**: `{FILENAME}`

**Reasoning**: {detailed explanation}

**Prerequisites**:
- [ ] {prerequisite 1}
- [ ] {prerequisite 2}
- [ ] {prerequisite 3}

**Expected Duration**: {X} hours

**Expected Outcome**: {description}

---

## 📋 ISSUES FOUND

{List any issues, errors, or warnings discovered}

1. {Issue 1}
2. {Issue 2}
3. {Issue 3}

---

## 📝 NOTES

{Any additional observations or context}

---

**Report Generated**: {TIMESTAMP}  
**Validation Duration**: {X} minutes  
**Confidence Level**: {HIGH/MEDIUM/LOW}

---

## ✅ VALIDATION COMPLETE

**Status Report Created**: ✅  
**Recommendation Made**: ✅  
**Ready to Proceed**: {YES/NO}

**Next Action**: {Clear instruction}
```

---

## 🎯 DECISION MATRIX

Use this matrix to determine the recommendation:

| Infrastructure | Phase 2A | Phase 2B | Recommendation |
|----------------|----------|----------|----------------|
| <80% | Any | Any | FIX INFRASTRUCTURE |
| 100% | 0% | 0% | PHASE2A_PROMPT_COMPLETE.md |
| 100% | 1-2 services | 0% | Continue PHASE2A |
| 100% | 100% | 0% | PHASE2B_PROMPT_COMPLETE.md |
| 100% | 100% | 1-5 services | Continue PHASE2B |
| 100% | 100% | 100% | PHASE2_FINAL_VALIDATION_PROMPT.md |
| Validated | Validated | Validated | PHASE3_PROMPT00_VALIDATION_GATE.md |

---

## 📊 OUTPUT FORMAT

The STATUS_REPORT.md must include:

1. **Summary Section** - High-level status
2. **Detailed Status** - All services with status
3. **Functional Tests** - Test results
4. **Phase Determination** - Current phase
5. **Recommendation** - Clear next step
6. **Specific Prompt** - Exact filename to execute
7. **Reasoning** - Why this recommendation
8. **Prerequisites** - What must be true
9. **Issues** - Problems found
10. **Confidence** - How sure are we

---

## ⚠️ CRITICAL REQUIREMENTS

1. **Do NOT skip any validation step**
2. **Do NOT assume anything - test everything**
3. **Do NOT proceed if infrastructure <80%**
4. **Do create STATUS_REPORT.md**
5. **Do provide clear next action**
6. **Do list all issues found**

---

## ✅ SUCCESS CRITERIA

This validation is complete when:

- [ ] All Docker services checked
- [ ] All health endpoints tested
- [ ] All functional tests run
- [ ] STATUS_REPORT.md created
- [ ] Clear recommendation made
- [ ] Next prompt identified
- [ ] Prerequisites listed
- [ ] Issues documented

---

## 📝 EXAMPLE OUTPUT

```bash
# Example output in terminal:

=== TRADE2026 SYSTEM VALIDATION ===

Infrastructure Services: 8/8 (100%) ✅
Application Services: 3/14 (21%) ⚠️
Functional Tests: 2/5 (40%) ⚠️

DETECTED SCENARIO: Phase 2A In Progress
RECOMMENDATION: Continue PHASE2A_PROMPT_COMPLETE.md
REASON: risk and oms deployed, exeq missing

STATUS REPORT: STATUS_REPORT.md created ✅

NEXT ACTION: 
1. Review STATUS_REPORT.md
2. Deploy exeq service (remaining Phase 2A service)
3. Complete Phase 2A validation

CONFIDENCE: HIGH
```

---

## 🚀 EXECUTION INSTRUCTIONS

**For Claude Code**:

```
1. Run all validation commands
2. Document all results
3. Create STATUS_REPORT.md with complete details
4. Make clear recommendation based on Decision Matrix
5. Identify exact next prompt filename
6. List all prerequisites
7. Report confidence level
```

**For Human**:

```
1. Review STATUS_REPORT.md
2. Verify recommendation makes sense
3. Check issues found
4. Approve next prompt execution
```

---

## 🎯 DELIVERABLES

When this prompt completes, you will have:

1. ✅ **STATUS_REPORT.md** - Complete system status
2. ✅ **Clear recommendation** - Next prompt to execute
3. ✅ **Issue list** - Problems to address
4. ✅ **Phase determination** - Where we are
5. ✅ **Next actions** - What to do

---

**Prompt Status**: ✅ READY TO EXECUTE

**Priority**: CRITICAL - Run this FIRST

**Duration**: 30 minutes

**Output**: STATUS_REPORT.md with clear next step

---

**Created By**: Claude (Sonnet 4.5)  
**Date**: 2025-10-17  
**For**: Claude Code  
**Purpose**: Validate current state, recommend next prompt
