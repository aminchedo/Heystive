/**
 * Voice Recorder Module for Heystive Persian Voice Assistant
 * Handles voice recording, processing, and WebRTC integration
 */

class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioStream = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.isProcessing = false;
        
        // Audio configuration
        this.audioConfig = {
            sampleRate: 44100,
            channels: 1,
            bitDepth: 16,
            format: 'webm;codecs=opus'
        };
        
        // Voice activity detection
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.voiceThreshold = 30;
        this.silenceThreshold = 10;
        this.silenceTimeout = 2000; // 2 seconds of silence
        this.silenceTimer = null;
        
        // Event callbacks
        this.onRecordingStart = null;
        this.onRecordingStop = null;
        this.onVoiceDetected = null;
        this.onSilenceDetected = null;
        this.onVolumeChange = null;
        this.onError = null;
        this.onProcessingComplete = null;
        
        this.init();
    }
    
    async init() {
        try {
            // Check browser support
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('مرورگر شما از ضبط صوت پشتیبانی نمی‌کند');
            }
            
            // Initialize audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            console.log('🎤 Voice Recorder initialized successfully');
        } catch (error) {
            console.error('❌ Voice Recorder initialization failed:', error);
            this.handleError(error);
        }
    }
    
    async requestMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: this.audioConfig.sampleRate,
                    channelCount: this.audioConfig.channels,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // Test and immediately stop
            stream.getTracks().forEach(track => track.stop());
            
            console.log('✅ Microphone permission granted');
            return true;
        } catch (error) {
            console.error('❌ Microphone permission denied:', error);
            this.handleError(new Error('دسترسی به میکروفن مجاز نیست'));
            return false;
        }
    }
    
    async startRecording() {
        if (this.isRecording) {
            console.warn('⚠️ Recording already in progress');
            return;
        }
        
        try {
            // Request microphone access
            this.audioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: this.audioConfig.sampleRate,
                    channelCount: this.audioConfig.channels,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // Setup voice activity detection
            this.setupVoiceActivityDetection();
            
            // Create media recorder
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
                ? 'audio/webm;codecs=opus' 
                : 'audio/webm';
                
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: mimeType
            });
            
            // Setup event handlers
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };
            
            // Start recording
            this.audioChunks = [];
            this.mediaRecorder.start(100); // Collect data every 100ms
            this.isRecording = true;
            
            console.log('🎤 Recording started');
            
            if (this.onRecordingStart) {
                this.onRecordingStart();
            }
            
            // Start silence detection
            this.startSilenceDetection();
            
        } catch (error) {
            console.error('❌ Failed to start recording:', error);
            this.handleError(error);
        }
    }
    
    stopRecording() {
        if (!this.isRecording) {
            console.warn('⚠️ No active recording to stop');
            return;
        }
        
        try {
            // Stop media recorder
            if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                this.mediaRecorder.stop();
            }
            
            // Stop audio stream
            if (this.audioStream) {
                this.audioStream.getTracks().forEach(track => track.stop());
                this.audioStream = null;
            }
            
            // Clear silence timer
            if (this.silenceTimer) {
                clearTimeout(this.silenceTimer);
                this.silenceTimer = null;
            }
            
            this.isRecording = false;
            
            console.log('⏹️ Recording stopped');
            
            if (this.onRecordingStop) {
                this.onRecordingStop();
            }
            
        } catch (error) {
            console.error('❌ Failed to stop recording:', error);
            this.handleError(error);
        }
    }
    
    setupVoiceActivityDetection() {
        if (!this.audioContext || !this.audioStream) return;
        
        try {
            // Create analyser node
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;
            
            // Connect audio stream to analyser
            const source = this.audioContext.createMediaStreamSource(this.audioStream);
            source.connect(this.analyser);
            
            // Create data array for frequency analysis
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            
            // Start monitoring
            this.monitorVoiceActivity();
            
        } catch (error) {
            console.error('❌ Failed to setup voice activity detection:', error);
        }
    }
    
    monitorVoiceActivity() {
        if (!this.isRecording || !this.analyser) return;
        
        // Get frequency data
        this.analyser.getByteFrequencyData(this.dataArray);
        
        // Calculate average volume
        const average = this.dataArray.reduce((sum, value) => sum + value, 0) / this.dataArray.length;
        
        // Emit volume change event
        if (this.onVolumeChange) {
            this.onVolumeChange(average);
        }
        
        // Voice activity detection
        if (average > this.voiceThreshold) {
            // Voice detected
            if (this.onVoiceDetected) {
                this.onVoiceDetected(average);
            }
            
            // Reset silence timer
            if (this.silenceTimer) {
                clearTimeout(this.silenceTimer);
                this.silenceTimer = null;
            }
        } else if (average < this.silenceThreshold) {
            // Silence detected
            if (this.onSilenceDetected) {
                this.onSilenceDetected(average);
            }
        }
        
        // Continue monitoring
        if (this.isRecording) {
            requestAnimationFrame(() => this.monitorVoiceActivity());
        }
    }
    
    startSilenceDetection() {
        // Auto-stop after silence period
        this.silenceTimer = setTimeout(() => {
            if (this.isRecording) {
                console.log('🔇 Auto-stopping due to silence');
                this.stopRecording();
            }
        }, this.silenceTimeout);
    }
    
    async processRecording() {
        if (this.audioChunks.length === 0) {
            console.warn('⚠️ No audio data to process');
            return;
        }
        
        try {
            this.isProcessing = true;
            
            // Create audio blob
            const audioBlob = new Blob(this.audioChunks, { 
                type: this.mediaRecorder.mimeType || 'audio/webm' 
            });
            
            console.log(`🎵 Processing audio: ${audioBlob.size} bytes`);
            
            // Create form data for upload
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            
            // Send to server for processing
            const response = await fetch('/api/voice-process', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log('✅ Voice processing complete:', result);
            
            if (this.onProcessingComplete) {
                this.onProcessingComplete(result);
            }
            
        } catch (error) {
            console.error('❌ Failed to process recording:', error);
            this.handleError(error);
        } finally {
            this.isProcessing = false;
            this.audioChunks = [];
        }
    }
    
    // Get current recording state
    getState() {
        return {
            isRecording: this.isRecording,
            isProcessing: this.isProcessing,
            hasPermission: this.audioStream !== null,
            duration: this.isRecording ? Date.now() - this.recordingStartTime : 0
        };
    }
    
    // Set voice detection thresholds
    setThresholds(voiceThreshold, silenceThreshold) {
        this.voiceThreshold = voiceThreshold || this.voiceThreshold;
        this.silenceThreshold = silenceThreshold || this.silenceThreshold;
        
        console.log(`🔊 Voice thresholds updated: voice=${this.voiceThreshold}, silence=${this.silenceThreshold}`);
    }
    
    // Set silence timeout
    setSilenceTimeout(timeout) {
        this.silenceTimeout = timeout;
        console.log(`⏰ Silence timeout set to ${timeout}ms`);
    }
    
    // Handle errors
    handleError(error) {
        console.error('🚨 Voice Recorder Error:', error);
        
        // Reset state
        this.isRecording = false;
        this.isProcessing = false;
        
        // Stop any active recording
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }
        
        if (this.onError) {
            this.onError(error);
        }
    }
    
    // Cleanup resources
    destroy() {
        this.stopRecording();
        
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        
        console.log('🗑️ Voice Recorder destroyed');
    }
}

// Voice Visualizer Component
class VoiceVisualizer {
    constructor(container, bars = 20) {
        this.container = container;
        this.bars = bars;
        this.barElements = [];
        this.isActive = false;
        this.animationId = null;
        
        this.createBars();
    }
    
    createBars() {
        this.container.innerHTML = '';
        this.barElements = [];
        
        for (let i = 0; i < this.bars; i++) {
            const bar = document.createElement('div');
            bar.className = 'voice-bar';
            bar.style.height = '10px';
            this.container.appendChild(bar);
            this.barElements.push(bar);
        }
    }
    
    updateVisualization(volume) {
        if (!this.isActive) return;
        
        // Convert volume to bar heights
        const normalizedVolume = Math.min(volume / 100, 1);
        
        this.barElements.forEach((bar, index) => {
            // Create wave effect
            const barHeight = Math.random() * normalizedVolume * 40 + 10;
            bar.style.height = `${barHeight}px`;
            
            // Add delay for wave effect
            setTimeout(() => {
                bar.style.height = '10px';
            }, 100 + index * 20);
        });
    }
    
    start() {
        this.isActive = true;
        this.container.classList.add('active');
    }
    
    stop() {
        this.isActive = false;
        this.container.classList.remove('active');
        
        // Reset all bars
        this.barElements.forEach(bar => {
            bar.style.height = '10px';
        });
    }
}

// Export for global use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VoiceRecorder, VoiceVisualizer };
} else {
    window.VoiceRecorder = VoiceRecorder;
    window.VoiceVisualizer = VoiceVisualizer;
}