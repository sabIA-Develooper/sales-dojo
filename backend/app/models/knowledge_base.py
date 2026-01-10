"""
Modelos Pydantic para knowledge base e documentos.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal
from uuid import UUID


class KnowledgeBaseEntryBase(BaseModel):
    """Schema base para entrada de knowledge base."""
    content: str = Field(..., min_length=1)
    source_type: Literal["document", "website", "manual"] = "document"
    source_name: str = Field(..., min_length=1, max_length=500)


class KnowledgeBaseEntryCreate(KnowledgeBaseEntryBase):
    """Schema para criação de entrada na KB."""
    company_id: UUID
    embedding: Optional[List[float]] = Field(
        None,
        description="Embedding vetorial (gerado automaticamente se não fornecido)"
    )


class KnowledgeBaseEntryInDB(KnowledgeBaseEntryBase):
    """Schema para entrada no banco de dados."""
    id: UUID
    company_id: UUID
    embedding: Optional[List[float]] = None  # Não retornamos o embedding por padrão
    created_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeBaseEntryResponse(KnowledgeBaseEntryInDB):
    """Schema para resposta de API."""
    pass


class DocumentUploadResponse(BaseModel):
    """Resposta de upload de documento."""
    file_id: str
    filename: str
    file_size_bytes: int
    status: str
    message: str


class WebScrapingRequest(BaseModel):
    """Request para scraping de website."""
    company_id: UUID
    url: str = Field(..., description="URL do site para fazer scraping")
    max_pages: int = Field(default=10, ge=1, le=50, description="Máximo de páginas para scrape")
    include_subdomains: bool = Field(default=False)


class WebScrapingResponse(BaseModel):
    """Resposta de scraping."""
    job_id: str
    status: str
    pages_scraped: int
    entries_created: int
    message: str


class OnboardingStatusResponse(BaseModel):
    """Status do processo de onboarding."""
    company_id: UUID
    total_documents: int
    total_kb_entries: int
    total_embeddings: int
    last_updated: datetime
    is_ready: bool = Field(
        ...,
        description="True se a empresa já tem knowledge base suficiente para treinar"
    )


class SearchKnowledgeRequest(BaseModel):
    """Request para buscar na knowledge base."""
    query: str = Field(..., min_length=1)
    company_id: UUID
    max_results: int = Field(default=3, ge=1, le=10)
    similarity_threshold: float = Field(default=0.75, ge=0, le=1)


class SearchKnowledgeResult(BaseModel):
    """Resultado de busca na KB."""
    id: UUID
    content: str
    source_type: str
    source_name: str
    similarity_score: float


class SearchKnowledgeResponse(BaseModel):
    """Resposta de busca na KB."""
    results: List[SearchKnowledgeResult]
    total_results: int
