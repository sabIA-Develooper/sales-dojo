"""
Configurações centralizadas da aplicação.
Todas as variáveis de ambiente são validadas no startup.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    # API Keys - Serviços de IA
    OPENAI_API_KEY: str
    VAPI_API_KEY: str
    DEEPGRAM_API_KEY: str
    ELEVENLABS_API_KEY: str

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sales AI Dojo"
    VERSION: str = "1.0.0"

    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Converte string de origens permitidas em lista."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # OpenAI Models
    OPENAI_CHAT_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # RAG Configuration
    RAG_SIMILARITY_THRESHOLD: float = 0.75
    RAG_MAX_RESULTS: int = 3

    # Vapi Configuration
    VAPI_PHONE_NUMBER_ID: str = ""  # Optional: configured per company
    VAPI_WEBHOOK_SECRET: str = ""  # For webhook validation

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

    # Rate Limiting (future implementation)
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignora variáveis não definidas
    )


# Singleton instance
settings = Settings()
