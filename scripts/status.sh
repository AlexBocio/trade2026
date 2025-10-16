#!/bin/bash
# Check status of Trade2026 services
#
# Usage:
#   bash scripts/status.sh

cd "$(dirname "$0")/../infrastructure/docker"

echo "📊 Trade2026 Service Status"
echo "======================================"
echo ""

# Check if services are running
docker-compose ps

echo ""
echo "🏥 Health Checks:"
echo "======================================"

# NATS
if curl -s -m 2 http://localhost:8222/healthz > /dev/null 2>&1; then
    echo "✅ NATS:        Healthy (http://localhost:8222)"
else
    echo "❌ NATS:        Unhealthy or not responding"
fi

# Valkey
if docker exec valkey valkey-cli ping > /dev/null 2>&1; then
    echo "✅ Valkey:      Healthy (localhost:6379)"
else
    echo "❌ Valkey:      Unhealthy or not running"
fi

# QuestDB (note: can be slow to respond)
if curl -s -m 5 "http://localhost:9000/exec?query=SELECT%201" > /dev/null 2>&1; then
    echo "✅ QuestDB:     Healthy (http://localhost:9000)"
else
    echo "⚠️  QuestDB:     Timeout or not responding (may still be starting)"
fi

# ClickHouse
if curl -s -m 2 http://localhost:8123/ping > /dev/null 2>&1; then
    echo "✅ ClickHouse:  Healthy (http://localhost:8123)"
else
    echo "❌ ClickHouse:  Unhealthy or not responding"
fi

# SeaweedFS
if curl -s -m 2 http://localhost:9333/dir/status > /dev/null 2>&1; then
    echo "✅ SeaweedFS:   Healthy (http://localhost:9333)"
else
    echo "❌ SeaweedFS:   Unhealthy or not responding"
fi

# OpenSearch
if curl -s -m 2 http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo "✅ OpenSearch:  Healthy (http://localhost:9200)"
else
    echo "❌ OpenSearch:  Unhealthy or not responding"
fi

# authn
if curl -s -m 2 http://localhost:8114/health > /dev/null 2>&1; then
    echo "✅ authn:       Healthy (http://localhost:8114)"
else
    echo "❌ authn:       Unhealthy or not responding"
fi

# OPA
if curl -s -m 2 http://localhost:8181/health > /dev/null 2>&1; then
    echo "✅ OPA:         Healthy (http://localhost:8181)"
else
    echo "❌ OPA:         Unhealthy or not responding"
fi

echo ""
echo "======================================"

# Count healthy vs total
TOTAL=8
HEALTHY=0

# Count healthy services
curl -s -m 2 http://localhost:8222/healthz > /dev/null 2>&1 && ((HEALTHY++)) || true
docker exec valkey valkey-cli ping > /dev/null 2>&1 && ((HEALTHY++)) || true
curl -s -m 5 "http://localhost:9000/exec?query=SELECT%201" > /dev/null 2>&1 && ((HEALTHY++)) || true
curl -s -m 2 http://localhost:8123/ping > /dev/null 2>&1 && ((HEALTHY++)) || true
curl -s -m 2 http://localhost:9333/dir/status > /dev/null 2>&1 && ((HEALTHY++)) || true
curl -s -m 2 http://localhost:9200/_cluster/health > /dev/null 2>&1 && ((HEALTHY++)) || true
curl -s -m 2 http://localhost:8114/health > /dev/null 2>&1 && ((HEALTHY++)) || true
curl -s -m 2 http://localhost:8181/health > /dev/null 2>&1 && ((HEALTHY++)) || true

echo "📈 Overall: $HEALTHY/$TOTAL services healthy"
echo ""

if [ $HEALTHY -eq $TOTAL ]; then
    echo "✅ All systems operational!"
elif [ $HEALTHY -ge 6 ]; then
    echo "⚠️  Some services degraded"
else
    echo "❌ Critical: Multiple services down"
    exit 1
fi

echo ""
