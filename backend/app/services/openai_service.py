"""
Serviço para interações com OpenAI API.
Centraliza chamadas para embeddings, chat completion, etc.
"""

from openai import OpenAI, AsyncOpenAI
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Serviço para gerenciar interações com OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa cliente OpenAI.

        Args:
            api_key: Chave da API (usa settings se não fornecido)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding vetorial para um texto.

        Args:
            text: Texto para gerar embedding

        Returns:
            Lista de floats representando o embedding (dimensão 1536)

        Raises:
            Exception: Se houver erro na geração do embedding
        """
        try:
            response = await self.async_client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=text,
                encoding_format="float"
            )

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text (length: {len(text)} chars)")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para múltiplos textos de uma vez (mais eficiente).

        Args:
            texts: Lista de textos

        Returns:
            Lista de embeddings
        """
        try:
            response = await self.async_client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=texts,
                encoding_format="float"
            )

            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Executa chat completion com GPT-4o.

        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "..."}]
            temperature: Criatividade (0-2, default 0.7)
            max_tokens: Máximo de tokens na resposta
            response_format: Formato da resposta (ex: {"type": "json_object"})

        Returns:
            Conteúdo da resposta do modelo

        Raises:
            Exception: Se houver erro na completion
        """
        try:
            kwargs = {
                "model": settings.OPENAI_CHAT_MODEL,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            if response_format:
                kwargs["response_format"] = response_format

            response = await self.async_client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content
            logger.debug(f"Chat completion successful (tokens: {response.usage.total_tokens})")
            return content

        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise

    async def analyze_transcript(
        self,
        transcript: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analisa transcrição de chamada e gera feedback estruturado.

        Args:
            transcript: Transcrição da conversa
            context: Contexto adicional (informações sobre a empresa, produto, etc)

        Returns:
            Dicionário com análise estruturada
        """
        system_prompt = """Você é um especialista em análise de vendas. Analise a transcrição fornecida e
gere um feedback estruturado para ajudar o vendedor a melhorar.

Avalie as seguintes categorias (0-100 para cada):
1. Rapport: Construção de relacionamento e conexão
2. Discovery: Qualidade das perguntas de descoberta
3. Objection Handling: Tratamento de objeções
4. Closing: Habilidade de fechamento

Retorne JSON no formato:
{
    "overall_score": float,
    "category_scores": [
        {"category": "rapport", "score": float, "feedback": "...", "examples": [...]},
        ...
    ],
    "strengths": ["...", "..."],
    "areas_for_improvement": ["...", "..."],
    "key_moments": [{"timestamp": "...", "type": "positive/negative", "description": "..."}],
    "recommendations": ["...", "..."]
}"""

        user_message = f"Transcrição:\n\n{transcript}"
        if context:
            user_message = f"Contexto: {context}\n\n{user_message}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response_text = await self.chat_completion(
                messages=messages,
                temperature=0.3,  # Mais determinístico para análise
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            import json
            analysis = json.loads(response_text)
            logger.info(f"Transcript analysis completed. Score: {analysis.get('overall_score')}")
            return analysis

        except Exception as e:
            logger.error(f"Transcript analysis failed: {e}")
            raise

    async def generate_personas(
        self,
        company_context: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Gera personas de clientes baseadas no contexto da empresa.

        Args:
            company_context: Informações sobre a empresa, produtos, mercado
            count: Número de personas a gerar

        Returns:
            Lista de personas geradas
        """
        system_prompt = """Você é um especialista em criação de buyer personas.
Gere personas realistas de clientes baseadas no contexto fornecido.

Cada persona deve ter:
- name: Nome fictício
- role: Papel na decisão (decision_maker, influencer, gatekeeper, user)
- personality_traits: Dicionário com traços de personalidade
- pain_points: Lista de dores e problemas
- objections: Objeções típicas que essa persona levanta
- background: Background profissional

Retorne JSON com array de personas."""

        user_message = f"""Crie {count} personas diferentes para a seguinte empresa:

{company_context}

Garanta diversidade nos papéis e personalidades."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response_text = await self.chat_completion(
                messages=messages,
                temperature=0.8,  # Mais criativo para gerar diversidade
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response_text)
            personas = result.get("personas", [])
            logger.info(f"Generated {len(personas)} personas")
            return personas

        except Exception as e:
            logger.error(f"Persona generation failed: {e}")
            raise
