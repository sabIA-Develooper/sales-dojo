"""
Serviço para gerar e armazenar embeddings com SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import logging
from uuid import UUID
from app.services.openai_service import OpenAIService
from app.db.models import KnowledgeBaseEntry
from sqlalchemy import select, func, delete

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Gerencia geração e armazenamento de embeddings."""

    def __init__(self, db: AsyncSession, openai_service: OpenAIService):
        """
        Inicializa serviço de embeddings.

        Args:
            db: Sessão do banco de dados SQLAlchemy
            openai_service: Serviço OpenAI para gerar embeddings
        """
        self.db = db
        self.openai = openai_service

    async def process_and_store_chunks(
        self,
        chunks: List[Dict[str, Any]],
        company_id: UUID,
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

            # Gera embeddings em batch (mais eficiente ou mock se API não configurada)
            embeddings = await self.openai.generate_embeddings_batch(texts)

            # Cria registros ORM para inserção em batch
            kb_entries = []
            for chunk, embedding in zip(chunks, embeddings):
                metadata = chunk.get("metadata", {})

                entry = KnowledgeBaseEntry(
                    company_id=company_id,
                    content=chunk["content"],
                    source_type=source_type,
                    source_name=metadata.get("source_file", "unknown"),
                    embedding=embedding
                )
                kb_entries.append(entry)

            # Adiciona em batch e faz commit
            self.db.add_all(kb_entries)
            await self.db.commit()

            inserted_count = len(kb_entries)
            logger.info(f"Successfully stored {inserted_count} embeddings")

            return inserted_count

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to process and store embeddings: {e}")
            raise

    async def add_single_entry(
        self,
        content: str,
        company_id: UUID,
        source_type: str,
        source_name: str
    ) -> KnowledgeBaseEntry:
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
            # Gera embedding (real ou mock)
            embedding = await self.openai.generate_embedding(content)

            # Cria nova entrada
            entry = KnowledgeBaseEntry(
                company_id=company_id,
                content=content,
                source_type=source_type,
                source_name=source_name,
                embedding=embedding
            )

            self.db.add(entry)
            await self.db.commit()
            await self.db.refresh(entry)

            logger.info(f"Added single KB entry for company {company_id}")
            return entry

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to add KB entry: {e}")
            raise

    async def update_embedding(self, entry_id: UUID, new_content: str) -> KnowledgeBaseEntry:
        """
        Atualiza conteúdo e embedding de uma entrada existente.

        Args:
            entry_id: ID da entrada
            new_content: Novo conteúdo

        Returns:
            Registro atualizado
        """
        try:
            # Busca a entrada
            result = await self.db.execute(
                select(KnowledgeBaseEntry).where(KnowledgeBaseEntry.id == entry_id)
            )
            entry = result.scalar_one_or_none()

            if not entry:
                raise ValueError(f"KB entry {entry_id} not found")

            # Gera novo embedding
            new_embedding = await self.openai.generate_embedding(new_content)

            # Atualiza
            entry.content = new_content
            entry.embedding = new_embedding

            await self.db.commit()
            await self.db.refresh(entry)

            logger.info(f"Updated KB entry {entry_id}")
            return entry

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update KB entry: {e}")
            raise

    async def delete_entries_by_source(
        self,
        company_id: UUID,
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
            result = await self.db.execute(
                delete(KnowledgeBaseEntry).where(
                    KnowledgeBaseEntry.company_id == company_id,
                    KnowledgeBaseEntry.source_name == source_name
                ).returning(KnowledgeBaseEntry.id)
            )

            await self.db.commit()

            deleted_count = len(result.all())
            logger.info(f"Deleted {deleted_count} entries from source '{source_name}'")

            return deleted_count

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete KB entries: {e}")
            raise

    async def get_company_kb_stats(self, company_id: UUID) -> Dict[str, Any]:
        """
        Obtém estatísticas da knowledge base de uma empresa.

        Args:
            company_id: ID da empresa

        Returns:
            Dicionário com estatísticas
        """
        try:
            # Conta total de entradas
            count_result = await self.db.execute(
                select(func.count()).select_from(KnowledgeBaseEntry).where(
                    KnowledgeBaseEntry.company_id == company_id
                )
            )
            total_entries = count_result.scalar()

            # Busca todas as entradas para análise
            result = await self.db.execute(
                select(KnowledgeBaseEntry.source_type, KnowledgeBaseEntry.source_name).where(
                    KnowledgeBaseEntry.company_id == company_id
                )
            )
            entries = result.all()

            # Agrupa por tipo de fonte
            sources_by_type = {}
            unique_sources = set()

            for source_type, source_name in entries:
                sources_by_type[source_type] = sources_by_type.get(source_type, 0) + 1
                unique_sources.add(source_name)

            stats = {
                "company_id": str(company_id),
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
