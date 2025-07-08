# ⚡ Guía de Inicio Rápido - AI Server

Configuración express para tener el servidor funcionando en **menos de 5 minutos**.

> 📋 **Para documentación completa**: Ver [README.md](README.md) y [README_KAFKA.md](../README_KAFKA.md)

## 🎯 Prerequisitos Mínimos

✅ **Python 3.11+** instalado  
✅ **Ollama** descargado e instalado  
✅ **Git** para clonar (opcional)

## 🚀 Instalación Express (5 minutos)

### ⏱️ Paso 1: Preparar Modelos (2 min)

```powershell
# Descargar modelos necesarios
ollama pull phi3:3.8b
ollama pull nomic-embed-text

# Verificar descarga
ollama list
```

### ⏱️ Paso 2: Configurar Entorno (2 min)

```powershell
# Navegar al directorio
cd server-python

# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables
copy .env.example .env
```

### ⏱️ Paso 3: Iniciar Servidor (1 min)

```powershell
# Método 1: Script directo
python run.py

# Método 2: Con utilidades (recomendado)
python utils.py start
```

### ✅ Verificación

```powershell
# Test rápido
curl http://localhost:8000/health/

# Abrir documentación
start http://localhost:8000/docs
```

## 🛠️ Configuración Automática

### 🎛️ Script Todo-en-Uno

```powershell
# Configurar todo automáticamente
python utils.py setup

# Verificar instalación
python utils.py check

# Iniciar servidor
python utils.py start
```

## 🧪 Primeras Pruebas

### 💬 Test de Chat Básico

```powershell
# Chat simple
curl -X POST "http://localhost:8000/chat/" `
  -H "Content-Type: application/json" `
  -d '{"message": "Hola, ¿cómo estás?"}'

# Con parámetros
curl -X POST "http://localhost:8000/chat/" `
  -H "Content-Type: application/json" `
  -d '{"message": "Explica qué es Python", "temperature": 0.8, "use_context": false}'
```

### 📄 Test de Documentos

```powershell
# Añadir documento
curl -X POST "http://localhost:8000/documents/" `
  -H "Content-Type: application/json" `
  -d '{"content": "Python es un lenguaje de programación de alto nivel...", "conversation_id": "test-001"}'

# Chat con contexto
curl -X POST "http://localhost:8000/chat/" `
  -H "Content-Type: application/json" `
  -d '{"message": "¿Qué características tiene Python?", "use_context": true, "conversation_id": "test-001"}'
```

### 🎯 Cliente de Prueba Incluido

```powershell
# Ejecutar cliente interactivo
python client_example.py
```

## 🌐 URLs Importantes

Una vez iniciado el servidor:

| Servicio          | URL                          | Descripción               |
| ----------------- | ---------------------------- | ------------------------- |
| **API Principal** | http://localhost:8000        | Endpoint base             |
| **Documentación** | http://localhost:8000/docs   | Swagger UI interactivo    |
| **ReDoc**         | http://localhost:8000/redoc  | Documentación alternativa |
| **Health Check**  | http://localhost:8000/health | Estado del sistema        |

## ⚙️ Configuración Kafka (Opcional)

Si quieres habilitar Kafka para streaming:

```powershell
# Desde el directorio raíz del proyecto
cd ..
docker-compose up -d

# Crear topics
cd server-python
python create_kafka_topics.py

# Verificar Kafka
python verify_kafka.py
```

## 🚨 Solución de Problemas Express

### ❌ Error: "BaseSettings has been moved to pydantic-settings"

```powershell
pip install pydantic-settings
```

### ❌ Error: "Ollama not running"

```powershell
# Iniciar Ollama
ollama serve

# En otra terminal, verificar
ollama list
```

### ❌ Error: "Model not found"

```powershell
ollama pull phi3:3.8b
ollama pull nomic-embed-text
```

### ❌ Error: "Port already in use"

```powershell
# Cambiar puerto en .env
echo "PORT=8001" >> .env

# O usar puerto diferente
python utils.py start --port 8001
```

### 🔍 Diagnóstico Automático

```powershell
# Ejecutar diagnóstico completo
python diagnose.py

# Verificar configuración
python utils.py check
```

## 🎯 Próximos Pasos

Una vez que el servidor esté funcionando:

1. **🧪 Explorar API**: http://localhost:8000/docs
2. **💬 Probar Chat**: Usar la interfaz Swagger
3. **📄 Añadir Documentos**: Mejorar el contexto
4. **⚡ Configurar Kafka**: Para distribución de mensajes
5. **🔧 Personalizar**: Modificar configuraciones según necesidades

## 📋 Comandos de Referencia Rápida

```powershell
# Setup inicial
python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt

# Preparar modelos
ollama pull phi3:3.8b && ollama pull nomic-embed-text

# Configurar
copy .env.example .env

# Iniciar
python run.py

# Verificar
curl http://localhost:8000/health/

# Documentación
start http://localhost:8000/docs
```

---

## 🎉 ¡Listo!

El servidor está funcionando. Para documentación completa consulta:

- **README.md** - Documentación del servidor
- **../README_KAFKA.md** - Sistema completo con Kafka
