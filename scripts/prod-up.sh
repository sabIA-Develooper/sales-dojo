#!/bin/bash
# ============================================
# Start Production Environment
# ============================================

set -e

echo "🚀 Starting Sales AI Dojo - Production Environment"
echo ""

# Check if .env files exist
if [ ! -f ./backend/.env ]; then
    echo "❌ Backend .env file not found!"
    echo "Please create backend/.env with production configuration"
    exit 1
fi

if [ ! -f ./frontend/.env.local ]; then
    echo "❌ Frontend .env.local file not found!"
    echo "Please create frontend/.env.local with production configuration"
    exit 1
fi

echo ""
echo "📦 Building production images (this may take a while)..."
docker-compose -f docker-compose.prod.yml build

echo ""
echo "🚢 Starting production containers..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 15

echo ""
echo "✅ Production environment is running!"
echo ""
echo "🌐 Access points:"
echo "   - Frontend: http://localhost (or your domain)"
echo "   - Backend API: http://localhost/api/v1"
echo "   - API Docs: http://localhost/docs"
echo ""
echo "📝 View logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "📊 Check status:"
echo "   docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "🛑 Stop environment:"
echo "   ./scripts/prod-down.sh"
