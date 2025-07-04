// Archivo principal de la aplicación
class ChatApp {
    constructor() {
        this.initialized = false;
    }

    // Inicializar aplicación
    async init() {
        if (this.initialized) return;

        try {
            console.log('Iniciando aplicación de chat...');

            // Inicializar módulos
            UI.init();
            UI.loadSettings();
            Chat.init();

            // Configurar manejadores de eventos globales
            this.setupGlobalEventHandlers();

            // Marcar como inicializada
            this.initialized = true;

            console.log('Aplicación de chat iniciada exitosamente');

        } catch (error) {
            console.error('Error iniciando aplicación:', error);
            this.showStartupError(error);
        }
    }

    // Configurar manejadores de eventos globales
    setupGlobalEventHandlers() {
        // Prevenir cierre accidental
        window.addEventListener('beforeunload', (e) => {
            if (AppState.messages.length > 1) { // Más que solo el mensaje de bienvenida
                e.preventDefault();
                e.returnValue = '';
            }
        });

        // Manejar errores no capturados
        window.addEventListener('error', (e) => {
            console.error('Error no capturado:', e.error);
            UI.showError('Se produjo un error inesperado. Recarga la página si el problema persiste.');
        });

        // Manejar errores de promesas no capturadas
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Promesa rechazada no capturada:', e.reason);
            UI.showError('Error de conexión. Verifica tu conexión a internet.');
        });

        // Manejar visibilidad de la página
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                // Página visible, verificar estado del servidor
                Chat.checkServerStatus();
            }
        });

        // Manejar conexión/desconexión
        window.addEventListener('online', () => {
            console.log('Conexión restaurada');
            Chat.checkServerStatus();
        });

        window.addEventListener('offline', () => {
            console.log('Conexión perdida');
            UI.updateServerStatus(false);
            UI.showError('Conexión a internet perdida');
        });
    }

    // Mostrar error de inicio
    showStartupError(error) {
        document.body.innerHTML = `
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            ">
                <div style="
                    background: white;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    max-width: 400px;
                ">
                    <h2 style="color: #c62828; margin-bottom: 15px;">Error de Inicio</h2>
                    <p style="color: #666; margin-bottom: 20px;">
                        No se pudo inicializar la aplicación de chat.
                    </p>
                    <p style="color: #999; font-size: 14px; margin-bottom: 20px;">
                        ${error.message}
                    </p>
                    <button onclick="location.reload()" style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 20px;
                        cursor: pointer;
                        font-size: 16px;
                    ">
                        Reintentar
                    </button>
                </div>
            </div>
        `;
    }

    // Limpiar chat
    clearChat() {
        if (confirm('¿Estás seguro de que quieres limpiar el chat? Esta acción no se puede deshacer.')) {
            UI.clearChat();
            AppState.conversationId = '';
            console.log('Chat limpiado');
        }
    }

    // Exportar historial
    exportHistory() {
        try {
            const data = {
                timestamp: new Date().toISOString(),
                conversationId: AppState.conversationId,
                messages: AppState.messages,
                settings: {
                    serverUrl: AppState.serverUrl,
                    temperature: AppState.temperature,
                    useStreaming: AppState.useStreaming
                }
            };

            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            console.log('Historial exportado exitosamente');
        } catch (error) {
            console.error('Error exportando historial:', error);
            UI.showError('Error al exportar el historial');
        }
    }

    // Importar historial
    importHistory(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);

                if (data.messages && Array.isArray(data.messages)) {
                    // Limpiar chat actual
                    UI.clearChat();

                    // Cargar mensajes
                    data.messages.forEach(msg => {
                        UI.addMessage(msg.type, msg.content, msg.time, false);
                    });

                    // Actualizar estado
                    AppState.messages = data.messages;
                    if (data.conversationId) {
                        AppState.conversationId = data.conversationId;
                        UI.elements.conversationId.value = data.conversationId;
                    }

                    UI.saveChatHistory();
                    console.log('Historial importado exitosamente');
                } else {
                    throw new Error('Formato de archivo inválido');
                }
            } catch (error) {
                console.error('Error importando historial:', error);
                UI.showError('Error al importar el historial. Verifica el formato del archivo.');
            }
        };
        reader.readAsText(file);
    }

    // Obtener información de la aplicación
    getAppInfo() {
        return {
            version: '1.0.0',
            messages: AppState.messages.length,
            connected: AppState.isConnected,
            serverUrl: AppState.serverUrl,
            conversationId: AppState.conversationId,
            uptime: performance.now()
        };
    }
}

// Crear instancia global de la aplicación
const app = new ChatApp();

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// Funciones globales para consola/debugging
window.chatApp = app;
window.clearChat = () => app.clearChat();
window.exportHistory = () => app.exportHistory();
window.getAppInfo = () => app.getAppInfo();

// Funciones de utilidad para desarrollador
window.debugInfo = () => {
    console.log('=== Debug Info ===');
    console.log('App State:', AppState);
    console.log('Config:', CONFIG);
    console.log('App Info:', app.getAppInfo());
    console.log('==================');
};

console.log('🚀 Chat con IA cargado. Usa debugInfo() para información de debug.');
