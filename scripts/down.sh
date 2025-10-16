#!/bin/bash
# Stop Trade2026 services
#
# Usage:
#   bash scripts/down.sh           # Stop all services (preserve volumes)
#   bash scripts/down.sh -v        # Stop and remove volumes (DESTRUCTIVE!)

set -e

cd "$(dirname "$0")/../infrastructure/docker"

if [ "$1" == "-v" ]; then
    echo "⚠️  WARNING: This will remove all volumes and delete data!"
    echo "   Press Ctrl+C to cancel, or wait 5 seconds to continue..."
    sleep 5
    echo ""
    echo "🛑 Stopping Trade2026 services and removing volumes..."
    docker-compose down -v
    echo ""
    echo "✅ Services stopped and volumes removed!"
else
    echo "🛑 Stopping Trade2026 services..."
    docker-compose down
    echo ""
    echo "✅ Services stopped! (volumes preserved)"
    echo ""
    echo "💡 To remove volumes (delete data):"
    echo "   bash scripts/down.sh -v"
fi

echo ""
