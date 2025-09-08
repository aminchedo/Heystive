/**
 * WebSocket Client for Heystive Persian Voice Assistant
 * Real-time communication with backend services
 */

class HeystiveWebSocketClient {
    constructor(url = null) {
        this.url = url || `ws://${window.location.host}/ws`;
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.heartbeatInterval = null;
        this.heartbeatTimeout = null;
        
        // Message queue for offline messages
        this.messageQueue = [];
        
        // Event callbacks
        this.onConnect = null;
        this.onDisconnect = null;
        this.onMessage = null;
        this.onError = null;
        this.onReconnecting = null;
        this.onReconnected = null;
        
        // Message handlers
        this.messageHandlers = new Map();
        
        this.init();
    }
    
    init() {
        console.log('🔌 Initializing WebSocket client...');
        this.connect();
    }
    
    connect() {
        try {
            console.log(`🔗 Connecting to ${this.url}...`);
            
            this.socket = new WebSocket(this.url);
            
            this.socket.onopen = (event) => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                
                // Start heartbeat
                this.startHeartbeat();
                
                // Process queued messages
                this.processMessageQueue();
                
                if (this.onConnect) {
                    this.onConnect(event);
                }
                
                // Send connection info
                this.send({
                    type: 'connection',
                    data: {
                        timestamp: Date.now(),
                        userAgent: navigator.userAgent,
                        language: navigator.language || 'fa-IR'
                    }
                });
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (error) {
                    console.error('❌ Failed to parse WebSocket message:', error);
                    console.log('Raw message:', event.data);
                }
            };
            
            this.socket.onclose = (event) => {
                console.log('🔌 WebSocket disconnected:', event.code, event.reason);
                this.isConnected = false;
                
                // Stop heartbeat
                this.stopHeartbeat();
                
                if (this.onDisconnect) {
                    this.onDisconnect(event);
                }
                
                // Attempt reconnection if not intentional close
                if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.attemptReconnect();
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('🚨 WebSocket error:', error);
                
                if (this.onError) {
                    this.onError(error);
                }
            };
            
        } catch (error) {
            console.error('❌ Failed to create WebSocket connection:', error);
            this.attemptReconnect();
        }
    }
    
    disconnect() {
        console.log('🔌 Disconnecting WebSocket...');
        
        if (this.socket) {
            this.socket.close(1000, 'Client disconnect');
        }
        
        this.stopHeartbeat();
        this.isConnected = false;
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            return;
        }
        
        this.reconnectAttempts++;
        
        console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        if (this.onReconnecting) {
            this.onReconnecting(this.reconnectAttempts);
        }
        
        setTimeout(() => {
            this.connect();
        }, this.reconnectDelay);
        
        // Exponential backoff
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    }
    
    send(message) {
        if (!this.isConnected) {
            console.warn('⚠️ WebSocket not connected, queuing message');
            this.messageQueue.push(message);
            return false;
        }
        
        try {
            const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
            this.socket.send(messageStr);
            return true;
        } catch (error) {
            console.error('❌ Failed to send WebSocket message:', error);
            this.messageQueue.push(message);
            return false;
        }
    }
    
    processMessageQueue() {
        console.log(`📤 Processing ${this.messageQueue.length} queued messages`);
        
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }
    
    handleMessage(message) {
        console.log('📨 Received message:', message);
        
        // Handle system messages
        if (message.type === 'pong') {
            this.handlePong();
            return;
        }
        
        // Call specific handler if registered
        if (this.messageHandlers.has(message.type)) {
            const handler = this.messageHandlers.get(message.type);
            try {
                handler(message);
            } catch (error) {
                console.error(`❌ Error in message handler for ${message.type}:`, error);
            }
        }
        
        // Call general message callback
        if (this.onMessage) {
            this.onMessage(message);
        }
    }
    
    // Register message handler for specific message types
    registerHandler(messageType, handler) {
        this.messageHandlers.set(messageType, handler);
        console.log(`📝 Registered handler for message type: ${messageType}`);
    }
    
    // Unregister message handler
    unregisterHandler(messageType) {
        this.messageHandlers.delete(messageType);
        console.log(`🗑️ Unregistered handler for message type: ${messageType}`);
    }
    
    // Heartbeat mechanism
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'ping', timestamp: Date.now() });
                
                // Set timeout for pong response
                this.heartbeatTimeout = setTimeout(() => {
                    console.warn('⚠️ Heartbeat timeout, connection may be lost');
                    this.socket.close();
                }, 5000);
            }
        }, 30000); // Send ping every 30 seconds
    }
    
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
        
        if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
            this.heartbeatTimeout = null;
        }
    }
    
    handlePong() {
        if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
            this.heartbeatTimeout = null;
        }
    }
    
    // Voice-specific methods
    sendVoiceData(audioBlob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = () => {
                const base64Data = reader.result.split(',')[1]; // Remove data URL prefix
                
                const message = {
                    type: 'voice_data',
                    data: {
                        audio: base64Data,
                        format: 'webm',
                        timestamp: Date.now()
                    }
                };
                
                if (this.send(message)) {
                    resolve();
                } else {
                    reject(new Error('Failed to send voice data'));
                }
            };
            
            reader.onerror = () => {
                reject(new Error('Failed to read audio blob'));
            };
            
            reader.readAsDataURL(audioBlob);
        });
    }
    
    sendTextMessage(text) {
        const message = {
            type: 'text_message',
            data: {
                message: text,
                timestamp: Date.now(),
                language: 'persian'
            }
        };
        
        return this.send(message);
    }
    
    sendSystemCommand(command, params = {}) {
        const message = {
            type: 'system_command',
            data: {
                command: command,
                params: params,
                timestamp: Date.now()
            }
        };
        
        return this.send(message);
    }
    
    // Request system status
    requestSystemStatus() {
        return this.sendSystemCommand('get_status');
    }
    
    // Request available voices
    requestVoices() {
        return this.sendSystemCommand('get_voices');
    }
    
    // Set TTS voice
    setVoice(voiceId) {
        return this.sendSystemCommand('set_voice', { voice_id: voiceId });
    }
    
    // Set wake word sensitivity
    setWakeWordSensitivity(sensitivity) {
        return this.sendSystemCommand('set_wake_word_sensitivity', { sensitivity: sensitivity });
    }
    
    // Get connection info
    getConnectionInfo() {
        return {
            url: this.url,
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            queuedMessages: this.messageQueue.length
        };
    }
    
    // Cleanup
    destroy() {
        console.log('🗑️ Destroying WebSocket client');
        
        this.disconnect();
        this.messageHandlers.clear();
        this.messageQueue = [];
        
        // Clear callbacks
        this.onConnect = null;
        this.onDisconnect = null;
        this.onMessage = null;
        this.onError = null;
        this.onReconnecting = null;
        this.onReconnected = null;
    }
}

