"""
Aplicación FastAPI principal con integración de LangChain y Ollama
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.logging_config import setup_logging
from app.api import chat_router, documents_router, health_router
from app.dependencies import get_chat_service

# Configurar logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    """
    logger.info("Iniciando aplicación...")
    
    # Inicializar servicios
    try:
        chat_service = get_chat_service()
        health_status = await chat_service.health_check()
        
        if "error" in health_status:
            logger.warning(f"Algunos servicios no están disponibles: {health_status}")
        else:
            logger.info("Todos los servicios inicializados correctamente")
            
    except Exception as e:
        logger.error(f"Error inicializando servicios: {str(e)}")
        # No interrumpir el inicio, permitir que la aplicación arranque
    
    logger.info("Aplicación iniciada exitosamente")
    yield
    
    logger.info("Cerrando aplicación...")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Servidor de IA con LangChain, Ollama y ChromaDB para procesamiento de lenguaje natural",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(health_router)


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Manejador global de excepciones
    """
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "details": str(exc) if settings.debug else "Error interno"
        }
    )


# Endpoint raíz
@app.get("/")
async def root():
    """
    Endpoint raíz con información de la API
    """
    return {
        "message": "Servidor de IA con LangChain y Ollama",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


# Endpoint de información
@app.get("/info")
async def get_info():
    """
    Información detallada de la aplicación
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "ollama_url": settings.ollama_base_url,
        "debug": settings.debug
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Iniciando servidor en {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
