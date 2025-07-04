"""
Dependencias para inyección de dependencias en FastAPI
"""
from functools import lru_cache
from app.services.chat_service import ChatService

# Cache para servicios singleton
_chat_service_instance = None


def get_chat_service() -> ChatService:
    """
    Obtiene la instancia singleton del servicio de chat
    
    Returns:
        Instancia del servicio de chat
    """
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
    return _chat_service_instance


@lru_cache()
def get_settings():
    """
    Obtiene la configuración de la aplicación
    
    Returns:
        Configuración de la aplicación
    """
    from app.config import settings
    return settings
