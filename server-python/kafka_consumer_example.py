#!/usr/bin/env python3
"""
Script de ejemplo para consumir mensajes del topic ia-responses
"""
import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def consume_ia_responses():
    """Consume mensajes del topic ia-responses"""
    try:
        # Crear consumidor
        consumer = KafkaConsumer(
            'ia-responses',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',  # Leer desde el principio
            enable_auto_commit=True,
            group_id='ia-response-consumer',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        logger.info("Consumidor iniciado. Esperando mensajes...")
        logger.info("Presiona Ctrl+C para detener")
        
        for message in consumer:
            try:
                data = message.value
                
                print("\n" + "="*80)
                print(f"NUEVO MENSAJE - Offset: {message.offset}")
                print(f"Conversación ID: {data.get('conversation_id')}")
                print(f"Timestamp: {data.get('timestamp')}")
                print(f"Contexto usado: {data.get('context_used')}")
                print("-" * 80)
                print(f"Usuario: {data.get('user_message')}")
                print("-" * 80)
                print(f"IA: {data.get('ai_response')}")
                
                # Mostrar metadatos si existen
                metadata = data.get('metadata')
                if metadata:
                    print("-" * 80)
                    print("Metadatos:")
                    for key, value in metadata.items():
                        print(f"  {key}: {value}")
                
                print("="*80)
                
            except Exception as e:
                logger.error(f"Error procesando mensaje: {str(e)}")
                
    except KeyboardInterrupt:
        logger.info("Deteniendo consumidor...")
    except KafkaError as e:
        logger.error(f"Error de Kafka: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
    finally:
        try:
            consumer.close()
            logger.info("Consumidor cerrado")
        except:
            pass


def consume_streaming_responses():
    """Consume mensajes del topic de streaming"""
    try:
        consumer = KafkaConsumer(
            'ia-responses-streaming',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='ia-streaming-consumer',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        logger.info("Consumidor de streaming iniciado. Esperando chunks...")
        logger.info("Presiona Ctrl+C para detener")
        
        current_conversation = None
        chunks = []
        
        for message in consumer:
            try:
                data = message.value
                conversation_id = data.get('conversation_id')
                
                if current_conversation != conversation_id:
                    # Nueva conversación
                    if chunks:
                        print(f"\n[Conversación {current_conversation} completada]")
                    current_conversation = conversation_id
                    chunks = []
                    print(f"\n[Iniciando conversación {conversation_id}]")
                
                if data.get('is_final'):
                    print(f"\n[Conversación {conversation_id} finalizada - Total chunks: {len(chunks)}]")
                    chunks = []
                else:
                    chunk = data.get('chunk', '')
                    chunks.append(chunk)
                    print(chunk, end='', flush=True)
                    
            except Exception as e:
                logger.error(f"Error procesando chunk: {str(e)}")
                
    except KeyboardInterrupt:
        logger.info("Deteniendo consumidor de streaming...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        try:
            consumer.close()
        except:
            pass


def main():
    """Función principal"""
    print("Selecciona el tipo de consumidor:")
    print("1. Respuestas completas (ia-responses)")
    print("2. Streaming chunks (ia-responses-streaming)")
    
    try:
        choice = input("Opción (1 o 2): ").strip()
        
        if choice == "1":
            consume_ia_responses()
        elif choice == "2":
            consume_streaming_responses()
        else:
            print("Opción inválida")
            
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario")


if __name__ == "__main__":
    main()
