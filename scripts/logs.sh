#!/bin/bash
# View logs for Trade2026 services
#
# Usage:
#   bash scripts/logs.sh              # All services (follow mode)
#   bash scripts/logs.sh nats         # Specific service (follow mode)
#   bash scripts/logs.sh --tail=100   # Last 100 lines (all services)
#   bash scripts/logs.sh nats --tail=50  # Last 50 lines (specific service)

cd "$(dirname "$0")/../infrastructure/docker"

if [ -z "$1" ]; then
    # No arguments - show all logs in follow mode
    echo "📋 Showing logs for all services (Ctrl+C to exit)..."
    echo ""
    docker-compose logs -f
elif [ "$1" == "--tail="* ]; then
    # --tail flag for all services
    LINES="${1#--tail=}"
    echo "📋 Showing last $LINES lines for all services..."
    echo ""
    docker-compose logs --tail="$LINES"
else
    # Service name provided
    SERVICE="$1"
    shift  # Remove first argument

    if [ ! -z "$1" ] && [[ "$1" == --tail=* ]]; then
        LINES="${1#--tail=}"
        echo "📋 Showing last $LINES lines for $SERVICE..."
        echo ""
        docker-compose logs --tail="$LINES" "$SERVICE"
    else
        echo "📋 Showing logs for $SERVICE (Ctrl+C to exit)..."
        echo ""
        docker-compose logs -f "$SERVICE" "$@"
    fi
fi
