"""
Endpoints de la API para chat con IA
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.models import (
    ChatRequest, 
    ChatResponse, 
    DocumentRequest, 
    DocumentResponse, 
    ErrorResponse
)
from app.services.chat_service import ChatService
from app.dependencies import get_chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Endpoint principal para chat con IA
    
    Args:
        request: Petición de chat
        chat_service: Servicio de chat inyectado
        
    Returns:
        Respuesta del modelo de IA
    """
    try:
        logger.info(f"Procesando petición de chat: {request.message[:50]}...")
        
        response = await chat_service.process_chat_request(request)
        
        logger.info(f"Chat procesado exitosamente para conversación: {response.conversation_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error en endpoint de chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando petición de chat: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Endpoint para chat con respuesta streaming
    
    Args:
        request: Petición de chat
        chat_service: Servicio de chat inyectado
        
    Returns:
        Respuesta streaming del modelo de IA
    """
    try:
        logger.info(f"Procesando petición de chat streaming: {request.message[:50]}...")
        
        async def generate_response():
            try:
                async for chunk_data in chat_service.process_streaming_chat_request(request):
                    yield f"data: {chunk_data['chunk']}\n\n"
            except Exception as e:
                logger.error(f"Error en streaming: {str(e)}")
                yield f"data: [ERROR] {str(e)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Error en endpoint de chat streaming: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando petición de chat streaming: {str(e)}"
        )


@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    limit: int = 20,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Obtiene el historial de una conversación
    
    Args:
        conversation_id: ID de la conversación
        limit: Límite de mensajes a devolver
        chat_service: Servicio de chat inyectado
        
    Returns:
        Historial de la conversación
    """
    try:
        logger.info(f"Obteniendo historial para conversación: {conversation_id}")
        
        history = await chat_service.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit
        )
        
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial de conversación: {str(e)}"
        )
