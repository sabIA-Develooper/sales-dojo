#!/bin/bash
# ============================================
# Stop Development Environment
# ============================================

set -e

echo "🛑 Stopping Sales AI Dojo - Development Environment"
echo ""

docker-compose down

echo ""
echo "✅ Development environment stopped!"
echo ""
echo "💡 To remove volumes as well (will delete data):"
echo "   docker-compose down -v"
