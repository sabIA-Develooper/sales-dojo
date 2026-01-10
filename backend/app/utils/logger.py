"""
Configuração de logging para a aplicação.
"""

import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configura o sistema de logging da aplicação.
    """
    # Define nível de log baseado no ambiente
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Formato do log
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )

    # Configuração básica
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Reduz verbosidade de bibliotecas externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("supabase").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {logging.getLevelName(log_level)}")
