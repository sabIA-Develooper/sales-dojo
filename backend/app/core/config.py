"""
Configurações centralizadas da aplicação.
Variáveis de ambiente são validadas no startup.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    # PostgreSQL Database
    DATABASE_URL: str = "postgresql://sales_user:sales_password_dev@postgres:5432/sales_dojo"
    DATABASE_ECHO: bool = False  # Set True to see SQL queries in logs

    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sales AI Dojo"
    VERSION: str = "1.0.0"

    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost,http://localhost:80,http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Converte string de origens permitidas em lista."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # JWT Secret (for authentication)
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours

    # API Keys - Serviços de IA (OPTIONAL - app funciona sem eles)
    OPENAI_API_KEY: Optional[str] = None
    VAPI_API_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None

    # OpenAI Models (usado apenas se OPENAI_API_KEY estiver configurado)
    OPENAI_CHAT_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # RAG Configuration
    RAG_SIMILARITY_THRESHOLD: float = 0.75
    RAG_MAX_RESULTS: int = 3

    # Vapi Configuration (opcional)
    VAPI_PHONE_NUMBER_ID: str = ""
    VAPI_WEBHOOK_SECRET: str = ""

    # File Upload Settings
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_DOCUMENT_TYPES: List[str] = [".pdf", ".docx", ".txt", ".xlsx", ".csv"]
    UPLOAD_DIR: str = "/tmp/uploads"

    # Web Scraping Settings
    SCRAPER_USER_AGENT: str = "SalesAIDojo/1.0"
    SCRAPER_MAX_PAGES: int = 50
    SCRAPER_TIMEOUT_SECONDS: int = 30

    # Persona Generation
    PERSONAS_PER_GENERATION: int = 5

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Helper properties para check se APIs externas estão configuradas
    @property
    def has_openai(self) -> bool:
        """Verifica se OpenAI está configurado."""
        return self.OPENAI_API_KEY is not None and len(self.OPENAI_API_KEY) > 0

    @property
    def has_vapi(self) -> bool:
        """Verifica se Vapi está configurado."""
        return self.VAPI_API_KEY is not None and len(self.VAPI_API_KEY) > 0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Singleton instance
settings = Settings()
