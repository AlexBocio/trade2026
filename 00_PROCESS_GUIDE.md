# Trade2026 - Development Process Guide

**Purpose**: Standard operating procedures for all work sessions
**Created**: 2025-10-23
**Status**: MANDATORY - Follow this for every session

---

## 📚 MASTER GUIDELINES REFERENCE

**This process guide is Trade2026-specific. It extends (not replaces) the universal master guidelines.**

**ALWAYS read the master guidelines first:**
- **Location**: `C:/ClaudeDesktop_Projects/ClaudeKnowledge/MASTER_GUIDELINES.md`
- **Scope**: Universal patterns for ALL projects
- **Key Sections**: Session Startup Protocol, Core Dev Rules, 6-Phase Workflow, Git Workflow

**Master guidelines provide the foundation. This document adds Trade2026-specific documentation cascade requirements.**

---

## 🔄 SESSION STARTUP CHECKLIST

When starting ANY session, read these files IN ORDER:

1. **00_PROCESS_GUIDE.md** (THIS FILE) - How to work
2. **01_README_START_HERE.md** - Project overview
3. **01_MASTER_PLAN.md** - Current status and phases
4. **01_COMPLETION_TRACKER_UPDATED.md** - Detailed task tracking
5. **SESSION_SUMMARY_[latest].md** - What happened last session

**WHY THIS ORDER?**
- Process guide first = know HOW to work
- README = understand WHAT we're building
- Master Plan = know WHERE we are
- Completion Tracker = know WHAT to do next
- Session Summary = know what was JUST done

---

## 📝 DOCUMENTATION CASCADE (MANDATORY)

**CRITICAL**: Always update documents in this EXACT order after completing work:

### Step 1: Do the Work
- Write code, test, debug, etc.
- Take notes as you go

### Step 2: Specific Reports (Most Detailed)
Create technical reports for the specific work:
- Implementation reports (e.g., `BACKEND_ANALYTICS_TESTING_REPORT.md`)
- Testing reports
- Architecture decision records
- Bug fix reports

**Purpose**: Capture technical details, decisions, findings

### Step 3: Session Summary (Mid-Level)
Create `SESSION_SUMMARY_YYYY-MM-DD_PhaseX.md` with:
- Objectives for the session
- Work completed
- Key findings
- Files created/modified
- Git commits
- Next session priorities
- Time tracking

**Purpose**: Record what happened in this session for next session continuity

### Step 4: Completion Tracker (High-Level Phase Tracking)
Update `01_COMPLETION_TRACKER_UPDATED.md`:
- Update phase progress percentages
- Update phase status (PENDING/IN PROGRESS/COMPLETE)
- Add new phase sections as needed
- Update overall completion percentage
- Update timeline estimates
- Document blockers

**Purpose**: Track phase-level progress and status

### Step 5: Master Plan (Highest-Level Project Overview)
Update `01_MASTER_PLAN.md`:
- Update overall completion percentage
- Update phase status in summary table
- Update current status section
- Update timeline
- Add/update phase detail sections

**Purpose**: Provide project-level overview and status

### Step 6: Supporting Documents (As Needed)
Update appendices, architecture docs, etc. if relevant:
- `ARCHITECTURE_DECISIONS.md`
- `TRADE2026_COMPLETION_PLAN.md`
- Appendix files
- README files

### Step 7: Git Commit & Push (ALWAYS)
```bash
# Stage files
git add [specific files]

# Commit with detailed message
git commit -m "Descriptive commit message with:
- What was done
- Why it was done
- Key changes
- Files affected
"

# Push to GitHub
git push
```

**CRITICAL**: NEVER skip steps 4 & 5 (Completion Tracker and Master Plan)!

---

## 🚫 COMMON MISTAKES TO AVOID

### ❌ DON'T:
1. **Skip the documentation cascade** - All steps must be done
2. **Update documents out of order** - Follow the exact sequence
3. **Update only some documents** - All must be updated together
4. **Commit without updating master docs** - Master Plan and Completion Tracker are mandatory
5. **Leave todo lists stale** - Clean up when tasks are done
6. **Batch multiple sessions** - Document after each session

### ✅ DO:
1. **Follow the cascade every time** - No exceptions
2. **Keep documents in sync** - All should show same percentages
3. **Create session summaries** - Essential for continuity
4. **Update percentages consistently** - Use same values across all docs
5. **Document blockers** - Critical for next session planning
6. **Commit frequently** - After each major milestone

---

## 📊 PROGRESS TRACKING RULES

### Completion Percentages
- Must be consistent across ALL documents
- Round to nearest 1% (e.g., 92%, not 92.3%)
- Update in order: Specific → Session → Tracker → Master Plan

### Phase Status Values
- **⏸️ PENDING**: Not started, approved for future work
- **🚀 IN PROGRESS**: Currently active work
- **✅ COMPLETE**: Fully finished and verified
- **⏸️ SKIPPED**: Intentionally not doing
- **❌ BLOCKED**: Cannot proceed due to dependencies

### Time Estimates
- Always provide ranges (e.g., 6-11 hours)
- Update as work progresses
- Reduce total remaining time as phases complete

---

## 🔍 PHASE TRANSITION CHECKLIST

When completing a phase:

1. **Verify all phase objectives met**
2. **Run final tests/validation**
3. **Create phase completion report**
4. **Update all documentation cascade**
5. **Mark phase as COMPLETE in all docs**
6. **Update next phase to IN PROGRESS**
7. **Commit with "Phase X COMPLETE" message**
8. **Push to GitHub**

