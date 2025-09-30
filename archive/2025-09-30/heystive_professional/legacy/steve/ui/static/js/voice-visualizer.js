/**
 * STEVE PERSIAN VOICE ASSISTANT - VOICE VISUALIZER
 * Real-time audio visualization with Persian voice feedback
 * Production-ready with accessibility support
 */

class PersianVoiceVisualizer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container with id "${containerId}" not found`);
        }

        // Configuration
        this.config = {
            width: options.width || 400,
            height: options.height || 400,
            centerX: (options.width || 400) / 2,
            centerY: (options.height || 400) / 2,
            baseRadius: options.baseRadius || 80,
            maxRadius: options.maxRadius || 150,
            colors: {
                idle: ['#3B82F6', '#1E40AF'],
                listening: ['#EF4444', '#DC2626'],
                speaking: ['#10B981', '#059669'],
                processing: ['#F59E0B', '#D97706'],
                error: ['#DC2626', '#B91C1C']
            },
            animation: {
                duration: 300,
                easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
            },
            accessibility: {
                announcements: true,
                visualFeedback: true,
                highContrast: false
            },
            ...options
        };

        // State
        this.state = 'idle'; // idle, listening, speaking, processing, error
        this.amplitude = 0;
        this.frequency = 0;
        this.isAnimating = false;
        this.animationId = null;

        // Audio context for real-time visualization
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.mediaStream = null;

        // Accessibility
        this.announcer = null;
        this.lastAnnouncement = '';

        this.init();
    }

    init() {
        this.createVisualizer();
        this.setupAccessibility();
        this.setupEventListeners();
        this.startAnimation();
        
        console.log('Persian Voice Visualizer initialized');
    }

    createVisualizer() {
        // Create SVG container
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', this.config.width);
        svg.setAttribute('height', this.config.height);
        svg.setAttribute('class', 'voice-visualizer-svg');
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', 'نمایش‌گر وضعیت صوتی');

        // Create gradient definitions
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        this.createGradients(defs);
        svg.appendChild(defs);

        // Main circle (voice indicator)
        this.mainCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        this.mainCircle.setAttribute('cx', this.config.centerX);
        this.mainCircle.setAttribute('cy', this.config.centerY);
        this.mainCircle.setAttribute('r', this.config.baseRadius);
        this.mainCircle.setAttribute('fill', 'url(#gradient-idle)');
        this.mainCircle.setAttribute('class', 'voice-main-circle');
        svg.appendChild(this.mainCircle);

        // Pulse rings
        this.pulseRings = [];
        for (let i = 0; i < 3; i++) {
            const ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            ring.setAttribute('cx', this.config.centerX);
            ring.setAttribute('cy', this.config.centerY);
            ring.setAttribute('r', this.config.baseRadius + (i + 1) * 20);
            ring.setAttribute('fill', 'none');
            ring.setAttribute('stroke', 'url(#gradient-idle)');
            ring.setAttribute('stroke-width', '2');
            ring.setAttribute('opacity', '0');
            ring.setAttribute('class', `voice-pulse-ring pulse-ring-${i}`);
            svg.appendChild(ring);
            this.pulseRings.push(ring);
        }

        // Frequency bars (for speaking visualization)
        this.frequencyBars = [];
        const barCount = 16;
        const angleStep = (2 * Math.PI) / barCount;
        
        for (let i = 0; i < barCount; i++) {
            const angle = i * angleStep;
            const x1 = this.config.centerX + Math.cos(angle) * (this.config.baseRadius + 10);
            const y1 = this.config.centerY + Math.sin(angle) * (this.config.baseRadius + 10);
            const x2 = this.config.centerX + Math.cos(angle) * (this.config.baseRadius + 30);
            const y2 = this.config.centerY + Math.sin(angle) * (this.config.baseRadius + 30);

            const bar = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            bar.setAttribute('x1', x1);
            bar.setAttribute('y1', y1);
            bar.setAttribute('x2', x2);
            bar.setAttribute('y2', y2);
            bar.setAttribute('stroke', 'url(#gradient-speaking)');
            bar.setAttribute('stroke-width', '3');
            bar.setAttribute('opacity', '0');
            bar.setAttribute('class', `frequency-bar bar-${i}`);
            svg.appendChild(bar);
            this.frequencyBars.push(bar);
        }

        // Central icon
        this.iconGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        this.iconGroup.setAttribute('class', 'voice-icon-group');
        this.createIcon('microphone');
        svg.appendChild(this.iconGroup);

        // Status text
        this.statusText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        this.statusText.setAttribute('x', this.config.centerX);
        this.statusText.setAttribute('y', this.config.centerY + this.config.baseRadius + 40);
        this.statusText.setAttribute('text-anchor', 'middle');
        this.statusText.setAttribute('class', 'voice-status-text persian-text');
        this.statusText.setAttribute('fill', '#374151');
        this.statusText.setAttribute('font-size', '18');
        this.statusText.setAttribute('font-weight', '500');
        this.statusText.textContent = 'آماده شنیدن...';
        svg.appendChild(this.statusText);

        this.container.appendChild(svg);
    }

    createGradients(defs) {
        Object.entries(this.config.colors).forEach(([state, colors]) => {
            const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'radialGradient');
            gradient.setAttribute('id', `gradient-${state}`);
            gradient.setAttribute('cx', '50%');
            gradient.setAttribute('cy', '50%');
            gradient.setAttribute('r', '50%');

            const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop1.setAttribute('offset', '0%');
            stop1.setAttribute('stop-color', colors[0]);
            stop1.setAttribute('stop-opacity', '0.9');

            const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop2.setAttribute('offset', '100%');
            stop2.setAttribute('stop-color', colors[1]);
            stop2.setAttribute('stop-opacity', '0.7');

            gradient.appendChild(stop1);
            gradient.appendChild(stop2);
            defs.appendChild(gradient);
        });
    }

    createIcon(iconType) {
        // Clear existing icon
        this.iconGroup.innerHTML = '';

        const iconSize = 40;
        const iconX = this.config.centerX - iconSize / 2;
        const iconY = this.config.centerY - iconSize / 2;

        switch (iconType) {
            case 'microphone':
                this.createMicrophoneIcon(iconX, iconY, iconSize);
                break;
            case 'speaker':
                this.createSpeakerIcon(iconX, iconY, iconSize);
                break;
            case 'processing':
                this.createProcessingIcon(iconX, iconY, iconSize);
                break;
            case 'error':
                this.createErrorIcon(iconX, iconY, iconSize);
                break;
            default:
                this.createMicrophoneIcon(iconX, iconY, iconSize);
        }
    }

    createMicrophoneIcon(x, y, size) {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M12 2a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3Z M19 10v1a7 7 0 0 1-14 0v-1 M12 18.5v2.5 M8 21h8');
        path.setAttribute('stroke', '#FFFFFF');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke-linecap', 'round');
        path.setAttribute('stroke-linejoin', 'round');
        path.setAttribute('transform', `translate(${x}, ${y}) scale(${size / 24})`);
        this.iconGroup.appendChild(path);
    }

    createSpeakerIcon(x, y, size) {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M11 5 6 9H2v6h4l5 4V5Z m5.54 3.46a5 5 0 0 1 0 7.07 M15 12a3 3 0 0 1 0 0');
        path.setAttribute('stroke', '#FFFFFF');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke-linecap', 'round');
        path.setAttribute('stroke-linejoin', 'round');
        path.setAttribute('transform', `translate(${x}, ${y}) scale(${size / 24})`);
        this.iconGroup.appendChild(path);
    }

    createProcessingIcon(x, y, size) {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', x + size / 2);
        circle.setAttribute('cy', y + size / 2);
        circle.setAttribute('r', size / 4);
        circle.setAttribute('stroke', '#FFFFFF');
        circle.setAttribute('stroke-width', '3');
        circle.setAttribute('fill', 'none');
        circle.setAttribute('stroke-dasharray', '15 5');
        circle.setAttribute('class', 'processing-spinner');
        this.iconGroup.appendChild(circle);

        // Add rotation animation
        const animateTransform = document.createElementNS('http://www.w3.org/2000/svg', 'animateTransform');
        animateTransform.setAttribute('attributeName', 'transform');
        animateTransform.setAttribute('attributeType', 'XML');
        animateTransform.setAttribute('type', 'rotate');
        animateTransform.setAttribute('from', `0 ${x + size / 2} ${y + size / 2}`);
        animateTransform.setAttribute('to', `360 ${x + size / 2} ${y + size / 2}`);
        animateTransform.setAttribute('dur', '1s');
        animateTransform.setAttribute('repeatCount', 'indefinite');
        circle.appendChild(animateTransform);
    }

    createErrorIcon(x, y, size) {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M12 2 L22 20 L2 20 Z M12 8 L12 13 M12 16 L12 18');
        path.setAttribute('stroke', '#FFFFFF');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke-linecap', 'round');
        path.setAttribute('stroke-linejoin', 'round');
        path.setAttribute('transform', `translate(${x}, ${y}) scale(${size / 24})`);
        this.iconGroup.appendChild(path);
    }

    setupAccessibility() {
        // Create screen reader announcer
        this.announcer = document.createElement('div');
        this.announcer.setAttribute('aria-live', 'polite');
        this.announcer.setAttribute('aria-atomic', 'true');
        this.announcer.setAttribute('class', 'sr-only');
        this.announcer.id = 'voice-announcer';
        document.body.appendChild(this.announcer);

        // Make visualizer focusable and interactive
        this.container.setAttribute('tabindex', '0');
        this.container.setAttribute('role', 'button');
        this.container.setAttribute('aria-label', 'دکمه کنترل صوتی - برای فعال‌سازی کلیک کنید');
        this.container.setAttribute('aria-describedby', 'voice-announcer');
    }

    setupEventListeners() {
        // Click/touch events
        this.container.addEventListener('click', () => this.handleInteraction());
        this.container.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.handleInteraction();
            }
        });

        // Accessibility events
        this.container.addEventListener('focus', () => {
            this.container.style.outline = '3px solid #3B82F6';
            this.container.style.outlineOffset = '2px';
        });

        this.container.addEventListener('blur', () => {
            this.container.style.outline = 'none';
        });

        // Check for high contrast mode
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            this.config.accessibility.highContrast = true;
            this.applyHighContrastMode();
        }

        // Listen for contrast preference changes
        window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
            this.config.accessibility.highContrast = e.matches;
            if (e.matches) {
                this.applyHighContrastMode();
            } else {
                this.removeHighContrastMode();
            }
        });
    }

    handleInteraction() {
        // Emit custom event for parent components to handle
        const event = new CustomEvent('voiceVisualizerClick', {
            detail: { 
                currentState: this.state,
                visualizer: this 
            }
        });
        this.container.dispatchEvent(event);
    }

    setState(newState, options = {}) {
        if (this.state === newState) return;

        const oldState = this.state;
        this.state = newState;

        // Update visual appearance
        this.updateVisualState(newState, oldState);

        // Update accessibility
        this.announceStateChange(newState, options.message);

        // Update icon
        const iconMap = {
            idle: 'microphone',
            listening: 'microphone',
            speaking: 'speaker',
            processing: 'processing',
            error: 'error'
        };
        this.createIcon(iconMap[newState]);

        console.log(`Voice visualizer state changed: ${oldState} → ${newState}`);
    }

    updateVisualState(newState, oldState) {
        // Update main circle gradient
        this.mainCircle.setAttribute('fill', `url(#gradient-${newState})`);

        // Update pulse rings
        this.pulseRings.forEach((ring, index) => {
            ring.setAttribute('stroke', `url(#gradient-${newState})`);
        });

        // Update frequency bars
        this.frequencyBars.forEach(bar => {
            bar.setAttribute('stroke', `url(#gradient-${newState})`);
        });

        // Update status text
        const statusMessages = {
            idle: 'آماده شنیدن...',
            listening: 'در حال شنیدن...',
            speaking: 'در حال صحبت...',
            processing: 'در حال پردازش...',
            error: 'خطا رخ داده است'
        };
        this.statusText.textContent = statusMessages[newState] || statusMessages.idle;

        // State-specific animations
        this.applyStateAnimations(newState, oldState);
    }

    applyStateAnimations(newState, oldState) {
        // Clear existing animations
        this.clearAnimations();

        switch (newState) {
            case 'listening':
                this.startListeningAnimation();
                break;
            case 'speaking':
                this.startSpeakingAnimation();
                break;
            case 'processing':
                this.startProcessingAnimation();
                break;
            case 'error':
                this.startErrorAnimation();
                break;
            default:
                this.startIdleAnimation();
        }
    }

    startListeningAnimation() {
        // Pulse rings animation
        this.pulseRings.forEach((ring, index) => {
            const animation = ring.animate([
                { opacity: 0, transform: 'scale(1)' },
                { opacity: 0.6, transform: 'scale(1.2)' },
                { opacity: 0, transform: 'scale(1.4)' }
            ], {
                duration: 1500,
                delay: index * 200,
                iterations: Infinity,
                easing: 'ease-out'
            });
            ring.currentAnimation = animation;
        });

        // Main circle pulsing
        this.mainCircle.currentAnimation = this.mainCircle.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(1.1)' },
            { transform: 'scale(1)' }
        ], {
            duration: 1000,
            iterations: Infinity,
            easing: 'ease-in-out'
        });
    }

    startSpeakingAnimation() {
        // Show frequency bars
        this.frequencyBars.forEach((bar, index) => {
            bar.style.opacity = '1';
            
            // Animate bar height based on frequency data
            const animation = bar.animate([
                { strokeWidth: '2', opacity: '0.5' },
                { strokeWidth: '5', opacity: '1' },
                { strokeWidth: '2', opacity: '0.5' }
            ], {
                duration: 200 + Math.random() * 300,
                iterations: Infinity,
                easing: 'ease-in-out',
                delay: index * 50
            });
            bar.currentAnimation = animation;
        });

        // Gentle main circle animation
        this.mainCircle.currentAnimation = this.mainCircle.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(1.05)' },
            { transform: 'scale(1)' }
        ], {
            duration: 800,
            iterations: Infinity,
            easing: 'ease-in-out'
        });
    }

    startProcessingAnimation() {
        // Rotating animation for main circle
        this.mainCircle.currentAnimation = this.mainCircle.animate([
            { transform: 'rotate(0deg)' },
            { transform: 'rotate(360deg)' }
        ], {
            duration: 2000,
            iterations: Infinity,
            easing: 'linear'
        });

        // Subtle pulse rings
        this.pulseRings.forEach((ring, index) => {
            const animation = ring.animate([
                { opacity: 0 },
                { opacity: 0.3 },
                { opacity: 0 }
            ], {
                duration: 2000,
                delay: index * 300,
                iterations: Infinity,
                easing: 'ease-in-out'
            });
            ring.currentAnimation = animation;
        });
    }

    startErrorAnimation() {
        // Shake animation
        this.mainCircle.currentAnimation = this.mainCircle.animate([
            { transform: 'translateX(0)' },
            { transform: 'translateX(-5px)' },
            { transform: 'translateX(5px)' },
            { transform: 'translateX(-5px)' },
            { transform: 'translateX(0)' }
        ], {
            duration: 500,
            iterations: 3,
            easing: 'ease-in-out'
        });

        // Flash effect
        this.pulseRings.forEach(ring => {
            const animation = ring.animate([
                { opacity: 0 },
                { opacity: 0.8 },
                { opacity: 0 }
            ], {
                duration: 200,
                iterations: 3,
                easing: 'ease-in-out'
            });
            ring.currentAnimation = animation;
        });
    }

    startIdleAnimation() {
        // Gentle breathing animation
        this.mainCircle.currentAnimation = this.mainCircle.animate([
            { transform: 'scale(1)', opacity: '0.9' },
            { transform: 'scale(1.02)', opacity: '1' },
            { transform: 'scale(1)', opacity: '0.9' }
        ], {
            duration: 3000,
            iterations: Infinity,
            easing: 'ease-in-out'
        });
    }

    clearAnimations() {
        // Stop all current animations
        [this.mainCircle, ...this.pulseRings, ...this.frequencyBars].forEach(element => {
            if (element.currentAnimation) {
                element.currentAnimation.cancel();
                element.currentAnimation = null;
            }
        });

        // Reset frequency bars
        this.frequencyBars.forEach(bar => {
            bar.style.opacity = '0';
        });
    }

    announceStateChange(state, customMessage) {
        if (!this.config.accessibility.announcements) return;

        const messages = {
            idle: 'دستیار صوتی آماده است',
            listening: 'در حال شنیدن صدای شما',
            speaking: 'دستیار در حال پاسخ دادن است',
            processing: 'در حال پردازش درخواست شما',
            error: 'خطا رخ داده است، لطفاً دوباره تلاش کنید'
        };

        const message = customMessage || messages[state] || messages.idle;
        
        if (message !== this.lastAnnouncement) {
            this.announcer.textContent = message;
            this.lastAnnouncement = message;
        }
    }

    applyHighContrastMode() {
        // Update colors for high contrast
        this.config.colors = {
            idle: ['#0000FF', '#000080'],
            listening: ['#FF0000', '#800000'],
            speaking: ['#008000', '#004000'],
            processing: ['#FFA500', '#FF8C00'],
            error: ['#FF0000', '#800000']
        };

        // Recreate gradients
        const defs = this.container.querySelector('defs');
        defs.innerHTML = '';
        this.createGradients(defs);

        // Update current state
        this.updateVisualState(this.state, this.state);
    }

    removeHighContrastMode() {
        // Restore original colors
        this.config.colors = {
            idle: ['#3B82F6', '#1E40AF'],
            listening: ['#EF4444', '#DC2626'],
            speaking: ['#10B981', '#059669'],
            processing: ['#F59E0B', '#D97706'],
            error: ['#DC2626', '#B91C1C']
        };

        // Recreate gradients
        const defs = this.container.querySelector('defs');
        defs.innerHTML = '';
        this.createGradients(defs);

        // Update current state
        this.updateVisualState(this.state, this.state);
    }

    startAnimation() {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        this.animate();
    }

    stopAnimation() {
        this.isAnimating = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.clearAnimations();
    }

    animate() {
        if (!this.isAnimating) return;

        // Update visualization based on audio data if available
        if (this.analyser && this.dataArray) {
            this.analyser.getByteFrequencyData(this.dataArray);
            this.updateFrequencyVisualization();
        }

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    updateFrequencyVisualization() {
        if (this.state !== 'speaking') return;

        // Update frequency bars based on audio data
        this.frequencyBars.forEach((bar, index) => {
            const dataIndex = Math.floor(index * this.dataArray.length / this.frequencyBars.length);
            const amplitude = this.dataArray[dataIndex] / 255;
            
            // Update bar appearance based on amplitude
            const strokeWidth = 2 + amplitude * 6;
            const opacity = 0.3 + amplitude * 0.7;
            
            bar.setAttribute('stroke-width', strokeWidth);
            bar.setAttribute('opacity', opacity);
        });
    }

    async initializeAudioVisualization() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            source.connect(this.analyser);
            
            this.analyser.fftSize = 64;
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            
            console.log('Audio visualization initialized');
        } catch (error) {
            console.warn('Audio visualization not available:', error);
        }
    }

    destroy() {
        // Stop animations
        this.stopAnimation();

        // Clean up audio context
        if (this.audioContext) {
            this.audioContext.close();
        }

        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }

        // Remove announcer
        if (this.announcer && this.announcer.parentNode) {
            this.announcer.parentNode.removeChild(this.announcer);
        }

        // Clear container
        this.container.innerHTML = '';
        
        console.log('Persian Voice Visualizer destroyed');
    }

    // Public API methods
    setAmplitude(amplitude) {
        this.amplitude = Math.max(0, Math.min(1, amplitude));
    }

    setFrequency(frequency) {
        this.frequency = frequency;
    }

    getState() {
        return this.state;
    }

    isListening() {
        return this.state === 'listening';
    }

    isSpeaking() {
        return this.state === 'speaking';
    }

    isProcessing() {
        return this.state === 'processing';
    }

    hasError() {
        return this.state === 'error';
    }
}

// Export for use in other modules
window.PersianVoiceVisualizer = PersianVoiceVisualizer;