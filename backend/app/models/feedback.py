"""
Modelos Pydantic para feedback de sessões.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID


class FeedbackBase(BaseModel):
    """Schema base para Feedback."""
    overall_score: float = Field(..., ge=0, le=100, description="Score geral de 0-100")
    strengths: List[str] = Field(
        default_factory=list,
        description="Pontos fortes identificados na conversa"
    )
    areas_for_improvement: List[str] = Field(
        default_factory=list,
        description="Áreas que precisam melhorar"
    )
    detailed_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Análise detalhada por categorias "
            "(rapport, discovery, objection_handling, closing)"
        )
    )


class FeedbackCreate(FeedbackBase):
    """Schema para criação de feedback."""
    session_id: UUID


class FeedbackInDB(FeedbackBase):
    """Schema para feedback no banco de dados."""
    id: UUID
    session_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackResponse(FeedbackInDB):
    """Schema para resposta de API com dados do feedback."""
    pass


class CategoryScore(BaseModel):
    """Score de uma categoria específica."""
    category: str
    score: float = Field(..., ge=0, le=100)
    feedback: str
    examples: Optional[List[str]] = None


class DetailedFeedback(BaseModel):
    """Feedback detalhado estruturado."""
    overall_score: float = Field(..., ge=0, le=100)
    summary: str
    category_scores: List[CategoryScore]
    strengths: List[str]
    areas_for_improvement: List[str]
    key_moments: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Momentos chave da conversa (positivos e negativos)"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recomendações específicas para próximas sessões"
    )


class RegenerateFeedbackRequest(BaseModel):
    """Request para regenerar feedback."""
    session_id: UUID
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Áreas específicas para focar na análise"
    )