---

## 🎯 SESSION END CHECKLIST

Before ending ANY session:

- [ ] All work committed to git
- [ ] Session summary created
- [ ] Completion Tracker updated
- [ ] Master Plan updated
- [ ] All changes pushed to GitHub
- [ ] Next session priorities documented
- [ ] Blockers clearly identified
- [ ] Time estimates updated

**If ANY checkbox is unchecked, session is NOT complete!**

---

## 🆘 TROUBLESHOOTING

### "I forgot to update master docs!"
1. Read the last commit message
2. Check what work was done
3. Update Completion Tracker immediately
4. Update Master Plan immediately
5. Create follow-up commit: "docs: Complete documentation cascade"
6. Push to GitHub

### "Percentages are inconsistent across docs!"
1. Decide on the correct percentage
2. Update ALL documents to match:
   - Session summary
   - Completion Tracker (header + phase table)
   - Master Plan (header + phase table + current status)
3. Commit: "docs: Fix inconsistent completion percentages"

### "I'm not sure what to work on next"
1. Read `01_COMPLETION_TRACKER_UPDATED.md`
2. Look for phase marked IN PROGRESS
3. Check "Next Steps" section in that phase
4. Read last session summary for context
5. Start with highest priority (P0) items first

---

## 💡 WHY THIS PROCESS MATTERS

### For You (Developer/AI):
- Know exactly what to do each session
- Avoid forgetting critical updates
- Maintain consistency across documentation
- Enable traceability from overview to details

### For Future Sessions:
- Stateless AI can pick up exactly where you left off
- No context loss between sessions
- Clear priorities and next steps
- Complete work history

### For Project Quality:
- Professional documentation
- Consistent tracking
- Easy handoff to other developers
- Audit trail of all decisions

---

## 📅 SESSION WORKFLOW EXAMPLE

**Example: Completing 4 hours of Phase 7 work**

1. **Start Session** (5 min)
   - Read process guide (this file)
   - Read master plan
   - Read completion tracker
   - Read last session summary
   - Understand current priorities

2. **Do the Work** (3 hours)
   - Fix QuestDB connectivity
   - Test backend services
   - Document findings

3. **Create Documentation** (45 min)
   - Write testing report (specific)
   - Write session summary (mid-level)
   - Update completion tracker (high-level)
   - Update master plan (overview)

4. **Git Commit & Push** (10 min)
   - Stage all files
   - Write detailed commit message
   - Push to GitHub
   - Verify push succeeded

**Total**: 4 hours (including documentation)

---

## 🔗 DOCUMENT RELATIONSHIPS

```
00_PROCESS_GUIDE.md (THIS FILE)
    ↓ (guides how to work)
    ↓
01_MASTER_PLAN.md (Project Overview)
    ↓ (references)
    ↓
01_COMPLETION_TRACKER_UPDATED.md (Phase Details)
    ↓ (references)
    ↓
SESSION_SUMMARY_YYYY-MM-DD.md (Session History)
    ↓ (references)
    ↓
[Specific Reports] (Technical Details)
    - BACKEND_ANALYTICS_TESTING_REPORT.md
    - OPTION_2B_IMPLEMENTATION_REPORT.md
    - ARCHITECTURE_DECISIONS.md
    - etc.
```

**Navigation Path**: Always start at the top and drill down as needed.

---

## 🎓 LEARNING FROM MISTAKES

### Mistake Made: 2025-10-23 Session
**What Happened**: Completed Phase 7 work but only updated specific reports and session summary. Skipped Completion Tracker and Master Plan updates.

**Impact**: Documentation was inconsistent. Master docs showed 91% while reality was 92%. Phase 7 showed "NEXT" when it was actually "IN PROGRESS at 50%".

**Lesson**: ALWAYS complete the full cascade. Never skip steps 4 & 5.

**Fix Applied**: Created this process guide to prevent future occurrences.

---

## 🤖 CLAUDE CODE INTEGRATION

### Automatic Instructions (.claude folder)

**Claude Code automatically loads instructions from `.claude/instructions.md` at session start!**

**File**: `.claude/instructions.md`
**Purpose**: Remind Claude to follow the process at EVERY session start
**Status**: ✅ Configured

**What it contains:**
- Mandatory reading order (5 files)
- Documentation cascade (7 steps)
- Session end checklist
- Current project status
- Critical reminders (don't skip steps 4 & 5!)
- Quick links to key documents

**How it works:**
1. User starts Claude Code session
2. Claude automatically reads `.claude/instructions.md`
3. Instructions are injected into context
4. Claude is reminded to:
   - Read process guide first
   - Follow documentation cascade
   - Update all master docs
   - Complete session end checklist

**This provides automatic enforcement of the process!**

---

## ✅ PROCESS ADOPTION CHECKLIST

To adopt this process:

- [x] Process guide created (00_PROCESS_GUIDE.md)
- [x] Process guide added to README
- [x] Process guide added to .claude/instructions.md
- [x] Claude Code automatic instructions configured
- [ ] All team members trained on process
- [ ] Process validated in next session

---

**Remember**: This process exists because we learned it's needed. Follow it religiously, and documentation will always be consistent and complete.

**Questions?** Add them to this file so future sessions have the answers.

---

**Last Updated**: 2025-10-23
**Next Review**: After 3 sessions using this process
**Owner**: Project Lead (enforces process compliance)
