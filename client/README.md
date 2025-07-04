# Chat con IA - Cliente Web

Cliente web modular para interactuar con el servidor de IA basado en LangChain y Ollama.

## 🚀 Características

- **Interfaz moderna y responsive** - Se adapta a diferentes dispositivos
- **Streaming en tiempo real** - Respuestas que se escriben en tiempo real
- **Persistencia de conversaciones** - Historial guardado localmente
- **Configuración flexible** - Ajusta temperatura, URLs y más
- **Detección automática de servidor** - Indica estado de conexión
- **Arquitectura modular** - Código separado por responsabilidades

## 📁 Estructura del Proyecto

```
client/
├── index.html          # Archivo principal HTML
├── css/
│   └── styles.css      # Estilos de la aplicación
├── js/
│   ├── config.js       # Configuración y constantes
│   ├── ui.js           # Interfaz de usuario
│   ├── chat.js         # Lógica de chat y comunicación
│   └── app.js          # Aplicación principal
└── README.md           # Este archivo
```

## 🎯 Cómo Usar

### 1. Preparar el Servidor

Asegúrate de que tu servidor FastAPI esté funcionando:

```bash
cd server-python
python run.py
```

### 2. Abrir el Cliente

Simplemente abre el archivo `index.html` en tu navegador:

- **Opción 1**: Doble clic en `index.html`
- **Opción 2**: Arrastrar el archivo al navegador
- **Opción 3**: Usar un servidor local (recomendado para desarrollo)

### 3. Configurar Conexión

1. Haz clic en "⚙️ Config" en la parte superior
2. Verifica que la URL del servidor sea correcta (por defecto: `http://localhost:8000`)
3. Ajusta otros parámetros según necesites

### 4. ¡Conversar!

Escribe tu mensaje y presiona Enter. El bot responderá usando streaming para una experiencia más fluida.

## ⚙️ Configuraciones Disponibles

### Panel de Configuración

- **URL del Servidor**: Cambia si tu servidor está en otro puerto o host
- **ID de Conversación**: Para mantener contexto entre sesiones
- **Temperatura**: Controla la creatividad del modelo (0.0-1.0)
- **Usar Streaming**: Activa/desactiva respuestas en tiempo real

### Persistencia

- **Historial de Chat**: Se guarda automáticamente en el navegador
- **Configuraciones**: Se mantienen entre sesiones
- **ID de Conversación**: Se genera automáticamente o puedes especificar uno

## 🔧 Funcionalidades Técnicas

### Streaming de Respuestas

El cliente utiliza Server-Sent Events para recibir respuestas en tiempo real:

```javascript
// Endpoint usado para streaming
POST / chat / stream;
```

### Manejo de Errores

- **Conexión perdida**: Reintenta automáticamente
- **Errores del servidor**: Muestra mensajes informativos
- **Errores de red**: Manejo graceful con reconexión

### Arquitectura Modular

- **config.js**: Configuración centralizada
- **ui.js**: Manejo de la interfaz de usuario
- **chat.js**: Lógica de comunicación con el servidor
- **app.js**: Orquestación de la aplicación

## 🛠️ Desarrollo

### Depuración

Abre la consola del navegador y usa:

```javascript
debugInfo(); // Información de debug
clearChat(); // Limpiar chat
exportHistory(); // Exportar historial
getAppInfo(); // Información de la app
```

### Personalización

- **Estilos**: Modifica `css/styles.css`
- **Configuración**: Ajusta `js/config.js`
- **Funcionalidades**: Extiende los módulos en `js/`

## 📱 Compatibilidad

- **Navegadores**: Chrome, Firefox, Safari, Edge (versiones modernas)
- **Dispositivos**: Desktop, tablet, móvil
- **Funcionalidades**: Streaming, localStorage, Fetch API

## 🔒 Seguridad

- **CORS**: Configurado en el servidor
- **Validación**: Entrada de usuario validada
- **Sanitización**: Contenido HTML sanitizado

## 🚨 Solución de Problemas

### "Desconectado" permanente

- Verifica que el servidor esté funcionando
- Revisa la URL en configuración
- Comprueba la consola del navegador

### Mensajes no se muestran

- Refresca la página
- Limpia el localStorage del navegador
- Verifica la consola por errores

### Streaming no funciona

- Verifica soporte de Server-Sent Events
- Revisa la configuración del servidor
- Usa modo no-streaming como alternativa

## 📄 Licencia

Este proyecto es parte del sistema de chat con IA y sigue la misma licencia del proyecto principal.

## 🤝 Contribuciones

Para contribuir:

1. Asegúrate de que el código siga la estructura modular
2. Documenta nuevas funcionalidades
3. Mantén compatibilidad con navegadores modernos
4. Prueba en diferentes dispositivos

---

**¡Disfruta conversando con tu IA!** 🤖✨
