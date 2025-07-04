"""
Configuración central de la aplicación
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # FastAPI
    app_name: str = "AI Server with LangChain"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "phi3:3.8b"
    embedding_model: str = "nomic-embed-text"
    
    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"
    collection_name: str = "conversation_context"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuración
settings = Settings()
