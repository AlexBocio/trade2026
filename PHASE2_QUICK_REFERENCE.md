# 🚀 PHASE 2 - QUICK REFERENCE CARD

**What You Need**: Give these prompts to Claude Code in order

---

## 📋 EXECUTION ORDER

### 1️⃣ PHASE 2A (20 hours)
**File**: `instructions/PHASE2A_PROMPT_COMPLETE.md`

**Give to Claude Code**:
```
Read and execute: C:\ClaudeDesktop_Projects\trade2026\instructions\PHASE2A_PROMPT_COMPLETE.md

Migrate risk, oms, and exeq services following the 10-step pattern.
Test comprehensively at every step.
Run CRITICAL validation gate at the end.
```

**What It Does**:
- Migrates 3 critical trading services
- Builds trading pipeline
- Tests everything thoroughly
- 20 hours of work

**You Get**:
- Working trading core
- Risk checks operational
- Order management working
- Ready for more services

---

### 2️⃣ PHASE 2B (16 hours)
**File**: `instructions/PHASE2B_PROMPT_COMPLETE.md`

**Give to Claude Code** (after 2A passes):
```
Read and execute: C:\ClaudeDesktop_Projects\trade2026\instructions\PHASE2B_PROMPT_COMPLETE.md

Migrate supporting services (ptrc, pnl, hot_cache, questdb_writer, feast-pipeline, execution-quality).
Follow same 10-step pattern.
Run validation gate at the end.
```

**What It Does**:
- Migrates 6 supporting services
- Adds P&L and reporting
- Adds data optimization
- Adds analytics
- 16 hours of work

**You Get**:
- Complete backend
- P&L calculation
- Reports and analytics
- Production-ready features

---

### 3️⃣ FINAL VALIDATION (3 hours)
**File**: `instructions/PHASE2_FINAL_VALIDATION_PROMPT.md`

**Give to Claude Code** (after 2B complete):
```
Read and execute: C:\ClaudeDesktop_Projects\trade2026\instructions\PHASE2_FINAL_VALIDATION_PROMPT.md

Run all 6 test suites.
Create validation report.
Determine if system is ready for Phase 3.
```

**What It Does**:
- Tests all 19-21 services
- Validates everything
- Performance benchmarks
- Creates report
- 3 hours of work

**You Get**:
- Validation report
- Performance metrics
- PASS/CONDITIONAL/FAIL decision
- Ready for Phase 3 (if PASS)

---

## ✅ SUCCESS CHECKLIST

### After Phase 2A:
- [ ] 3 services running
- [ ] Trading flow working
- [ ] Performance SLAs met
- [ ] CRITICAL gate passed

### After Phase 2B:
- [ ] 9 services running total
- [ ] P&L working
- [ ] Reports generating
- [ ] Validation gate passed

### After Final Validation:
- [ ] All tests passed
- [ ] System stable
- [ ] Validation report created
- [ ] Decision: PASS → Phase 3

---

## 📊 TIME ESTIMATE

**Total**: 39 hours (~5 days)
- Day 1-2.5: Phase 2A
- Day 3-4.5: Phase 2B
- Day 5: Final validation

---

## 📁 WHERE ARE THE FILES?

All in: `C:\ClaudeDesktop_Projects\trade2026\instructions\`

- PHASE2A_PROMPT_COMPLETE.md
- PHASE2B_PROMPT_COMPLETE.md
- PHASE2_FINAL_VALIDATION_PROMPT.md
- PHASE2_MASTER_INDEX.md

---

## 🎯 WHAT YOU DO

1. **Give prompt to Claude Code**
2. **Let Claude Code work** (don't interrupt)
3. **Review results** when complete
4. **Approve next step** if passing
5. **Repeat** for next phase

---

## ⚠️ IMPORTANT

- **Don't modify code yourself** - let Claude Code do it
- **Don't skip validation gates** - they catch issues
- **Don't proceed if tests fail** - fix first
- **Do review validation reports** - understand status

---

**Ready to Start**: ✅ Yes

**First Action**: Give PHASE2A_PROMPT_COMPLETE.md to Claude Code

**Expected Completion**: 5-7 days

**Result**: Complete validated backend ready for frontend

---

**Quick Reference Card** | **Phase 2** | **October 2025**
