// Módulo de chat
const Chat = {
    // Verificar estado del servidor
    async checkServerStatus() {
        try {
            const response = await fetch(`${AppState.serverUrl}${CONFIG.ENDPOINTS.HEALTH}`);
            UI.updateServerStatus(response.ok);
        } catch (error) {
            UI.updateServerStatus(false);
            console.error('Error verificando servidor:', error);
        }
    },

    // Enviar mensaje
    async sendMessage() {
        const message = UI.elements.messageInput.value.trim();

        if (!message) return;

        if (!AppState.isConnected) {
            UI.showError(CONFIG.MESSAGES.DISCONNECTED);
            return;
        }

        // Limpiar input y deshabilitar envío
        UI.elements.messageInput.value = '';
        UI.elements.messageInput.style.height = 'auto';
        UI.setInputDisabled(true);

        // Mostrar mensaje del usuario
        UI.addMessage('user', message);

        try {
            if (AppState.useStreaming) {
                await this.sendStreamingMessage(message);
            } else {
                await this.sendRegularMessage(message);
            }
        } catch (error) {
            console.error('Error enviando mensaje:', error);
            UI.showError(error.message);
        } finally {
            // Rehabilitar envío
            UI.setInputDisabled(false);
            UI.elements.messageInput.focus();
        }
    },

    // Enviar mensaje con streaming
    async sendStreamingMessage(message) {
        const requestBody = {
            message: message,
            temperature: AppState.temperature,
            use_context: true
        };

        if (AppState.conversationId) {
            requestBody.conversation_id = AppState.conversationId;
        }

        try {
            const response = await fetch(`${AppState.serverUrl}${CONFIG.ENDPOINTS.CHAT_STREAM}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            // Crear mensaje de streaming
            UI.createStreamingMessage();

            // Procesar stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Mantener línea incompleta

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);

                        if (data.startsWith('[ERROR]')) {
                            throw new Error(data.substring(8));
                        }

                        if (data.trim()) {
                            UI.updateStreamingMessage(data);
                        }
                    }
                }
            }

            // Finalizar mensaje de streaming
            UI.finishStreamingMessage();

        } catch (error) {
            // Limpiar mensaje de streaming si hay error
            if (AppState.currentStreamingMessage) {
                AppState.currentStreamingMessage.element.remove();
                AppState.currentStreamingMessage = null;
            }
            throw error;
        }
    },

    // Enviar mensaje regular (sin streaming)
    async sendRegularMessage(message) {
        const requestBody = {
            message: message,
            temperature: AppState.temperature,
            use_context: true
        };

        if (AppState.conversationId) {
            requestBody.conversation_id = AppState.conversationId;
        }

        // Mostrar indicador de escritura
        UI.showTypingIndicator();

        try {
            const response = await fetch(`${AppState.serverUrl}${CONFIG.ENDPOINTS.CHAT}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Ocultar indicador de escritura
            UI.hideTypingIndicator();

            // Mostrar respuesta
            UI.addMessage('ai', data.response);

            // Actualizar conversation_id si es nuevo
            if (data.conversation_id && data.conversation_id !== AppState.conversationId) {
                AppState.conversationId = data.conversation_id;
                UI.elements.conversationId.value = AppState.conversationId;
                localStorage.setItem(CONFIG.STORAGE_KEYS.CONVERSATION_ID, AppState.conversationId);
            }

        } catch (error) {
            UI.hideTypingIndicator();
            throw error;
        }
    },

    // Obtener historial de conversación del servidor
    async loadConversationHistory(conversationId) {
        if (!conversationId) return;

        try {
            const response = await fetch(`${AppState.serverUrl}${CONFIG.ENDPOINTS.CHAT_HISTORY}/${conversationId}`);

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Limpiar chat actual
            UI.clearChat();

            // Cargar mensajes del servidor
            data.messages.forEach(msg => {
                UI.addMessage(msg.type, msg.content, msg.timestamp);
            });

        } catch (error) {
            console.error('Error cargando historial:', error);
            UI.showError(`Error cargando historial: ${error.message}`);
        }
    },

    // Inicializar verificación periódica del servidor
    startHealthCheck() {
        // Verificar inmediatamente
        this.checkServerStatus();

        // Verificar cada 30 segundos
        setInterval(() => {
            this.checkServerStatus();
        }, CONFIG.TIMEOUTS.HEALTH_CHECK_INTERVAL);
    },

    // Reconectar al servidor
    async reconnect() {
        console.log('Intentando reconectar...');
        await this.checkServerStatus();

        if (!AppState.isConnected) {
            setTimeout(() => this.reconnect(), CONFIG.TIMEOUTS.RECONNECT_DELAY);
        }
    },

    // Inicializar módulo de chat
    init() {
        this.startHealthCheck();

        // Intentar reconectar si no está conectado
        if (!AppState.isConnected) {
            this.reconnect();
        }
    }
};

// Función global para enviar mensaje
function sendMessage() {
    Chat.sendMessage();
}

// Exportar módulo
window.Chat = Chat;
