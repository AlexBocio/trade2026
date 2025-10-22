# Phase 2 - Complete Prompt Index

**Phase**: 2 - Backend Migration  
**Status**: All prompts created ✅  
**Total Prompts**: 7 (00-06)  
**Created**: 2025-10-14

---

## 📋 PROMPT SEQUENCE

### Prompt 00: Validation Gate ✅
**File**: `PHASE2_PROMPT00_VALIDATION_GATE.md`  
**Purpose**: Validate Phase 1 complete before starting Phase 2  
**Duration**: 5 minutes  
**Status**: Run first, before any Phase 2 work

**What it does**:
- Validates all Phase 1 work complete
- Checks all infrastructure services healthy
- Verifies networks configured
- 26 mandatory checks

**Next**: Prompt 01

---

### Prompt 01: Survey Backend Services ✅
**File**: `PHASE2_PROMPT01_SURVEY_BACKEND_SERVICES.md`  
**Duration**: 2 hours  
**Status**: ✅ COMPLETE  
**Services**: Documentation of 18 services

**What was done**:
- Surveyed all 18 backend services
- Mapped dependencies
- Established priorities (P1-P5)
- Risk assessment
- Created migration plan

**Deliverables**:
- BACKEND_SERVICES_INVENTORY.md
- Migration priorities
- Testing requirements

**Next**: Prompt 02

---

### Prompt 02: Migrate P1 Services ⏳
**File**: `PHASE2_PROMPT02_MIGRATE_P1_SERVICES.md`  
**Duration**: 8 hours  
**Status**: ⏳ IN PROGRESS (Claude Code implementing)  
**Services**: normalizer, sink-ticks, sink-alt

**What to do**:
- Follow 30-step comprehensive guide
- Migrate foundation services
- No dependencies on other app services

**Success Criteria**:
- All 3 services healthy
- Data flowing: ticks → normalizer → QuestDB/S3
- Performance: 100k ticks/sec

**Next**: Prompt 03 (after validation)

---

### Prompt 03: Migrate P2 Services ⏸️
**File**: `PHASE2_PROMPT03_MIGRATE_P2_SERVICES.md`  
**Duration**: 11 hours  
**Status**: ⏸️ READY (after Prompt 02)  
**Services**: gateway (6h), live-gateway (5h)

**What to do**:
- Market data ingestion (gateway)
- Order execution (live-gateway)
- External API integration (CCXT)
- **Paper trading mode only**

**Key Requirements**:
- Exchange API keys needed
- Start with paper trading
- Security critical

**Success Criteria**:
- Both services healthy
- Market data flowing
- Paper trading orders executing

**Next**: Prompt 04 (after validation)

---

### Prompt 04: Migrate P3 Services (CRITICAL) ⏸️
**File**: `PHASE2_PROMPT04_MIGRATE_P3_SERVICES_CRITICAL.md`  
**Duration**: 14 hours  
**Status**: ⏸️ READY (after Prompt 03)  
**Services**: risk (6h), oms (8h)

**⚠️ CRITICAL TASK**

**What to do**:
- Pre-trade risk checks (risk)
- Order management system (oms)
- Most critical services

**Key Requirements**:
- Risk: P50 ≤ 1.5ms (NON-NEGOTIABLE)
- OMS: P50 ≤ 10ms, P99 ≤ 50ms
- Extensive testing required

**Success Criteria**:
- Both services healthy
- Full trading flow works
- Load test: 1000 orders/sec sustained

**CRITICAL VALIDATION GATE**:
- Must pass before Prompt 05
- Full trading flow test
- Load test mandatory
- All SLAs must be met

**Next**: Prompt 05 (ONLY after CRITICAL validation passes)

---

### Prompt 05: Migrate P4 Services ⏸️
**File**: `PHASE2_PROMPT05_MIGRATE_P4_SERVICES.md`  
**Duration**: 13 hours  
**Status**: ⏸️ READY (after Prompt 04 validation)  
**Services**: ptrc, feast-pipeline, execution-quality, + 3 others

**What to do**:
- Supporting services (non-critical)
- Reporting (ptrc)
- Feature store (feast-pipeline)
- Quality monitoring

**Success Criteria**:
- All services healthy
- Reports generating
- Features materializing
- Core trading not impacted

**Phase 2 MVP Complete**: After Prompt 05 ✅

**Next**: Decision Point (Phase 3 recommended)

---

### Prompt 06: Migrate P5 Services (OPTIONAL) ⏸️
**File**: `PHASE2_PROMPT06_MIGRATE_P5_SERVICES_OPTIONAL.md`  
**Duration**: 22 hours  
**Status**: ⏸️ NOT RECOMMENDED  
**Services**: serving, bt-orchestrator, ml-training, marketplace, modelops

**⚠️ RECOMMENDATION: SKIP THIS PROMPT**

**Why Skip**:
- Not required for MVP
- Better to do in Phase 4 (ML Library)
- Saves 22 hours
- Phase 2 MVP complete without it

**If You Insist**:
- ML model serving
- Backtesting engine
- ML training infrastructure
- Strategy marketplace
- Model governance

