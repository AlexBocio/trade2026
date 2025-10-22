# Trade2026 - System Validation Gate

**Purpose**: Comprehensive validation of ALL Trade2026 requirements before implementing Money Flow & Screener components

**Created**: 2025-10-21
**Status**: VALIDATION CHECKPOINT
**Priority**: 🔴 CRITICAL - MUST PASS BEFORE ANY NEW IMPLEMENTATION

---

## 🚦 VALIDATION GATE - MANDATORY CHECKPOINT

**This validation ensures that:**
1. All existing Trade2026 infrastructure is healthy
2. All dependencies are operational
3. All data sources are accessible
4. System is ready for Money Flow & Screener implementation

**If ANY validation fails**: STOP - Fix issues before proceeding

---

## Validation Checklist Summary

**Total Checkpoints**: 50

### Categories:
1. **Infrastructure** (8 checkpoints) - Docker, directories, resources
2. **Services** (10 checkpoints) - QuestDB, ClickHouse, Valkey, backend services
3. **Databases** (9 checkpoints) - Connectivity, queries, writes
4. **Dependencies** (8 checkpoints) - Python packages, libraries
5. **IBKR** (8 checkpoints) - TWS/Gateway, connection, API
6. **Networks & Ports** (7 checkpoints) - Docker networks, port availability

---

## Quick Validation Script

```bash
#!/bin/bash
# Run this script to validate all 50 checkpoints

echo "=== Trade2026 System Validation ==="
echo "Started: $(date)"
echo ""

PASSED=0
FAILED=0

check() {
    if eval "$1" > /dev/null 2>&1; then
        echo "✅ PASS: $2"
        ((PASSED++))
    else
        echo "❌ FAIL: $2"
        ((FAILED++))
    fi
}

# Infrastructure (8)
echo "--- Infrastructure ---"
check "docker --version" "Docker installed"
check "docker ps" "Docker running"
check "test -d C:/ClaudeDesktop_Projects/Trade2026/backend" "backend/ exists"
check "test -d C:/ClaudeDesktop_Projects/Trade2026/frontend" "frontend/ exists"
check "test -d C:/ClaudeDesktop_Projects/Trade2026/library" "library/ exists"
check "test -d C:/ClaudeDesktop_Projects/Trade2026/infrastructure" "infrastructure/ exists"
check "test -f C:/ClaudeDesktop_Projects/Trade2026/docker-compose.yml" "docker-compose.yml exists"
check "df -h | grep -q '20G'" "Sufficient disk space"

# Services (10)
echo ""
echo "--- Services ---"
check "curl -s http://localhost:9000/health" "QuestDB healthy"
check "curl -s http://localhost:8123/ping" "ClickHouse healthy"
check "redis-cli -p 6379 ping" "Valkey healthy"
check "curl -s http://localhost:3001/" "Grafana accessible"
check "curl -s http://localhost:8000/health" "Order Service healthy"
check "curl -s http://localhost:8001/health" "Portfolio Service healthy"
check "curl -s http://localhost:8002/health" "Risk Service healthy"
check "curl -s http://localhost:8003/health" "Execution Service healthy"
check "docker ps | grep -q order_service" "Order Service running"
check "docker ps | grep -q portfolio_service" "Portfolio Service running"

# Databases (9)
echo ""
echo "--- Databases ---"
check "curl -s 'http://localhost:9000/exec?query=SELECT%201'" "QuestDB queries"
check "nc -zv localhost 9009 2>&1 | grep -q succeeded" "QuestDB ILP port"
check "echo 'SELECT 1' | curl -s 'http://localhost:8123/' --data-binary @-" "ClickHouse queries"
check "echo 'SHOW DATABASES' | curl -s 'http://localhost:8123/' --data-binary @-" "ClickHouse databases"
check "redis-cli -p 6379 SET test_key test_value" "Valkey writes"
check "redis-cli -p 6379 GET test_key | grep -q test_value" "Valkey reads"
check "redis-cli -p 6379 DEL test_key" "Valkey deletes"
check "curl -s 'http://localhost:9000/exec?query=SELECT%20COUNT(*)%20FROM%20trades'" "QuestDB has data"
check "echo 'SELECT count() FROM system.tables' | curl -s 'http://localhost:8123/' --data-binary @-" "ClickHouse tables"

# Dependencies (8)
echo ""
echo "--- Dependencies ---"
check "test -f C:/ClaudeDesktop_Projects/Trade2026/backend/requirements.txt" "backend requirements.txt"
check "test -f C:/ClaudeDesktop_Projects/Trade2026/library/requirements.txt" "library requirements.txt"
check "python -c 'import ib_insync'" "ib_insync installed"
check "python -c 'import questdb'" "questdb installed"
check "python -c 'import feast'" "feast installed"
check "python -c 'import xgboost'" "xgboost installed"
check "python -c 'import pandas'" "pandas installed"
check "python -c 'import redis'" "redis installed"

# IBKR (8)
echo ""
echo "--- IBKR ---"
check "test -f C:/ClaudeDesktop_Projects/Trade2026/backend/apps/live_gateway/config.yaml" "IBKR config exists"
check "grep -q '7497\|7496' C:/ClaudeDesktop_Projects/Trade2026/backend/apps/live_gateway/config.yaml" "IBKR ports configured"
check "tasklist | grep -iq 'tws.exe\|ibgateway.exe'" "TWS/Gateway running"
check "netstat -ano | grep -q ':7497'" "Paper trading port listening"
check "python -c 'from ib_insync import IB; ib = IB(); ib.connect(\"127.0.0.1\", 7497, clientId=999); print(\"OK\"); ib.disconnect()'" "IBKR connection test"
check "test -d C:/ClaudeDesktop_Projects/Trade2026/backend/apps/live_gateway" "IBKR gateway directory"
check "grep -q 'client_id' C:/ClaudeDesktop_Projects/Trade2026/backend/apps/live_gateway/config.yaml" "IBKR client ID configured"
check "grep -q 'mode' C:/ClaudeDesktop_Projects/Trade2026/backend/apps/live_gateway/config.yaml" "IBKR mode configured"

# Networks & Ports (7)
echo ""
echo "--- Networks & Ports ---"
check "docker network ls | grep -q trade2026_backend" "Backend network exists"
check "docker network inspect trade2026_backend | grep -q Containers" "Services connected to network"
check "netstat -ano | grep -q ':8000'" "Port 8000 in use"
check "netstat -ano | grep -q ':9000'" "Port 9000 in use"
check "netstat -ano | grep -q ':8123'" "Port 8123 in use"
check "netstat -ano | grep -q ':6379'" "Port 6379 in use"
check "netstat -ano | grep -q ':3001'" "Port 3001 in use"

# Summary
echo ""
echo "=== Summary ==="
TOTAL=$((PASSED + FAILED))
echo "Total Validations: $TOTAL"
echo "Passed: $PASSED / 50"
echo "Failed: $FAILED / 50"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "🎉 ALL VALIDATIONS PASSED"
    echo "✅ Ready to proceed to 01_CONSOLIDATED_IMPLEMENTATION_PROMPT.md"
    exit 0
else
    echo ""
    echo "❌ VALIDATION FAILED"
    echo "⚠️ Fix $FAILED issue(s) before proceeding"
    exit 1
fi
