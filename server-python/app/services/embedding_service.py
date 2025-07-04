"""
Servicio de embeddings usando LangChain y Ollama
"""
import logging
from typing import List, Optional
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Servicio para generar embeddings usando Ollama"""
    
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model=settings.embedding_model,
            base_url=settings.ollama_base_url
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de textos
        
        Args:
            texts: Lista de textos para generar embeddings
            
        Returns:
            Lista de embeddings (vectores)
        """
        try:
            logger.info(f"Generando embeddings para {len(texts)} textos")
            embeddings = await self.embeddings.aembed_documents(texts)
            logger.info(f"Embeddings generados exitosamente")
            return embeddings
        except Exception as e:
            logger.error(f"Error generando embeddings: {str(e)}")
            raise
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Genera embedding para una consulta
        
        Args:
            query: Texto de la consulta
            
        Returns:
            Vector embedding de la consulta
        """
        try:
            logger.info(f"Generando embedding para consulta: {query[:50]}...")
            embedding = await self.embeddings.aembed_query(query)
            logger.info("Embedding de consulta generado exitosamente")
            return embedding
        except Exception as e:
            logger.error(f"Error generando embedding de consulta: {str(e)}")
            raise
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Divide documentos en chunks más pequeños
        
        Args:
            documents: Lista de documentos a dividir
            
        Returns:
            Lista de documentos divididos en chunks
        """
        try:
            logger.info(f"Dividiendo {len(documents)} documentos en chunks")
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Creados {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error dividiendo documentos: {str(e)}")
            raise
    
    def create_document_from_text(
        self, 
        content: str, 
        metadata: Optional[dict] = None
    ) -> Document:
        """
        Crea un Document de LangChain desde texto
        
        Args:
            content: Contenido del documento
            metadata: Metadatos opcionales
            
        Returns:
            Documento de LangChain
        """
        return Document(
            page_content=content,
            metadata=metadata or {}
        )
