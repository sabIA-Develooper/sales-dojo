"""
Modelos Pydantic para empresas.
"""

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional
from uuid import UUID


class CompanyBase(BaseModel):
    """Schema base para Company."""
    name: str = Field(..., min_length=1, max_length=200)
    website: Optional[HttpUrl] = None


class CompanyCreate(CompanyBase):
    """Schema para criação de empresa."""
    pass


class CompanyUpdate(BaseModel):
    """Schema para atualização de empresa."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    website: Optional[HttpUrl] = None


class CompanyInDB(CompanyBase):
    """Schema para empresa no banco de dados."""
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanyResponse(CompanyInDB):
    """Schema para resposta de API com dados da empresa."""
    pass
