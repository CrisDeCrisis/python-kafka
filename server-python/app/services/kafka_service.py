"""
Servicio de Kafka para envío de mensajes
"""
import json
import logging
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from app.config import settings

logger = logging.getLogger(__name__)


class KafkaService:
    """Servicio para envío de mensajes a Kafka"""
    
    def __init__(self):
        self.producer: Optional[KafkaProducer] = None
        self.topic = "ia-responses"
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Inicializa el productor de Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None,
                acks='all',  # Esperar confirmación de todos los brokers
                retries=3,
                max_in_flight_requests_per_connection=1,
                enable_idempotence=True,
                compression_type='gzip'
            )
            logger.info("Productor de Kafka inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando productor de Kafka: {str(e)}")
            self.producer = None
    
    async def send_ia_response(
        self, 
        conversation_id: str,
        user_message: str,
        ai_response: str,
        context_used: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Envía una respuesta de IA al topic de Kafka
        
        Args:
            conversation_id: ID de la conversación
            user_message: Mensaje del usuario
            ai_response: Respuesta generada por la IA
            context_used: Si se usó contexto en la respuesta
            metadata: Metadatos adicionales
            
        Returns:
            True si el mensaje se envió correctamente, False en caso contrario
        """
        if not self.producer:
            logger.warning("Productor de Kafka no disponible")
            return False
        
        try:
            message = {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "context_used": context_used,
                "metadata": metadata or {},
                "timestamp": self._get_current_timestamp()
            }
            
            # Enviar mensaje
            future = self.producer.send(
                topic=self.topic,
                key=conversation_id,
                value=message
            )
            
            # Esperar confirmación (con timeout)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Mensaje enviado a Kafka - Topic: {record_metadata.topic}, "
                f"Partition: {record_metadata.partition}, "
                f"Offset: {record_metadata.offset}"
            )
            
            return True
            
        except KafkaError as e:
            logger.error(f"Error de Kafka enviando mensaje: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado enviando mensaje a Kafka: {str(e)}")
            return False
    
    async def send_streaming_response_chunk(
        self,
        conversation_id: str,
        chunk: str,
        chunk_index: int,
        is_final: bool = False
    ) -> bool:
        """
        Envía un chunk de respuesta streaming a Kafka
        
        Args:
            conversation_id: ID de la conversación
            chunk: Contenido del chunk
            chunk_index: Índice del chunk
            is_final: Si es el último chunk
            
        Returns:
            True si el mensaje se envió correctamente, False en caso contrario
        """
        if not self.producer:
            logger.warning("Productor de Kafka no disponible")
            return False
        
        try:
            message = {
                "conversation_id": conversation_id,
                "chunk": chunk,
                "chunk_index": chunk_index,
                "is_final": is_final,
                "timestamp": self._get_current_timestamp(),
                "message_type": "streaming_chunk"
            }
            
            # Enviar mensaje
            future = self.producer.send(
                topic=f"{self.topic}-streaming",
                key=f"{conversation_id}-{chunk_index}",
                value=message
            )
            
            # Para chunks de streaming, no esperamos confirmación para mejor performance
            if is_final:
                # Solo esperar confirmación en el último chunk
                future.get(timeout=5)
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando chunk streaming a Kafka: {str(e)}")
            return False
    
    def flush(self):
        """Fuerza el envío de todos los mensajes pendientes"""
        if self.producer:
            try:
                self.producer.flush(timeout=10)
                logger.debug("Kafka producer flushed successfully")
            except Exception as e:
                logger.error(f"Error flushing Kafka producer: {str(e)}")
    
    def close(self):
        """Cierra el productor de Kafka"""
        if self.producer:
            try:
                self.producer.close(timeout=10)
                logger.info("Productor de Kafka cerrado correctamente")
            except Exception as e:
                logger.error(f"Error cerrando productor de Kafka: {str(e)}")
    
    def is_healthy(self) -> bool:
        """Verifica si el servicio de Kafka está funcionando"""
        if not self.producer:
            return False
        
        try:
            # Intentar obtener metadatos del cluster
            metadata = self.producer.bootstrap_connected()
            return metadata
        except Exception:
            return False
    
    def _get_current_timestamp(self) -> str:
        """Obtiene el timestamp actual en formato ISO"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Instancia singleton del servicio
kafka_service = KafkaService()
