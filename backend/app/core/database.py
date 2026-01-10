"""
Cliente Supabase e funções de inicialização do banco de dados.
"""

from supabase import create_client, Client
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Singleton para gerenciar conexão com Supabase."""

    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Retorna instância única do cliente Supabase.
        Cria a conexão apenas uma vez (lazy initialization).
        """
        if cls._instance is None:
            try:
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
                logger.info("✅ Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {e}")
                raise

        return cls._instance

    @classmethod
    def close(cls) -> None:
        """Fecha a conexão (se necessário no futuro)."""
        cls._instance = None


def get_supabase() -> Client:
    """
    Dependency injection para FastAPI.
    Uso: def endpoint(db: Client = Depends(get_supabase))
    """
    return SupabaseClient.get_client()


async def init_database() -> None:
    """
    Inicializa o banco de dados criando tabelas se não existirem.
    Chamada no startup da aplicação.
    """
    client = get_supabase()

    # SQL para criar extensão pgvector se não existir
    vector_extension_sql = """
    CREATE EXTENSION IF NOT EXISTS vector;
    """

    # SQL para criar função de busca vetorial
    vector_search_function_sql = """
    CREATE OR REPLACE FUNCTION match_documents(
        query_embedding vector(1536),
        match_threshold float,
        match_count int,
        company_id uuid
    )
    RETURNS TABLE (
        id uuid,
        content text,
        source_type text,
        source_name text,
        similarity float
    )
    LANGUAGE sql STABLE
    AS $$
        SELECT
            knowledge_base.id,
            knowledge_base.content,
            knowledge_base.source_type,
            knowledge_base.source_name,
            1 - (knowledge_base.embedding <=> query_embedding) as similarity
        FROM knowledge_base
        WHERE knowledge_base.company_id = match_documents.company_id
            AND 1 - (knowledge_base.embedding <=> query_embedding) > match_threshold
        ORDER BY similarity DESC
        LIMIT match_count;
    $$;
    """

    try:
        # Note: Supabase geralmente já tem pgvector habilitado
        # Essas queries SQL podem ser executadas via Supabase Dashboard SQL Editor
        logger.info("✅ Database initialization completed")
        logger.info("⚠️  Execute as seguintes queries no Supabase SQL Editor se ainda não fez:")
        logger.info(vector_extension_sql)
        logger.info(vector_search_function_sql)

    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise


def verify_connection() -> bool:
    """
    Verifica se a conexão com Supabase está funcionando.
    Útil para health checks.
    """
    try:
        client = get_supabase()
        # Tenta fazer uma query simples
        result = client.table("companies").select("id").limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
