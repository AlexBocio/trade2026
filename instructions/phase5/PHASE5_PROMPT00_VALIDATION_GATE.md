# PHASE 5 - PROMPT 00: VALIDATION GATE
# PRISM Physics Engine - Prerequisites Check

**Task ID**: PHASE5_PROMPT00
**Estimated Time**: 30 minutes
**Component**: Pre-implementation Validation
**Dependencies**: PHASE4 (ML Library must be complete)

---

## 🎯 OBJECTIVE

**Validate that Phase 4 is complete and the system is ready for PRISM Physics Engine.**

PRISM (Probability-based Risk Integration & Simulation Model) is an advanced physics-based trading engine that simulates market forces, order flow dynamics, and price discovery mechanisms.

This is an **OPTIONAL** phase - only proceed if:
- Phase 4 is 100% complete
- You want advanced market simulation capabilities
- You need realistic backtesting with market microstructure
- You want to model complex order flow dynamics

---

## ⚠️ CRITICAL DECISION POINT

### Is PRISM Right for You?

**Proceed with Phase 5 IF**:
- ✅ You need physics-based market simulation
- ✅ You want order book dynamics modeling
- ✅ You need liquidity impact analysis
- ✅ You want realistic slippage modeling
- ✅ You need multi-agent market simulation
- ✅ You have 40-50 hours available (2-3 weeks)

**Skip Phase 5 IF**:
- ❌ Basic backtesting is sufficient
- ❌ You don't need order book simulation
- ❌ Statistical models are enough
- ❌ Time-constrained project
- ❌ Simpler execution is preferred

---

## 📋 VALIDATION CHECKLIST

### PHASE 4 COMPLETION VALIDATION

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

echo "=== PHASE 4 VALIDATION GATE ==="
echo ""

# ==================== 1. LIBRARY SERVICE ====================
echo "1. Checking Library Service..."

# API healthy
curl -sf http://localhost:8350/health > /dev/null 2>&1 && \
    echo "   ✅ Library API running" || \
    { echo "   ❌ Library API DOWN - Complete Phase 4 first"; exit 1; }

# Database operational
docker exec postgres-library psql -U postgres -d library -c "SELECT COUNT(*) FROM entities;" > /dev/null 2>&1 && \
    echo "   ✅ PostgreSQL healthy" || \
    { echo "   ❌ PostgreSQL DOWN"; exit 1; }

# NATS connected
curl -s http://localhost:8350/health/detailed | grep -q "nats" && \
    echo "   ✅ NATS integrated" || \
    echo "   ⚠️  NATS may not be connected"

echo ""

# ==================== 2. ENTITY MANAGEMENT ====================
echo "2. Checking Entity Management..."

# Can list entities
ENTITY_COUNT=$(curl -s "http://localhost:8350/api/v1/entities" | jq -r '.total' 2>/dev/null)
if [ -n "$ENTITY_COUNT" ] && [ "$ENTITY_COUNT" -ge 0 ]; then
    echo "   ✅ Entity CRUD working ($ENTITY_COUNT entities)"
else
    echo "   ❌ Entity CRUD not working"
    exit 1
fi

# Can create test entity
TEST_ENTITY=$(curl -s -X POST "http://localhost:8350/api/v1/entities" \
  -H "Content-Type: application/json" \
  -d '{"name":"phase5_validation_'$(date +%s)'","type":"strategy","version":"1.0.0"}' 2>/dev/null | \
  jq -r '.entity_id' 2>/dev/null)

if [ -n "$TEST_ENTITY" ] && [ "$TEST_ENTITY" != "null" ]; then
    echo "   ✅ Can create entities"
    # Clean up test entity
    curl -s -X DELETE "http://localhost:8350/api/v1/entities/$TEST_ENTITY" > /dev/null 2>&1
else
    echo "   ❌ Cannot create entities"
    exit 1
fi

echo ""

# ==================== 3. DEPLOYMENT SYSTEM ====================
echo "3. Checking Deployment System..."

# Deployments table exists
docker exec postgres-library psql -U postgres -d library -c \
    "SELECT COUNT(*) FROM deployments;" > /dev/null 2>&1 && \
    echo "   ✅ Deployments table exists" || \
    { echo "   ❌ Deployments table missing"; exit 1; }

# Can list deployments
DEPLOY_COUNT=$(curl -s "http://localhost:8350/api/v1/deployments" 2>/dev/null | jq -r '.total' 2>/dev/null)
if [ -n "$DEPLOY_COUNT" ] && [ "$DEPLOY_COUNT" -ge 0 ]; then
    echo "   ✅ Deployment API working ($DEPLOY_COUNT deployments)"
else
    echo "   ❌ Deployment API not working"
    exit 1
fi

echo ""

