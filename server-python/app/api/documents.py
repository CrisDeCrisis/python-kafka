"""
Endpoints de la API para gestión de documentos
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.models import DocumentRequest, DocumentResponse
from app.services.chat_service import ChatService
from app.dependencies import get_chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse)
async def add_document(
    request: DocumentRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Añade un documento al contexto de la conversación
    
    Args:
        request: Petición de documento
        chat_service: Servicio de chat inyectado
        
    Returns:
        Información sobre el documento añadido
    """
    try:
        logger.info(f"Añadiendo documento de {len(request.content)} caracteres")
        
        result = await chat_service.add_document_to_context(
            content=request.content,
            metadata=request.metadata,
            conversation_id=request.conversation_id
        )
        
        return DocumentResponse(
            message="Documento añadido exitosamente",
            document_id=result["document_id"],
            chunks_created=result["chunks_created"]
        )
        
    except Exception as e:
        logger.error(f"Error añadiendo documento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error añadiendo documento: {str(e)}"
        )


@router.get("/stats")
async def get_document_stats(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Obtiene estadísticas de los documentos almacenados
    
    Args:
        chat_service: Servicio de chat inyectado
        
    Returns:
        Estadísticas de la base de datos de documentos
    """
    try:
        stats = chat_service.vector_db_service.get_collection_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )
