"""
Utilidades para gestionar el servidor de IA
"""
import asyncio
import sys
import argparse
from pathlib import Path
import subprocess
import time
import requests
from typing import Optional


def check_ollama_running() -> bool:
    """
    Verifica si Ollama está ejecutándose
    
    Returns:
        True si Ollama está ejecutándose, False en caso contrario
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def check_models_available() -> dict:
    """
    Verifica si los modelos necesarios están disponibles
    
    Returns:
        Diccionario con el estado de los modelos
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_names = [model["name"] for model in models.get("models", [])]
            
            return {
                "phi3:3.8b": any("phi3" in name for name in model_names),
                "nomic-embed-text": any("nomic" in name for name in model_names),
                "available_models": model_names
            }
    except requests.RequestException:
        pass
    
    return {
        "phi3:3.8b": False,
        "nomic-embed-text": False,
        "available_models": []
    }


def setup_environment():
    """
    Configura el entorno de desarrollo
    """
    print("🔧 Configurando entorno...")
    
    # Verificar si existe .env
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creando archivo .env desde .env.example...")
        example_file = Path(".env.example")
        if example_file.exists():
            env_file.write_text(example_file.read_text())
            print("✅ Archivo .env creado")
        else:
            print("❌ No se encontró .env.example")
    
    # Crear directorio de logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("✅ Directorio de logs creado")
    
    # Crear directorio de ChromaDB
    chroma_dir = Path("chroma_db")
    chroma_dir.mkdir(exist_ok=True)
    print("✅ Directorio de ChromaDB creado")


def check_dependencies():
    """
    Verifica las dependencias del proyecto
    """
    print("🔍 Verificando dependencias...")
    
    # Verificar dependencias de Python
    if not check_python_dependencies():
        return False
    
    # Verificar Ollama
    if check_ollama_running():
        print("✅ Ollama está ejecutándose")
    else:
        print("❌ Ollama no está ejecutándose")
        print("   Inicia Ollama con: ollama serve")
        return False
    
    # Verificar modelos
    models = check_models_available()
    if models["phi3:3.8b"]:
        print("✅ Modelo phi3:3.8b disponible")
    else:
        print("❌ Modelo phi3:3.8b no disponible")
        print("   Descarga con: ollama pull phi3:3.8b")
        return False
    
    if models["nomic-embed-text"]:
        print("✅ Modelo nomic-embed-text disponible")
    else:
        print("❌ Modelo nomic-embed-text no disponible")
        print("   Descarga con: ollama pull nomic-embed-text")
        return False
    
    return True


def install_dependencies():
    """
    Instala las dependencias de Python
    """
    print("📦 Instalando dependencias...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencias instaladas")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias")
        return False


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Inicia el servidor
    
    Args:
        host: Host del servidor
        port: Puerto del servidor
        reload: Si usar recarga automática
    """
    print(f"🚀 Iniciando servidor en {host}:{port}")
    
    if not check_dependencies():
        print("❌ Faltan dependencias. Ejecuta primero: python utils.py check")
        return
    
    try:
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", host,
            "--port", str(port)
        ]
        
        if reload:
            cmd.append("--reload")
        
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("❌ Error iniciando servidor")
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")


def test_server():
    """
    Prueba el servidor
    """
    print("🧪 Probando servidor...")
    
    try:
        # Verificar que el servidor esté ejecutándose
        response = requests.get("http://localhost:8000/health/", timeout=10)
        if response.status_code == 200:
            print("✅ Servidor respondiendo correctamente")
            
            # Probar chat
            chat_response = requests.post(
                "http://localhost:8000/chat/",
                json={
                    "message": "Hola, ¿cómo estás?",
                    "use_context": False
                },
                timeout=30
            )
            
            if chat_response.status_code == 200:
                print("✅ Chat funcionando correctamente")
                result = chat_response.json()
                print(f"   Respuesta: {result['response'][:100]}...")
            else:
                print("❌ Error en chat")
                print(f"   Status: {chat_response.status_code}")
        else:
            print("❌ Servidor no está respondiendo correctamente")
            print(f"   Status: {response.status_code}")
    
    except requests.RequestException as e:
        print("❌ No se pudo conectar al servidor")
        print(f"   Error: {e}")
        print("   Asegúrate de que el servidor esté ejecutándose")


def download_models():
    """
    Descarga los modelos necesarios
    """
    print("📥 Descargando modelos...")
    
    models = ["phi3:3.8b", "nomic-embed-text"]
    
    for model in models:
        print(f"Descargando {model}...")
        try:
            subprocess.run(["ollama", "pull", model], check=True)
            print(f"✅ {model} descargado")
        except subprocess.CalledProcessError:
            print(f"❌ Error descargando {model}")
        except FileNotFoundError:
            print("❌ Ollama no encontrado. Instala Ollama primero.")
            return


def check_python_dependencies() -> bool:
    """
    Verifica si las dependencias de Python están instaladas correctamente
    
    Returns:
        True si todas las dependencias están instaladas, False en caso contrario
    """
    try:
        # Verificar dependencias críticas
        critical_packages = [
            'fastapi',
            'uvicorn',
            'pydantic',
            'pydantic_settings',
            'langchain',
            'langchain_ollama',
            'chromadb'
        ]
        
        missing_packages = []
        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Paquetes faltantes: {', '.join(missing_packages)}")
            print("   Ejecuta: pip install -r requirements.txt")
            return False
        
        print("✅ Todas las dependencias de Python están instaladas")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando dependencias: {e}")
        return False


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Utilidades para el servidor de IA")
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando setup
    subparsers.add_parser("setup", help="Configura el entorno")
    
    # Comando check
    subparsers.add_parser("check", help="Verifica dependencias")
    
    # Comando install
    subparsers.add_parser("install", help="Instala dependencias de Python")
    
    # Comando download
    subparsers.add_parser("download", help="Descarga modelos de Ollama")
    
    # Comando start
    start_parser = subparsers.add_parser("start", help="Inicia el servidor")
    start_parser.add_argument("--host", default="0.0.0.0", help="Host del servidor")
    start_parser.add_argument("--port", type=int, default=8000, help="Puerto del servidor")
    start_parser.add_argument("--reload", action="store_true", help="Recarga automática")
    
    # Comando test
    subparsers.add_parser("test", help="Prueba el servidor")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_environment()
    elif args.command == "check":
        if check_dependencies():
            print("✅ Todas las dependencias están correctas")
        else:
            print("❌ Faltan dependencias")
    elif args.command == "install":
        install_dependencies()
    elif args.command == "download":
        download_models()
    elif args.command == "start":
        start_server(args.host, args.port, args.reload)
    elif args.command == "test":
        test_server()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
