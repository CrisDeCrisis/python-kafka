# Guía de Inicio Rápido

## Prerequisitos

1. **Python 3.8+** instalado
2. **Ollama** instalado y ejecutándose
3. **Modelos descargados** en Ollama

## Configuración Inicial

### 1. Descargar Modelos

```bash
# Descargar los modelos necesarios
ollama pull phi3:3.8b
ollama pull nomic-embed-text

# Verificar que están disponibles
ollama list
```

### 2. Configurar Entorno

#### Opción B: Instalación Manual

```bash
# Navegar al directorio del servidor
cd server-python

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate

# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tu configuración si es necesario
```

## Iniciar el Servidor

### Opción 1: Usando el script de utilidades

```bash
# Configurar todo automáticamente
python utils.py setup

# Verificar dependencias
python utils.py check

# Iniciar servidor
python utils.py start
```

### Opción 2: Manualmente

```bash
# Ejecutar directamente
python run.py

# O con uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Verificar que Funciona

### 1. Verificar Estado

```bash
# Verificar salud del servidor
curl http://localhost:8000/health/

# Ver documentación automática
# Abrir en navegador: http://localhost:8000/docs
```

### 2. Probar Chat

```bash
# Probar chat básico
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cómo estás?",
    "use_context": false
  }'
```

### 3. Ejecutar Cliente de Prueba

```bash
# Ejecutar cliente de ejemplo
python client_example.py
```

## Endpoints Principales

- `GET /` - Información básica
- `GET /health/` - Estado del servidor
- `POST /chat/` - Chat con IA
- `POST /chat/stream` - Chat con streaming
- `POST /documents/` - Añadir documentos
- `GET /docs` - Documentación automática

## Solución de Problemas

### 🔍 Script de Diagnóstico Automático

Si tienes problemas, ejecuta primero el script de diagnóstico:

```bash
# Ejecutar diagnóstico completo
python diagnose.py

# Esto identificará automáticamente los problemas y generará scripts de reparación
```

### Error: "BaseSettings has been moved to pydantic-settings"

Este error ocurre porque Pydantic v2 ha movido `BaseSettings` a un paquete separado.

**Solución:**

```bash
# Método 1: Instalar pydantic-settings específicamente
pip install pydantic-settings

# Método 2: Reinstalar todas las dependencias
pip install -r requirements.txt --force-reinstall

# Método 3: Usar archivo de requisitos específico para Pydantic
pip install -r requirements-pydantic.txt

# Método 4: Verificar instalación
python -c "from pydantic_settings import BaseSettings; print('✅ pydantic-settings instalado correctamente')"
```

### Error: "Ollama not running"

```bash
# Iniciar Ollama
ollama serve
```

### Error: "Model not found"

```bash
# Verificar modelos disponibles
ollama list

# Descargar modelo faltante
ollama pull phi3:3.8b
ollama pull nomic-embed-text
```

### Error: "Port already in use"

```bash
# Cambiar puerto en .env
PORT=8001

# O especificar puerto diferente
python utils.py start --port 8001
```

## Desarrollo

### Estructura del Proyecto

```
server-python/
├── app/                    # Código principal
│   ├── main.py            # Aplicación FastAPI
│   ├── config.py          # Configuración
│   ├── models.py          # Modelos de datos
│   ├── api/               # Endpoints
│   └── services/          # Lógica de negocio
├── requirements.txt       # Dependencias
├── run.py                # Punto de entrada
├── utils.py              # Utilidades
└── client_example.py     # Cliente de prueba
```

### Comandos Útiles

```bash
# Verificar todo
python utils.py check

# Probar servidor
python utils.py test

# Iniciar con recarga automática
python utils.py start --reload

# Ver logs
tail -f logs/app.log
```

### Personalización

1. **Configuración**: Editar `app/config.py`
2. **Nuevos endpoints**: Añadir en `app/api/`
3. **Lógica de negocio**: Modificar `app/services/`
4. **Modelos de datos**: Actualizar `app/models.py`

## Monitoreo

### Logs

- Consola: Nivel INFO
- Archivo: `logs/app.log` (Nivel DEBUG)

### Métricas

- Estado: `GET /health/`
- Modelos: `GET /health/models`
- Estadísticas de documentos: `GET /documents/stats`

## Siguiente Paso

¡El servidor está listo! Ahora puedes:

1. Probar el chat en `http://localhost:8000/docs`
2. Integrar con tu aplicación frontend
3. Añadir documentos para mejorar el contexto
4. Personalizar los prompts y configuración
