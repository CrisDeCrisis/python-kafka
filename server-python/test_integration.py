#!/usr/bin/env python3
"""
Script de prueba para verificar la integración completa con Kafka
"""
import json
import time
import requests
import threading
from kafka import KafkaConsumer


def test_kafka_consumer():
    """Consume mensajes de Kafka en un hilo separado"""
    try:
        consumer = KafkaConsumer(
            'ia-responses',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='test-consumer',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        print("🎯 Consumidor de Kafka iniciado, esperando mensajes...")
        
        for message in consumer:
            data = message.value
            print(f"\n📨 MENSAJE RECIBIDO DE KAFKA:")
            print(f"   Conversación: {data.get('conversation_id')}")
            print(f"   Usuario: {data.get('user_message')}")
            print(f"   IA: {data.get('ai_response')[:100]}...")
            print(f"   Timestamp: {data.get('timestamp')}")
            break  # Solo recibir un mensaje para la prueba
            
    except Exception as e:
        print(f"❌ Error en consumidor de Kafka: {e}")
    finally:
        try:
            consumer.close()
        except:
            pass


def test_api_request():
    """Envía una petición de prueba a la API"""
    time.sleep(2)  # Dar tiempo al consumidor para iniciarse
    
    try:
        print("🚀 Enviando petición de prueba a la API...")
        
        response = requests.post(
            "http://localhost:8000/chat",
            json={
                "message": "¿Qué es Apache Kafka y para qué sirve?",
                "use_context": False,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta de la API recibida:")
            print(f"   Conversación: {data.get('conversation_id')}")
            print(f"   Respuesta: {data.get('response')[:100]}...")
        else:
            print(f"❌ Error en API: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error enviando petición: {e}")


def test_health_endpoints():
    """Prueba los endpoints de health check"""
    print("🏥 Verificando endpoints de salud...")
    
    endpoints = [
        ("http://localhost:8000/health", "Health general"),
        ("http://localhost:8000/health/kafka", "Health de Kafka"),
        ("http://localhost:8000/info", "Información del sistema")
    ]
    
    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                if "kafka" in url:
                    data = response.json()
                    print(f"   Estado Kafka: {data.get('status')}")
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")


def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DE INTEGRACIÓN KAFKA")
    print("=" * 50)
    
    # Verificar que los servicios estén disponibles
    test_health_endpoints()
    
    print("\n🔄 Iniciando prueba de flujo completo...")
    
    # Iniciar consumidor en hilo separado
    consumer_thread = threading.Thread(target=test_kafka_consumer, daemon=True)
    consumer_thread.start()
    
    # Enviar petición a la API
    test_api_request()
    
    # Esperar a que termine el consumidor
    consumer_thread.join(timeout=5)
    
    print("\n✨ Pruebas completadas!")
    print("\n📋 Para pruebas manuales:")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Kafka UI: http://localhost:8080")
    print("   • Consumidor: python kafka_consumer_example.py")


if __name__ == "__main__":
    main()
