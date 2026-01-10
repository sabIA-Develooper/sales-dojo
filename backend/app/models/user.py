"""
Modelos Pydantic para usuários.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID


class UserBase(BaseModel):
    """Schema base para User."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)
    role: Literal["salesperson", "manager", "admin"] = "salesperson"


class UserCreate(UserBase):
    """Schema para criação de usuário."""
    password: str = Field(..., min_length=8, max_length=100)
    company_id: UUID


class UserUpdate(BaseModel):
    """Schema para atualização de usuário."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[Literal["salesperson", "manager", "admin"]] = None


class UserLogin(BaseModel):
    """Schema para login."""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """Schema para usuário no banco de dados."""
    id: UUID
    company_id: UUID
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    """Schema para resposta de API com dados do usuário."""
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    company_id: UUID
    is_active: bool
    created_at: datetime


class AuthResponse(BaseModel):
    """Schema para resposta de autenticação."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