**Recommended Instead**: Proceed to Phase 3 (Frontend Integration)

---

## 🎯 PROMPT USAGE GUIDE

### Current Status Check

**Where are you now?**
- ✅ Prompt 01: COMPLETE
- ⏳ Prompt 02: IN PROGRESS (Claude Code)
- ⏸️ Prompts 03-06: READY

### Next Prompt Decision Tree

```
Are you on Prompt 02?
├─ YES → Wait for Claude Code to finish, then validate
│         └─ Validation passed? → Start Prompt 03
│                                  
└─ NO → Are you on Prompt 03?
        ├─ YES → Complete Prompt 03, validate, then Prompt 04
        │
        └─ NO → Are you on Prompt 04?
                ├─ YES → Complete Prompt 04
                │        Run CRITICAL validation
                │        └─ All passed? → Prompt 05
                │
                └─ NO → Are you on Prompt 05?
                        ├─ YES → Complete Prompt 05
                        │        Phase 2 MVP COMPLETE! 🎉
                        │        → Proceed to Phase 3
                        │
                        └─ Are you on Prompt 06?
                                └─ STOP! Skip Prompt 06
                                   → Go to Phase 3 instead
```

---

## 📊 PHASE 2 METRICS

### Time Investment

| Prompt | Duration | Status | Progress |
|--------|----------|--------|----------|
| 00 | 5 min | ✅ Complete | 100% |
| 01 | 2h | ✅ Complete | 100% |
| 02 | 8h | ⏳ In Progress | ~50% |
| 03 | 11h | ⏸️ Ready | 0% |
| 04 | 14h | ⏸️ Ready | 0% |
| 05 | 13h | ⏸️ Ready | 0% |
| 06 | 22h | ⏸️ Skip | 0% |

**MVP Path (Prompts 01-05)**:
- Total: 48 hours
- Complete: 2 hours
- Remaining: 46 hours

**With Prompt 06 (Not Recommended)**:
- Total: 70 hours
- Complete: 2 hours
- Remaining: 68 hours

---

## 🚀 QUICK START PROMPTS

### For Claude Code

**When Prompt 02 Complete**:
```
Prompt 02 validation complete. Proceed with Prompt 03:
Migrate gateway and live-gateway services.
Follow same 10-step pattern. Use paper trading mode.
Begin with gateway.
```

**When Prompt 03 Complete**:
```
Prompt 03 validation complete. Proceed with Prompt 04 (CRITICAL):
Migrate risk and oms services.
These are mission-critical. Extensive testing required.
After both complete, run full CRITICAL validation gate.
Begin with risk service (oms depends on it).
```

**When Prompt 04 Complete**:
```
Prompt 04 CRITICAL validation PASSED. Proceed with Prompt 05:
Migrate supporting services (ptrc, feast-pipeline, etc).
After completion, Phase 2 MVP is complete.
Begin with ptrc.
```

**When Prompt 05 Complete**:
```
Phase 2 MVP COMPLETE! 🎉

Proceed to Phase 3: Frontend Integration
Connect React UI to backend APIs.
```

---

## 📁 FILE LOCATIONS

All Phase 2 prompt files located in:
```
C:\ClaudeDesktop_Projects\Trade2026\instructions\
├── PHASE2_PROMPT00_VALIDATION_GATE.md
├── PHASE2_PROMPT01_SURVEY_BACKEND_SERVICES.md
├── PHASE2_PROMPT02_MIGRATE_P1_SERVICES.md
├── PHASE2_PROMPT03_MIGRATE_P2_SERVICES.md
├── PHASE2_PROMPT04_MIGRATE_P3_SERVICES_CRITICAL.md
├── PHASE2_PROMPT05_MIGRATE_P4_SERVICES.md
└── PHASE2_PROMPT06_MIGRATE_P5_SERVICES_OPTIONAL.md
```

---

## ✅ COMPLETION CRITERIA

### Phase 2 MVP Complete When:

- [x] Prompt 00: Validation complete
- [x] Prompt 01: Survey complete
- [ ] Prompt 02: P1 services operational
- [ ] Prompt 03: P2 services operational
- [ ] Prompt 04: P3 services + CRITICAL validation passed
- [ ] Prompt 05: P4 services operational

**Total Services**: 11-13 services (after Prompt 05)

**Capabilities**: Fully functional trading platform ✅

**Next Phase**: Phase 3 - Frontend Integration

---

## 🎯 RECOMMENDATIONS

### DO:
- ✅ Follow prompts in order (02 → 03 → 04 → 05)
- ✅ Validate after each prompt
- ✅ Run CRITICAL validation after Prompt 04
- ✅ Proceed to Phase 3 after Prompt 05

### DON'T:
- ❌ Skip validation gates
- ❌ Proceed if validation fails
- ❌ Do Prompt 06 (defer to Phase 4)
- ❌ Rush through Prompt 04 (it's critical)

---

**Master Index Status**: ✅ Complete

**Phase 2 Prompt Files**: All created and ready

**Current Prompt**: Prompt 02 (in progress with Claude Code)

**Next Action**: Wait for Prompt 02 completion, then proceed to Prompt 03
