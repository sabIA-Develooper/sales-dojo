#!/bin/bash
# ============================================
# View Docker Logs
# ============================================

set -e

# Default to development
COMPOSE_FILE="docker-compose.yml"
ENV="development"

# Check if production flag is passed
if [ "$1" == "prod" ] || [ "$1" == "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV="production"
fi

echo "📝 Viewing logs for $ENV environment"
echo "Press Ctrl+C to exit"
echo ""

# If service name is provided, show only that service
if [ -n "$2" ]; then
    docker-compose -f $COMPOSE_FILE logs -f --tail=100 $2
else
    # Show all services
    docker-compose -f $COMPOSE_FILE logs -f --tail=100
fi
