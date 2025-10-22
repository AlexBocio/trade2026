# PHASE 2 MASTER INDEX - All Prompts for Claude Code

**Phase**: 2 - Backend Migration  
**Total Prompts**: 3 main prompts + 1 validation  
**Estimated Time**: 39 hours total  
**Status**: All prompts ready for Claude Code execution

---

## 📋 PROMPT EXECUTION ORDER

### Prerequisites
Before starting Phase 2:
- [ ] Phase 1 complete (all infrastructure operational)
- [ ] Trade2025 source available (if copying code)
- [ ] Docker and docker-compose working
- [ ] Read MASTER_GUIDELINES.md

---

## 🚀 PHASE 2A: Critical Trading Core

**File**: `instructions/PHASE2A_PROMPT_COMPLETE.md`  
**Services**: risk, oms, exeq (3 services)  
**Time**: 20 hours (6h + 8h + 6h)  
**Priority**: CRITICAL  
**Dependencies**: Phase 1 infrastructure

**What It Does**:
- Migrates risk management service
- Migrates order management system
- Migrates execution & queueing service
- Enables core trading functionality
- Includes CRITICAL validation gate

**Success Criteria**:
- All 3 services operational
- Full trading flow working (Order → Risk → OMS → EXEQ)
- Risk latency P50 ≤ 1.5ms
- OMS latency P50 ≤ 10ms, P99 ≤ 50ms
- Load test: 1000 orders/sec sustained

**Execute**:
```
Give Phase2A_PROMPT_COMPLETE.md to Claude Code
```

---

## 🔧 PHASE 2B: Supporting Services

**File**: `instructions/PHASE2B_PROMPT_COMPLETE.md`  
**Services**: ptrc, pnl, hot_cache, questdb_writer, feast-pipeline, execution-quality (6 services)  
**Time**: 16 hours  
**Priority**: MEDIUM  
**Dependencies**: Phase 2A complete

**What It Does**:
- Migrates P&L and reporting (ptrc, pnl)
- Migrates data optimization (hot_cache, questdb_writer)
- Migrates analytics (feast-pipeline, execution-quality)
- Enables production features

**Success Criteria**:
- All 6 services operational
- P&L calculation accurate
- Reports generating
- Data optimization working
- Analytics operational

**Execute**:
```
After Phase 2A validation passes:
Give Phase2B_PROMPT_COMPLETE.md to Claude Code
```

---

## ✅ PHASE 2 FINAL VALIDATION

**File**: `instructions/PHASE2_FINAL_VALIDATION_PROMPT.md`  
**Purpose**: Comprehensive backend validation  
**Time**: 3 hours  
**Priority**: MANDATORY  
**Dependencies**: Phase 2A + 2B complete

**What It Does**:
- Tests all 19-21 services comprehensively
- Validates data pipeline end-to-end
- Validates trading flow end-to-end
- Performance benchmarks
- Integration tests
- Resilience tests
- Error handling tests

**Success Criteria**:
- All critical requirements met
- 90%+ important requirements met
- System stable
- Ready for Phase 3

**Execute**:
```
After Phase 2B complete:
Give PHASE2_FINAL_VALIDATION_PROMPT.md to Claude Code
```

**Decision Point**:
- PASS ✅ → Proceed to Phase 3
- CONDITIONAL ⚠️ → Proceed with cautions
- FAIL ❌ → Fix issues, re-validate

---

## 📊 PHASE 2 SUMMARY

### Total Services to Migrate
- **Phase 2A**: 3 services (critical trading core)
- **Phase 2B**: 6 services (supporting services)
- **Already Complete**: 5 services (from previous work)
- **Total Backend**: 14 application services
- **Plus Infrastructure**: 8 services
- **Grand Total**: 22 services

### Total Time Estimate
- Phase 2A: 20 hours
- Phase 2B: 16 hours
- Validation: 3 hours
- **Total**: 39 hours (~5 working days)

### Migration Pattern
All services follow the same 10-step pattern:
1. Survey service
2. Create configuration
3. Verify/update code
4. Verify Dockerfile
5. Build Docker image
6. Verify docker-compose entry
7. Start service
8. Component testing
9. Integration testing
10. Validation gate

---

## 🎯 WHAT EACH PROMPT PROVIDES

### Phase 2A Prompt Includes:
- Complete service descriptions
- 10-step migration pattern (detailed)
- Execution order
- Prerequisites check
- Testing requirements (component + integration + performance)
- CRITICAL validation gate
- Success criteria
- All necessary commands
- Troubleshooting guidance

### Phase 2B Prompt Includes:
- 6 service descriptions
- Same 10-step pattern (reference to 2A)
- Execution order
- Special considerations per service
- Validation gate
- Success criteria
- Optional vs mandatory services
- Integration requirements

