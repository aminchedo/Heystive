#!/usr/bin/env python3
"""
Modern Web Components for Heystive Persian Voice Assistant
=========================================================

This module provides modern web UI components that enhance the existing
web interface without modifying any existing files.

Key Features:
- Material Design 3.0 web components
- Advanced Persian RTL support
- Voice-first interaction patterns
- Progressive Web App (PWA) capabilities
- Real-time audio visualization
- Accessibility improvements (WCAG 2.1 AA)
- Modern CSS Grid and Flexbox layouts
- Dark/light theme support with system preference detection
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ModernWebComponentsGenerator:
    """
    Generator for modern web components that enhance existing web interface
    
    Creates modern HTML, CSS, and JavaScript components that can be integrated
    with existing web applications without modification.
    """
    
    def __init__(self, output_dir: str = "/workspace/enhancements/web_components"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.components = {}
        self.themes = {}
        
        # Initialize component library
        self._initialize_component_library()
        
    def _initialize_component_library(self):
        """Initialize the modern web component library"""
        logger.info("🌐 Initializing Modern Web Components Library...")
        
        # Material Design Persian theme
        self.themes["material_persian"] = {
            "colors": {
                "primary": "#1976D2",
                "primary_variant": "#0D47A1", 
                "secondary": "#FF9800",
                "secondary_variant": "#F57C00",
                "background": "#FAFAFA",
                "surface": "#FFFFFF",
                "error": "#D32F2F",
                "on_primary": "#FFFFFF",
                "on_secondary": "#000000",
                "on_background": "#212121",
                "on_surface": "#212121",
                "persian_turquoise": "#1ABC9C",
                "persian_rose": "#E91E63",
                "persian_saffron": "#FFC107"
            },
            "fonts": {
                "primary": "'Vazirmatn', 'Vazir', 'Sahel', 'Tahoma', Arial, sans-serif",
                "heading": "'Vazirmatn', 'Vazir', 'Sahel', 'Tahoma', Arial, sans-serif",
                "body": "'Vazirmatn', 'Vazir', 'Sahel', 'Tahoma', Arial, sans-serif",
                "mono": "'Vazirmatn Code', 'Courier New', monospace"
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px", 
                "md": "16px",
                "lg": "24px",
                "xl": "32px"
            },
            "borders": {
                "radius": "8px",
                "radius_large": "16px",
                "width": "2px"
            }
        }
        
        logger.info("✅ Modern Web Components Library initialized")
        
    def generate_material_css(self) -> str:
        """Generate Material Design CSS with Persian RTL support"""
        theme = self.themes["material_persian"]
        
        css = f"""
/* Material Design 3.0 Persian RTL Theme */
:root {{
    /* Colors */
    --md-primary: {theme['colors']['primary']};
    --md-primary-variant: {theme['colors']['primary_variant']};
    --md-secondary: {theme['colors']['secondary']};
    --md-secondary-variant: {theme['colors']['secondary_variant']};
    --md-background: {theme['colors']['background']};
    --md-surface: {theme['colors']['surface']};
    --md-error: {theme['colors']['error']};
    --md-on-primary: {theme['colors']['on_primary']};
    --md-on-secondary: {theme['colors']['on_secondary']};
    --md-on-background: {theme['colors']['on_background']};
    --md-on-surface: {theme['colors']['on_surface']};
    --md-persian-turquoise: {theme['colors']['persian_turquoise']};
    --md-persian-rose: {theme['colors']['persian_rose']};
    --md-persian-saffron: {theme['colors']['persian_saffron']};
    
    /* Typography */
    --md-font-primary: {theme['fonts']['primary']};
    --md-font-heading: {theme['fonts']['heading']};
    --md-font-body: {theme['fonts']['body']};
    --md-font-mono: {theme['fonts']['mono']};
    
    /* Spacing */
    --md-spacing-xs: {theme['spacing']['xs']};
    --md-spacing-sm: {theme['spacing']['sm']};
    --md-spacing-md: {theme['spacing']['md']};
    --md-spacing-lg: {theme['spacing']['lg']};
    --md-spacing-xl: {theme['spacing']['xl']};
    
    /* Borders */
    --md-border-radius: {theme['borders']['radius']};
    --md-border-radius-large: {theme['borders']['radius_large']};
    --md-border-width: {theme['borders']['width']};
}}

