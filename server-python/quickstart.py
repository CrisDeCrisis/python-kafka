#!/usr/bin/env python3
"""
Script de inicio rápido para la aplicación con Kafka
"""
import subprocess
import sys
import time
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_command(command, description, shell=True):
    """Ejecuta un comando y maneja errores"""
    logger.info(f"Ejecutando: {description}")
    try:
        result = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        logger.info(f"✓ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Error en {description}: {e.stderr}")
        return False


def check_service(url, name, timeout=30):
    """Verifica si un servicio está disponible"""
    logger.info(f"Verificando {name}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ {name} está disponible")
                return True
        except:
            pass
        time.sleep(2)
    
    logger.warning(f"✗ {name} no está disponible después de {timeout}s")
    return False


def main():
    """Función principal de inicio rápido"""
    logger.info("🚀 Iniciando configuración completa del AI Server con Kafka")
    
    # Paso 1: Iniciar servicios Docker
    logger.info("\n📦 Paso 1: Iniciando servicios Docker...")
    if not run_command("docker-compose up -d", "Iniciar servicios Docker"):
        logger.error("No se pudo iniciar Docker. Asegúrate de que Docker esté instalado y ejecutándose.")
        return False
    
    # Paso 2: Esperar a que Kafka esté disponible
    logger.info("\n⏳ Paso 2: Esperando a que Kafka esté disponible...")
    time.sleep(10)  # Dar tiempo inicial a Kafka para iniciar
    
    # Verificar Kafka UI (indirectamente verifica que Kafka esté funcionando)
    if not check_service("http://localhost:8080", "Kafka UI"):
        logger.warning("Kafka UI no está disponible, pero continuando...")
    
    # Paso 3: Crear topics de Kafka
    logger.info("\n🔧 Paso 3: Creando topics de Kafka...")
    if not run_command("python create_kafka_topics.py", "Crear topics de Kafka"):
        logger.warning("No se pudieron crear los topics. Puede que ya existan.")
    
    # Paso 4: Verificar Ollama
    logger.info("\n🤖 Paso 4: Verificando Ollama...")
    if not run_command("ollama list", "Verificar Ollama"):
        logger.error("Ollama no está disponible. Instálalo desde https://ollama.ai")
        logger.info("Comandos necesarios:")
        logger.info("  ollama pull phi3:3.8b")
        logger.info("  ollama pull nomic-embed-text")
        return False
    
    # Paso 5: Iniciar el servidor Python
    logger.info("\n🌐 Paso 5: Iniciando servidor Python...")
    logger.info("El servidor se iniciará en http://localhost:8000")
    logger.info("Documentación API: http://localhost:8000/docs")
    logger.info("Kafka UI: http://localhost:8080")
    logger.info("\nPresiona Ctrl+C para detener el servidor")
    
    try:
        # Ejecutar el servidor
        subprocess.run([sys.executable, "run.py"], check=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 Deteniendo servidor...")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error ejecutando el servidor: {e}")
        return False
    
    return True


def cleanup():
    """Función de limpieza"""
    logger.info("\n🧹 Limpiando recursos...")
    run_command("docker-compose down", "Deteniendo servicios Docker")


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n👋 Proceso interrumpido por el usuario")
    finally:
        cleanup()
