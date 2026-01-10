#!/bin/bash
# ============================================
# Start Development Environment
# ============================================

set -e

echo "🚀 Starting Sales AI Dojo - Development Environment"
echo ""

# Check if .env files exist
if [ ! -f ./backend/.env ]; then
    echo "⚠️  Backend .env file not found!"
    echo "Creating from .env.example..."
    cp ./backend/.env.example ./backend/.env
    echo "✅ Please edit backend/.env with your API keys"
fi

if [ ! -f ./frontend/.env.local ]; then
    echo "⚠️  Frontend .env.local file not found!"
    echo "Creating from .env.local.example..."
    cp ./frontend/.env.local.example ./frontend/.env.local
    echo "✅ Please edit frontend/.env.local with your configuration"
fi

echo ""
echo "📦 Building and starting containers..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "🌐 Access points:"
echo "   - Frontend: http://localhost"
echo "   - Backend API: http://localhost/api/v1"
echo "   - API Docs: http://localhost/docs"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop environment:"
echo "   ./scripts/dev-down.sh"
