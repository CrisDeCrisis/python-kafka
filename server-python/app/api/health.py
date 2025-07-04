"""
Endpoints de la API para health check y estado del sistema
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.models import HealthResponse
from app.services.chat_service import ChatService
from app.dependencies import get_chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Verifica el estado de todos los servicios
    
    Args:
        chat_service: Servicio de chat inyectado
        
    Returns:
        Estado de los servicios
    """
    try:
        logger.info("Ejecutando health check")
        
        health_status = await chat_service.health_check()
        
        # Determinar estado general
        if "error" in health_status:
            raise HTTPException(
                status_code=503,
                detail="Servicios no disponibles"
            )
        
        # Verificar disponibilidad de modelos
        models_available = []
        if health_status.get("llm_service") == "available":
            models_available.append("phi3:3.8b")
        if health_status.get("embedding_service") == "available":
            models_available.append("nomic-embed-text")
        
        return HealthResponse(
            status="healthy" if models_available else "unhealthy",
            models_available=models_available,
            database_status=health_status.get("vector_database", "unknown")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando health check: {str(e)}"
        )


@router.get("/models")
async def get_available_models(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Obtiene información sobre los modelos disponibles
    
    Args:
        chat_service: Servicio de chat inyectado
        
    Returns:
        Información de los modelos
    """
    try:
        llm_info = chat_service.llm_service.get_model_info()
        
        return {
            "llm_model": llm_info,
            "embedding_model": {
                "model": "nomic-embed-text",
                "base_url": chat_service.embedding_service.embeddings.base_url
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo información de modelos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo información de modelos: {str(e)}"
        )
