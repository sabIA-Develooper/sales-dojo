"""
Serviço para gerar e armazenar embeddings no Supabase.
"""

from supabase import Client
from typing import List, Dict, Any
import logging
from uuid import UUID
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Gerencia geração e armazenamento de embeddings."""

    def __init__(self, supabase_client: Client, openai_service: OpenAIService):
        """
        Inicializa serviço de embeddings.

        Args:
            supabase_client: Cliente Supabase
            openai_service: Serviço OpenAI para gerar embeddings
        """
        self.supabase = supabase_client
        self.openai = openai_service

    async def process_and_store_chunks(
        self,
        chunks: List[Dict[str, Any]],
        company_id: str,
        source_type: str = "document"
    ) -> int:
        """
        Processa chunks, gera embeddings e armazena no banco.

        Args:
            chunks: Lista de chunks (da DocumentProcessor)
            company_id: ID da empresa
            source_type: Tipo da fonte ('document', 'website', 'manual')

        Returns:
            Número de embeddings criados

        Raises:
            Exception: Se houver erro no processamento
        """
        if not chunks:
            logger.warning("No chunks to process")
            return 0

        try:
            logger.info(f"Processing {len(chunks)} chunks for company {company_id}")

            # Extrai textos dos chunks
            texts = [chunk["content"] for chunk in chunks]

            # Gera embeddings em batch (mais eficiente)
            embeddings = await self.openai.generate_embeddings_batch(texts)

            # Prepara registros para inserção
            records = []
            for chunk, embedding in zip(chunks, embeddings):
                metadata = chunk.get("metadata", {})

                record = {
                    "company_id": company_id,
                    "content": chunk["content"],
                    "source_type": source_type,
                    "source_name": metadata.get("source_file", "unknown"),
                    "embedding": embedding
                }
                records.append(record)

            # Insere em batch no Supabase
            result = self.supabase.table("knowledge_base").insert(records).execute()

            inserted_count = len(result.data) if result.data else 0
            logger.info(f"Successfully stored {inserted_count} embeddings")

            return inserted_count

        except Exception as e:
            logger.error(f"Failed to process and store embeddings: {e}")
            raise

    async def add_single_entry(
        self,
        content: str,
        company_id: str,
        source_type: str,
        source_name: str
    ) -> Dict[str, Any]:
        """
        Adiciona uma única entrada à knowledge base.

        Args:
            content: Conteúdo textual
            company_id: ID da empresa
            source_type: Tipo da fonte
            source_name: Nome da fonte

        Returns:
            Registro criado
        """
        try:
            # Gera embedding
            embedding = await self.openai.generate_embedding(content)

            # Insere no banco
            record = {
                "company_id": company_id,
                "content": content,
                "source_type": source_type,
                "source_name": source_name,
                "embedding": embedding
            }

            result = self.supabase.table("knowledge_base").insert(record).execute()

            logger.info(f"Added single KB entry for company {company_id}")
            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Failed to add KB entry: {e}")
            raise

    async def update_embedding(self, entry_id: str, new_content: str) -> Dict[str, Any]:
        """
        Atualiza conteúdo e embedding de uma entrada existente.

        Args:
            entry_id: ID da entrada
            new_content: Novo conteúdo

        Returns:
            Registro atualizado
        """
        try:
            # Gera novo embedding
            new_embedding = await self.openai.generate_embedding(new_content)

            # Atualiza no banco
            result = self.supabase.table("knowledge_base").update({
                "content": new_content,
                "embedding": new_embedding
            }).eq("id", entry_id).execute()

            logger.info(f"Updated KB entry {entry_id}")
            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Failed to update KB entry: {e}")
            raise

    async def delete_entries_by_source(
        self,
        company_id: str,
        source_name: str
    ) -> int:
        """
        Remove todas as entradas de uma fonte específica.

        Args:
            company_id: ID da empresa
            source_name: Nome da fonte

        Returns:
            Número de entradas removidas
        """
        try:
            result = self.supabase.table("knowledge_base").delete().eq(
                "company_id", company_id
            ).eq(
                "source_name", source_name
            ).execute()

            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted_count} entries from source '{source_name}'")

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete KB entries: {e}")
            raise

    async def get_company_kb_stats(self, company_id: str) -> Dict[str, Any]:
        """
        Obtém estatísticas da knowledge base de uma empresa.

        Args:
            company_id: ID da empresa

        Returns:
            Dicionário com estatísticas
        """
        try:
            # Conta total de entradas
            result = self.supabase.table("knowledge_base").select(
                "id, source_type, source_name", count="exact"
            ).eq("company_id", company_id).execute()

            total_entries = result.count if hasattr(result, 'count') else len(result.data)

            # Agrupa por tipo de fonte
            sources_by_type = {}
            unique_sources = set()

            if result.data:
                for entry in result.data:
                    source_type = entry.get("source_type", "unknown")
                    source_name = entry.get("source_name", "unknown")

                    sources_by_type[source_type] = sources_by_type.get(source_type, 0) + 1
                    unique_sources.add(source_name)

            stats = {
                "company_id": company_id,
                "total_entries": total_entries,
                "unique_sources": len(unique_sources),
                "entries_by_type": sources_by_type,
                "is_ready": total_entries >= 5  # Mínimo de 5 entradas para considerar pronto
            }

            logger.debug(f"KB stats for company {company_id}: {total_entries} entries")
            return stats

        except Exception as e:
            logger.error(f"Failed to get KB stats: {e}")
            raise
