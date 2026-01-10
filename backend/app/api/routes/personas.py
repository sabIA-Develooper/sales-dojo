"""
Rotas para gerenciamento de personas de clientes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import List, Dict
from uuid import UUID
from app.core.database import get_supabase
from app.core.dependencies import get_current_company_id, verify_manager_role
from app.models.persona import (
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse,
    PersonaGenerationRequest,
    PersonaGenerationResponse
)
from app.services.openai_service import OpenAIService
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=PersonaGenerationResponse)
async def generate_personas(
    request: PersonaGenerationRequest,
    current_user: dict = Depends(verify_manager_role),
    db: Client = Depends(get_supabase)
):
    """
    Gera personas automaticamente usando GPT-4o baseado no knowledge base da empresa.

    Args:
        request: Parâmetros de geração (quantidade, contexto adicional)
        current_user: Usuário autenticado (deve ser gerente)
        db: Cliente Supabase

    Returns:
        Lista de personas geradas

    Raises:
        HTTPException: Se falhar na geração
    """
    try:
        company_id = str(request.company_id)

        # Busca informações da company knowledge base para contexto
        kb_result = db.table("knowledge_base").select("content").eq(
            "company_id", company_id
        ).limit(10).execute()

        if not kb_result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No knowledge base found. Please upload documents first."
            )

        # Monta contexto para geração
        kb_texts = [entry["content"] for entry in kb_result.data]
        company_context = "\n\n".join(kb_texts[:5])  # Usa primeiros 5 documentos

        if request.context:
            company_context = f"{request.context}\n\n{company_context}"

        # Gera personas usando OpenAI
        openai_service = OpenAIService()

        personas_data = await openai_service.generate_personas(
            company_context=company_context,
            count=request.count
        )

        # Armazena personas no banco
        created_personas = []

        for persona_data in personas_data:
            persona_record = {
                "company_id": company_id,
                "name": persona_data.get("name"),
                "role": persona_data.get("role", "decision_maker"),
                "personality_traits": persona_data.get("personality_traits", {}),
                "pain_points": persona_data.get("pain_points", []),
                "objections": persona_data.get("objections", []),
                "background": persona_data.get("background", "")
            }

            result = db.table("personas").insert(persona_record).execute()

            if result.data:
                created_personas.append(PersonaResponse(**result.data[0]))

        logger.info(f"✅ Generated {len(created_personas)} personas for company {company_id}")

        return PersonaGenerationResponse(
            personas=created_personas,
            total_generated=len(created_personas)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Persona generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate personas: {str(e)}"
        )


@router.get("/", response_model=List[PersonaResponse])
async def list_personas(
    company_id: str = Depends(get_current_company_id),
    db: Client = Depends(get_supabase)
):
    """
    Lista todas as personas da empresa.

    Args:
        company_id: ID da empresa
        db: Cliente Supabase

    Returns:
        Lista de personas
    """
    try:
        result = db.table("personas").select("*").eq("company_id", company_id).execute()

        return [PersonaResponse(**persona) for persona in result.data]

    except Exception as e:
        logger.error(f"❌ Failed to list personas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list personas: {str(e)}"
        )


@router.get("/random", response_model=PersonaResponse)
async def get_random_persona(
    company_id: str = Depends(get_current_company_id),
    db: Client = Depends(get_supabase)
):
    """
    Retorna uma persona aleatória da empresa.

    Útil para iniciar sessões de treinamento sem escolher persona específica.

    Args:
        company_id: ID da empresa
        db: Cliente Supabase

    Returns:
        Persona aleatória

    Raises:
        HTTPException: Se não houver personas
    """
    try:
        result = db.table("personas").select("*").eq("company_id", company_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No personas found. Please generate personas first."
            )

        random_persona = random.choice(result.data)

        return PersonaResponse(**random_persona)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get random persona: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get random persona: {str(e)}"
        )


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: UUID,
    company_id: str = Depends(get_current_company_id),
    db: Client = Depends(get_supabase)
):
    """
    Obtém detalhes de uma persona específica.

    Args:
        persona_id: ID da persona
        company_id: ID da empresa
        db: Cliente Supabase

    Returns:
        Dados da persona

    Raises:
        HTTPException: Se persona não encontrada ou não pertence à empresa
    """
    try:
        result = db.table("personas").select("*").eq(
            "id", str(persona_id)
        ).eq("company_id", company_id).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona not found"
            )

        return PersonaResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get persona: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get persona: {str(e)}"
        )


@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(
    persona: PersonaCreate,
    current_user: dict = Depends(verify_manager_role),
    db: Client = Depends(get_supabase)
):
    """
    Cria persona manualmente.

    Args:
        persona: Dados da persona
        current_user: Usuário autenticado (deve ser gerente)
        db: Cliente Supabase

    Returns:
        Persona criada
    """
    try:
        persona_dict = persona.model_dump()
        persona_dict["company_id"] = str(persona_dict["company_id"])

        result = db.table("personas").insert(persona_dict).execute()

        logger.info(f"✅ Persona created: {persona.name}")

        return PersonaResponse(**result.data[0])

    except Exception as e:
        logger.error(f"❌ Failed to create persona: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create persona: {str(e)}"
        )


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: UUID,
    persona_update: PersonaUpdate,
    company_id: str = Depends(get_current_company_id),
    current_user: dict = Depends(verify_manager_role),
    db: Client = Depends(get_supabase)
):
    """
    Atualiza persona existente.

    Args:
        persona_id: ID da persona
        persona_update: Dados para atualizar
        company_id: ID da empresa
        current_user: Usuário autenticado
        db: Cliente Supabase

    Returns:
        Persona atualizada
    """
    try:
        # Verifica se persona existe e pertence à empresa
        check_result = db.table("personas").select("id").eq(
            "id", str(persona_id)
        ).eq("company_id", company_id).execute()

        if not check_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona not found"
            )

        # Atualiza apenas campos fornecidos
        update_dict = persona_update.model_dump(exclude_unset=True)

        result = db.table("personas").update(update_dict).eq(
            "id", str(persona_id)
        ).execute()

        logger.info(f"✅ Persona updated: {persona_id}")

        return PersonaResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update persona: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update persona: {str(e)}"
        )


@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: UUID,
    company_id: str = Depends(get_current_company_id),
    current_user: dict = Depends(verify_manager_role),
    db: Client = Depends(get_supabase)
):
    """
    Remove uma persona.

    Args:
        persona_id: ID da persona
        company_id: ID da empresa
        current_user: Usuário autenticado
        db: Cliente Supabase

    Returns:
        Mensagem de confirmação
    """
    try:
        result = db.table("personas").delete().eq(
            "id", str(persona_id)
        ).eq("company_id", company_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona not found"
            )

        logger.info(f"✅ Persona deleted: {persona_id}")

        return {"message": "Persona deleted successfully", "persona_id": str(persona_id)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete persona: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete persona: {str(e)}"
        )
