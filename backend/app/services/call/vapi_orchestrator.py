"""
Serviço para orquestração de chamadas de voz via Vapi.ai.
"""

import httpx
from typing import Dict, Any, Optional, List
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

VAPI_BASE_URL = "https://api.vapi.ai"


class VapiOrchestratorService:
    """Gerencia interações com Vapi.ai para chamadas de voz."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa serviço Vapi.

        Args:
            api_key: Chave da API (usa settings se não fornecido)
        """
        self.api_key = api_key or settings.VAPI_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_call(
        self,
        assistant_config: Dict[str, Any],
        customer_phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cria uma nova chamada de voz com Vapi.

        Args:
            assistant_config: Configuração do assistente (model, voice, instructions, etc)
            customer_phone: Número de telefone do cliente (se outbound)
            metadata: Metadados customizados (session_id, persona_id, etc)

        Returns:
            Dicionário com dados da chamada criada (call_id, call_url, etc)

        Raises:
            Exception: Se houver erro na criação da chamada
        """
        payload = {
            "assistant": assistant_config,
            "metadata": metadata or {}
        }

        if customer_phone:
            payload["customer"] = {"number": customer_phone}
            payload["type"] = "outboundPhoneCall"
        else:
            payload["type"] = "webCall"  # Chamada via browser

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{VAPI_BASE_URL}/call",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                response.raise_for_status()
                call_data = response.json()

                logger.info(f"Vapi call created: {call_data.get('id')}")
                return call_data

        except httpx.HTTPStatusError as e:
            logger.error(f"Vapi API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to create Vapi call: {e.response.text}")
        except Exception as e:
            logger.error(f"Failed to create Vapi call: {e}")
            raise

    async def create_training_call(
        self,
        persona_config: Dict[str, Any],
        session_id: str,
        company_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cria chamada configurada especificamente para treinamento de vendas.

        Args:
            persona_config: Configuração da persona (name, role, personality, etc)
            session_id: ID da sessão de treinamento
            company_context: Contexto da empresa para RAG

        Returns:
            Dados da chamada criada
        """
        # Monta instruções do sistema para a IA
        system_instructions = self._build_persona_instructions(
            persona_config,
            company_context
        )

        # Configuração do assistente
        assistant_config = {
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.8,
                "messages": [
                    {
                        "role": "system",
                        "content": system_instructions
                    }
                ]
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "EXAVITQu4vr4xnSDxMaL"  # Default voice, pode customizar
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "pt-BR"
            },
            "firstMessage": self._generate_first_message(persona_config),
            "endCallMessage": "Obrigado pela conversa. Até a próxima!",
            "recordingEnabled": True,
            "silenceTimeoutSeconds": 30,
            "maxDurationSeconds": 600  # 10 minutos máximo
        }

        # Metadados para rastreamento
        metadata = {
            "session_id": session_id,
            "persona_name": persona_config.get("name"),
            "persona_role": persona_config.get("role"),
            "type": "sales_training"
        }

        return await self.create_call(
            assistant_config=assistant_config,
            metadata=metadata
        )

    def _build_persona_instructions(
        self,
        persona_config: Dict[str, Any],
        company_context: Optional[str]
    ) -> str:
        """
        Constrói instruções do sistema para a IA representar a persona.

        Args:
            persona_config: Configuração da persona
            company_context: Contexto da empresa

        Returns:
            String com instruções completas
        """
        name = persona_config.get("name", "Cliente")
        role = persona_config.get("role", "decision_maker")
        personality = persona_config.get("personality_traits", {})
        pain_points = persona_config.get("pain_points", [])
        objections = persona_config.get("objections", [])
        background = persona_config.get("background", "")

        instructions = f"""Você é {name}, um(a) {role} em uma empresa.

BACKGROUND:
{background}

PERSONALIDADE:
{self._format_personality(personality)}

PRINCIPAIS DORES:
{self._format_list(pain_points)}

OBJEÇÕES TÍPICAS:
{self._format_list(objections)}

INSTRUÇÕES DE COMPORTAMENTO:
- Comporte-se como esta persona de forma realista e consistente
- Seja desafiador(a) mas justo(a) com o vendedor
- Levante objeções naturalmente durante a conversa
- Não facilite demais, mas também não seja impossível
- Se o vendedor fizer boas perguntas de descoberta, revele informações gradualmente
- Avalie a capacidade do vendedor de construir rapport e entender suas necessidades
- Fale em português brasileiro de forma natural
"""

        if company_context:
            instructions += f"\n\nCONTEXTO DA EMPRESA/PRODUTO:\n{company_context}"

        return instructions

    def _format_personality(self, traits: Dict[str, Any]) -> str:
        """Formata traços de personalidade."""
        if not traits:
            return "Personalidade equilibrada"

        formatted = []
        for trait, value in traits.items():
            formatted.append(f"- {trait}: {value}")
        return "\n".join(formatted)

    def _format_list(self, items: List[str]) -> str:
        """Formata lista de items."""
        if not items:
            return "Nenhum específico"

        return "\n".join([f"- {item}" for item in items])

    def _generate_first_message(self, persona_config: Dict[str, Any]) -> str:
        """
        Gera primeira mensagem da persona para iniciar conversa.

        Args:
            persona_config: Configuração da persona

        Returns:
            Mensagem inicial
        """
        name = persona_config.get("name", "Cliente")
        role = persona_config.get("role", "decision_maker")

        # Mensagens variadas baseadas no role
        greetings = {
            "decision_maker": (
                f"Olá, aqui é {name}. Vi que vocês entraram em contato. "
                f"Como posso ajudar?"
            ),
            "influencer": (
                f"Oi, sou {name}. Recebi o contato de vocês. Do que se trata?"
            ),
            "gatekeeper": f"Alô, {name} falando. Quem gostaria?",
            "user": f"Oi! Sou {name}. Tudo bem?"
        }

        return greetings.get(role, f"Olá, aqui é {name}. Podemos conversar?")

    async def get_call_details(self, call_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de uma chamada.

        Args:
            call_id: ID da chamada

        Returns:
            Dados da chamada
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{VAPI_BASE_URL}/call/{call_id}",
                    headers=self.headers,
                    timeout=30.0
                )

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get call details: {e}")
            raise

    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        Finaliza uma chamada em andamento.

        Args:
            call_id: ID da chamada

        Returns:
            Status da chamada
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{VAPI_BASE_URL}/call/{call_id}/end",
                    headers=self.headers,
                    timeout=30.0
                )

                response.raise_for_status()
                logger.info(f"Call {call_id} ended successfully")
                return response.json()

        except Exception as e:
            logger.error(f"Failed to end call: {e}")
            raise
