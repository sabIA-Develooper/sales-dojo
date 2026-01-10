"""
Modelos Pydantic para personas de clientes.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from uuid import UUID


class PersonaBase(BaseModel):
    """Schema base para Persona."""
    name: str = Field(..., min_length=1, max_length=200)
    role: Literal["decision_maker", "influencer", "gatekeeper", "user"] = "decision_maker"
    personality_traits: Dict[str, Any] = Field(
        default_factory=dict,
        description="Traços de personalidade (ex: assertive, analytical, friendly)"
    )
    pain_points: List[str] = Field(
        default_factory=list,
        description="Principais dores e problemas do cliente"
    )
    objections: List[str] = Field(
        default_factory=list,
        description="Objeções típicas que essa persona levanta"
    )
    background: Optional[str] = Field(
        None,
        description="Background profissional e contexto"
    )


class PersonaCreate(PersonaBase):
    """Schema para criação de persona."""
    company_id: UUID


class PersonaUpdate(BaseModel):
    """Schema para atualização de persona."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[Literal["decision_maker", "influencer", "gatekeeper", "user"]] = None
    personality_traits: Optional[Dict[str, Any]] = None
    pain_points: Optional[List[str]] = None
    objections: Optional[List[str]] = None
    background: Optional[str] = None


class PersonaInDB(PersonaBase):
    """Schema para persona no banco de dados."""
    id: UUID
    company_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class PersonaResponse(PersonaInDB):
    """Schema para resposta de API com dados da persona."""
    pass


class PersonaGenerationRequest(BaseModel):
    """Request para gerar novas personas."""
    company_id: UUID
    count: int = Field(default=5, ge=1, le=10, description="Número de personas a gerar")
    context: Optional[str] = Field(
        None,
        description="Contexto adicional para guiar a geração"
    )


class PersonaGenerationResponse(BaseModel):
    """Resposta da geração de personas."""
    personas: List[PersonaResponse]
    total_generated: int
