#!/bin/bash
# ============================================
# Rebuild Docker Containers
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

echo "🔧 Rebuilding containers for $ENV environment"
echo ""

# Stop containers
echo "🛑 Stopping containers..."
docker-compose -f $COMPOSE_FILE down

# Rebuild with no cache
echo "📦 Rebuilding images (no cache)..."
docker-compose -f $COMPOSE_FILE build --no-cache

# Start containers
echo "🚀 Starting containers..."
docker-compose -f $COMPOSE_FILE up -d

echo ""
echo "✅ Rebuild complete!"
echo ""
echo "📝 View logs:"
echo "   ./scripts/logs.sh $1"