### Validation Prompt Includes:
- 6 comprehensive test suites
- Service health tests
- Data pipeline tests
- Performance benchmarks
- Integration tests
- Resilience tests
- Error handling tests
- Decision criteria (PASS/CONDITIONAL/FAIL)
- Validation report template

---

## 📁 REFERENCE FILES

### Instructions Created:
- ✅ `PHASE2A_PROMPT_COMPLETE.md` - Critical trading core
- ✅ `PHASE2B_PROMPT_COMPLETE.md` - Supporting services
- ✅ `PHASE2_FINAL_VALIDATION_PROMPT.md` - Comprehensive validation
- ✅ `PHASE2_MASTER_INDEX.md` - This file

### Supporting Documentation:
- `docs/BACKEND_SERVICES_INVENTORY.md` - All 50 services cataloged
- `docs/PHASE2_COMPLETE_SUMMARY.md` - Phase 2 overview
- `infrastructure/docker/docker-compose.apps.yml` - All service definitions
- `COMPLETION_TRACKER.md` - Progress tracking

### Original Instructions (Reference):
- `PHASE2_PROMPT03_MIGRATE_P2_SERVICES.md`
- `PHASE2_PROMPT04_MIGRATE_P3_SERVICES_CRITICAL.md`
- `PHASE2_PROMPT05_MIGRATE_P4_SERVICES.md`

---

## ⚡ QUICK START

### For Claude Code:

**Step 1**: Execute Phase 2A
```
Read: instructions/PHASE2A_PROMPT_COMPLETE.md
Execute: Migrate risk, oms, exeq services
Validate: CRITICAL gate must pass
```

**Step 2**: Execute Phase 2B
```
Read: instructions/PHASE2B_PROMPT_COMPLETE.md
Execute: Migrate ptrc, pnl, hot_cache, questdb_writer, feast-pipeline, execution-quality
Validate: Phase 2B gate must pass
```

**Step 3**: Final Validation
```
Read: instructions/PHASE2_FINAL_VALIDATION_PROMPT.md
Execute: Run all 6 test suites
Decision: PASS/CONDITIONAL/FAIL
```

**Step 4**: If PASS
```
Proceed to Phase 3 (Frontend Integration)
```

---

## ⚠️ CRITICAL REMINDERS

### For Claude Code:
1. **Follow the 10-step pattern** for every service
2. **Test at every step** (component → integration → performance)
3. **Do not skip validation gates**
4. **Fix all critical issues before proceeding**
5. **Document everything** in COMPLETION_TRACKER.md

### For Human:
1. **Do not manually edit service code** unless explicitly in prompt
2. **Let Claude Code execute the prompts**
3. **Review validation reports**
4. **Approve proceeding to next phase**

---

## 📊 PROGRESS TRACKING

Track progress in `COMPLETION_TRACKER.md`:

```markdown
## Phase 2 Progress

### Phase 2A (20 hours)
- [ ] risk service (6h)
- [ ] oms service (8h)
- [ ] exeq service (6h)
- [ ] CRITICAL validation gate

### Phase 2B (16 hours)
- [ ] ptrc service (4h)
- [ ] pnl service (3h)
- [ ] hot_cache service (2h)
- [ ] questdb_writer service (2h)
- [ ] feast-pipeline service (3h)
- [ ] execution-quality service (2h)
- [ ] Phase 2B validation gate

### Phase 2 Final (3 hours)
- [ ] Comprehensive validation
- [ ] Performance benchmarks
- [ ] Integration tests
- [ ] Resilience tests
- [ ] Final decision: PASS/CONDITIONAL/FAIL
```

---

## ✅ CHECKLIST FOR PHASE 2 COMPLETE

### Before Starting:
- [ ] Phase 1 infrastructure operational
- [ ] All prompts read and understood
- [ ] Trade2025 source accessible
- [ ] Docker environment ready

### After Phase 2A:
- [ ] 3 services operational (risk, oms, exeq)
- [ ] CRITICAL validation gate passed
- [ ] Trading flow working
- [ ] Performance SLAs met

### After Phase 2B:
- [ ] 6 services operational
- [ ] P&L and reporting working
- [ ] Data optimization active
- [ ] Analytics operational

### After Final Validation:
- [ ] All test suites passed
- [ ] Validation report created
- [ ] System stable
- [ ] Ready for Phase 3

---

## 🚦 NEXT PHASE

After Phase 2 validation passes:
→ **Phase 3: Frontend Integration**

**Prerequisites for Phase 3**:
- [ ] Phase 2 validation PASSED
- [ ] All backend services healthy
- [ ] API endpoints tested and working
- [ ] Performance benchmarks met
- [ ] System stable for 1+ hour

---

**Index Status**: ✅ COMPLETE

**All Prompts Ready**: Yes

**Total Execution Time**: 39 hours

**Ready For**: Claude Code execution

---

**Created By**: Claude (Sonnet 4.5)  
**Date**: 2025-10-16  
**Purpose**: Master index for all Phase 2 prompts  
**For**: Claude Code execution guidance
