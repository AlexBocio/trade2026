# VALIDATION GATE TEMPLATE

**Add this section to EVERY task instruction file**

---

## 🚦 VALIDATION GATE - MANDATORY CHECKPOINT

**Before starting this task, validate ALL previous tasks are working correctly.**

### Prerequisites Validation

**For this task, you MUST verify**:

#### Previous Task Integration Tests
```bash
# [TASK-SPECIFIC INTEGRATION TESTS GO HERE]
# Example:
# - Verify Task 01 directories exist
# - Verify Task 02 networks operational
# - Test integration between previous tasks
```

#### Component Health Checks
```bash
# [TASK-SPECIFIC HEALTH CHECKS GO HERE]
# Example:
# - All services from Task 03 healthy
# - Networks from Task 02 operational
# - Directories from Task 01 accessible
```

#### Integration Testing
Test that all previous tasks work TOGETHER:
```bash
# [CROSS-TASK INTEGRATION TESTS GO HERE]
# Example:
# - Services use correct networks
# - Services write to correct directories
# - All components communicating
```

### Validation Checklist

**I confirm that**:
- [ ] All previous tasks completed successfully
- [ ] All integration tests passed
- [ ] All health checks passing
- [ ] No errors in previous task logs
- [ ] Documentation from previous tasks complete

**If ANY item fails**:
1. ❌ STOP - Do NOT proceed with this task
2. Go back to failed task
3. Fix the issue
4. Re-run validation
5. Only proceed when ALL pass

### Proceed/Stop Decision

**Can I proceed to this task?**
- ✅ YES - All validations passed → Continue to OBJECTIVE section
- ❌ NO - Something failed → STOP and fix issues first

---

**Only proceed to OBJECTIVE section after passing this validation gate.**

---
