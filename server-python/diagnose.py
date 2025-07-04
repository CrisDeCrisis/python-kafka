"""
Script de diagnóstico para identificar y resolver problemas del servidor de IA
"""
import sys
import subprocess
import importlib
import json
import requests
from pathlib import Path


def print_header(title: str):
    """Imprime un encabezado formateado"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def check_python_version():
    """Verifica la versión de Python"""
    print_header("VERIFICACIÓN DE PYTHON")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    else:
        print("✅ Versión de Python compatible")
        return True


def check_virtual_environment():
    """Verifica si se está usando un entorno virtual"""
    print_header("VERIFICACIÓN DE ENTORNO VIRTUAL")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Entorno virtual activo")
        print(f"   Ubicación: {sys.prefix}")
        return True
    else:
        print("⚠️  No se detectó entorno virtual")
        print("   Recomendación: Usar entorno virtual para evitar conflictos")
        return False


def check_critical_packages():
    """Verifica paquetes críticos"""
    print_header("VERIFICACIÓN DE PAQUETES CRÍTICOS")
    
    critical_packages = {
        'fastapi': 'FastAPI framework',
        'uvicorn': 'ASGI server',
        'pydantic': 'Data validation',
        'pydantic_settings': 'Settings management',
        'langchain': 'LangChain framework',
        'langchain_ollama': 'Ollama integration',
        'chromadb': 'Vector database',
        'requests': 'HTTP requests',
        'aiohttp': 'Async HTTP client'
    }
    
    results = {}
    for package, description in critical_packages.items():
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'Unknown')
            print(f"✅ {package} v{version} - {description}")
            results[package] = {'installed': True, 'version': version}
        except ImportError:
            print(f"❌ {package} - {description} (NO INSTALADO)")
            results[package] = {'installed': False, 'version': None}
    
    return results


def check_pydantic_compatibility():
    """Verifica compatibilidad específica de Pydantic"""
    print_header("VERIFICACIÓN DE COMPATIBILIDAD PYDANTIC")
    
    try:
        from pydantic_settings import BaseSettings
        print("✅ pydantic-settings importado correctamente")
        
        # Probar creación de configuración
        class TestSettings(BaseSettings):
            test_field: str = "test"
        
        settings = TestSettings()
        print("✅ BaseSettings funciona correctamente")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando pydantic-settings: {e}")
        print("   Solución: pip install pydantic-settings")
        return False
    except Exception as e:
        print(f"❌ Error con BaseSettings: {e}")
        return False


def check_ollama_connection():
    """Verifica conexión con Ollama"""
    print_header("VERIFICACIÓN DE OLLAMA")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama está ejecutándose")
            
            # Verificar modelos
            models = response.json()
            model_names = [model["name"] for model in models.get("models", [])]
            
            required_models = ["phi3:3.8b", "nomic-embed-text"]
            for model in required_models:
                if any(model in name for name in model_names):
                    print(f"✅ Modelo {model} disponible")
                else:
                    print(f"❌ Modelo {model} no disponible")
                    print(f"   Solución: ollama pull {model}")
            
            return True
        else:
            print(f"❌ Ollama responde con código {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ No se puede conectar a Ollama: {e}")
        print("   Solución: Iniciar Ollama con 'ollama serve'")
        return False


def check_file_structure():
    """Verifica estructura de archivos"""
    print_header("VERIFICACIÓN DE ESTRUCTURA DE ARCHIVOS")
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/models.py",
        "app/services/__init__.py",
        "app/api/__init__.py",
        "requirements.txt",
        "run.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (FALTANTE)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def generate_fix_script():
    """Genera script de reparación"""
    print_header("GENERANDO SCRIPT DE REPARACIÓN")
    
    fix_commands = [
        "# Script de reparación automática",
        "echo 'Reparando instalación...'",
        "",
        "# Actualizar pip",
        "python -m pip install --upgrade pip",
        "",
        "# Reinstalar dependencias críticas",
        "pip install pydantic-settings --force-reinstall",
        "pip install -r requirements.txt --force-reinstall",
        "",
        "# Verificar instalación",
        "python -c \"from pydantic_settings import BaseSettings; print('✅ Reparación completada')\"",
        "",
        "echo 'Reparación completada. Intenta iniciar el servidor nuevamente.'"
    ]
    
    script_content = "\n".join(fix_commands)
    
    # Crear script para Windows
    with open("fix_installation.bat", "w") as f:
        f.write("@echo off\n")
        f.write(script_content.replace("echo", "echo."))
        f.write("\npause")
    
    # Crear script para Linux/Mac
    with open("fix_installation.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(script_content)
    
    print("✅ Scripts de reparación generados:")
    print("   - fix_installation.bat (Windows)")
    print("   - fix_installation.sh (Linux/Mac)")


def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO DEL SERVIDOR DE IA")
    print("Este script identificará y ayudará a resolver problemas comunes")
    
    results = {}
    
    # Ejecutar verificaciones
    results['python'] = check_python_version()
    results['venv'] = check_virtual_environment()
    results['packages'] = check_critical_packages()
    results['pydantic'] = check_pydantic_compatibility()
    results['ollama'] = check_ollama_connection()
    results['files'] = check_file_structure()
    
    # Resumen
    print_header("RESUMEN DEL DIAGNÓSTICO")
    
    issues = []
    if not results['python']:
        issues.append("Versión de Python incompatible")
    if not results['pydantic']:
        issues.append("Problema con pydantic-settings")
    if not results['ollama']:
        issues.append("Problema con Ollama")
    if not results['files']:
        issues.append("Archivos faltantes")
    
    if issues:
        print("❌ Problemas encontrados:")
        for issue in issues:
            print(f"   - {issue}")
        
        print("\n🔧 Generando script de reparación...")
        generate_fix_script()
        
        print("\n📋 PASOS RECOMENDADOS:")
        print("1. Ejecutar script de reparación (fix_installation.bat/sh)")
        print("2. Verificar que Ollama esté ejecutándose")
        print("3. Descargar modelos necesarios")
        print("4. Intentar iniciar el servidor nuevamente")
        
    else:
        print("✅ No se encontraron problemas críticos")
        print("   El servidor debería funcionar correctamente")


if __name__ == "__main__":
    main()
