#!/bin/bash
# Start Trade2026 services
#
# Usage:
#   bash scripts/up.sh              # Start all services
#   bash scripts/up.sh --build      # Rebuild and start

set -e

cd "$(dirname "$0")/../infrastructure/docker"

echo "🚀 Starting Trade2026 services..."
echo ""

# Check if --build flag provided
if [ "$1" == "--build" ]; then
    echo "🔨 Building images..."
    docker-compose up -d --build
else
    docker-compose up -d
fi

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Check status:"
echo "   bash scripts/status.sh"
echo "   docker-compose ps"
echo ""
echo "📋 View logs:"
echo "   bash scripts/logs.sh"
echo "   docker-compose logs -f"
echo ""
echo "🌐 Access points:"
echo "   - NATS:        http://localhost:8222 (monitoring)"
echo "   - Valkey:      localhost:6379 (TCP)"
echo "   - QuestDB:     http://localhost:9000 (web console)"
echo "   - ClickHouse:  http://localhost:8123 (HTTP API)"
echo "   - SeaweedFS:   http://localhost:9333 (master)"
echo "   - OpenSearch:  http://localhost:9200 (REST API)"
echo "   - authn:       http://localhost:8114 (authentication)"
echo "   - OPA:         http://localhost:8181 (authorization)"
echo ""
