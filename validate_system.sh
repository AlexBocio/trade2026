#!/bin/bash
# Trade2026 System Validation - 50 Checkpoints

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
check "test -d /c/claudedesktop_projects/trade2026/backend" "backend/ exists"
check "test -d /c/claudedesktop_projects/trade2026/frontend" "frontend/ exists"
check "test -d /c/claudedesktop_projects/trade2026/library" "library/ exists"
check "test -d /c/claudedesktop_projects/trade2026/infrastructure" "infrastructure/ exists"
check "test -f /c/claudedesktop_projects/trade2026/infrastructure/docker/docker-compose.core.yml" "docker-compose files exist"
check "df -h | grep -q '20G\|100G\|200G'" "Sufficient disk space"

# Services (10)
echo ""
echo "--- Services ---"
check "curl -sf http://localhost:9000/" "QuestDB healthy"
check "curl -sf http://localhost:8123/ping" "ClickHouse healthy"
check "docker exec valkey valkey-cli PING" "Valkey healthy"
check "curl -sf http://localhost:8222/healthz" "NATS healthy"
check "curl -sf http://localhost:8000/health" "Order Service healthy"
check "curl -sf http://localhost:8100/health" "Portfolio Service healthy"
check "curl -sf http://localhost:8150/health" "Risk Service healthy"
check "curl -sf http://localhost:8010/health" "Execution Service healthy"
check "docker ps | grep -q order" "Order Service container running"
check "docker ps | grep -q portfolio" "Portfolio Service container running"

# Databases (9)
echo ""
echo "--- Databases ---"
check "curl -sf 'http://localhost:9000/exec?query=SELECT%201'" "QuestDB queries"
check "echo 'SELECT 1' | curl -sf 'http://localhost:8123/' --data-binary @-" "ClickHouse queries"
check "echo 'SHOW DATABASES' | curl -sf 'http://localhost:8123/' --data-binary @-" "ClickHouse databases"
check "docker exec valkey valkey-cli SET test_key test_value" "Valkey writes"
check "docker exec valkey valkey-cli GET test_key | grep -q test_value" "Valkey reads"
check "docker exec valkey valkey-cli DEL test_key" "Valkey deletes"
check "docker exec postgres-library pg_isready -U trader" "PostgreSQL healthy"
check "docker ps | grep -q questdb" "QuestDB container running"
check "docker ps | grep -q clickhouse" "ClickHouse container running"

# Dependencies (8)
echo ""
echo "--- Dependencies ---"
check "test -f /c/claudedesktop_projects/trade2026/backend/core/requirements.txt" "backend requirements.txt"
check "test -f /c/claudedesktop_projects/trade2026/library/requirements.txt" "library requirements.txt"
check "python -c 'import questdb'" "questdb package installed"
check "python -c 'import pandas'" "pandas installed"
check "python -c 'import numpy'" "numpy installed"
check "python -c 'import asyncio'" "asyncio available"
check "python -c 'import yaml'" "pyyaml installed"
check "python -c 'import nats'" "nats-py installed"

# IBKR (8)
echo ""
echo "--- IBKR ---"
check "test -f /c/claudedesktop_projects/trade2026/backend/apps/live_gateway/config.yaml" "IBKR config exists"
check "grep -q '7497\|7496' /c/claudedesktop_projects/trade2026/backend/apps/live_gateway/config.yaml" "IBKR ports configured"
check "grep -q 'IBKR' /c/claudedesktop_projects/trade2026/backend/apps/live_gateway/config.yaml" "IBKR section in config"
check "test -d /c/claudedesktop_projects/trade2026/backend/apps/live_gateway" "Live gateway directory exists"
check "grep -q 'client_id' /c/claudedesktop_projects/trade2026/backend/apps/live_gateway/config.yaml" "IBKR client ID configured"
check "grep -q 'mode' /c/claudedesktop_projects/trade2026/backend/apps/live_gateway/config.yaml" "IBKR mode configured"
check "grep -q 'SHADOW' /c/claudedesktop_projects/trade2026/backend/apps/live_gateway/config.yaml" "IBKR in SHADOW mode"
check "test -f /c/claudedesktop_projects/trade2026/infrastructure/docker/.env" ".env file exists"

# Networks & Ports (7)
echo ""
echo "--- Networks & Ports ---"
check "docker network ls | grep -q trade2026" "Docker network exists"
check "netstat -ano | grep -q ':8000'" "Port 8000 in use (Order)"
check "netstat -ano | grep -q ':9000'" "Port 9000 in use (QuestDB)"
check "netstat -ano | grep -q ':8123'" "Port 8123 in use (ClickHouse)"
check "netstat -ano | grep -q ':6379'" "Port 6379 in use (Valkey)"
check "netstat -ano | grep -q ':4222'" "Port 4222 in use (NATS)"
check "netstat -ano | grep -q ':8222'" "Port 8222 in use (NATS monitor)"

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
    echo "✅ Ready to proceed to Phase 6 implementation"
    exit 0
else
    echo ""
    echo "❌ VALIDATION FAILED"
    echo "⚠️ Fix $FAILED issue(s) before proceeding"
    exit 1
fi
