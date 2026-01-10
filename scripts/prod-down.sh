#!/bin/bash
# ============================================
# Stop Production Environment
# ============================================

set -e

echo "🛑 Stopping Sales AI Dojo - Production Environment"
echo ""

read -p "Are you sure you want to stop production? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

docker-compose -f docker-compose.prod.yml down

echo ""
echo "✅ Production environment stopped!"
echo ""
echo "💡 To remove volumes as well (⚠️  will delete production data):"
echo "   docker-compose -f docker-compose.prod.yml down -v"