/* Dark theme support */
@media (prefers-color-scheme: dark) {{
    :root {{
        --md-background: #121212;
        --md-surface: #1E1E1E;
        --md-on-background: #FFFFFF;
        --md-on-surface: #FFFFFF;
    }}
}}

/* Persian RTL Base Styles */
html[dir="rtl"] {{
    direction: rtl;
    text-align: right;
}}

body {{
    font-family: var(--md-font-body);
    background-color: var(--md-background);
    color: var(--md-on-background);
    margin: 0;
    padding: 0;
    line-height: 1.6;
    direction: rtl;
    text-align: right;
}}

/* Material Design Components */

/* Buttons */
.md-button {{
    background-color: var(--md-primary);
    color: var(--md-on-primary);
    border: none;
    border-radius: var(--md-border-radius);
    padding: 12px 24px;
    font-family: var(--md-font-primary);
    font-size: 14px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.25px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
    position: relative;
    overflow: hidden;
    user-select: none;
    outline: none;
}}

.md-button:hover {{
    background-color: var(--md-primary-variant);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
}}

.md-button:active {{
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
}}

.md-button--outlined {{
    background-color: transparent;
    color: var(--md-primary);
    border: var(--md-border-width) solid var(--md-primary);
}}

.md-button--outlined:hover {{
    background-color: rgba(25, 118, 210, 0.08);
}}

.md-button--text {{
    background-color: transparent;
    color: var(--md-primary);
    box-shadow: none;
}}

.md-button--text:hover {{
    background-color: rgba(25, 118, 210, 0.08);
}}

/* Cards */
.md-card {{
    background-color: var(--md-surface);
    color: var(--md-on-surface);
    border-radius: var(--md-border-radius-large);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
    padding: var(--md-spacing-lg);
    margin: var(--md-spacing-md);
    transition: box-shadow 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
}}

.md-card:hover {{
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.16);
}}

.md-card__header {{
    margin-bottom: var(--md-spacing-md);
    padding-bottom: var(--md-spacing-md);
    border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}}

.md-card__title {{
    font-family: var(--md-font-heading);
    font-size: 20px;
    font-weight: 500;
    margin: 0;
    color: var(--md-primary);
}}

.md-card__subtitle {{
    font-size: 14px;
    color: rgba(33, 33, 33, 0.6);
    margin: var(--md-spacing-xs) 0 0 0;
}}

/* Text Fields */
.md-textfield {{
    position: relative;
    margin: var(--md-spacing-md) 0;
}}

.md-textfield__input {{
    width: 100%;
    padding: 16px 12px 8px 12px;
    border: var(--md-border-width) solid rgba(0, 0, 0, 0.38);
    border-radius: var(--md-border-radius);
    font-family: var(--md-font-body);
    font-size: 16px;
    background-color: var(--md-surface);
    color: var(--md-on-surface);
    transition: border-color 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
    outline: none;
    box-sizing: border-box;
}}

.md-textfield__input:focus {{
    border-color: var(--md-primary);
    border-width: 3px;
}}

.md-textfield__label {{
    position: absolute;
    top: 16px;
    right: 12px;
    font-size: 16px;
    color: rgba(33, 33, 33, 0.6);
    transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
    pointer-events: none;
    background-color: var(--md-surface);
    padding: 0 4px;
}}

.md-textfield__input:focus + .md-textfield__label,
.md-textfield__input:not(:placeholder-shown) + .md-textfield__label {{
    top: -8px;
    font-size: 12px;
    color: var(--md-primary);
}}

/* Voice Components */
.md-voice-visualizer {{
    width: 100%;
    height: 200px;
    background-color: var(--md-surface);
    border-radius: var(--md-border-radius);
    border: var(--md-border-width) solid var(--md-primary);
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.md-voice-wave {{
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 2px;
}}

.md-voice-bar {{
    width: 4px;
    background: linear-gradient(to top, var(--md-primary), var(--md-persian-turquoise));
    border-radius: 2px;
    transition: height 0.1s ease;
    min-height: 4px;
}}

.md-voice-status {{
    display: flex;
    align-items: center;
    gap: var(--md-spacing-sm);
    padding: var(--md-spacing-sm) var(--md-spacing-md);
    background-color: var(--md-primary);
    color: var(--md-on-primary);
    border-radius: var(--md-border-radius);
    font-weight: 500;
}}

.md-voice-status__indicator {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: var(--md-persian-saffron);
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
    100% {{ opacity: 1; }}
}}

/* Persian-specific components */
.md-persian-text {{
    direction: rtl;
    text-align: right;
    font-family: var(--md-font-body);
}}

.md-persian-number {{
    direction: ltr;
    display: inline-block;
}}

/* Responsive design */
@media (max-width: 768px) {{
    .md-card {{
        margin: var(--md-spacing-sm);
        padding: var(--md-spacing-md);
    }}
    
    .md-button {{
        padding: 10px 20px;
        font-size: 13px;
    }}
}}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {{
    * {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }}
}}

/* High contrast mode */
@media (prefers-contrast: high) {{
    .md-button {{
        border: 2px solid var(--md-on-primary);
    }}
    
    .md-card {{
        border: 1px solid var(--md-on-surface);
    }}
}}

/* Focus indicators for keyboard navigation */
.md-button:focus-visible,
.md-textfield__input:focus-visible {{
    outline: 3px solid var(--md-persian-saffron);
    outline-offset: 2px;
}}
"""
        
        return css
        
    def generate_voice_components_js(self) -> str:
        """Generate JavaScript for voice interaction components"""
        js = """
/**
 * Modern Voice Components for Heystive Persian Voice Assistant
 * Provides real-time voice visualization and interaction
 */

class PersianVoiceVisualizer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            barCount: 32,
            maxHeight: 150,
            color: '#1976D2',
            gradientColor: '#1ABC9C',
            animationSpeed: 100,
            ...options
        };
        
        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.dataArray = null;
        this.animationId = null;
        this.isActive = false;
        
        this.init();
    }
    
    init() {
        this.createVisualizerElements();
        this.setupAudioContext();
    }
    
    createVisualizerElements() {
        this.container.innerHTML = '';
        this.container.className = 'md-voice-visualizer';
        
        const waveContainer = document.createElement('div');
        waveContainer.className = 'md-voice-wave';
        
        for (let i = 0; i < this.options.barCount; i++) {
            const bar = document.createElement('div');
            bar.className = 'md-voice-bar';
            bar.style.height = '4px';
            waveContainer.appendChild(bar);
        }
        
        this.container.appendChild(waveContainer);
        this.bars = waveContainer.querySelectorAll('.md-voice-bar');
    }
    
    async setupAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;
            
            const bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(bufferLength);
        } catch (error) {
            console.error('Failed to setup audio context:', error);
        }
    }
    
    async startListening() {
        if (this.isActive) return;
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            this.microphone = this.audioContext.createMediaStreamSource(stream);
            this.microphone.connect(this.analyser);
            
            this.isActive = true;
            this.animate();
            
            // Update status
            this.updateStatus('در حال گوش دادن...', 'listening');
            
        } catch (error) {
            console.error('Failed to access microphone:', error);
            this.updateStatus('خطا در دسترسی به میکروفون', 'error');
        }
    }
    
    stopListening() {
        if (!this.isActive) return;
        
        this.isActive = false;
        
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.microphone) {
            this.microphone.disconnect();
            this.microphone = null;
        }
        
        // Reset bars
        this.bars.forEach(bar => {
            bar.style.height = '4px';
        });
        
        this.updateStatus('آماده برای دریافت فرمان', 'ready');
    }
    
    animate() {
        if (!this.isActive) return;
        
        this.analyser.getByteFrequencyData(this.dataArray);
        
        // Update bars based on frequency data
        const step = Math.floor(this.dataArray.length / this.options.barCount);
        
        for (let i = 0; i < this.options.barCount; i++) {
            const value = this.dataArray[i * step];
            const height = (value / 255) * this.options.maxHeight;
            this.bars[i].style.height = `${Math.max(4, height)}px`;
        }
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    updateStatus(message, type) {
        // Find or create status element
        let statusElement = this.container.querySelector('.md-voice-status');
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.className = 'md-voice-status';
            statusElement.innerHTML = `
                <div class="md-voice-status__indicator"></div>
                <span class="md-voice-status__text"></span>
            `;
            this.container.appendChild(statusElement);
        }
        
        const textElement = statusElement.querySelector('.md-voice-status__text');
        const indicator = statusElement.querySelector('.md-voice-status__indicator');
        
        textElement.textContent = message;
        
        // Update indicator color based on status
        const colors = {
            ready: '#4CAF50',
            listening: '#FF5722', 
            processing: '#FF9800',
            speaking: '#2196F3',
            error: '#F44336'
        };
        
        indicator.style.backgroundColor = colors[type] || colors.ready;
    }
}

