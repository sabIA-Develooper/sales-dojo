"""
Serviço para interações com OpenAI API.
Centraliza chamadas para embeddings, chat completion, etc.
Suporta modo mock quando API key não está configurada.
"""

from typing import List, Dict, Any, Optional
import logging
import random
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

# Import OpenAI apenas se a API key estiver configurada
try:
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. Mock mode will be used.")


class OpenAIService:
    """Serviço para gerenciar interações com OpenAI API com suporte a mock."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa cliente OpenAI.

        Args:
            api_key: Chave da API (usa settings se não fornecido)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.use_mock = not self.api_key or not settings.has_openai

        if self.use_mock:
            logger.warning("⚠️  OpenAI API key not configured. Using MOCK mode.")
            self.client = None
            self.async_client = None
        else:
            if OPENAI_AVAILABLE:
                self.client = OpenAI(api_key=self.api_key)
                self.async_client = AsyncOpenAI(api_key=self.api_key)
                logger.info("✅ OpenAI client initialized successfully")
            else:
                logger.error("OpenAI library not available")
                raise ImportError("openai library is required when API key is configured")

    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Gera embedding mock (vetor aleatório determinístico baseado no texto)."""
        # Usa hash do texto para gerar seed deterministico
        seed = hash(text) % (2**32)
        random.seed(seed)
        # Gera vetor de 1536 dimensões (compatível com text-embedding-3-small)
        return [random.uniform(-1, 1) for _ in range(settings.EMBEDDING_DIMENSION)]

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
        # Modo mock: retorna embedding fake
        if self.use_mock:
            logger.debug(f"[MOCK] Generating mock embedding for text (length: {len(text)} chars)")
            return self._generate_mock_embedding(text)

        # Modo real: usa OpenAI API
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
        # Modo mock: retorna embeddings fake
        if self.use_mock:
            logger.info(f"[MOCK] Generating {len(texts)} mock embeddings in batch")
            return [self._generate_mock_embedding(text) for text in texts]

        # Modo real: usa OpenAI API
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

    def _generate_mock_response(self, messages: List[Dict[str, str]], response_format: Optional[Dict[str, str]] = None) -> str:
        """Gera resposta mock baseada no contexto."""
        # Se espera JSON, retorna JSON mock
        if response_format and response_format.get("type") == "json_object":
            return json.dumps({
                "message": "Mock response (OpenAI API not configured)",
                "generated_by": "mock"
            })
        # Caso contrário, retorna texto simples
        return "This is a mock response. Configure OpenAI API key for real responses."

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
        # Modo mock: retorna resposta fake
        if self.use_mock:
            logger.debug("[MOCK] Generating mock chat completion")
            return self._generate_mock_response(messages, response_format)

        # Modo real: usa OpenAI API
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

    def _generate_mock_analysis(self, transcript: str) -> Dict[str, Any]:
        """Gera análise mock de transcrição."""
        # Análise baseada em regras simples para mock
        words = transcript.lower().split()
        word_count = len(words)

        # Score baseado no tamanho da transcrição (mock)
        base_score = min(70 + (word_count / 10), 95)
        score_variation = random.uniform(-10, 10)
        overall_score = max(0, min(100, base_score + score_variation))

        return {
            "overall_score": round(overall_score, 1),
            "category_scores": [
                {
                    "category": "rapport",
                    "score": round(random.uniform(60, 90), 1),
                    "feedback": "[MOCK] Boa construção de relacionamento inicial",
                    "examples": ["Cumprimentou adequadamente", "Demonstrou empatia"]
                },
                {
                    "category": "discovery",
                    "score": round(random.uniform(65, 85), 1),
                    "feedback": "[MOCK] Perguntas de descoberta poderiam ser mais profundas",
                    "examples": ["Fez perguntas abertas", "Explorou necessidades"]
                },
                {
                    "category": "objection_handling",
                    "score": round(random.uniform(55, 80), 1),
                    "feedback": "[MOCK] Tratamento de objeções adequado",
                    "examples": ["Reconheceu a objeção", "Forneceu evidências"]
                },
                {
                    "category": "closing",
                    "score": round(random.uniform(60, 85), 1),
                    "feedback": "[MOCK] Fechamento poderia ser mais assertivo",
                    "examples": ["Propôs próximos passos", "Tentou criar urgência"]
                }
            ],
            "strengths": [
                "[MOCK] Boa escuta ativa",
                "[MOCK] Demonstrou conhecimento do produto",
                "[MOCK] Manteve o cliente engajado"
            ],
            "areas_for_improvement": [
                "[MOCK] Fazer mais perguntas de descoberta",
                "[MOCK] Ser mais assertivo no fechamento",
                "[MOCK] Usar mais provas sociais e casos de sucesso"
            ],
            "key_moments": [
                {
                    "timestamp": "0:30",
                    "type": "positive",
                    "description": "[MOCK] Excelente rapport inicial"
                },
                {
                    "timestamp": "2:15",
                    "type": "negative",
                    "description": "[MOCK] Perdeu oportunidade de explorar pain point"
                }
            ],
            "recommendations": [
                "[MOCK] Pratique o framework SPIN Selling",
                "[MOCK] Estude técnicas de fechamento consultivo",
                "[MOCK] Prepare-se melhor para objeções comuns"
            ],
            "_mock_mode": True
        }

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
        # Modo mock: retorna análise fake
        if self.use_mock:
            logger.info("[MOCK] Generating mock transcript analysis")
            return self._generate_mock_analysis(transcript)

        # Modo real: usa OpenAI API
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
            analysis = json.loads(response_text)
            logger.info(f"Transcript analysis completed. Score: {analysis.get('overall_score')}")
            return analysis

        except Exception as e:
            logger.error(f"Transcript analysis failed: {e}")
            raise

    def _generate_mock_personas(self, count: int) -> List[Dict[str, Any]]:
        """Gera personas mock."""
        mock_personas = []
        roles = ["decision_maker", "influencer", "gatekeeper", "user"]
        names = [
            "Carlos Oliveira", "Ana Paula Santos", "Roberto Lima",
            "Juliana Costa", "Fernando Alves", "Mariana Silva",
            "Pedro Ferreira", "Camila Rocha"
        ]

        for i in range(min(count, len(names))):
            persona = {
                "name": names[i],
                "role": roles[i % len(roles)],
                "personality_traits": {
                    "analytical": random.choice([True, False]),
                    "risk_averse": random.choice([True, False]),
                    "detail_oriented": random.choice([True, False]),
                    "friendly": random.choice([True, False])
                },
                "pain_points": [
                    "[MOCK] Custos operacionais elevados",
                    "[MOCK] Falta de integração entre sistemas",
                    "[MOCK] Processos manuais demorados"
                ],
                "objections": [
                    "[MOCK] Preço muito alto",
                    "[MOCK] Implementação complexa",
                    "[MOCK] Já temos solução atual"
                ],
                "background": f"[MOCK] Profissional com {random.randint(5, 15)} anos de experiência em {random.choice(['TI', 'Vendas', 'Operações', 'Finanças'])}",
                "_mock_mode": True
            }
            mock_personas.append(persona)

        return mock_personas

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
        # Modo mock: retorna personas fake
        if self.use_mock:
            logger.info(f"[MOCK] Generating {count} mock personas")
            return self._generate_mock_personas(count)

        # Modo real: usa OpenAI API
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

            result = json.loads(response_text)
            personas = result.get("personas", [])
            logger.info(f"Generated {len(personas)} personas")
            return personas

        except Exception as e:
            logger.error(f"Persona generation failed: {e}")
            raise
