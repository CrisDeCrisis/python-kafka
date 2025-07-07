"""
Modelos de datos para las peticiones y respuestas de la API
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Modelo para un mensaje de chat"""
    role: str = Field(..., description="Rol del mensaje: 'user' o 'assistant'")
    content: str = Field(..., description="Contenido del mensaje")
    timestamp: Optional[str] = Field(None, description="Timestamp del mensaje")


class ChatRequest(BaseModel):
    """Modelo para la petición de chat"""
    message: str = Field(..., description="Mensaje del usuario")
    conversation_id: Optional[str] = Field(None, description="ID de la conversación")
    use_context: bool = Field(True, description="Si usar contexto previo")
    max_tokens: Optional[int] = Field(None, description="Máximo número de tokens")
    temperature: Optional[float] = Field(0.4, description="Temperatura del modelo")


class ChatResponse(BaseModel):
    """Modelo para la respuesta de chat"""
    response: str = Field(..., description="Respuesta del modelo")
    conversation_id: str = Field(..., description="ID de la conversación")
    usage: Optional[Dict[str, Any]] = Field(None, description="Información de uso")
    context_used: bool = Field(False, description="Si se utilizó contexto")


class DocumentRequest(BaseModel):
    """Modelo para añadir documentos"""
    content: str = Field(..., description="Contenido del documento")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos del documento")
    conversation_id: Optional[str] = Field(None, description="ID de la conversación")


class DocumentResponse(BaseModel):
    """Modelo para la respuesta de documento"""
    message: str = Field(..., description="Mensaje de confirmación")
    document_id: str = Field(..., description="ID del documento")
    chunks_created: int = Field(..., description="Número de chunks creados")


class HealthResponse(BaseModel):
    """Modelo para la respuesta de health check"""
    status: str = Field(..., description="Estado del servicio")
    models_available: List[str] = Field(..., description="Modelos disponibles")
    database_status: str = Field(..., description="Estado de la base de datos")


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    error: str = Field(..., description="Mensaje de error")
    details: Optional[str] = Field(None, description="Detalles del error")
    code: Optional[str] = Field(None, description="Código de error")