class PersianVoiceController {
    constructor(options = {}) {
        this.options = {
            apiEndpoint: '/api/voice',
            apiKey: null,
            language: 'fa',
            autoStart: false,
            ...options
        };
        
        this.visualizer = null;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        
        if (this.options.autoStart) {
            this.startListening();
        }
    }
    
    setupEventListeners() {
        // Voice control buttons
        const startBtn = document.getElementById('start-voice-btn');
        const stopBtn = document.getElementById('stop-voice-btn');
        const testBtn = document.getElementById('test-voice-btn');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startListening());
        }
        
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopListening());
        }
        
        if (testBtn) {
            testBtn.addEventListener('click', () => this.testTTS());
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.toggleListening();
            }
            
            if (e.key === 'F1') {
                e.preventDefault();
                this.startListening();
            }
            
            if (e.key === 'F2') {
                e.preventDefault();
                this.stopListening();
            }
        });
    }
    
    async startListening() {
        if (this.isRecording) return;
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };
            
            this.mediaRecorder.start(1000); // Record in 1-second chunks
            this.isRecording = true;
            
            // Start visualizer
            if (this.visualizer) {
                this.visualizer.startListening();
            }
            
            this.updateUI('listening');
            
        } catch (error) {
            console.error('Failed to start recording:', error);
            this.showError('خطا در شروع ضبط صدا');
        }
    }
    
    stopListening() {
        if (!this.isRecording) return;
        
        this.mediaRecorder.stop();
        this.isRecording = false;
        
        // Stop all tracks
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        // Stop visualizer
        if (this.visualizer) {
            this.visualizer.stopListening();
        }
        
        this.updateUI('processing');
    }
    
    toggleListening() {
        if (this.isRecording) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
    
    async processRecording() {
        if (this.audioChunks.length === 0) return;
        
        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('language', this.options.language);
            
            const headers = {};
            if (this.options.apiKey) {
                headers['X-API-Key'] = this.options.apiKey;
            }
            
            const response = await fetch(this.options.apiEndpoint, {
                method: 'POST',
                headers: headers,
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.handleVoiceResponse(result);
            
        } catch (error) {
            console.error('Failed to process recording:', error);
            this.showError('خطا در پردازش صدا');
        }
        
        this.updateUI('ready');
    }
    
    handleVoiceResponse(response) {
        // Display transcription
        const transcriptionEl = document.getElementById('voice-transcription');
        if (transcriptionEl && response.transcription) {
            transcriptionEl.textContent = response.transcription;
        }
        
        // Display response
        const responseEl = document.getElementById('voice-response');
        if (responseEl && response.response) {
            responseEl.textContent = response.response;
        }
        
        // Play TTS audio if available
        if (response.audio) {
            this.playTTSAudio(response.audio);
        }
    }
    
    async playTTSAudio(audioData) {
        try {
            const audio = new Audio();
            
            if (audioData.startsWith('data:')) {
                // Base64 encoded audio
                audio.src = audioData;
            } else {
                // URL to audio file
                audio.src = audioData;
            }
            
            audio.onloadstart = () => this.updateUI('speaking');
            audio.onended = () => this.updateUI('ready');
            audio.onerror = () => this.showError('خطا در پخش صدا');
            
            await audio.play();
            
        } catch (error) {
            console.error('Failed to play TTS audio:', error);
            this.showError('خطا در پخش پاسخ صوتی');
        }
    }
    
    async testTTS() {
        try {
            const testText = 'سلام! من استیو هستم، دستیار صوتی فارسی شما.';
            
            const headers = { 'Content-Type': 'application/json' };
            if (this.options.apiKey) {
                headers['X-API-Key'] = this.options.apiKey;
            }
            
            const response = await fetch('/api/speak', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ 
                    text: testText,
                    language: 'fa'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.audio) {
                this.playTTSAudio(result.audio);
            }
            
        } catch (error) {
            console.error('TTS test failed:', error);
            this.showError('خطا در تست سیستم صوتی');
        }
    }
    
    updateUI(state) {
        const statusMap = {
            ready: { text: 'آماده برای دریافت فرمان', color: '#4CAF50' },
            listening: { text: 'در حال گوش دادن...', color: '#FF5722' },
            processing: { text: 'در حال پردازش...', color: '#FF9800' },
            speaking: { text: 'در حال صحبت...', color: '#2196F3' }
        };
        
        const status = statusMap[state] || statusMap.ready;
        
        // Update status elements
        const statusElements = document.querySelectorAll('.voice-status');
        statusElements.forEach(el => {
            el.textContent = status.text;
            el.style.color = status.color;
        });
        
        // Update button states
        const startBtn = document.getElementById('start-voice-btn');
        const stopBtn = document.getElementById('stop-voice-btn');
        
        if (startBtn && stopBtn) {
            startBtn.disabled = (state === 'listening' || state === 'processing');
            stopBtn.disabled = (state !== 'listening');
        }
    }
    
    showError(message) {
        // Create or update error display
        let errorEl = document.getElementById('voice-error');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.id = 'voice-error';
            errorEl.className = 'md-card';
            errorEl.style.backgroundColor = '#FFEBEE';
            errorEl.style.color = '#C62828';
            errorEl.style.border = '1px solid #E57373';
            document.body.appendChild(errorEl);
        }
        
        errorEl.textContent = message;
        errorEl.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorEl.style.display = 'none';
        }, 5000);
    }
    
    setVisualizer(visualizer) {
        this.visualizer = visualizer;
    }
}

