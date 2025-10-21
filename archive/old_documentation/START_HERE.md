# 🚀 START HERE - Quick Reference

**CRITICAL**: Run this validation FIRST before any other work!

---

## 📋 FIRST STEP - Validate Current State

**Give to Claude Code**:
```
Read and execute: instructions/1CURRENT_STATE_VALIDATION_PROMPT.md
```

**What it does** (30 minutes):
1. ✅ Checks all Docker containers
2. ✅ Tests all health endpoints
3. ✅ Runs functional tests
4. ✅ Creates STATUS_REPORT.md
5. ✅ **Recommends next prompt to execute**

**Output**: STATUS_REPORT.md with clear recommendation

---

## 🎯 AFTER VALIDATION

Review STATUS_REPORT.md - it will tell you one of these:

### Scenario A: Infrastructure Only
**Recommendation**: Execute PHASE2A_PROMPT_COMPLETE.md  
**Why**: Backend not deployed yet  
**Next**: Deploy risk, oms, exeq services (20 hours)

### Scenario B: Phase 2A Partial
**Recommendation**: Continue PHASE2A_PROMPT_COMPLETE.md  
**Why**: Phase 2A not complete  
**Next**: Complete remaining services

### Scenario C: Phase 2A Complete
**Recommendation**: Execute PHASE2B_PROMPT_COMPLETE.md  
**Why**: Ready for supporting services  
**Next**: Deploy ptrc, pnl, etc (16 hours)

### Scenario D: Phase 2 Complete
**Recommendation**: Execute PHASE2_FINAL_VALIDATION_PROMPT.md  
**Why**: Need validation  
**Next**: Validate everything (3 hours)

### Scenario E: Phase 2 Validated
**Recommendation**: Execute PHASE3_PROMPT00_VALIDATION_GATE.md  
**Why**: Ready for frontend  
**Next**: Start Phase 3 (35-40 hours)

### Scenario F: Infrastructure Broken
**Recommendation**: FIX INFRASTRUCTURE FIRST  
**Why**: Can't proceed with broken foundation  
**Next**: Debug and repair

---

## 📝 ALL AVAILABLE PROMPTS

**Phase 1** (Infrastructure):
- ✅ Already deployed (assumed)

**Phase 2A** (Critical Trading - 20h):
- PHASE2A_PROMPT_COMPLETE.md - Deploy risk, oms, exeq

**Phase 2B** (Supporting Services - 16h):
- PHASE2B_PROMPT_COMPLETE.md - Deploy ptrc, pnl, etc

**Phase 2 Validation** (3h):
- PHASE2_FINAL_VALIDATION_PROMPT.md - Validate everything

**Phase 3** (Frontend - 35-40h):
- PHASE3_PROMPT00_VALIDATION_GATE.md - Prerequisites check
- PHASE3_PROMPT01_SURVEY_FRONTEND_CODE.md - Survey
- PHASE3_PROMPT02_COPY_FRONTEND_CODE.md - Copy code
- PHASE3_PROMPTS_03-08_GUIDE.md - Integration guide

---

## ⚡ QUICK START

```
Step 1: Give 1CURRENT_STATE_VALIDATION_PROMPT.md to Claude Code
Step 2: Wait 30 minutes
Step 3: Read STATUS_REPORT.md
Step 4: Execute recommended prompt
Step 5: Repeat until MVP complete
```

---

## 🎯 YOUR GOAL

**MVP Complete** = All phases done:
- ✅ Phase 1: Infrastructure
- ✅ Phase 2: Backend (39 hours)
- ✅ Phase 3: Frontend (35-40 hours)
- ✅ Total: ~80 hours (~2-3 weeks)

---

## 📁 FILE LOCATIONS

All prompts in:
```
C:\ClaudeDesktop_Projects\trade2026\instructions\
```

All documentation in:
```
C:\ClaudeDesktop_Projects\trade2026\docs\
```

---

**🚀 START NOW: Give 1CURRENT_STATE_VALIDATION_PROMPT.md to Claude Code!**