# ==================== 4. HOTSWAP ENGINE ====================
echo "4. Checking HotSwap Engine..."

# Swaps table exists
docker exec postgres-library psql -U postgres -d library -c \
    "SELECT COUNT(*) FROM swaps;" > /dev/null 2>&1 && \
    echo "   ✅ Swaps table exists" || \
    { echo "   ❌ Swaps table missing"; exit 1; }

# Can list swaps
SWAP_COUNT=$(curl -s "http://localhost:8350/api/v1/swaps" 2>/dev/null | jq -r '.total' 2>/dev/null)
if [ -n "$SWAP_COUNT" ] && [ "$SWAP_COUNT" -ge 0 ]; then
    echo "   ✅ HotSwap API working ($SWAP_COUNT swaps)"
else
    echo "   ❌ HotSwap API not working"
    exit 1
fi

echo ""

# ==================== 5. DATA INFRASTRUCTURE ====================
echo "5. Checking Data Infrastructure..."

# QuestDB
curl -sf http://localhost:9000/status > /dev/null 2>&1 && \
    echo "   ✅ QuestDB running" || \
    echo "   ⚠️  QuestDB not accessible"

# ClickHouse
curl -sf http://localhost:8123/ping > /dev/null 2>&1 && \
    echo "   ✅ ClickHouse running" || \
    echo "   ⚠️  ClickHouse not accessible"

# Valkey (Redis)
docker exec valkey redis-cli ping > /dev/null 2>&1 && \
    echo "   ✅ Valkey running" || \
    echo "   ⚠️  Valkey not accessible"

echo ""

# ==================== 6. ML PIPELINE ====================
echo "6. Checking ML Pipeline (Optional components)..."

# Check if ML components are running
docker ps | grep -q "feature-pipeline" && \
    echo "   ✅ Feature pipeline container exists" || \
    echo "   ℹ️  Feature pipeline not deployed (optional)"

docker ps | grep -q "ml-training" && \
    echo "   ✅ ML training container exists" || \
    echo "   ℹ️  ML training not deployed (optional)"

docker ps | grep -q "bentoml" && \
    echo "   ✅ BentoML serving" || \
    echo "   ℹ️  BentoML not deployed (optional)"

# MLflow
curl -sf http://localhost:5000 > /dev/null 2>&1 && \
    echo "   ✅ MLflow running" || \
    echo "   ℹ️  MLflow not accessible (optional)"

echo ""

# ==================== 7. BACKEND SERVICES ====================
echo "7. Checking Backend Services..."

# Core services from Phase 3
EXPECTED_SERVICES=("postgres" "timescaledb" "questdb" "clickhouse" "valkey" "nats" "mlflow")
MISSING_SERVICES=0

for service in "${EXPECTED_SERVICES[@]}"; do
    if docker ps | grep -q "$service"; then
        echo "   ✅ $service running"
    else
        echo "   ❌ $service NOT running"
        MISSING_SERVICES=$((MISSING_SERVICES + 1))
    fi
done

if [ $MISSING_SERVICES -gt 0 ]; then
    echo ""
    echo "   ⚠️  $MISSING_SERVICES services missing"
    echo "   Consider completing Phase 3 fully before Phase 5"
fi

echo ""

# ==================== 8. SYSTEM HEALTH ====================
echo "8. Checking System Health..."

# Check for errors in library logs
ERROR_COUNT=$(docker logs library --tail 100 2>&1 | grep -i "error\|fatal\|critical" | wc -l)
if [ "$ERROR_COUNT" -lt 5 ]; then
    echo "   ✅ Library logs clean ($ERROR_COUNT errors)"
else
    echo "   ⚠️  Library has errors ($ERROR_COUNT recent errors)"
    echo "   Review: docker logs library --tail 100"
fi

# Check system resources
CONTAINER_COUNT=$(docker ps | wc -l)
echo "   ℹ️  Running containers: $CONTAINER_COUNT"

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "   ✅ Disk space available (${DISK_USAGE}% used)"
else
    echo "   ⚠️  Disk space low (${DISK_USAGE}% used)"
fi

echo ""

# ==================== 9. FINAL DECISION ====================
echo "9. Phase 5 Readiness Assessment..."
echo ""

# Count critical issues
CRITICAL_ISSUES=0

# Must have library service
curl -sf http://localhost:8350/health > /dev/null 2>&1 || CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))

# Must have database
docker exec postgres-library psql -U postgres -d library -c "SELECT 1;" > /dev/null 2>&1 || \
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))

# Must have entity CRUD
[ -n "$ENTITY_COUNT" ] && [ "$ENTITY_COUNT" -ge 0 ] || CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))

# Must have deployment system
[ -n "$DEPLOY_COUNT" ] && [ "$DEPLOY_COUNT" -ge 0 ] || CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))

