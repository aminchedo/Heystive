/**
 * Main Application JavaScript for Heystive Modern Web Interface
 * Orchestrates all components and handles user interactions
 */

class HeystiveWebApp {
    constructor() {
        // Core components
        this.voiceRecorder = null;
        this.voiceVisualizer = null;
        this.websocketClient = null;
        this.persianUtils = null;
        this.persianFormatter = null;
        
        // UI elements
        this.elements = {};
        
        // Application state
        this.state = {
            isRecording: false,
            isProcessing: false,
            isConnected: false,
            currentVoice: 'default',
            systemStatus: null,
            conversationHistory: [],
            settings: {
                autoRecord: false,
                silenceTimeout: 2000,
                voiceThreshold: 30,
                silenceThreshold: 10
            }
        };
        
        // Initialize application
        this.init();
    }
    
    async init() {
        console.log('🚀 Initializing Heystive Web Application...');
        
        try {
            // Initialize utilities
            this.persianUtils = new PersianUtils();
            this.persianFormatter = new PersianFormatter();
            
            // Initialize DOM elements
            this.initializeElements();
            
            // Initialize components
            await this.initializeComponents();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load settings
            this.loadSettings();
            
            // Initialize UI
            this.initializeUI();
            
            console.log('✅ Heystive Web Application initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize application:', error);
            this.showError('خطا در راه‌اندازی برنامه: ' + error.message);
        }
    }
    
    initializeElements() {
        // Voice control elements
        this.elements.voiceButton = document.getElementById('voice-button');
        this.elements.voiceStatus = document.getElementById('voice-status');
        this.elements.voiceLevel = document.getElementById('voice-level');
        this.elements.voiceVisualizer = document.getElementById('voice-visualizer');
        this.elements.voiceResponse = document.getElementById('voice-response');
        
        // Chat elements
        this.elements.chatContainer = document.getElementById('chat-container');
        this.elements.chatInput = document.getElementById('chat-input');
        this.elements.chatSendButton = document.getElementById('chat-send');
        
        // Status elements
        this.elements.connectionStatus = document.getElementById('connection-status');
        this.elements.systemStatus = document.getElementById('system-status');
        
        // Settings elements
        this.elements.voiceSelect = document.getElementById('voice-select');
        this.elements.thresholdSlider = document.getElementById('threshold-slider');
        this.elements.timeoutSlider = document.getElementById('timeout-slider');
        
        console.log('📋 DOM elements initialized');
    }
    
    async initializeComponents() {
        // Initialize voice recorder
        this.voiceRecorder = new VoiceRecorder();
        
        // Setup voice recorder callbacks
        this.voiceRecorder.onRecordingStart = () => this.handleRecordingStart();
        this.voiceRecorder.onRecordingStop = () => this.handleRecordingStop();
        this.voiceRecorder.onVoiceDetected = (level) => this.handleVoiceDetected(level);
        this.voiceRecorder.onSilenceDetected = (level) => this.handleSilenceDetected(level);
        this.voiceRecorder.onVolumeChange = (level) => this.handleVolumeChange(level);
        this.voiceRecorder.onError = (error) => this.handleVoiceError(error);
        this.voiceRecorder.onProcessingComplete = (result) => this.handleProcessingComplete(result);
        
        // Initialize voice visualizer
        if (this.elements.voiceVisualizer) {
            this.voiceVisualizer = new VoiceVisualizer(this.elements.voiceVisualizer, 20);
        }
        
        // Initialize WebSocket client
        this.websocketClient = new HeystiveWebSocketClient();
        
        // Setup WebSocket callbacks
        this.websocketClient.onConnect = () => this.handleWebSocketConnect();
        this.websocketClient.onDisconnect = () => this.handleWebSocketDisconnect();
        this.websocketClient.onMessage = (message) => this.handleWebSocketMessage(message);
        this.websocketClient.onError = (error) => this.handleWebSocketError(error);
        
        // Register WebSocket message handlers
        this.websocketClient.registerHandler('voice_response', (message) => this.handleVoiceResponse(message));
        this.websocketClient.registerHandler('text_response', (message) => this.handleTextResponse(message));
        this.websocketClient.registerHandler('system_response', (message) => this.handleSystemResponse(message));
        
        // Request microphone permission
        await this.voiceRecorder.requestMicrophonePermission();
        
        console.log('🔧 Components initialized');
    }
    
