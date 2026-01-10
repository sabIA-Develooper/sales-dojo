"""
Rotas para sessões de treinamento de vendas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import Dict, List
from uuid import UUID
from app.core.database import get_supabase
from app.core.dependencies import get_current_user, get_current_company_id
from app.models.training_session import (
    StartSessionRequest,
    StartSessionResponse,
    EndSessionRequest,
    TrainingSessionResponse,
    SessionStatsResponse
)
from app.services.call.vapi_orchestrator import VapiOrchestratorService
from app.services.call.rag_service import RAGService
from app.services.openai_service import OpenAIService
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start", response_model=StartSessionResponse)
async def start_training_session(
    request: StartSessionRequest,
    current_user: Dict = Depends(get_current_user),
    company_id: str = Depends(get_current_company_id),
    db: Client = Depends(get_supabase)
):
    """
    Inicia uma nova sessão de treinamento com Vapi.ai.

    Se persona_id não fornecido, seleciona uma persona aleatória.

    Args:
        request: Dados da requisição (persona_id opcional)
        current_user: Usuário autenticado
        company_id: ID da empresa do usuário
        db: Cliente Supabase

    Returns:
        Dados da sessão criada incluindo call_id do Vapi

    Raises:
        HTTPException: Se falhar ao criar sessão ou chamada
    """
    try:
        user_id = current_user["id"]
        persona_id = request.persona_id

        # Se persona não fornecida, seleciona aleatória
        if not persona_id:
            personas_result = db.table("personas").select("id").eq(
                "company_id", company_id
            ).execute()

            if not personas_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No personas found for this company. Please generate personas first."
                )

            # Seleciona aleatória
            random_persona = random.choice(personas_result.data)
            persona_id = random_persona["id"]

        # Busca dados completos da persona
        persona_result = db.table("personas").select("*").eq("id", str(persona_id)).single().execute()

        if not persona_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona not found"
            )

        persona = persona_result.data

        # Cria registro de sessão no banco
        session_data = {
            "user_id": user_id,
            "company_id": company_id,
            "persona_id": str(persona_id),
            "status": "ongoing"
        }

        session_result = db.table("training_sessions").insert(session_data).execute()
        session_id = session_result.data[0]["id"]

        # Busca contexto da empresa para RAG (opcional)
        # Poderíamos buscar alguns documentos principais aqui
        company_context = f"Empresa: {company_id}"  # Simplificado

        # Cria chamada no Vapi.ai
        vapi_service = VapiOrchestratorService()

        call_data = await vapi_service.create_training_call(
            persona_config=persona,
            session_id=session_id,
            company_context=company_context
        )

        vapi_call_id = call_data.get("id")

        # Atualiza sessão com vapi_call_id
        db.table("training_sessions").update({
            "vapi_call_id": vapi_call_id
        }).eq("id", session_id).execute()

        logger.info(f"✅ Training session started: {session_id}, Vapi call: {vapi_call_id}")

        return StartSessionResponse(
            session_id=session_id,
            persona_id=persona_id,
            vapi_call_id=vapi_call_id,
            call_url=call_data.get("webCallUrl")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to start training session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@router.post("/{session_id}/end")
async def end_training_session(
    session_id: UUID,
    request: EndSessionRequest,
    current_user: Dict = Depends(get_current_user),
    db: Client = Depends(get_supabase)
):
    """
    Finaliza sessão de treinamento.

    Args:
        session_id: ID da sessão
        request: Duração e transcrição
        current_user: Usuário autenticado
        db: Cliente Supabase

    Returns:
        Dados da sessão atualizada

    Raises:
        HTTPException: Se sessão não encontrada ou não pertence ao usuário
    """
    try:
        user_id = current_user["id"]

        # Verifica se sessão existe e pertence ao usuário
        session_result = db.table("training_sessions").select("*").eq(
            "id", str(session_id)
        ).eq("user_id", user_id).single().execute()

        if not session_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or access denied"
            )

        # Atualiza sessão
        update_data = {
            "status": "completed",
            "duration_seconds": request.duration_seconds,
            "transcript": request.transcript
        }

        db.table("training_sessions").update(update_data).eq("id", str(session_id)).execute()

        logger.info(f"✅ Session ended: {session_id}")

        return {"message": "Session ended successfully", "session_id": str(session_id)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to end session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )


@router.get("/{session_id}", response_model=TrainingSessionResponse)
async def get_session(
    session_id: UUID,
    current_user: Dict = Depends(get_current_user),
    db: Client = Depends(get_supabase)
):
    """
    Obtém detalhes de uma sessão.

    Args:
        session_id: ID da sessão
        current_user: Usuário autenticado
        db: Cliente Supabase

    Returns:
        Dados completos da sessão

    Raises:
        HTTPException: Se sessão não encontrada
    """
    try:
        user_id = current_user["id"]

        result = db.table("training_sessions").select("*").eq(
            "id", str(session_id)
        ).eq("user_id", user_id).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        return TrainingSessionResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session: {str(e)}"
        )


@router.get("/", response_model=List[TrainingSessionResponse])
async def list_sessions(
    current_user: Dict = Depends(get_current_user),
    db: Client = Depends(get_supabase),
    limit: int = 20,
    offset: int = 0
):
    """
    Lista sessões de treinamento do usuário.

    Args:
        current_user: Usuário autenticado
        db: Cliente Supabase
        limit: Máximo de resultados
        offset: Pular primeiros N resultados

    Returns:
        Lista de sessões
    """
    try:
        user_id = current_user["id"]

        result = db.table("training_sessions").select("*").eq(
            "user_id", user_id
        ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()

        return [TrainingSessionResponse(**session) for session in result.data]

    except Exception as e:
        logger.error(f"❌ Failed to list sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/stats/me", response_model=SessionStatsResponse)
async def get_my_stats(
    current_user: Dict = Depends(get_current_user),
    db: Client = Depends(get_supabase)
):
    """
    Obtém estatísticas das sessões do usuário autenticado.

    Returns:
        Estatísticas agregadas
    """
    try:
        user_id = current_user["id"]

        # Busca todas as sessões do usuário
        sessions_result = db.table("training_sessions").select("*").eq("user_id", user_id).execute()

        sessions = sessions_result.data

        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.get("status") == "completed"])
        abandoned_sessions = len([s for s in sessions if s.get("status") == "abandoned"])

        total_duration = sum(s.get("duration_seconds", 0) for s in sessions)
        avg_duration = total_duration / total_sessions if total_sessions > 0 else 0

        # Busca scores médios dos feedbacks
        feedback_result = db.table("feedback").select("overall_score").in_(
            "session_id", [s["id"] for s in sessions]
        ).execute()

        scores = [f["overall_score"] for f in feedback_result.data if f.get("overall_score")]
        avg_score = sum(scores) / len(scores) if scores else None

        return SessionStatsResponse(
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            abandoned_sessions=abandoned_sessions,
            total_duration_seconds=total_duration,
            average_duration_seconds=avg_duration,
            average_score=avg_score
        )

    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )
