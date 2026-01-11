#!/bin/bash
set -e

echo "🚀 Starting Sales AI Dojo Backend..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 0.5
done
echo "✅ PostgreSQL is ready!"

# Run database migrations
echo "📊 Running database migrations..."
alembic upgrade head || {
  echo "⚠️  Migration failed, but continuing..."
}

# Start the application
echo "🎯 Starting FastAPI application..."
exec "$@"