    setupEventListeners() {
        // Voice button
        if (this.elements.voiceButton) {
            this.elements.voiceButton.addEventListener('click', () => this.toggleRecording());
        }
        
        // Chat input
        if (this.elements.chatInput) {
            this.elements.chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendTextMessage();
                }
            });
            
            // Setup Persian input handler
            new PersianInputHandler(this.elements.chatInput);
        }
        
        // Chat send button
        if (this.elements.chatSendButton) {
            this.elements.chatSendButton.addEventListener('click', () => this.sendTextMessage());
        }
        
        // Voice selection
        if (this.elements.voiceSelect) {
            this.elements.voiceSelect.addEventListener('change', (e) => {
                this.changeVoice(e.target.value);
            });
        }
        
        // Settings sliders
        if (this.elements.thresholdSlider) {
            this.elements.thresholdSlider.addEventListener('input', (e) => {
                this.updateVoiceThreshold(parseInt(e.target.value));
            });
        }
        
        if (this.elements.timeoutSlider) {
            this.elements.timeoutSlider.addEventListener('input', (e) => {
                this.updateSilenceTimeout(parseInt(e.target.value));
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Space bar for voice recording
            if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                this.toggleRecording();
            }
            
            // Escape to stop recording
            if (e.key === 'Escape' && this.state.isRecording) {
                this.stopRecording();
            }
        });
        
        // Page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.state.isRecording) {
                this.stopRecording();
            }
        });
        
        console.log('👂 Event listeners setup complete');
    }
    
    loadSettings() {
        try {
            const savedSettings = localStorage.getItem('heystive-settings');
            if (savedSettings) {
                const settings = JSON.parse(savedSettings);
                this.state.settings = { ...this.state.settings, ...settings };
            }
        } catch (error) {
            console.warn('⚠️ Failed to load settings:', error);
        }
        
        // Apply settings to components
        this.voiceRecorder.setThresholds(
            this.state.settings.voiceThreshold,
            this.state.settings.silenceThreshold
        );
        this.voiceRecorder.setSilenceTimeout(this.state.settings.silenceTimeout);
    }
    
    saveSettings() {
        try {
            localStorage.setItem('heystive-settings', JSON.stringify(this.state.settings));
        } catch (error) {
            console.warn('⚠️ Failed to save settings:', error);
        }
    }
    
    initializeUI() {
        // Update voice button text
        this.updateVoiceButton();
        
        // Update connection status
        this.updateConnectionStatus();
        
        // Load available voices
        this.loadAvailableVoices();
        
        // Request system status
        this.requestSystemStatus();
        
        // Show welcome message
        this.showWelcomeMessage();
        
        // Apply Persian formatting to existing text
        this.applyPersianFormatting();
    }
    
    // Voice Recording Methods
    toggleRecording() {
        if (this.state.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }
    
    async startRecording() {
        if (this.state.isRecording || this.state.isProcessing) return;
        
        try {
            await this.voiceRecorder.startRecording();
        } catch (error) {
            this.showError('خطا در شروع ضبط: ' + error.message);
        }
    }
    
    stopRecording() {
        if (!this.state.isRecording) return;
        
        this.voiceRecorder.stopRecording();
    }
    
    // Voice Event Handlers
    handleRecordingStart() {
        this.state.isRecording = true;
        this.updateVoiceButton();
        this.updateVoiceStatus('در حال ضبط...');
        
        if (this.voiceVisualizer) {
            this.voiceVisualizer.start();
        }
        
        // Add recording animation
        if (this.elements.voiceButton) {
            this.elements.voiceButton.classList.add('recording');
        }
    }
    
    handleRecordingStop() {
        this.state.isRecording = false;
        this.state.isProcessing = true;
        this.updateVoiceButton();
        this.updateVoiceStatus('در حال پردازش...');
        
        if (this.voiceVisualizer) {
            this.voiceVisualizer.stop();
        }
        
        // Add processing animation
        if (this.elements.voiceButton) {
            this.elements.voiceButton.classList.remove('recording');
            this.elements.voiceButton.classList.add('processing');
        }
    }
    
    handleVoiceDetected(level) {
        // Visual feedback for voice detection
        if (this.elements.voiceLevel) {
            this.elements.voiceLevel.style.width = `${Math.min(level * 2, 100)}%`;
        }
    }
    
    handleSilenceDetected(level) {
        // Visual feedback for silence
        if (this.elements.voiceLevel) {
            this.elements.voiceLevel.style.width = `${level}%`;
        }
    }
    
    handleVolumeChange(level) {
        // Update voice visualizer
        if (this.voiceVisualizer) {
            this.voiceVisualizer.updateVisualization(level);
        }
    }
    
    handleVoiceError(error) {
        this.state.isRecording = false;
        this.state.isProcessing = false;
        this.updateVoiceButton();
        this.updateVoiceStatus('خطا در ضبط صوت');
        this.showError('خطا در ضبط صوت: ' + error.message);
    }
    
    handleProcessingComplete(result) {
        this.state.isProcessing = false;
        this.updateVoiceButton();
        this.updateVoiceStatus('آماده برای ضبط');
        
        // Remove processing animation
        if (this.elements.voiceButton) {
            this.elements.voiceButton.classList.remove('processing');
            this.elements.voiceButton.classList.add('success');
            
            setTimeout(() => {
                this.elements.voiceButton.classList.remove('success');
            }, 2000);
        }
        
        // Display result
        if (result.status === 'success') {
            this.displayVoiceResponse(result);
        } else {
            this.showError(result.message || 'خطا در پردازش صوت');
        }
    }
    
    // WebSocket Event Handlers
    handleWebSocketConnect() {
        this.state.isConnected = true;
        this.updateConnectionStatus();
        console.log('🔗 WebSocket connected');
    }
    
    handleWebSocketDisconnect() {
        this.state.isConnected = false;
        this.updateConnectionStatus();
        console.log('🔌 WebSocket disconnected');
    }
    
    handleWebSocketMessage(message) {
        console.log('📨 WebSocket message received:', message);
    }
    
    handleWebSocketError(error) {
        console.error('🚨 WebSocket error:', error);
        this.showError('خطا در ارتباط با سرور');
    }
    
    handleVoiceResponse(message) {
        this.displayVoiceResponse(message.data);
    }
    
    handleTextResponse(message) {
        this.displayTextResponse(message.data);
    }
    
    handleSystemResponse(message) {
        if (message.data.command === 'get_status') {
            this.state.systemStatus = message.data.result;
            this.updateSystemStatus();
        }
    }
    
    // Chat Methods
    async sendTextMessage() {
        const input = this.elements.chatInput;
        if (!input || !input.value.trim()) return;
        
        const message = input.value.trim();
        input.value = '';
        
        // Add user message to chat
        this.addChatMessage(message, 'user');
        
        try {
            // Send via WebSocket if connected
            if (this.state.isConnected) {
                this.websocketClient.sendTextMessage(message);
            } else {
                // Fallback to HTTP API
                const response = await fetch('/api/text-chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const result = await response.json();
                this.displayTextResponse(result);
            }
        } catch (error) {
            console.error('❌ Failed to send text message:', error);
            this.showError('خطا در ارسال پیام');
        }
    }
    
    addChatMessage(message, sender) {
        if (!this.elements.chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `voice-chat-message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = `voice-chat-avatar ${sender === 'user' ? 'user' : 'assistant'}`;
        avatar.textContent = sender === 'user' ? '👤' : '🤖';
        
        const bubble = document.createElement('div');
        bubble.className = 'voice-chat-bubble';
        bubble.textContent = this.persianFormatter.formatForDisplay(message);
        
        const time = document.createElement('div');
        time.className = 'voice-chat-time';
        time.textContent = this.persianUtils.formatTime();
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        bubble.appendChild(time);
        
        this.elements.chatContainer.appendChild(messageDiv);
        this.elements.chatContainer.scrollTop = this.elements.chatContainer.scrollHeight;
        
        // Store in conversation history
        this.state.conversationHistory.push({
            message: message,
            sender: sender,
            timestamp: Date.now()
        });
    }
    
    displayVoiceResponse(result) {
        if (result.response_text) {
            this.addChatMessage(result.response_text, 'assistant');
        }
        
        if (result.audio_url) {
            this.playAudioResponse(result.audio_url);
        }
        
        if (this.elements.voiceResponse) {
            this.elements.voiceResponse.textContent = this.persianFormatter.formatForDisplay(
                result.response_text || 'پاسخ دریافت شد'
            );
        }
    }
    
    displayTextResponse(result) {
        if (result.response) {
            this.addChatMessage(result.response, 'assistant');
        }
        
        if (result.audio_url) {
            this.playAudioResponse(result.audio_url);
        }
    }
    
    playAudioResponse(audioUrl) {
        try {
            const audio = new Audio(audioUrl);
            audio.play().catch(error => {
                console.warn('⚠️ Failed to play audio response:', error);
            });
        } catch (error) {
            console.warn('⚠️ Failed to create audio element:', error);
        }
    }
    
    // UI Update Methods
    updateVoiceButton() {
        if (!this.elements.voiceButton) return;
        
        const button = this.elements.voiceButton;
        const icon = button.querySelector('.voice-button-icon');
        
        if (this.state.isRecording) {
            button.title = 'توقف ضبط (فضا)';
            if (icon) icon.textContent = '⏹️';
        } else if (this.state.isProcessing) {
            button.title = 'در حال پردازش...';
            if (icon) icon.textContent = '⏳';
        } else {
            button.title = 'شروع ضبط صوت (فضا)';
            if (icon) icon.textContent = '🎤';
        }
    }
    
    updateVoiceStatus(status) {
        if (this.elements.voiceStatus) {
            this.elements.voiceStatus.textContent = status;
        }
    }
    
    updateConnectionStatus() {
        if (!this.elements.connectionStatus) return;
        
        const status = this.elements.connectionStatus;
        if (this.state.isConnected) {
            status.textContent = 'متصل';
            status.className = 'badge badge-success';
        } else {
            status.textContent = 'قطع شده';
            status.className = 'badge badge-error';
        }
    }
    
    updateSystemStatus() {
        if (!this.elements.systemStatus || !this.state.systemStatus) return;
        
        const status = this.state.systemStatus;
        const statusText = `CPU: ${status.system?.cpu_usage || 'N/A'} | RAM: ${status.system?.memory_usage || 'N/A'}`;
        this.elements.systemStatus.textContent = statusText;
    }
    
    // Settings Methods
    changeVoice(voiceId) {
        this.state.currentVoice = voiceId;
        this.saveSettings();
        
        if (this.websocketClient.isConnected) {
            this.websocketClient.setVoice(voiceId);
        }
        
        console.log(`🗣️ Voice changed to: ${voiceId}`);
    }
    
    updateVoiceThreshold(threshold) {
        this.state.settings.voiceThreshold = threshold;
        this.voiceRecorder.setThresholds(threshold, this.state.settings.silenceThreshold);
        this.saveSettings();
    }
    
    updateSilenceTimeout(timeout) {
        this.state.settings.silenceTimeout = timeout;
        this.voiceRecorder.setSilenceTimeout(timeout);
        this.saveSettings();
    }
    
    // Utility Methods
    async loadAvailableVoices() {
        try {
            const response = await fetch('/api/voices');
            const result = await response.json();
            
            if (result.status === 'success' && this.elements.voiceSelect) {
                this.elements.voiceSelect.innerHTML = '';
                result.voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.id;
                    option.textContent = voice.name;
                    option.selected = voice.id === this.state.currentVoice;
                    this.elements.voiceSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.warn('⚠️ Failed to load voices:', error);
        }
    }
    
    requestSystemStatus() {
        if (this.websocketClient.isConnected) {
            this.websocketClient.requestSystemStatus();
        } else {
            fetch('/api/system-status')
                .then(response => response.json())
                .then(result => {
                    this.state.systemStatus = result;
                    this.updateSystemStatus();
                })
                .catch(error => console.warn('⚠️ Failed to get system status:', error));
        }
    }
    
    showWelcomeMessage() {
        const greeting = this.persianUtils.getTimeBasedGreeting();
        const welcomeMsg = `${greeting}! من استیو هستم، دستیار صوتی شما. چطور می‌تونم کمکتون کنم؟`;
        
        setTimeout(() => {
            this.addChatMessage(welcomeMsg, 'assistant');
        }, 1000);
    }
    
    applyPersianFormatting() {
        // Apply Persian formatting to all text elements
        document.querySelectorAll('[data-persian]').forEach(element => {
            const text = element.textContent;
            element.textContent = this.persianFormatter.formatForDisplay(text);
        });
        
        // Apply Persian number formatting
        document.querySelectorAll('[data-persian-numbers]').forEach(element => {
            const text = element.textContent;
            element.textContent = this.persianUtils.toPersianDigits(text);
        });
    }
    
    showError(message) {
        console.error('🚨 Application Error:', message);
        
        // Show error in UI (implement based on your UI framework)
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.textContent = message;
        
        // Add to top of page temporarily
        document.body.insertBefore(errorDiv, document.body.firstChild);
        
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
    
    // Cleanup method
    destroy() {
        console.log('🗑️ Destroying Heystive Web Application');
        
        if (this.voiceRecorder) {
            this.voiceRecorder.destroy();
        }
        
        if (this.websocketClient) {
            this.websocketClient.destroy();
        }
        
        this.saveSettings();
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.heystiveApp = new HeystiveWebApp();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.heystiveApp) {
        window.heystiveApp.destroy();
    }
});