// WebSocket Manager for handling multiple connections
class WebSocketManager {
    constructor() {
        this.clients = new Map();
        this.defaultClient = null;
    }
    
    createClient(name = 'default', url = null) {
        if (this.clients.has(name)) {
            console.warn(`⚠️ Client ${name} already exists`);
            return this.clients.get(name);
        }
        
        const client = new HeystiveWebSocketClient(url);
        this.clients.set(name, client);
        
        if (name === 'default' || this.clients.size === 1) {
            this.defaultClient = client;
        }
        
        console.log(`✅ Created WebSocket client: ${name}`);
        return client;
    }
    
    getClient(name = 'default') {
        return this.clients.get(name) || this.defaultClient;
    }
    
    removeClient(name) {
        const client = this.clients.get(name);
        if (client) {
            client.destroy();
            this.clients.delete(name);
            
            if (this.defaultClient === client) {
                this.defaultClient = this.clients.size > 0 ? this.clients.values().next().value : null;
            }
            
            console.log(`🗑️ Removed WebSocket client: ${name}`);
        }
    }
    
    broadcast(message) {
        let sent = 0;
        for (const client of this.clients.values()) {
            if (client.send(message)) {
                sent++;
            }
        }
        return sent;
    }
    
    getStatus() {
        const status = {};
        for (const [name, client] of this.clients) {
            status[name] = client.getConnectionInfo();
        }
        return status;
    }
    
    destroy() {
        for (const client of this.clients.values()) {
            client.destroy();
        }
        this.clients.clear();
        this.defaultClient = null;
    }
}

// Export for global use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { HeystiveWebSocketClient, WebSocketManager };
} else {
    window.HeystiveWebSocketClient = HeystiveWebSocketClient;
    window.WebSocketManager = WebSocketManager;
}