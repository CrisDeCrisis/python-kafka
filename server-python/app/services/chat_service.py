"""
Servicio principal de chat que orquesta todos los componentes
"""
import logging
import uuid
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.vector_db_service import VectorDatabaseService
from app.services.kafka_service import kafka_service
from app.models import ChatRequest, ChatResponse
from app.config import settings

logger = logging.getLogger(__name__)


class ChatService:
    """Servicio principal que orquesta el chat con IA"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()
        self.vector_db_service = VectorDatabaseService()
    
    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """
        Procesa una petición de chat completa
        
        Args:
            request: Petición de chat
            
        Returns:
            Respuesta de chat
        """
        try:
            # Generar ID de conversación si no se proporciona
            conversation_id = request.conversation_id or str(uuid.uuid4())
            
            # Obtener contexto si se solicita
            context = None
            context_used = False
            
            if request.use_context:
                context = await self._get_context_for_query(
                    request.message, 
                    conversation_id
                )
                context_used = bool(context)
            
            # Generar respuesta
            response = await self.llm_service.generate_response(
                question=request.message,
                context=context,
                temperature=request.temperature
            )
            
            # Almacenar la conversación en el contexto
            await self._store_conversation(
                conversation_id=conversation_id,
                user_message=request.message,
                assistant_response=response
            )
            
            # Enviar respuesta a Kafka si está habilitado
            if settings.kafka_enable:
                try:
                    await kafka_service.send_ia_response(
                        conversation_id=conversation_id,
                        user_message=request.message,
                        ai_response=response,
                        context_used=context_used,
                        metadata={
                            "temperature": request.temperature,
                            "model": "ollama",
                            "use_context": request.use_context
                        }
                    )
                except Exception as e:
                    logger.warning(f"Error enviando mensaje a Kafka: {str(e)}")
            
            return ChatResponse(
                response=response,
                conversation_id=conversation_id,
                context_used=context_used
            )
            
        except Exception as e:
            logger.error(f"Error procesando petición de chat: {str(e)}")
            raise
    
    async def process_streaming_chat_request(self, request: ChatRequest):
        """
        Procesa una petición de chat con respuesta streaming
        
        Args:
            request: Petición de chat
            
        Yields:
            Chunks de la respuesta
        """
        try:
            # Generar ID de conversación si no se proporciona
            conversation_id = request.conversation_id or str(uuid.uuid4())
            
            # Obtener contexto si se solicita
            context = None
            if request.use_context:
                context = await self._get_context_for_query(
                    request.message, 
                    conversation_id
                )
            
            # Generar respuesta streaming
            response_chunks = []
            chunk_index = 0
            async for chunk in self.llm_service.generate_streaming_response(
                question=request.message,
                context=context,
                temperature=request.temperature
            ):
                response_chunks.append(chunk)
                
                # Enviar chunk a Kafka si está habilitado
                if settings.kafka_enable:
                    try:
                        await kafka_service.send_streaming_response_chunk(
                            conversation_id=conversation_id,
                            chunk=chunk,
                            chunk_index=chunk_index,
                            is_final=False
                        )
                    except Exception as e:
                        logger.warning(f"Error enviando chunk streaming a Kafka: {str(e)}")
                
                chunk_index += 1
                yield {
                    "chunk": chunk,
                    "conversation_id": conversation_id,
                    "context_used": bool(context)
                }
            
            # Almacenar la conversación completa
            full_response = "".join(response_chunks)
            await self._store_conversation(
                conversation_id=conversation_id,
                user_message=request.message,
                assistant_response=full_response
            )
            
            # Enviar chunk final a Kafka
            if settings.kafka_enable:
                try:
                    await kafka_service.send_streaming_response_chunk(
                        conversation_id=conversation_id,
                        chunk="",
                        chunk_index=chunk_index,
                        is_final=True
                    )
                    # Enviar también la respuesta completa al topic principal
                    await kafka_service.send_ia_response(
                        conversation_id=conversation_id,
                        user_message=request.message,
                        ai_response=full_response,
                        context_used=bool(context),
                        metadata={
                            "temperature": request.temperature,
                            "model": "ollama",
                            "use_context": request.use_context,
                            "streaming": True,
                            "total_chunks": chunk_index
                        }
                    )
                except Exception as e:
                    logger.warning(f"Error enviando respuesta final a Kafka: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error procesando petición de chat streaming: {str(e)}")
            raise
    
    async def add_document_to_context(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Añade un documento al contexto de la conversación
        
        Args:
            content: Contenido del documento
            metadata: Metadatos del documento
            conversation_id: ID de la conversación
            
        Returns:
            Información sobre el documento añadido
        """
        try:
            # Crear documento
            document = self.embedding_service.create_document_from_text(
                content=content,
                metadata=metadata or {}
            )
            
            # Dividir en chunks si es necesario
            chunks = self.embedding_service.split_documents([document])
            
            # Generar embeddings
            texts = [chunk.page_content for chunk in chunks]
            embeddings = await self.embedding_service.generate_embeddings(texts)
            
            # Almacenar en base de datos vectorial
            document_ids = await self.vector_db_service.add_documents(
                documents=chunks,
                embeddings=embeddings,
                conversation_id=conversation_id
            )
            
            logger.info(f"Documento añadido con {len(chunks)} chunks")
            
            return {
                "document_id": document_ids[0] if document_ids else None,
                "chunks_created": len(chunks),
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            logger.error(f"Error añadiendo documento: {str(e)}")
            raise
    
    async def _get_context_for_query(
        self, 
        query: str, 
        conversation_id: str,
        max_results: int = 5
    ) -> Optional[str]:
        """
        Obtiene contexto relevante para una consulta
        
        Args:
            query: Consulta del usuario
            conversation_id: ID de la conversación
            max_results: Número máximo de resultados
            
        Returns:
            Contexto formateado o None si no hay contexto
        """
        try:
            # Generar embedding de la consulta
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            # Buscar documentos similares
            similar_docs = await self.vector_db_service.search_similar_documents(
                query_embedding=query_embedding,
                n_results=max_results,
                conversation_id=conversation_id
            )
            
            # Obtener contexto de la conversación
            conversation_context = await self.vector_db_service.get_conversation_context(
                conversation_id=conversation_id,
                limit=max_results
            )
            
            # Combinar contextos
            all_docs = similar_docs + conversation_context
            
            # Eliminar duplicados y formatear
            if all_docs:
                return self.llm_service.format_context(all_docs)
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto: {str(e)}")
            return None
    
    async def _store_conversation(
        self, 
        conversation_id: str, 
        user_message: str, 
        assistant_response: str
    ):
        """
        Almacena la conversación en el contexto
        
        Args:
            conversation_id: ID de la conversación
            user_message: Mensaje del usuario
            assistant_response: Respuesta del asistente
        """
        try:
            # Crear documentos para el intercambio
            conversation_text = f"Usuario: {user_message}\nAsistente: {assistant_response}"
            
            # Añadir al contexto
            await self.add_document_to_context(
                content=conversation_text,
                metadata={
                    "type": "conversation",
                    "user_message": user_message,
                    "assistant_response": assistant_response
                },
                conversation_id=conversation_id
            )
            
        except Exception as e:
            logger.error(f"Error almacenando conversación: {str(e)}")
            # No lanzar excepción aquí para no interrumpir el flujo principal
    
    async def get_conversation_history(
        self, 
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de una conversación
        
        Args:
            conversation_id: ID de la conversación
            limit: Límite de mensajes
            
        Returns:
            Lista de mensajes de la conversación
        """
        try:
            context = await self.vector_db_service.get_conversation_context(
                conversation_id=conversation_id,
                limit=limit
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {str(e)}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de todos los servicios
        
        Returns:
            Estado de los servicios
        """
        try:
            # Verificar modelo LLM
            llm_available = await self.llm_service.check_model_availability()
            
            # Verificar base de datos
            db_stats = self.vector_db_service.get_collection_stats()
            
            return {
                "llm_service": "available" if llm_available else "unavailable",
                "vector_database": "available" if "error" not in db_stats else "unavailable",
                "embedding_service": "available",  # Asumimos que está disponible si LLM está disponible
                "database_stats": db_stats
            }
            
        except Exception as e:
            logger.error(f"Error en health check: {str(e)}")
            return {
                "error": str(e),
                "status": "unhealthy"
            }
