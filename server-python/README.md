# Servidor de IA con LangChain y Ollama

Este proyecto implementa un servidor HTTP con FastAPI que integra modelos de IA a través de LangChain y Ollama, con capacidades de embeddings y almacenamiento vectorial usando ChromaDB.

## Características

- **FastAPI**: Framework web moderno y rápido
- **LangChain**: Framework para aplicaciones con LLM
- **Ollama**: Servidor local de modelos de IA
- **ChromaDB**: Base de datos vectorial para embeddings
- **Arquitectura modular**: Código organizado en servicios separados
- **Contexto conversacional**: Mantiene el contexto de las conversaciones
- **Embeddings**: Procesamiento de documentos con embeddings
- **Streaming**: Respuestas en tiempo real

## Modelos Utilizados

- **LLM**: phi3:3.8b (modelo de lenguaje principal)
- **Embeddings**: nomic-embed-text (para generar embeddings)

## Estructura del Proyecto

```
server-python/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación FastAPI principal
│   ├── config.py               # Configuración centralizada
│   ├── models.py               # Modelos de datos (Pydantic)
│   ├── dependencies.py         # Inyección de dependencias
│   ├── logging_config.py       # Configuración de logging
│   ├── api/                    # Endpoints de la API
│   │   ├── __init__.py
│   │   ├── chat.py             # Endpoints de chat
│   │   ├── documents.py        # Endpoints de documentos
│   │   └── health.py           # Endpoints de salud
│   └── services/               # Servicios de negocio
│       ├── __init__.py
│       ├── chat_service.py     # Servicio principal de chat
│       ├── llm_service.py      # Servicio de modelo de lenguaje
│       ├── embedding_service.py # Servicio de embeddings
│       └── vector_db_service.py # Servicio de base de datos vectorial
├── requirements.txt            # Dependencias de Python
├── .env.example               # Ejemplo de variables de entorno
└── run.py                     # Punto de entrada
```

## Requisitos Previos

1. **Python 3.8+**
2. **Ollama** instalado y ejecutándose localmente
3. **Modelos descargados en Ollama**:
   ```bash
   ollama pull phi3:3.8b
   ollama pull nomic-embed-text
   ```

## Instalación

1. **Clonar el repositorio** (si aplicable)

2. **Crear entorno virtual**:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:

   ```bash
   copy .env.example .env
   # Editar .env con tu configuración
   ```

5. **Verificar que Ollama esté ejecutándose**:
   ```bash
   ollama list
   ```

## Uso

### Ejecutar el servidor

```bash
python run.py
```

O alternativamente:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Endpoints disponibles

#### Chat

- `POST /chat/` - Chat básico
- `POST /chat/stream` - Chat con streaming
- `GET /chat/history/{conversation_id}` - Historial de conversación

#### Documentos

- `POST /documents/` - Añadir documento al contexto
- `GET /documents/stats` - Estadísticas de documentos

#### Salud

- `GET /health/` - Estado de los servicios
- `GET /health/models` - Información de modelos

### Ejemplo de uso con curl

```bash
# Chat básico
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cómo estás?",
    "use_context": true,
    "temperature": 0.7
  }'

# Añadir documento
curl -X POST "http://localhost:8000/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Este es un documento de ejemplo con información importante.",
    "metadata": {"tipo": "ejemplo"},
    "conversation_id": "conv-123"
  }'

# Health check
curl -X GET "http://localhost:8000/health/"
```

## Configuración

### Variables de entorno

- `OLLAMA_BASE_URL`: URL base de Ollama (default: http://localhost:11434)
- `LLM_MODEL`: Modelo de lenguaje (default: phi3:3.8b)
- `EMBEDDING_MODEL`: Modelo de embeddings (default: nomic-embed-text)
- `CHROMA_PERSIST_DIRECTORY`: Directorio de ChromaDB (default: ./chroma_db)
- `HOST`: Host del servidor (default: 0.0.0.0)
- `PORT`: Puerto del servidor (default: 8000)
- `LOG_LEVEL`: Nivel de logging (default: INFO)

### Personalización

Puedes personalizar el comportamiento modificando:

- `app/config.py`: Configuración general
- `app/services/`: Lógica de negocio
- `app/api/`: Endpoints de la API

## Funcionalidades Principales

### 1. Chat con IA

- Procesa mensajes del usuario
- Genera respuestas usando phi3:3.8b
- Mantiene contexto de conversación
- Soporte para streaming

### 2. Gestión de Documentos

- Añade documentos al contexto
- Genera embeddings automáticamente
- Divide documentos en chunks
- Almacena en base de datos vectorial

### 3. Búsqueda Semántica

- Busca documentos similares
- Utiliza embeddings para similitud
- Recupera contexto relevante
- Mejora respuestas con contexto

### 4. Persistencia

- Almacena conversaciones en ChromaDB
- Mantiene embeddings de documentos
- Permite recuperar historial

## Desarrollo

### Estructura de servicios

1. **ChatService**: Orquesta todos los componentes
2. **LLMService**: Interactúa con el modelo de lenguaje
3. **EmbeddingService**: Genera embeddings
4. **VectorDatabaseService**: Gestiona ChromaDB

### Añadir nuevas funcionalidades

1. Crear nuevo servicio en `app/services/`
2. Añadir endpoints en `app/api/`
3. Actualizar modelos en `app/models.py`
4. Actualizar dependencias si es necesario

## Troubleshooting

### Problemas comunes

1. **Error de conexión a Ollama**:

   - Verificar que Ollama esté ejecutándose
   - Comprobar URL en configuración

2. **Modelo no encontrado**:

   - Verificar que los modelos estén descargados
   - Usar `ollama list` para verificar

3. **Error de permisos en ChromaDB**:
   - Verificar permisos del directorio
   - Crear directorio manualmente si es necesario

### Logs

Los logs se guardan en:

- Consola: Nivel INFO
- Archivo: `logs/app.log` (Nivel DEBUG)

## Contribución

1. Fork el repositorio
2. Crear rama de feature
3. Realizar cambios
4. Añadir tests si es necesario
5. Crear pull request

## Licencia

[Especificar licencia]
