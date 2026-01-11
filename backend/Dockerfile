# ============================================
# Multi-stage Dockerfile for Backend (FastAPI)
# ============================================

# Stage 1: Base image with dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ============================================
# Stage 2: Development
# ============================================
FROM base as development

# Install development dependencies
RUN pip install --upgrade pip

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create upload directory
RUN mkdir -p /tmp/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]

# Run with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Stage 3: Builder (for production)
# ============================================
FROM base as builder

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# ============================================
# Stage 4: Production
# ============================================
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /tmp/uploads && \
    chown -R appuser:appuser /app /tmp/uploads

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]

# Run with multiple workers for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
