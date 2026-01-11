"""
Configuração do banco de dados PostgreSQL com SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


# Base class para models SQLAlchemy
class Base(DeclarativeBase):
    """Base class para todos os models."""
    pass


# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,  # Verifica conexão antes de usar
)

# Create sync engine (para migrations e ops síncronas)
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,
)

# Session factories
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency para obter sessão async do banco.

    Usage em FastAPI:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    """
    Dependency para obter sessão síncrona (migrations, scripts).
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_database() -> None:
    """
    Inicializa o banco de dados.

    - Verifica conexão
    - Extensões (pgvector, uuid-ossp) são criadas via init.sql

    Note: Tabelas são criadas via Alembic migrations, não aqui.
    """
    try:
        async with async_engine.begin() as conn:
            # Verifica se consegue conectar
            result = await conn.execute("SELECT 1")

        logger.info("✅ Database connection successful")
        logger.info(f"📊 Database: {settings.DATABASE_URL.split('@')[1]}")  # Não loga senha

    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise


async def verify_connection() -> bool:
    """
    Verifica se a conexão com o banco está funcionando.
    Útil para health checks.

    Returns:
        True se conectado, False caso contrário
    """
    try:
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def close_database() -> None:
    """
    Fecha conexões do banco.
    Chamado no shutdown da aplicação.
    """
    try:
        await async_engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
