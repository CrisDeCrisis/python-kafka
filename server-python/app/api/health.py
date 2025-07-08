"""
Endpoints de la API para health check y estado del sistema
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.models import HealthResponse
from app.services.chat_service import ChatService
from app.services.kafka_service import kafka_service
from app.dependencies import get_chat_service
from app.config import settings

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
        
        # Verificar estado de Kafka si está habilitado
        kafka_status = "disabled"
        if settings.kafka_enable:
            kafka_status = "available" if kafka_service.is_healthy() else "unavailable"
        
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
            database_status=health_status.get("vector_database", "unknown"),
            kafka_status=kafka_status
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


@router.get("/kafka")
async def get_kafka_status():
    """
    Obtiene el estado del servicio de Kafka
    
    Returns:
        Estado y configuración de Kafka
    """
    try:
        if not settings.kafka_enable:
            return {
                "status": "disabled",
                "message": "Kafka está deshabilitado en la configuración"
            }
        
        is_healthy = kafka_service.is_healthy()
        
        return {
            "status": "available" if is_healthy else "unavailable",
            "bootstrap_servers": settings.kafka_bootstrap_servers,
            "topics": {
                "ia_responses": "ia-responses",
                "ia_responses_streaming": "ia-responses-streaming"
            },
            "producer_healthy": is_healthy
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de Kafka: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado de Kafka: {str(e)}"
        )
