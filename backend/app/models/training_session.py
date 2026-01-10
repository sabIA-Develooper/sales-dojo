"""
Modelos Pydantic para sessões de treinamento.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, Literal
from uuid import UUID


class TrainingSessionBase(BaseModel):
    """Schema base para TrainingSession."""
    persona_id: UUID


class TrainingSessionCreate(TrainingSessionBase):
    """Schema para criação de sessão."""
    user_id: UUID
    company_id: UUID


class TrainingSessionUpdate(BaseModel):
    """Schema para atualização de sessão."""
    status: Literal["ongoing", "completed", "abandoned"]
    duration_seconds: Optional[int] = None
    transcript: Optional[Dict[str, Any]] = None


class TrainingSessionInDB(TrainingSessionBase):
    """Schema para sessão no banco de dados."""
    id: UUID
    user_id: UUID
    company_id: UUID
    persona_id: UUID
    vapi_call_id: Optional[str] = None
    transcript: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[int] = None
    status: Literal["ongoing", "completed", "abandoned"] = "ongoing"
    created_at: datetime

    model_config = {"from_attributes": True}


class TrainingSessionResponse(TrainingSessionInDB):
    """Schema para resposta de API com dados da sessão."""
    pass


class StartSessionRequest(BaseModel):
    """Request para iniciar sessão de treinamento."""
    persona_id: Optional[UUID] = Field(
        None,
        description="ID da persona. Se não fornecido, uma aleatória será selecionada"
    )


class StartSessionResponse(BaseModel):
    """Resposta ao iniciar sessão."""
    session_id: UUID
    persona_id: UUID
    vapi_call_id: str
    call_url: Optional[str] = Field(
        None,
        description="URL para conectar na chamada (se aplicável)"
    )


class EndSessionRequest(BaseModel):
    """Request para finalizar sessão."""
    duration_seconds: int = Field(..., ge=0)
    transcript: Optional[Dict[str, Any]] = None


class SessionStatsResponse(BaseModel):
    """Estatísticas de sessões de um usuário."""
    total_sessions: int
    completed_sessions: int
    abandoned_sessions: int
    total_duration_seconds: int
    average_duration_seconds: float
    average_score: Optional[float] = None
