"""
Servicio de base de datos vectorial usando ChromaDB
"""
import logging
import uuid
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_core.documents import Document
from app.config import settings

logger = logging.getLogger(__name__)


class VectorDatabaseService:
    """Servicio para gestionar la base de datos vectorial con ChromaDB"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Obtiene o crea la colección de ChromaDB"""
        try:
            collection = self.client.get_or_create_collection(
                name=settings.collection_name,
                metadata={"description": "Contexto de conversaciones"}
            )
            logger.info(f"Colección '{settings.collection_name}' lista")
            return collection
        except Exception as e:
            logger.error(f"Error creando colección: {str(e)}")
            raise
    
    async def add_documents(
        self, 
        documents: List[Document], 
        embeddings: List[List[float]],
        conversation_id: Optional[str] = None
    ) -> List[str]:
        """
        Añade documentos a la base de datos vectorial
        
        Args:
            documents: Lista de documentos a añadir
            embeddings: Lista de embeddings correspondientes
            conversation_id: ID de la conversación (opcional)
            
        Returns:
            Lista de IDs de los documentos añadidos
        """
        try:
            document_ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                doc_id = str(uuid.uuid4())
                document_ids.append(doc_id)
                texts.append(doc.page_content)
                
                # Combinar metadatos del documento con conversation_id
                metadata = doc.metadata.copy() if doc.metadata else {}
                if conversation_id:
                    metadata["conversation_id"] = conversation_id
                metadata["timestamp"] = str(uuid.uuid1().time)
                metadatas.append(metadata)
            
            # Añadir a ChromaDB
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=document_ids
            )
            
            logger.info(f"Añadidos {len(document_ids)} documentos a la base de datos")
            return document_ids
            
        except Exception as e:
            logger.error(f"Error añadiendo documentos: {str(e)}")
            raise
    
    async def search_similar_documents(
        self, 
        query_embedding: List[float], 
        n_results: int = 5,
        conversation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos similares usando embedding de consulta
        
        Args:
            query_embedding: Embedding de la consulta
            n_results: Número de resultados a devolver
            conversation_id: ID de la conversación para filtrar
            
        Returns:
            Lista de documentos similares con metadatos
        """
        try:
            # Preparar filtros si se especifica conversation_id
            where_clause = None
            if conversation_id:
                where_clause = {"conversation_id": conversation_id}
            
            # Buscar en ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Formatear resultados
            documents = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            logger.info(f"Encontrados {len(documents)} documentos similares")
            return documents
            
        except Exception as e:
            logger.error(f"Error buscando documentos similares: {str(e)}")
            raise
    
    async def get_conversation_context(
        self, 
        conversation_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el contexto de una conversación específica
        
        Args:
            conversation_id: ID de la conversación
            limit: Límite de documentos a devolver
            
        Returns:
            Lista de documentos del contexto de la conversación
        """
        try:
            results = self.collection.get(
                where={"conversation_id": conversation_id},
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            documents = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {}
                    })
            
            logger.info(f"Obtenidos {len(documents)} documentos de contexto")
            return documents
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la colección
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": settings.collection_name
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {"error": str(e)}
    
    def reset_collection(self):
        """Resetea la colección (elimina todos los documentos)"""
        try:
            self.client.delete_collection(settings.collection_name)
            self.collection = self._get_or_create_collection()
            logger.info("Colección reseteada exitosamente")
        except Exception as e:
            logger.error(f"Error reseteando colección: {str(e)}")
            raise
