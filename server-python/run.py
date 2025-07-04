"""
Punto de entrada principal para ejecutar la aplicación
"""
if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    from app.logging_config import setup_logging
    
    # Configurar logging
    logger = setup_logging()
    
    logger.info(f"Iniciando servidor en {settings.host}:{settings.port}")
    logger.info(f"Modelo LLM: {settings.llm_model}")
    logger.info(f"Modelo Embedding: {settings.embedding_model}")
    logger.info(f"Base URL Ollama: {settings.ollama_base_url}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
