"""
Dependências comuns para injeção em rotas FastAPI.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.core.database import get_supabase
from app.core.config import settings
import jwt
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Security scheme para JWT
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_supabase)
) -> Dict:
    """
    Valida JWT token e retorna dados do usuário autenticado.

    Args:
        credentials: Token JWT do header Authorization
        db: Cliente Supabase

    Returns:
        Dict com dados do usuário (id, email, company_id, role, etc)

    Raises:
        HTTPException: Se token inválido ou usuário não encontrado
    """
    token = credentials.credentials

    try:
        # Decodifica e valida JWT
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase usa aud customizada
        )

        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )

        # Busca dados adicionais do usuário no banco
        # Assume que existe uma tabela 'users' com metadados
        user_result = db.table("users").select("*").eq("id", user_id).single().execute()

        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user_result.data

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


async def get_current_company_id(
    current_user: Dict = Depends(get_current_user)
) -> str:
    """
    Extrai company_id do usuário autenticado.

    Args:
        current_user: Dados do usuário da dependência get_current_user

    Returns:
        UUID da empresa do usuário

    Raises:
        HTTPException: Se usuário não tem empresa associada
    """
    company_id = current_user.get("company_id")

    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any company"
        )

    return company_id


async def verify_manager_role(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Verifica se usuário tem role de gerente.

    Args:
        current_user: Dados do usuário

    Returns:
        Dados do usuário se for gerente

    Raises:
        HTTPException: Se usuário não é gerente
    """
    role = current_user.get("role", "salesperson")

    if role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Manager role required."
        )

    return current_user


def get_openai_client():
    """
    Retorna cliente OpenAI configurado.
    Importação lazy para evitar dependência circular.
    """
    from openai import OpenAI
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_vapi_headers() -> Dict[str, str]:
    """
    Retorna headers para requisições à API do Vapi.ai.
    """
    return {
        "Authorization": f"Bearer {settings.VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
