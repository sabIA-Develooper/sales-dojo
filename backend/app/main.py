"""
FastAPI application entry point.
Sales AI Dojo - Plataforma de treinamento de vendas com IA.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.database import init_database, verify_connection
from app.utils.logger import setup_logging

# Import routers (serão criados depois)
# from app.api.routes import auth, companies, onboarding, personas, sessions, feedback, dashboard
# from app.api.webhooks import vapi

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia lifecycle da aplicação (startup e shutdown).
    """
    # Startup
    logger.info("🚀 Starting Sales AI Dojo API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Inicializa banco de dados
    try:
        await init_database()
        if verify_connection():
            logger.info("✅ Database connection verified")
        else:
            logger.warning("⚠️  Database connection could not be verified")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")

    logger.info("✅ Application startup complete")

    yield

    # Shutdown
    logger.info("👋 Shutting down Sales AI Dojo API...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para plataforma de treinamento de vendas com IA de voz",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log todas as requisições com tempo de processamento."""
    start_time = time.time()

    # Log request
    logger.info(f"➡️  {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response time
    process_time = time.time() - start_time
    logger.info(
        f"⬅️  {request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {process_time:.3f}s"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação do Pydantic."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error in request data"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler genérico para exceções não tratadas."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc) if settings.DEBUG else "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica se a API está funcionando."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health/db", tags=["Health"])
async def database_health_check():
    """Verifica se a conexão com o banco está funcionando."""
    is_healthy = verify_connection()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": "connected" if is_healthy else "disconnected"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "🎯 Sales AI Dojo API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Register API routers (uncomment quando criar as rotas)
# app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
# app.include_router(companies.router, prefix=f"{settings.API_V1_PREFIX}/companies", tags=["Companies"])
# app.include_router(onboarding.router, prefix=f"{settings.API_V1_PREFIX}/onboarding", tags=["Onboarding"])
# app.include_router(personas.router, prefix=f"{settings.API_V1_PREFIX}/personas", tags=["Personas"])
# app.include_router(sessions.router, prefix=f"{settings.API_V1_PREFIX}/sessions", tags=["Training Sessions"])
# app.include_router(feedback.router, prefix=f"{settings.API_V1_PREFIX}/feedback", tags=["Feedback"])
# app.include_router(dashboard.router, prefix=f"{settings.API_V1_PREFIX}/dashboard", tags=["Dashboard"])

# Webhooks
# app.include_router(vapi.router, prefix="/webhooks/vapi", tags=["Webhooks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
