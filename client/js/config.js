// Configuración de la aplicación
const CONFIG = {
    DEFAULT_SERVER_URL: 'http://localhost:8000',
    DEFAULT_TEMPERATURE: 0.7,
    DEFAULT_USE_STREAMING: true,
    STORAGE_KEYS: {
        SERVER_URL: 'aiChatServerUrl',
        CONVERSATION_ID: 'aiChatConversationId',
        TEMPERATURE: 'aiChatTemperature',
        USE_STREAMING: 'aiChatUseStreaming',
        CHAT_HISTORY: 'aiChatHistory'
    },
    ENDPOINTS: {
        HEALTH: '/health',
        CHAT: '/chat/',
        CHAT_STREAM: '/chat/stream',
        CHAT_HISTORY: '/chat/history'
    },
    MESSAGES: {
        WELCOME: '¡Hola! Soy tu asistente de IA. ¿En qué puedo ayudarte hoy?',
        DISCONNECTED: 'No hay conexión con el servidor. Verifica la configuración.',
        TYPING: 'Escribiendo',
        ERROR_PREFIX: 'Error: '
    },
    TIMEOUTS: {
        HEALTH_CHECK_INTERVAL: 30000, // 30 segundos
        RECONNECT_DELAY: 5000, // 5 segundos
        STREAM_TIMEOUT: 60000 // 60 segundos
    }
};

// Estado global de la aplicación
const AppState = {
    serverUrl: CONFIG.DEFAULT_SERVER_URL,
    conversationId: '',
    temperature: CONFIG.DEFAULT_TEMPERATURE,
    useStreaming: CONFIG.DEFAULT_USE_STREAMING,
    isConnected: false,
    messages: [],
    currentStreamingMessage: null,
    isTyping: false
};

// Exportar para uso en otros módulos
window.CONFIG = CONFIG;
window.AppState = AppState;