// Persian number formatting utility
function formatPersianNumber(number) {
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    const englishDigits = '0123456789';
    
    return number.toString().replace(/[0-9]/g, (digit) => {
        return persianDigits[englishDigits.indexOf(digit)];
    });
}

// RTL text direction utility
function ensurePersianDirection(element) {
    element.dir = 'rtl';
    element.style.textAlign = 'right';
    element.style.direction = 'rtl';
}

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize voice visualizer if container exists
    const visualizerContainer = document.getElementById('voice-visualizer');
    if (visualizerContainer) {
        const visualizer = new PersianVoiceVisualizer('voice-visualizer');
        
        // Initialize voice controller
        const voiceController = new PersianVoiceController({
            apiKey: document.querySelector('meta[name="api-key"]')?.content
        });
        
        voiceController.setVisualizer(visualizer);
    }
    
    // Ensure Persian direction for all Persian text elements
    document.querySelectorAll('.md-persian-text').forEach(ensurePersianDirection);
    
    // Format Persian numbers
    document.querySelectorAll('.md-persian-number').forEach(el => {
        el.textContent = formatPersianNumber(el.textContent);
    });
});
"""
        
        return js
        
    def generate_enhanced_html_template(self) -> str:
        """Generate enhanced HTML template with modern components"""
        html = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="استیو - دستیار صوتی فارسی پیشرفته">
    <meta name="keywords" content="Persian voice assistant, استیو, دستیار صوتی">
    <meta name="author" content="Heystive Team">
    <meta name="api-key" content="{{ api_key }}">
    
    <title>استیو - دستیار صوتی پیشرفته</title>
    
    <!-- Material Design Persian Theme -->
    <link rel="stylesheet" href="/enhancements/web_components/material_persian.css">
    
    <!-- Persian Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- PWA Manifest -->
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#1976D2">
    
    <!-- Icons -->
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
</head>
<body>
    <!-- Main Application Container -->
    <div id="app" class="app-container">
        
        <!-- Header -->
        <header class="app-header">
            <div class="md-card">
                <div class="md-card__header">
                    <h1 class="md-card__title">🎤 استیو - دستیار صوتی پیشرفته</h1>
                    <p class="md-card__subtitle">Persian Voice Assistant with Modern Interface</p>
                </div>
                
                <!-- Voice Status -->
                <div class="md-voice-status">
                    <div class="md-voice-status__indicator"></div>
                    <span class="voice-status">آماده برای دریافت فرمان</span>
                </div>
            </div>
        </header>
        
        <!-- Main Content -->
        <main class="app-main">
            
            <!-- Voice Control Panel -->
            <section class="voice-control-section">
                <div class="md-card">
                    <div class="md-card__header">
                        <h2 class="md-card__title">کنترل صوتی</h2>
                    </div>
                    
                    <!-- Voice Visualizer -->
                    <div id="voice-visualizer" class="md-voice-visualizer">
                        <!-- Visualizer bars will be generated by JavaScript -->
                    </div>
                    
                    <!-- Control Buttons -->
                    <div class="voice-controls">
                        <button id="start-voice-btn" class="md-button">
                            🎤 شروع گوش دادن
                        </button>
                        <button id="stop-voice-btn" class="md-button md-button--outlined">
                            ⏹️ توقف گوش دادن
                        </button>
                        <button id="test-voice-btn" class="md-button md-button--text">
                            🔊 تست سیستم صوتی
                        </button>
                    </div>
                </div>
            </section>
            
            <!-- Voice Input/Output -->
            <section class="voice-io-section">
                <div class="md-card">
                    <div class="md-card__header">
                        <h2 class="md-card__title">ورودی و خروجی صوتی</h2>
                    </div>
                    
                    <!-- Voice Input Display -->
                    <div class="md-textfield">
                        <textarea id="voice-transcription" class="md-textfield__input md-persian-text" 
                                  placeholder="متن شناسایی شده از صدای شما اینجا نمایش داده می‌شود..." 
                                  readonly rows="3"></textarea>
                        <label class="md-textfield__label">آخرین فرمان دریافتی</label>
                    </div>
                    
                    <!-- Voice Output Display -->
                    <div class="md-textfield">
                        <textarea id="voice-response" class="md-textfield__input md-persian-text" 
                                  placeholder="پاسخ سیستم اینجا نمایش داده می‌شود..." 
                                  readonly rows="3"></textarea>
                        <label class="md-textfield__label">پاسخ سیستم</label>
                    </div>
                </div>
            </section>
            
            <!-- System Status -->
            <section class="system-status-section">
                <div class="md-card">
                    <div class="md-card__header">
                        <h2 class="md-card__title">وضعیت سیستم</h2>
                    </div>
                    
                    <div class="status-grid">
                        <div class="status-item">
                            <span class="status-label">استفاده از پردازنده:</span>
                            <span id="cpu-usage" class="status-value md-persian-number">0%</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">استفاده از حافظه:</span>
                            <span id="memory-usage" class="status-value md-persian-number">0 MB</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">موتور تشخیص صدا:</span>
                            <span id="stt-engine" class="status-value">در حال بارگذاری...</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">موتور تولید صدا:</span>
                            <span id="tts-engine" class="status-value">در حال بارگذاری...</span>
                        </div>
                    </div>
                    
                    <div class="status-actions">
                        <button id="refresh-status-btn" class="md-button md-button--outlined">
                            🔄 بروزرسانی وضعیت
                        </button>
                        <button id="optimize-system-btn" class="md-button md-button--outlined">
                            ⚡ بهینه‌سازی سیستم
                        </button>
                    </div>
                </div>
            </section>
            
            <!-- Settings Panel -->
            <section class="settings-section">
                <div class="md-card">
                    <div class="md-card__header">
                        <h2 class="md-card__title">تنظیمات</h2>
                    </div>
                    
                    <!-- Theme Selection -->
                    <div class="setting-group">
                        <label for="theme-select" class="setting-label">تم رنگی:</label>
                        <select id="theme-select" class="md-textfield__input">
                            <option value="light">روشن</option>
                            <option value="dark">تاریک</option>
                            <option value="auto">خودکار</option>
                        </select>
                    </div>
                    
                    <!-- Voice Settings -->
                    <div class="setting-group">
                        <label for="voice-speed" class="setting-label">سرعت صدا:</label>
                        <input type="range" id="voice-speed" min="50" max="200" value="100" class="setting-slider">
                        <span id="voice-speed-value" class="md-persian-number">100%</span>
                    </div>
                    
                    <div class="setting-group">
                        <label for="voice-volume" class="setting-label">بلندی صدا:</label>
                        <input type="range" id="voice-volume" min="0" max="100" value="80" class="setting-slider">
                        <span id="voice-volume-value" class="md-persian-number">80%</span>
                    </div>
                    
                    <!-- Settings Actions -->
                    <div class="settings-actions">
                        <button id="save-settings-btn" class="md-button">
                            💾 ذخیره تنظیمات
                        </button>
                        <button id="reset-settings-btn" class="md-button md-button--outlined">
                            🔄 بازنشانی تنظیمات
                        </button>
                    </div>
                </div>
            </section>
            
        </main>
        
        <!-- Footer -->
        <footer class="app-footer">
            <div class="md-card">
                <p class="md-persian-text">
                    © 2024 استیو - دستیار صوتی فارسی | 
                    <a href="#help">راهنما</a> | 
                    <a href="#about">درباره ما</a>
                </p>
            </div>
        </footer>
        
    </div>
    
    <!-- Loading Indicator -->
    <div id="loading" class="loading-overlay" style="display: none;">
        <div class="loading-spinner"></div>
        <p class="loading-text md-persian-text">در حال بارگذاری...</p>
    </div>
    
    <!-- Error Display -->
    <div id="voice-error" class="error-display" style="display: none;"></div>
    
    <!-- Scripts -->
    <script src="/enhancements/web_components/voice_components.js"></script>
    <script>
        // Initialize theme based on system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
        
        // Keyboard shortcuts info
        console.log('استیو - کلیدهای میانبر:');
        console.log('Ctrl+Enter: تغییر وضعیت گوش دادن');
        console.log('F1: شروع گوش دادن');
        console.log('F2: توقف گوش دادن');
    </script>
</body>
</html>
"""
        
        return html
        
    def save_components(self):
        """Save all generated components to files"""
        try:
            # Save CSS
            css_content = self.generate_material_css()
            css_path = self.output_dir / "material_persian.css"
            css_path.write_text(css_content, encoding='utf-8')
            
            # Save JavaScript
            js_content = self.generate_voice_components_js()
            js_path = self.output_dir / "voice_components.js"
            js_path.write_text(js_content, encoding='utf-8')
            
            # Save HTML template
            html_content = self.generate_enhanced_html_template()
            html_path = self.output_dir / "enhanced_template.html"
            html_path.write_text(html_content, encoding='utf-8')
            
            logger.info("✅ Modern web components saved successfully")
            
            return {
                "css_file": str(css_path),
                "js_file": str(js_path),
                "html_file": str(html_path),
                "output_dir": str(self.output_dir)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save web components: {e}")
            return None

# Convenience functions
def generate_modern_web_components(output_dir: str = "/workspace/enhancements/web_components") -> Optional[Dict[str, str]]:
    """Generate and save modern web components"""
    generator = ModernWebComponentsGenerator(output_dir)
    return generator.save_components()

def get_component_info() -> Dict[str, Any]:
    """Get information about available web components"""
    return {
        "components": [
            "Material Design Persian Theme CSS",
            "Persian Voice Visualizer",
            "Voice Controller with Recording",
            "RTL-optimized HTML Template",
            "Accessibility Features",
            "Progressive Web App Support"
        ],
        "features": [
            "Real-time voice visualization",
            "Persian RTL layout support",
            "Material Design 3.0 components",
            "Dark/light theme support",
            "Keyboard shortcuts",
            "Mobile responsive design",
            "Accessibility compliance (WCAG 2.1)",
            "Progressive Web App capabilities"
        ],
        "browser_support": [
            "Chrome 90+",
            "Firefox 88+", 
            "Safari 14+",
            "Edge 90+"
        ]
    }