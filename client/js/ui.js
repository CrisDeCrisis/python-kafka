// Módulo de interfaz de usuario
const UI = {
    // Elementos del DOM
    elements: {
        chatMessages: null,
        messageInput: null,
        sendButton: null,
        typingIndicator: null,
        settingsPanel: null,
        serverStatus: null,
        statusDot: null,
        serverUrl: null,
        conversationId: null,
        temperature: null,
        useStreaming: null
    },

    // Inicializar elementos del DOM
    init() {
        this.elements.chatMessages = document.getElementById('chatMessages');
        this.elements.messageInput = document.getElementById('messageInput');
        this.elements.sendButton = document.getElementById('sendButton');
        this.elements.typingIndicator = document.getElementById('typingIndicator');
        this.elements.settingsPanel = document.getElementById('settingsPanel');
        this.elements.serverStatus = document.getElementById('serverStatus');
        this.elements.statusDot = document.getElementById('statusDot');
        this.elements.serverUrl = document.getElementById('serverUrl');
        this.elements.conversationId = document.getElementById('conversationId');
        this.elements.temperature = document.getElementById('temperature');
        this.elements.useStreaming = document.getElementById('useStreaming');

        this.setupEventListeners();
        this.loadChatHistory();
    },

    // Configurar event listeners
    setupEventListeners() {
        // Auto-resize textarea
        this.elements.messageInput.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });

        // Enviar con Enter (pero no con Shift+Enter)
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                Chat.sendMessage();
            }
        });

        // Guardar configuraciones cuando cambien
        this.elements.serverUrl.addEventListener('change', () => this.saveSettings());
        this.elements.conversationId.addEventListener('change', () => this.saveSettings());
        this.elements.temperature.addEventListener('change', () => this.saveSettings());
        this.elements.useStreaming.addEventListener('change', () => this.saveSettings());
    },

    // Cargar configuraciones guardadas
    loadSettings() {
        const savedServerUrl = localStorage.getItem(CONFIG.STORAGE_KEYS.SERVER_URL);
        const savedConversationId = localStorage.getItem(CONFIG.STORAGE_KEYS.CONVERSATION_ID);
        const savedTemperature = localStorage.getItem(CONFIG.STORAGE_KEYS.TEMPERATURE);
        const savedUseStreaming = localStorage.getItem(CONFIG.STORAGE_KEYS.USE_STREAMING);

        if (savedServerUrl) {
            this.elements.serverUrl.value = savedServerUrl;
            AppState.serverUrl = savedServerUrl;
        }
        if (savedConversationId) {
            this.elements.conversationId.value = savedConversationId;
            AppState.conversationId = savedConversationId;
        }
        if (savedTemperature) {
            this.elements.temperature.value = savedTemperature;
            AppState.temperature = parseFloat(savedTemperature);
        }
        if (savedUseStreaming !== null) {
            this.elements.useStreaming.checked = savedUseStreaming === 'true';
            AppState.useStreaming = savedUseStreaming === 'true';
        }
    },

    // Guardar configuraciones
    saveSettings() {
        const newServerUrl = this.elements.serverUrl.value;
        const newConversationId = this.elements.conversationId.value;
        const newTemperature = this.elements.temperature.value;
        const newUseStreaming = this.elements.useStreaming.checked;

        localStorage.setItem(CONFIG.STORAGE_KEYS.SERVER_URL, newServerUrl);
        localStorage.setItem(CONFIG.STORAGE_KEYS.CONVERSATION_ID, newConversationId);
        localStorage.setItem(CONFIG.STORAGE_KEYS.TEMPERATURE, newTemperature);
        localStorage.setItem(CONFIG.STORAGE_KEYS.USE_STREAMING, newUseStreaming.toString());

        // Actualizar estado global
        const serverUrlChanged = AppState.serverUrl !== newServerUrl;
        AppState.serverUrl = newServerUrl;
        AppState.conversationId = newConversationId;
        AppState.temperature = parseFloat(newTemperature);
        AppState.useStreaming = newUseStreaming;

        // Recomprobar estado del servidor si cambió la URL
        if (serverUrlChanged) {
            Chat.checkServerStatus();
        }
    },

    // Cargar historial de chat desde localStorage
    loadChatHistory() {
        const savedHistory = localStorage.getItem(CONFIG.STORAGE_KEYS.CHAT_HISTORY);
        if (savedHistory) {
            try {
                const messages = JSON.parse(savedHistory);
                AppState.messages = messages;

                // Limpiar mensajes existentes excepto el mensaje de bienvenida
                this.elements.chatMessages.innerHTML = '';

                // Añadir mensaje de bienvenida
                this.addMessage('ai', CONFIG.MESSAGES.WELCOME, 'Ahora', false);

                // Añadir mensajes del historial
                messages.forEach(msg => {
                    this.addMessage(msg.type, msg.content, msg.time, false);
                });
            } catch (error) {
                console.error('Error cargando historial:', error);
            }
        }
    },

    // Guardar historial de chat
    saveChatHistory() {
        try {
            localStorage.setItem(CONFIG.STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(AppState.messages));
        } catch (error) {
            console.error('Error guardando historial:', error);
        }
    },

    // Mostrar/ocultar panel de configuración
    toggleSettings() {
        this.elements.settingsPanel.classList.toggle('show');
    },

    // Actualizar estado del servidor
    updateServerStatus(connected) {
        AppState.isConnected = connected;

        if (connected) {
            this.elements.serverStatus.textContent = 'Conectado';
            this.elements.statusDot.classList.add('online');
        } else {
            this.elements.serverStatus.textContent = 'Desconectado';
            this.elements.statusDot.classList.remove('online');
        }
    },

    // Añadir mensaje al chat
    addMessage(type, content, time = null, saveToHistory = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        if (!time) {
            time = new Date().toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">${type === 'user' ? '👤' : '🤖'}</div>
            <div class="message-content">
                <div class="message-text">${content.replace(/\n/g, '<br>')}</div>
                <div class="message-time">${time}</div>
            </div>
        `;

        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // Guardar en historial
        if (saveToHistory) {
            AppState.messages.push({
                type: type,
                content: content,
                time: time,
                timestamp: Date.now()
            });
            this.saveChatHistory();
        }

        return messageDiv;
    },

    // Crear mensaje de streaming
    createStreamingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai streaming-message';

        const time = new Date().toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-text"></div>
                <div class="message-time">${time}</div>
            </div>
        `;

        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        AppState.currentStreamingMessage = {
            element: messageDiv,
            content: '',
            time: time
        };

        return messageDiv;
    },

    // Actualizar mensaje de streaming
    updateStreamingMessage(chunk) {
        if (AppState.currentStreamingMessage) {
            AppState.currentStreamingMessage.content += chunk;
            const messageText = AppState.currentStreamingMessage.element.querySelector('.message-text');
            messageText.innerHTML = AppState.currentStreamingMessage.content.replace(/\n/g, '<br>');
            this.scrollToBottom();
        }
    },

    // Finalizar mensaje de streaming
    finishStreamingMessage() {
        if (AppState.currentStreamingMessage) {
            // Remover clase de streaming
            AppState.currentStreamingMessage.element.classList.remove('streaming-message');

            // Guardar en historial
            AppState.messages.push({
                type: 'ai',
                content: AppState.currentStreamingMessage.content,
                time: AppState.currentStreamingMessage.time,
                timestamp: Date.now()
            });
            this.saveChatHistory();

            AppState.currentStreamingMessage = null;
        }
    },

    // Mostrar indicador de escritura
    showTypingIndicator() {
        this.elements.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
        AppState.isTyping = true;
    },

    // Ocultar indicador de escritura
    hideTypingIndicator() {
        this.elements.typingIndicator.style.display = 'none';
        AppState.isTyping = false;
    },

    // Mostrar mensaje de error
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = CONFIG.MESSAGES.ERROR_PREFIX + message;
        this.elements.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
    },

    // Scroll al final
    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    },

    // Limpiar chat
    clearChat() {
        // Mantener solo el mensaje de bienvenida
        this.elements.chatMessages.innerHTML = '';
        this.addMessage('ai', CONFIG.MESSAGES.WELCOME, 'Ahora', false);

        // Limpiar historial
        AppState.messages = [];
        AppState.conversationId = '';
        this.elements.conversationId.value = '';
        this.saveChatHistory();
        localStorage.removeItem(CONFIG.STORAGE_KEYS.CONVERSATION_ID);
    },

    // Habilitar/deshabilitar envío
    setInputDisabled(disabled) {
        this.elements.messageInput.disabled = disabled;
        this.elements.sendButton.disabled = disabled;
    }
};

// Función global para alternar configuración
function toggleSettings() {
    UI.toggleSettings();
}

// Exportar módulo
window.UI = UI;
