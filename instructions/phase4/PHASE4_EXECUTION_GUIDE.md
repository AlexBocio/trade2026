# PHASE 4 - CLEAN EXECUTION GUIDE
# Essential Files for ML Library Implementation

**Location**: `C:\ClaudeDesktop_Projects\Trade2026\instructions\phase4\`
**Status**: Cleaned and organized ✅

---

## 📂 ESSENTIAL FILES (Keep These)

### Execution Prompts (8 files):
1. **PHASE4_PROMPT00_VALIDATION_GATE.md** - Start here (30 min)
2. **PHASE4_PROMPT01_LIBRARY_SERVICE_DATABASE.md** - PostgreSQL (2-3 hours)
3. **PHASE4_PROMPT02_LIBRARY_CORE_API.md** - FastAPI (3-4 hours) [PARTIAL]
4. **PHASE4_PROMPT03_NATS_INTEGRATION.md** - Messaging (2-3 hours)
5. **PHASE4_PROMPT04_ENTITY_CRUD_ENDPOINTS.md** - API CRUD (3-4 hours)
6. **PHASE4_PROMPT05_DEPLOYMENT_LIFECYCLE.md** - Deploy/Rollback (3-4 hours)
7. **PHASE4_PROMPT06_HOTSWAP_ENGINE.md** - Hot-swap (4-5 hours)
8. **PHASE4_PROMPTS_06-13_CONSOLIDATED.md** - Remaining prompts (30+ hours)

### Main Guide (1 file):
9. **PHASE4_EXECUTION_GUIDE.md** - THIS FILE (how to use everything)

---

## 📋 DELETED FILES (Redundant Documentation)

The following files were redundant and have been removed:
- ❌ PHASE4_ALL_PROMPTS_READY.md (duplicate info)
- ❌ PHASE4_CREATION_COMPLETE.md (status report, not needed)
- ❌ PHASE4_DELIVERY_STATUS.md (duplicate info)
- ❌ PHASE4_FINAL_STATUS.md (duplicate info)
- ❌ PHASE4_HANDOFF.md (duplicate of this guide)
- ❌ PHASE4_INDEX.md (duplicate navigation)
- ❌ PHASE4_PROMPTS_04-13_SPECIFICATIONS.md (superseded by consolidated)
- ❌ PHASE4_PROMPTS_SUMMARY.md (duplicate overview)

**Kept**: Only execution prompts + this guide

---

## 🚀 HOW TO EXECUTE

### Step 1: Validation Gate (30 minutes)
```bash
# Execute this first
PHASE4_PROMPT00_VALIDATION_GATE.md

# Validates Phase 3 complete
# Go/No-Go decision
# Must pass before proceeding
```

### Step 2: Foundation (Week 1 - ~18 hours)
Execute these in order:
```bash
PHASE4_PROMPT01_LIBRARY_SERVICE_DATABASE.md     # 2-3 hours
PHASE4_PROMPT02_LIBRARY_CORE_API.md             # 3-4 hours (partial)
PHASE4_PROMPT03_NATS_INTEGRATION.md             # 2-3 hours
PHASE4_PROMPT04_ENTITY_CRUD_ENDPOINTS.md        # 3-4 hours
PHASE4_PROMPT05_DEPLOYMENT_LIFECYCLE.md         # 3-4 hours
PHASE4_PROMPT06_HOTSWAP_ENGINE.md               # 4-5 hours
```

### Step 3: ML Pipeline (Week 2-3 - ~35 hours)
```bash
# Open this file and follow sections sequentially
PHASE4_PROMPTS_06-13_CONSOLIDATED.md

