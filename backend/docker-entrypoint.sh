#!/bin/bash
set -e

echo "🚀 Starting Sales AI Dojo Backend..."

# Wait for PostgreSQL to be ready (with timeout)
echo "⏳ Waiting for PostgreSQL..."
POSTGRES_HOST="${DATABASE_HOST:-postgres}"
POSTGRES_PORT="${DATABASE_PORT:-5432}"
TIMEOUT=30
ELAPSED=0

while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "⚠️  PostgreSQL connection timeout after ${TIMEOUT}s"
    echo "⚠️  Continuing without database connection..."
    break
  fi
  sleep 0.5
  ELAPSED=$((ELAPSED + 1))
done

if nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; then
  echo "✅ PostgreSQL is ready!"
fi

# Run database migrations
echo "📊 Running database migrations..."
alembic upgrade head || {
  echo "⚠️  Migration failed, but continuing..."
}

# Start the application
echo "🎯 Starting FastAPI application..."
exec "$@"