# Must have hotswap
[ -n "$SWAP_COUNT" ] && [ "$SWAP_COUNT" -ge 0 ] || CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))

echo "=== VALIDATION RESULTS ==="
echo ""

if [ $CRITICAL_ISSUES -eq 0 ]; then
    echo "✅ ✅ ✅ PHASE 5 READY ✅ ✅ ✅"
    echo ""
    echo "All critical Phase 4 components are operational."
    echo "You may proceed with PRISM Physics Engine implementation."
    echo ""
    echo "Next: PHASE5_PRISM_CONSOLIDATED.md"
    echo ""
    exit 0
else
    echo "❌ ❌ ❌ NOT READY ❌ ❌ ❌"
    echo ""
    echo "Found $CRITICAL_ISSUES critical issue(s)."
    echo "Complete Phase 4 before starting Phase 5."
    echo ""
    echo "Fix issues and re-run this validation."
    echo ""
    exit 1
fi
```

---

## 🎓 UNDERSTANDING THE VALIDATION

### What This Checks

**Critical Requirements** (Must Pass):
1. Library Service API operational
2. PostgreSQL registry working
3. Entity CRUD functional
4. Deployment system operational
5. HotSwap engine working

**Optional Components** (Nice to Have):
- Feature pipeline deployed
- ML training working
- BentoML serving
- MLflow tracking

**Infrastructure Health**:
- All backend services running
- No critical errors in logs
- Sufficient system resources

---

## 📊 VALIDATION RESULTS INTERPRETATION

### ✅ ALL CHECKS PASS
**Action**: Proceed with Phase 5 implementation
**Next File**: PHASE5_PRISM_CONSOLIDATED.md

### ⚠️ SOME WARNINGS
**Action**: Review warnings, decide if acceptable
**Consider**: Fixing warnings before Phase 5

### ❌ CRITICAL FAILURES
**Action**: STOP - Complete Phase 4 first
**Fix**: Address all critical issues
**Re-run**: This validation gate

---

## 🚀 RUNNING THE VALIDATION

### Windows PowerShell:
```powershell
cd C:\ClaudeDesktop_Projects\Trade2026\instructions\phase5

# Make executable (if needed)
# Then run validation
bash PHASE5_PROMPT00_VALIDATION_GATE.md
```

### Git Bash / WSL:
```bash
cd /c/ClaudeDesktop_Projects/Trade2026/instructions/phase5
bash PHASE5_PROMPT00_VALIDATION_GATE.md
```

---

## 📝 DECISION MATRIX

### Proceed with Phase 5 IF:
```
✅ All critical checks pass
✅ You need advanced market simulation
✅ You have 40-50 hours available
✅ Team has physics/simulation knowledge
✅ Project requires realistic backtesting
```

### Skip Phase 5 IF:
```
❌ Any critical check fails
❌ Basic backtesting is sufficient
❌ Time-constrained project
❌ Team lacks simulation experience
❌ Simpler execution preferred
```

---

## 🎯 WHAT IS PRISM?

**PRISM Physics Engine** provides:

- **Order Book Simulation**: Realistic limit order book dynamics
- **Liquidity Modeling**: Market depth and liquidity impact
- **Price Discovery**: Physics-based price formation
- **Slippage Modeling**: Realistic execution costs
- **Market Impact**: Order size effect on prices
- **Multi-Agent Simulation**: Competing traders and market makers
- **Microstructure**: Bid-ask spread dynamics
- **Execution Simulation**: Realistic order fills

**Use Cases**:
- High-fidelity strategy backtesting
- Market impact analysis
- Liquidity research
- Execution algorithm development
- Risk analysis with realistic scenarios

---

## ✅ SUCCESS CRITERIA

After validation:

- [ ] All critical Phase 4 components operational
- [ ] Library Service API healthy
- [ ] PostgreSQL registry working
- [ ] Entity CRUD functional
- [ ] Deployment system operational
- [ ] HotSwap engine working
- [ ] No critical errors in logs
- [ ] Decision made: Proceed or Skip Phase 5
- [ ] Team aligned on Phase 5 scope

---

## 📞 NEXT STEPS

### If Validation Passes:
1. Review PRISM scope and requirements
2. Allocate 40-50 hours (2-3 weeks)
3. Proceed to PHASE5_PRISM_CONSOLIDATED.md
4. Begin implementation

### If Validation Fails:
1. Review error messages
2. Complete missing Phase 4 components
3. Fix critical issues
4. Re-run this validation
5. Do NOT proceed until all pass

---

**Validation Gate**: Phase 5 Prerequisites  
**Estimated Time**: 30 minutes  
**Next**: PHASE5_PRISM_CONSOLIDATED.md (if validation passes)
