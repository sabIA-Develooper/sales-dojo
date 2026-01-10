"""
Rotas para processo de onboarding da empresa.
Upload de documentos, scraping de sites, geração de knowledge base.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from supabase import Client
from typing import List
from app.core.database import get_supabase
from app.core.dependencies import get_current_company_id, verify_manager_role
from app.core.config import settings
from app.models.knowledge_base import (
    DocumentUploadResponse,
    WebScrapingRequest,
    WebScrapingResponse,
    OnboardingStatusResponse
)
from app.services.onboarding.document_processor import DocumentProcessor
from app.services.onboarding.embedding_service import EmbeddingService
from app.services.openai_service import OpenAIService
from app.utils.validators import validate_file_extension, sanitize_filename
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload-documents", response_model=List[DocumentUploadResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    company_id: str = Depends(get_current_company_id),
    current_user: dict = Depends(verify_manager_role),
    db: Client = Depends(get_supabase)
):
    """
    Upload de documentos para criar knowledge base.

    Aceita múltiplos arquivos (PDF, DOCX, TXT, CSV, XLSX).
    Processa documentos, gera embeddings e armazena no banco.

    Args:
        files: Lista de arquivos para upload
        company_id: ID da empresa
        current_user: Usuário autenticado (deve ser gerente)
        db: Cliente Supabase

    Returns:
        Lista de respostas com status de cada arquivo

    Raises:
        HTTPException: Se tipo de arquivo não suportado ou erro no processamento
    """
    responses = []

    # Inicializa serviços
    doc_processor = DocumentProcessor()
    openai_service = OpenAIService()
    embedding_service = EmbeddingService(db, openai_service)

    for file in files:
        try:
            # Valida extensão do arquivo
            if not validate_file_extension(file.filename, settings.ALLOWED_DOCUMENT_TYPES):
                responses.append(DocumentUploadResponse(
                    file_id="",
                    filename=file.filename,
                    file_size_bytes=0,
                    status="error",
                    message=f"File type not supported. Allowed: {settings.ALLOWED_DOCUMENT_TYPES}"
                ))
                continue

            # Valida tamanho do arquivo
            content = await file.read()
            file_size_mb = len(content) / (1024 * 1024)

            if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
                responses.append(DocumentUploadResponse(
                    file_id="",
                    filename=file.filename,
                    file_size_bytes=len(content),
                    status="error",
                    message=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
                ))
                continue

            # Sanitiza nome do arquivo
            safe_filename = sanitize_filename(file.filename)

            logger.info(f"Processing file: {safe_filename} ({file_size_mb:.2f}MB)")

            # Processa documento e extrai chunks de texto
            chunks = await doc_processor.process_file(
                file_content=content,
                filename=safe_filename,
                chunk_size=1000
            )

            # Gera embeddings e armazena no banco
            stored_count = await embedding_service.process_and_store_chunks(
                chunks=chunks,
                company_id=company_id,
                source_type="document"
            )

            logger.info(f"✅ File processed successfully: {safe_filename}, {stored_count} chunks stored")

            responses.append(DocumentUploadResponse(
                file_id=safe_filename,  # Poderia gerar UUID aqui
                filename=file.filename,
                file_size_bytes=len(content),
                status="success",
                message=f"File processed successfully. {stored_count} chunks stored."
            ))

        except Exception as e:
            logger.error(f"❌ Failed to process file {file.filename}: {e}")
            responses.append(DocumentUploadResponse(
                file_id="",
                filename=file.filename,
                file_size_bytes=0,
                status="error",
                message=f"Processing failed: {str(e)}"
            ))

    return responses


@router.post("/scrape-website", response_model=WebScrapingResponse)
async def scrape_website(
    request: WebScrapingRequest,
    current_user: dict = Depends(verify_manager_role),
    db: Client = Depends(get_supabase)
):
    """
    Faz scraping de um website para criar knowledge base.

    Args:
        request: URL e configurações de scraping
        current_user: Usuário autenticado (deve ser gerente)
        db: Cliente Supabase

    Returns:
        Status do job de scraping

    Note:
        Esta é uma implementação básica. Em produção, deveria ser um job assíncrono.
    """
    try:
        # TODO: Implementar scraping real
        # Por enquanto retorna placeholder
        logger.info(f"Scraping request for: {request.url}")

        # Em produção, deveria:
        # 1. Validar URL
        # 2. Criar job assíncrono de scraping
        # 3. Processar páginas encontradas
        # 4. Gerar embeddings e armazenar

        return WebScrapingResponse(
            job_id="scrape-" + str(request.company_id),
            status="queued",
            pages_scraped=0,
            entries_created=0,
            message="Scraping job queued. This feature is under development."
        )

    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )


@router.get("/status/{company_id}", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    company_id: str,
    current_user: dict = Depends(verify_manager_role),
    db: Client = Depends(get_supabase)
):
    """
    Obtém status do processo de onboarding da empresa.

    Args:
        company_id: ID da empresa
        current_user: Usuário autenticado
        db: Cliente Supabase

    Returns:
        Status completo do onboarding
    """
    try:
        # Busca estatísticas da knowledge base
        openai_service = OpenAIService()
        embedding_service = EmbeddingService(db, openai_service)

        stats = await embedding_service.get_company_kb_stats(company_id)

        # Busca última atualização
        last_entry_result = db.table("knowledge_base").select("created_at").eq(
            "company_id", company_id
        ).order("created_at", desc=True).limit(1).execute()

        last_updated = datetime.now()
        if last_entry_result.data:
            last_updated = datetime.fromisoformat(last_entry_result.data[0]["created_at"])

        return OnboardingStatusResponse(
            company_id=company_id,
            total_documents=stats["unique_sources"],
            total_kb_entries=stats["total_entries"],
            total_embeddings=stats["total_entries"],  # Mesmo valor (cada entry tem embedding)
            last_updated=last_updated,
            is_ready=stats["is_ready"]
        )

    except Exception as e:
        logger.error(f"❌ Failed to get onboarding status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.delete("/documents/{source_name}")
async def delete_document(
    source_name: str,
    company_id: str = Depends(get_current_company_id),
    current_user: dict = Depends(verify_manager_role),
    db: Client = Depends(get_supabase)
):
    """
    Remove todas as entradas de um documento específico.

    Args:
        source_name: Nome do documento a remover
        company_id: ID da empresa
        current_user: Usuário autenticado
        db: Cliente Supabase

    Returns:
        Mensagem de confirmação
    """
    try:
        openai_service = OpenAIService()
        embedding_service = EmbeddingService(db, openai_service)

        deleted_count = await embedding_service.delete_entries_by_source(
            company_id=company_id,
            source_name=source_name
        )

        logger.info(f"✅ Deleted {deleted_count} entries from document: {source_name}")

        return {
            "message": f"Document removed successfully",
            "source_name": source_name,
            "entries_deleted": deleted_count
        }

    except Exception as e:
        logger.error(f"❌ Failed to delete document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
