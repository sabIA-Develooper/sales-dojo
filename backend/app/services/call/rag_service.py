"""
Serviço RAG (Retrieval-Augmented Generation) para buscar conhecimento durante chamadas.
"""

from supabase import Client
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class RAGService:
    """Serviço de Retrieval-Augmented Generation para buscar conhecimento."""

    def __init__(self, supabase_client: Client, openai_service: OpenAIService):
        """
        Inicializa serviço RAG.

        Args:
            supabase_client: Cliente Supabase para busca vetorial
            openai_service: Serviço OpenAI para gerar embeddings
        """
        self.supabase = supabase_client
        self.openai = openai_service

    async def search(
        self,
        query: str,
        company_id: str,
        threshold: float = None,
        limit: int = None
    ) -> str:
        """
        Busca informações relevantes no knowledge base usando similaridade vetorial.

        Args:
            query: Pergunta ou tópico a buscar
            company_id: ID da empresa
            threshold: Score mínimo de similaridade (0-1)
            limit: Máximo de documentos a retornar

        Returns:
            Contexto concatenado dos documentos mais relevantes
        """
        threshold = threshold or settings.RAG_SIMILARITY_THRESHOLD
        limit = limit or settings.RAG_MAX_RESULTS

        try:
            # Gera embedding da query
            logger.debug(f"Generating embedding for query: {query[:50]}...")
            query_embedding = await self.openai.generate_embedding(query)

            # Busca vetorial no Supabase usando função RPC
            logger.debug(f"Searching knowledge base for company {company_id}")
            results = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': limit,
                    'company_id': company_id
                }
            ).execute()

            if not results.data:
                logger.info("No relevant documents found in knowledge base")
                return "Nenhuma informação específica encontrada na base de conhecimento."

            # Formata contexto dos documentos encontrados
            context_parts = []
            for i, doc in enumerate(results.data, 1):
                similarity = doc.get('similarity', 0)
                source_type = doc.get('source_type', 'unknown')
                source_name = doc.get('source_name', 'unknown')
                content = doc.get('content', '')

                context_parts.append(
                    f"[Documento {i} - {source_type}: {source_name}] "
                    f"(relevância: {similarity:.2%})\n{content}"
                )

            context = "\n\n".join(context_parts)
            logger.info(f"Found {len(results.data)} relevant documents (threshold: {threshold})")

            return context

        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            # Em caso de erro, retorna mensagem genérica ao invés de falhar
            return "Erro ao buscar informações na base de conhecimento."

    async def search_with_details(
        self,
        query: str,
        company_id: str,
        threshold: float = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Busca informações retornando detalhes estruturados.

        Args:
            query: Pergunta ou tópico
            company_id: ID da empresa
            threshold: Score mínimo de similaridade
            limit: Máximo de resultados

        Returns:
            Lista de dicionários com documentos e scores
        """
        threshold = threshold or settings.RAG_SIMILARITY_THRESHOLD
        limit = limit or settings.RAG_MAX_RESULTS

        try:
            query_embedding = await self.openai.generate_embedding(query)

            results = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': limit,
                    'company_id': company_id
                }
            ).execute()

            return results.data if results.data else []

        except Exception as e:
            logger.error(f"RAG detailed search failed: {e}")
            return []

    async def enrich_prompt(
        self,
        user_message: str,
        company_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Enriquece um prompt de usuário com contexto relevante do knowledge base.
        Útil para adicionar contexto antes de enviar para LLM.

        Args:
            user_message: Mensagem do usuário
            company_id: ID da empresa
            conversation_history: Histórico da conversa (para determinar tópico)

        Returns:
            Prompt enriquecido com contexto
        """
        # Determina tópico da busca
        # Se tiver histórico, pode usar últimas mensagens para contexto
        search_query = user_message

        if conversation_history and len(conversation_history) > 0:
            # Pega últimas 3 mensagens para contexto
            recent_messages = conversation_history[-3:]
            context_text = " ".join([msg.get("content", "") for msg in recent_messages])
            search_query = f"{context_text} {user_message}"

        # Busca contexto relevante
        context = await self.search(
            query=search_query,
            company_id=company_id,
            limit=2  # Menos resultados para não sobrecarregar prompt
        )

        # Monta prompt enriquecido
        enriched_prompt = f"""Contexto da base de conhecimento:
{context}

---

Mensagem do usuário: {user_message}

Responda baseando-se no contexto fornecido sempre que possível."""

        return enriched_prompt
