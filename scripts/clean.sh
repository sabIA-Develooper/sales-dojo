#!/bin/bash
# ============================================
# Clean Docker Resources
# ============================================

set -e

echo "🧹 Cleaning Docker Resources"
echo ""

read -p "This will remove stopped containers, unused networks, dangling images. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "🗑️  Removing stopped containers..."
docker container prune -f

echo ""
echo "🗑️  Removing unused networks..."
docker network prune -f

echo ""
echo "🗑️  Removing dangling images..."
docker image prune -f

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "💡 To remove ALL unused images (not just dangling):"
echo "   docker image prune -a"
echo ""
echo "💡 To remove volumes (⚠️  will delete data):"
echo "   docker volume prune"
