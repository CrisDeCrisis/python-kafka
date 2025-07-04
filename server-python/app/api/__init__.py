"""
Inicializador de rutas de API
"""
from .chat import router as chat_router
from .documents import router as documents_router
from .health import router as health_router

__all__ = [
    "chat_router",
    "documents_router",
    "health_router"
]