Sections:
- PROMPT 07: Default ML Features (4-5 hours)
- PROMPT 08: XGBoost Training (5-6 hours)
- PROMPT 09: Feast Integration (4-5 hours)
- PROMPT 10: BentoML Serving (4-5 hours)
- PROMPT 11: Default Alpha Strategy (5-6 hours)
- PROMPT 12: Integration Tests (3-4 hours)
- PROMPT 13: Production Deployment (3-4 hours)
```

---

## 🎯 EXECUTION PATTERN

Each prompt follows this structure:

1. **Validation Gate** - Verify previous prompt complete
2. **Implementation** - Step-by-step code with full examples
3. **Component Testing** - Test in isolation
4. **Integration Testing** - Test with dependencies
5. **Deployment** - Add to docker-compose
6. **Final Validation** - 5-minute stability check
7. **Success Criteria** - Checklist to verify completion

---

## ✅ WHAT YOU GET

After completing all prompts:

**Infrastructure**:
- PostgreSQL registry (6 tables, 20+ indexes)
- FastAPI application on port 8350
- NATS messaging system
- Health monitoring

**API Layer**:
- Entity CRUD endpoints (create, read, update, delete)
- Deployment lifecycle (deploy, rollback)
- Hot-swap engine (zero-downtime swapping)

**ML Pipeline**:
- Feature engineering (RSI, MACD, Bollinger Bands)
- XGBoost model training with MLflow
- Feast feature store (ClickHouse + Valkey)
- BentoML model serving
- Default alpha trading strategy

**Testing & Production**:
- Comprehensive integration tests
- Production-ready deployment
- Full docker-compose orchestration

---

## 📊 PROGRESS TRACKING

```
Phase 4 Execution Checklist:

Foundation:
[ ] PROMPT00 - Validation Gate (30 min)
[ ] PROMPT01 - Database (2-3 hours)
[ ] PROMPT02 - Core API (3-4 hours)
[ ] PROMPT03 - NATS (2-3 hours)
[ ] PROMPT04 - Entity CRUD (3-4 hours)
[ ] PROMPT05 - Deployment (3-4 hours)
[ ] PROMPT06 - HotSwap (4-5 hours)

ML Pipeline (use consolidated file):
[ ] PROMPT07 - Features (4-5 hours)
[ ] PROMPT08 - Training (5-6 hours)
[ ] PROMPT09 - Feast (4-5 hours)
[ ] PROMPT10 - BentoML (4-5 hours)
[ ] PROMPT11 - Strategy (5-6 hours)
[ ] PROMPT12 - Tests (3-4 hours)
[ ] PROMPT13 - Deploy (3-4 hours)

Total: 45-55 hours (2-3 weeks)
```

---

## 🔧 USING WITH CLAUDE CODE

Claude Code can execute these prompts directly:

```bash
# Example usage
claude-code "Execute PHASE4_PROMPT01_LIBRARY_SERVICE_DATABASE.md"

# Or for consolidated prompts
claude-code "Follow PROMPT 07 from PHASE4_PROMPTS_06-13_CONSOLIDATED.md"
```

Claude Code will:
1. Read the prompt file
2. Extract all commands and code
3. Execute step-by-step
4. Run all tests
5. Validate completion

---

## 💡 KEY PRINCIPLES

### Component Isolation
- Fix errors within component only
- Don't modify other services
- Clear boundaries defined

### Comprehensive Implementation
- No shortcuts
- Full code examples
- Complete testing

### Official Sources Only
- All verified sources
- Security guaranteed
- Stable implementations

### Test-Integrate-Deploy-Validate
- Test in isolation first
- Then test with dependencies
- Deploy to docker-compose
- Monitor for 5+ minutes

---

## 🎯 READY TO START

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\instructions\phase4

# 1. Start with validation
cat PHASE4_PROMPT00_VALIDATION_GATE.md

# 2. If validation passes, begin PROMPT01
cat PHASE4_PROMPT01_LIBRARY_SERVICE_DATABASE.md

# 3. Continue sequentially through all prompts
```

---

## 📞 QUICK REFERENCE

**File Count**: 9 files total (8 prompts + this guide)
**Total Size**: ~160 KB
**Estimated Time**: 45-55 hours
**Phases**: Foundation (18h) + ML Pipeline (35h)

**Next Action**: Execute PHASE4_PROMPT00_VALIDATION_GATE.md

---

**Status**: ✅ CLEANED AND READY
**Date**: 2025-10-20
**All redundant files removed**
**Ready for execution**
