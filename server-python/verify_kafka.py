#!/usr/bin/env python3
"""
Verificación rápida del sistema Kafka
"""
import asyncio
import sys
import os

# Agregar el directorio de la aplicación al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.kafka_service import kafka_service
from app.config import settings


async def test_kafka_integration():
    """Prueba básica de la integración con Kafka"""
    print("🔧 Verificando integración con Kafka...")
    
    # Verificar configuración
    print(f"✓ Kafka habilitado: {settings.kafka_enable}")
    print(f"✓ Bootstrap servers: {settings.kafka_bootstrap_servers}")
    
    # Verificar conectividad
    is_healthy = kafka_service.is_healthy()
    print(f"✓ Kafka saludable: {is_healthy}")
    
    if not is_healthy:
        print("❌ Kafka no está disponible")
        return False
    
    # Enviar mensaje de prueba
    print("\n📤 Enviando mensaje de prueba...")
    success = await kafka_service.send_ia_response(
        conversation_id="test-001",
        user_message="Mensaje de prueba",
        ai_response="Esta es una respuesta de prueba desde el sistema",
        context_used=False,
        metadata={"test": True, "version": "1.0"}
    )
    
    if success:
        print("✅ Mensaje enviado exitosamente a Kafka!")
    else:
        print("❌ Error enviando mensaje a Kafka")
        return False
    
    # Flush para asegurar envío
    kafka_service.flush()
    print("✓ Mensajes flushed correctamente")
    
    return True


def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN DEL SISTEMA KAFKA")
    print("=" * 40)
    
    try:
        success = asyncio.run(test_kafka_integration())
        
        if success:
            print("\n🎉 ¡Sistema Kafka funcionando correctamente!")
            print("\n📋 Próximos pasos:")
            print("   1. Iniciar el servidor: python run.py")
            print("   2. Probar la API: http://localhost:8000/docs")
            print("   3. Consumir mensajes: python kafka_consumer_example.py")
            print("   4. Ver Kafka UI: http://localhost:8080")
        else:
            print("\n❌ Hay problemas con el sistema Kafka")
            return False
            
    except Exception as e:
        print(f"\n💥 Error durante la verificación: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
