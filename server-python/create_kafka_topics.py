#!/usr/bin/env python3
"""
Script para crear los topics de Kafka necesarios para la aplicación
"""
import logging
import sys
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_topics():
    """Crea los topics necesarios para la aplicación"""
    try:
        # Crear cliente admin
        admin_client = KafkaAdminClient(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id='topic_creator'
        )
        
        # Definir topics
        topics = [
            NewTopic(
                name="ia-responses",
                num_partitions=3,
                replication_factor=1,
                topic_configs={
                    'cleanup.policy': 'delete',
                    'retention.ms': '604800000',  # 7 días
                    'compression.type': 'gzip'
                }
            ),
            NewTopic(
                name="ia-responses-streaming",
                num_partitions=3,
                replication_factor=1,
                topic_configs={
                    'cleanup.policy': 'delete',
                    'retention.ms': '86400000',  # 1 día
                    'compression.type': 'gzip'
                }
            )
        ]
        
        # Crear topics
        try:
            fs = admin_client.create_topics(new_topics=topics, validate_only=False)
            
            # Esperar resultados
            for topic, f in fs.items():
                try:
                    f.result()  # El resultado será None en caso de éxito
                    logger.info(f"Topic '{topic}' creado exitosamente")
                except TopicAlreadyExistsError:
                    logger.info(f"Topic '{topic}' ya existe")
                except Exception as e:
                    logger.error(f"Error creando topic '{topic}': {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error en la operación de creación de topics: {str(e)}")
            # Intentar crear topics individualmente si falla el batch
            try:
                for topic in topics:
                    try:
                        result = admin_client.create_topics([topic], validate_only=False)
                        for topic_name, future in result.items():
                            try:
                                future.result()
                                logger.info(f"Topic '{topic_name}' creado exitosamente")
                            except TopicAlreadyExistsError:
                                logger.info(f"Topic '{topic_name}' ya existe")
                            except Exception as e:
                                logger.error(f"Error creando topic '{topic_name}': {str(e)}")
                    except Exception as e:
                        logger.error(f"Error creando topic '{topic.name}': {str(e)}")
            except Exception as e:
                logger.error(f"Error en creación individual: {str(e)}")
                return False
        
        # Listar topics existentes
        metadata = admin_client.list_topics(timeout=10)
        logger.info(f"Topics disponibles: {list(metadata.topics.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error conectando con Kafka: {str(e)}")
        return False
    finally:
        try:
            admin_client.close()
        except:
            pass


def main():
    """Función principal"""
    logger.info("Iniciando creación de topics de Kafka...")
    
    if create_topics():
        logger.info("Topics de Kafka configurados correctamente")
        sys.exit(0)
    else:
        logger.error("Error configurando topics de Kafka")
        sys.exit(1)


if __name__ == "__main__":
    main()
