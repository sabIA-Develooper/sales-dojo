"""
Validações e utilitários comuns.
"""

from typing import List
from pathlib import Path
import re


def validate_email(email: str) -> bool:
    """
    Valida formato de email.

    Args:
        email: String de email para validar

    Returns:
        True se válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Valida formato de URL.

    Args:
        url: String de URL para validar

    Returns:
        True se válido, False caso contrário
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Valida se extensão do arquivo é permitida.

    Args:
        filename: Nome do arquivo
        allowed_extensions: Lista de extensões permitidas (ex: ['.pdf', '.docx'])

    Returns:
        True se extensão permitida, False caso contrário
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]


def sanitize_filename(filename: str) -> str:
    """
    Remove caracteres perigosos de nome de arquivo.

    Args:
        filename: Nome original do arquivo

    Returns:
        Nome sanitizado
    """
    # Remove caracteres especiais, mantém apenas alfanuméricos, underscores, hífens e pontos
    sanitized = re.sub(r'[^\w\-.]', '_', filename)
    return sanitized


def validate_uuid(uuid_string: str) -> bool:
    """
    Valida se string é um UUID válido.

    Args:
        uuid_string: String para validar

    Returns:
        True se UUID válido, False caso contrário
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, uuid_string.lower()))
