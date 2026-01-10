"""
Rotas de autenticação (login, registro, logout).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import Dict
from app.core.database import get_supabase
from app.core.dependencies import get_current_user
from app.models.user import UserCreate, UserLogin, AuthResponse, UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Client = Depends(get_supabase)
):
    """
    Registra novo usuário no sistema.

    Cria conta no Supabase Auth e adiciona metadados na tabela users.

    Args:
        user_data: Dados do usuário (email, senha, nome, empresa, role)

    Returns:
        Token JWT e dados do usuário criado

    Raises:
        HTTPException: Se falhar ao criar usuário
    """
    try:
        # Cria usuário no Supabase Auth
        auth_response = db.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )

        user_id = auth_response.user.id

        # Insere dados adicionais na tabela users
        user_record = {
            "id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "role": user_data.role,
            "company_id": str(user_data.company_id),
            "is_active": True
        }

        db.table("users").insert(user_record).execute()

        logger.info(f"✅ User registered successfully: {user_data.email}")

        return AuthResponse(
            access_token=auth_response.session.access_token,
            user=UserResponse(**user_record)
        )

    except Exception as e:
        logger.error(f"❌ Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    db: Client = Depends(get_supabase)
):
    """
    Autentica usuário e retorna JWT token.

    Args:
        credentials: Email e senha do usuário

    Returns:
        Token de acesso e dados do usuário

    Raises:
        HTTPException: Se credenciais inválidas
    """
    try:
        # Autentica com Supabase Auth
        auth_response = db.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        user_id = auth_response.session.user.id

        # Busca dados adicionais do usuário
        user_result = db.table("users").select("*").eq("id", user_id).single().execute()

        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"✅ User logged in: {credentials.email}")

        return AuthResponse(
            access_token=auth_response.session.access_token,
            user=UserResponse(**user_result.data)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/logout")
async def logout(
    current_user: Dict = Depends(get_current_user),
    db: Client = Depends(get_supabase)
):
    """
    Logout do usuário (invalida token no servidor).

    Returns:
        Mensagem de confirmação
    """
    try:
        db.auth.sign_out()
        logger.info(f"✅ User logged out: {current_user.get('email')}")

        return {"message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict = Depends(get_current_user)
):
    """
    Retorna informações do usuário autenticado.

    Requer token JWT válido no header Authorization.

    Returns:
        Dados completos do usuário
    """
    return UserResponse(**current_user)
