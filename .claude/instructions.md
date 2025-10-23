# Trade2026 - Claude Code Custom Instructions

**CRITICAL**: These instructions are AUTOMATICALLY loaded by Claude Code at session start.

---

## 📚 MASTER GUIDELINES (UNIVERSAL)

**FIRST, read the universal master guidelines:**

**[Master Guidelines](C:/ClaudeDesktop_Projects/ClaudeKnowledge/MASTER_GUIDELINES.md)** - Universal development patterns for ALL projects

**Key sections to review:**
- New Session Startup Protocol
- Core Development Rules
- 6-Phase Mandatory Workflow
- Documentation Standards
- Git Workflow

**Then proceed with Trade2026-specific instructions below...**

---

## 🚨 SESSION STARTUP - MANDATORY (TRADE2026-SPECIFIC)

**AFTER reading master guidelines, read these files IN ORDER:**

1. **[00_PROCESS_GUIDE.md](../00_PROCESS_GUIDE.md)** ⭐ **READ THIS FIRST**
   - Documentation cascade process (7 steps)
   - Session startup checklist
   - Session end checklist
   - Common mistakes to avoid

2. **[01_README_START_HERE.md](../01_README_START_HERE.md)**
   - Project overview
   - Current status

3. **[01_MASTER_PLAN.md](../01_MASTER_PLAN.md)**
   - Phase details
   - Current completion (92%)

4. **[01_COMPLETION_TRACKER_UPDATED.md](../01_COMPLETION_TRACKER_UPDATED.md)**
   - Detailed task tracking
   - Current phase: Phase 7 (50% complete)
   - Blockers and next steps

5. **Latest [SESSION_SUMMARY_*.md](../SESSION_SUMMARY_2025-10-23_Phase7.md)**
   - What happened last session
   - Priorities for this session

---

## 📝 DOCUMENTATION CASCADE - NON-NEGOTIABLE

**After completing ANY work, you MUST update documents in this EXACT order:**

### Step 1: Do the Work
- Write code, test, debug
- Take notes as you go

### Step 2: Create Specific Reports
- Technical implementation reports
- Testing reports
- Architecture decision records
- Bug fix reports

**Example files:**
- `BACKEND_ANALYTICS_TESTING_REPORT.md`
- `OPTION_2B_IMPLEMENTATION_REPORT.md`
- `PHASE_6.7_STATUS_REPORT.md`

### Step 3: Create Session Summary
**File:** `SESSION_SUMMARY_YYYY-MM-DD_PhaseX.md`

**Must include:**
- Objectives for the session
- Work completed (with checkmarks)
- Key findings
- Files created/modified
- Git commits
- Next session priorities
- Time tracking

### Step 4: Update Completion Tracker ⚠️ OFTEN FORGOTTEN
**File:** `01_COMPLETION_TRACKER_UPDATED.md`

**Must update:**
- Phase progress percentages
- Phase status (PENDING/IN PROGRESS/COMPLETE)
- Overall completion percentage
- Timeline estimates
- Blockers section for current phase

### Step 5: Update Master Plan ⚠️ OFTEN FORGOTTEN
**File:** `01_MASTER_PLAN.md`

**Must update:**
- Overall completion percentage (header)
- Phase status in summary table
- Phase details section
- Timeline
- Current status section

### Step 6: Update Supporting Docs (As Needed)
- `ARCHITECTURE_DECISIONS.md`
- `TRADE2026_COMPLETION_PLAN.md`
- Appendix files

### Step 7: Git Commit & Push (ALWAYS)
```bash
git add [files]
git commit -m "Detailed message"
git push
```

---

## ⚠️ CRITICAL REMINDERS

### DON'T SKIP STEPS 4 & 5!
**Step 4**: Update Completion Tracker
**Step 5**: Update Master Plan

These are the MOST COMMONLY FORGOTTEN steps. They are MANDATORY.

### Why This Matters
- **Consistency**: All docs show same completion percentage
- **Traceability**: Can trace from overview → details
- **Continuity**: Next session knows exactly where we are
- **Professional**: Proper documentation standards

---

## 🎯 CURRENT PROJECT STATUS (Quick Reference)

**Overall Completion**: 92%
**Current Phase**: Phase 7 - Testing & Validation (50% complete)
**Containers**: 27/27 running, 22/27 healthy (81%)
**Architecture**: Production-ready (validated)

**Phase 7 Blockers (CRITICAL)**:
1. Docker QuestDB connectivity (1-2h to fix)
2. yfinance fallback failure (1h to fix)
3. Limited historical data (2-3h to fix)

**Next Priorities**:
1. Fix QuestDB Docker networking
2. Debug yfinance fallback
3. Backfill historical data
4. Complete backend service testing (7/8 remaining)

---

## 📋 SESSION END CHECKLIST

Before ending ANY session, verify ALL checkboxes:

- [ ] All work committed to git
- [ ] Specific reports created (if applicable)
- [ ] Session summary created
- [ ] **Completion Tracker updated** ← DON'T FORGET
- [ ] **Master Plan updated** ← DON'T FORGET
- [ ] All changes pushed to GitHub
- [ ] Next session priorities documented
- [ ] Blockers clearly identified
- [ ] Time estimates updated

**If ANY checkbox is unchecked, session is NOT complete!**

---

## 🔗 Quick Links

- Process Guide: [00_PROCESS_GUIDE.md](../00_PROCESS_GUIDE.md)
- Master Plan: [01_MASTER_PLAN.md](../01_MASTER_PLAN.md)
- Completion Tracker: [01_COMPLETION_TRACKER_UPDATED.md](../01_COMPLETION_TRACKER_UPDATED.md)
- Latest Session: [SESSION_SUMMARY_2025-10-23_Phase7.md](../SESSION_SUMMARY_2025-10-23_Phase7.md)
- Architecture Decisions: [ARCHITECTURE_DECISIONS.md](../ARCHITECTURE_DECISIONS.md)

---

## 💡 REMEMBER

**These instructions are read by Claude Code at EVERY session start.**

**Purpose**: Ensure consistent process across all sessions, especially with stateless AI.

**Last Updated**: 2025-10-23
**Next Review**: After 5 sessions using this system
