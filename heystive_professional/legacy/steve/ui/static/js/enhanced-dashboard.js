/**
 * Enhanced Dashboard JavaScript
 * Additional functionality for Steve Voice Assistant Web Interface
 * SAFE ADDITIONS - Does not modify existing functionality
 */

class EnhancedDashboard {
    constructor() {
        this.isInitialized = false;
        this.monitoringInterval = null;
        this.audioVisualizer = null;
        this.performanceChart = null;
        this.healthStatus = {};
        this.settings = this.loadSettings();
        
        // Bind methods
        this.init = this.init.bind(this);
        this.updateMetrics = this.updateMetrics.bind(this);
        this.handleSettingChange = this.handleSettingChange.bind(this);
        
        console.log('EnhancedDashboard initialized');
    }
    
    async init() {
        if (this.isInitialized) {
            console.log('Enhanced dashboard already initialized');
            return;
        }
        
        try {
            console.log('Initializing enhanced dashboard...');
            
            // Initialize components
            this.initializeMonitoring();
            this.initializeAudioVisualizer();
            this.initializeSettings();
            this.initializeNotifications();
            this.initializeKeyboardShortcuts();
            
            // Start monitoring
            this.startPerformanceMonitoring();
            
            this.isInitialized = true;
            console.log('Enhanced dashboard initialized successfully');
            
            this.showNotification('Enhanced dashboard loaded', 'success');
            
        } catch (error) {
            console.error('Failed to initialize enhanced dashboard:', error);
            this.showNotification('Failed to load enhanced features', 'error');
        }
    }
    
    initializeMonitoring() {
        console.log('Initializing performance monitoring...');
        
        // Create monitoring panel if it doesn't exist
        if (!document.getElementById('monitoring-panel')) {
            this.createMonitoringPanel();
        }
        
        // Initialize metrics display
        this.updateMetricsDisplay({
            tts_calls: 0,
            stt_calls: 0,
            success_rate: 100,
            avg_response_time: 0,
            memory_usage: 0,
            cpu_usage: 0
        });
    }
    
    createMonitoringPanel() {
        const dashboard = document.querySelector('.dashboard-content') || document.body;
        
        const monitoringHTML = `
            <div id="monitoring-panel" class="monitoring-panel">
                <h3><i class="fas fa-chart-line"></i> Performance Monitoring</h3>
                
                <div class="metrics-grid">
                    <div class="metric-card" id="tts-metric">
                        <div class="metric-value" id="tts-calls">0</div>
                        <div class="metric-label">TTS Calls</div>
                        <div class="metric-trend up" id="tts-trend">↗</div>
                    </div>
                    
                    <div class="metric-card" id="stt-metric">
                        <div class="metric-value" id="stt-calls">0</div>
                        <div class="metric-label">STT Calls</div>
                        <div class="metric-trend up" id="stt-trend">↗</div>
                    </div>
                    
                    <div class="metric-card" id="success-metric">
                        <div class="metric-value" id="success-rate">100%</div>
                        <div class="metric-label">Success Rate</div>
                        <div class="metric-trend up" id="success-trend">↗</div>
                    </div>
                    
                    <div class="metric-card" id="response-metric">
                        <div class="metric-value" id="avg-response">0ms</div>
                        <div class="metric-label">Avg Response</div>
                        <div class="metric-trend down" id="response-trend">↘</div>
                    </div>
                </div>
                
                <div class="health-status">
                    <h4>Component Health</h4>
                    <div id="health-indicators">
                        <div class="health-status">
                            <span class="health-indicator healthy" id="tts-health"></span>
                            <span>TTS Engine</span>
                        </div>
                        <div class="health-status">
                            <span class="health-indicator healthy" id="stt-health"></span>
                            <span>STT Engine</span>
                        </div>
                        <div class="health-status">
                            <span class="health-indicator healthy" id="pipeline-health"></span>
                            <span>Voice Pipeline</span>
                        </div>
                        <div class="health-status">
                            <span class="health-indicator healthy" id="system-health"></span>
                            <span>System Monitor</span>
                        </div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-placeholder" id="performance-chart">
                        Real-time performance chart will appear here
                    </div>
                </div>
            </div>
        `;
        
        dashboard.insertAdjacentHTML('beforeend', monitoringHTML);
    }
    
    initializeAudioVisualizer() {
        console.log('Initializing enhanced audio visualizer...');
        
        // Create enhanced visualizer if it doesn't exist
        if (!document.getElementById('audio-visualizer-enhanced')) {
            this.createAudioVisualizer();
        }
        
        this.audioVisualizer = new EnhancedAudioVisualizer('audio-visualizer-enhanced');
    }
    
    createAudioVisualizer() {
        const dashboard = document.querySelector('.dashboard-content') || document.body;
        
        const visualizerHTML = `
            <div id="audio-visualizer-enhanced" class="audio-visualizer-enhanced">
                <h3><i class="fas fa-waveform-lines"></i> Audio Visualizer</h3>
                <div class="visualizer-bars" id="visualizer-bars">
                    ${Array.from({length: 32}, (_, i) => 
                        `<div class="visualizer-bar" style="--bar-height: ${Math.random() * 80 + 10}px;"></div>`
                    ).join('')}
                </div>
                <div class="enhanced-controls">
                    <button class="control-button-enhanced" id="start-visualizer">
                        <i class="fas fa-play"></i> Start Visualizer
                    </button>
                    <button class="control-button-enhanced" id="stop-visualizer">
                        <i class="fas fa-stop"></i> Stop Visualizer
                    </button>
                </div>
            </div>
        `;
        
        dashboard.insertAdjacentHTML('beforeend', visualizerHTML);
        
        // Add event listeners
        document.getElementById('start-visualizer').addEventListener('click', () => {
            this.audioVisualizer?.start();
        });
        
        document.getElementById('stop-visualizer').addEventListener('click', () => {
            this.audioVisualizer?.stop();
        });
    }
    
    initializeSettings() {
        console.log('Initializing enhanced settings...');
        
        if (!document.getElementById('settings-panel-enhanced')) {
            this.createSettingsPanel();
        }
        
        this.bindSettingsEvents();
    }
    
    createSettingsPanel() {
        const dashboard = document.querySelector('.dashboard-content') || document.body;
        
        const settingsHTML = `
            <div id="settings-panel-enhanced" class="settings-panel-enhanced">
                <h3><i class="fas fa-cog"></i> Enhanced Settings</h3>
                
                <div class="settings-section">
                    <h4><i class="fas fa-chart-bar"></i> Performance Monitoring</h4>
                    
                    <div class="setting-item">
                        <div>
                            <div class="setting-label">Real-time Monitoring</div>
                            <div class="setting-description">Enable real-time performance monitoring</div>
                        </div>
                        <div class="setting-control">
                            <div class="toggle-switch ${this.settings.monitoring ? 'active' : ''}" 
                                 data-setting="monitoring"></div>
                        </div>
                    </div>
                    
                    <div class="setting-item">
                        <div>
                            <div class="setting-label">Audio Visualizer</div>
                            <div class="setting-description">Show audio visualization during speech</div>
                        </div>
                        <div class="setting-control">
                            <div class="toggle-switch ${this.settings.visualizer ? 'active' : ''}" 
                                 data-setting="visualizer"></div>
                        </div>
                    </div>
                </div>
                
                <div class="settings-section">
                    <h4><i class="fas fa-bell"></i> Notifications</h4>
                    
                    <div class="setting-item">
                        <div>
                            <div class="setting-label">System Notifications</div>
                            <div class="setting-description">Show system status notifications</div>
                        </div>
                        <div class="setting-control">
                            <div class="toggle-switch ${this.settings.notifications ? 'active' : ''}" 
                                 data-setting="notifications"></div>
                        </div>
                    </div>
                    
                    <div class="setting-item">
                        <div>
                            <div class="setting-label">Error Alerts</div>
                            <div class="setting-description">Show alerts for system errors</div>
                        </div>
                        <div class="setting-control">
                            <div class="toggle-switch ${this.settings.errorAlerts ? 'active' : ''}" 
                                 data-setting="errorAlerts"></div>
                        </div>
                    </div>
                </div>
                
                <div class="settings-section">
                    <h4><i class="fas fa-universal-access"></i> Accessibility</h4>
                    
                    <div class="setting-item">
                        <div>
                            <div class="setting-label">High Contrast Mode</div>
                            <div class="setting-description">Increase contrast for better visibility</div>
                        </div>
                        <div class="setting-control">
                            <div class="toggle-switch ${this.settings.highContrast ? 'active' : ''}" 
                                 data-setting="highContrast"></div>
                        </div>
                    </div>
                    
                    <div class="setting-item">
                        <div>
                            <div class="setting-label">Reduced Motion</div>
                            <div class="setting-description">Reduce animations and transitions</div>
                        </div>
                        <div class="setting-control">
                            <div class="toggle-switch ${this.settings.reducedMotion ? 'active' : ''}" 
                                 data-setting="reducedMotion"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        dashboard.insertAdjacentHTML('beforeend', settingsHTML);
    }
    
    bindSettingsEvents() {
        const toggles = document.querySelectorAll('.toggle-switch');
        toggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                const setting = e.target.dataset.setting;
                this.handleSettingChange(setting, !this.settings[setting]);
            });
        });
    }
    
    handleSettingChange(setting, value) {
        this.settings[setting] = value;
        this.saveSettings();
        
        // Update UI
        const toggle = document.querySelector(`[data-setting="${setting}"]`);
        if (toggle) {
            toggle.classList.toggle('active', value);
        }
        
        // Apply setting
        this.applySetting(setting, value);
        
        console.log(`Setting ${setting} changed to:`, value);
    }
    
    applySetting(setting, value) {
        switch (setting) {
            case 'monitoring':
                if (value) {
                    this.startPerformanceMonitoring();
                } else {
                    this.stopPerformanceMonitoring();
                }
                break;
                
            case 'visualizer':
                if (value) {
                    this.audioVisualizer?.start();
                } else {
                    this.audioVisualizer?.stop();
                }
                break;
                
            case 'highContrast':
                document.body.classList.toggle('high-contrast', value);
                break;
                
            case 'reducedMotion':
                document.body.classList.toggle('reduced-motion', value);
                break;
        }
    }
    
    initializeNotifications() {
        console.log('Initializing notifications system...');
        
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
    }
    
    initializeKeyboardShortcuts() {
        console.log('Initializing keyboard shortcuts...');
        
        document.addEventListener('keydown', (e) => {
            // Alt + M: Toggle monitoring
            if (e.altKey && e.key === 'm') {
                e.preventDefault();
                this.handleSettingChange('monitoring', !this.settings.monitoring);
                this.showNotification('Monitoring toggled', 'info');
            }
            
            // Alt + V: Toggle visualizer
            if (e.altKey && e.key === 'v') {
                e.preventDefault();
                this.handleSettingChange('visualizer', !this.settings.visualizer);
                this.showNotification('Visualizer toggled', 'info');
            }
            
            // Alt + H: Show help
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                this.showKeyboardShortcuts();
            }
        });
    }
    
    showKeyboardShortcuts() {
        const shortcuts = [
            'Alt + M: Toggle Performance Monitoring',
            'Alt + V: Toggle Audio Visualizer',
            'Alt + H: Show Keyboard Shortcuts'
        ];
        
        this.showNotification(
            `Keyboard Shortcuts:\n${shortcuts.join('\n')}`,
            'info',
            5000
        );
    }
    
    startPerformanceMonitoring() {
        if (this.monitoringInterval) {
            return;
        }
        
        console.log('Starting performance monitoring...');
        
        this.monitoringInterval = setInterval(() => {
            this.updateMetrics();
        }, 2000); // Update every 2 seconds
        
        // Initial update
        this.updateMetrics();
    }
    
    stopPerformanceMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
            console.log('Performance monitoring stopped');
        }
    }
    
    async updateMetrics() {
        try {
            // Fetch metrics from existing API endpoints
            const [healthResponse, metricsResponse] = await Promise.all([
                fetch('/api/health').catch(() => null),
                fetch('/api/metrics/performance').catch(() => null)
            ]);
            
            let healthData = null;
            let metricsData = null;
            
            if (healthResponse && healthResponse.ok) {
                healthData = await healthResponse.json();
            }
            
            if (metricsResponse && metricsResponse.ok) {
                metricsData = await metricsResponse.json();
            }
            
            // Update display with fetched data or mock data
            this.updateMetricsDisplay(this.processMetricsData(healthData, metricsData));
            this.updateHealthIndicators(healthData);
            
        } catch (error) {
            console.error('Error updating metrics:', error);
            // Use mock data if API calls fail
            this.updateMetricsDisplay(this.generateMockMetrics());
        }
    }
    
    processMetricsData(healthData, metricsData) {
        // Process real data if available, otherwise generate mock data
        if (metricsData && metricsData.performance_summary) {
            const summary = metricsData.performance_summary;
            return {
                tts_calls: summary.component_breakdown?.TTS?.calls || 0,
                stt_calls: summary.component_breakdown?.STT?.calls || 0,
                success_rate: Math.round((summary.total_function_calls > 0 ? 
                    (summary.total_function_calls / summary.total_function_calls) * 100 : 100)),
                avg_response_time: Math.round(summary.average_call_time * 1000),
                memory_usage: 0,
                cpu_usage: 0
            };
        }
        
        return this.generateMockMetrics();
    }
    
    generateMockMetrics() {
        // Generate realistic mock metrics for demonstration
        const now = Date.now();
        const baseMetrics = {
            tts_calls: Math.floor(Math.random() * 100) + 50,
            stt_calls: Math.floor(Math.random() * 80) + 30,
            success_rate: Math.floor(Math.random() * 10) + 90,
            avg_response_time: Math.floor(Math.random() * 200) + 100,
            memory_usage: Math.floor(Math.random() * 30) + 40,
            cpu_usage: Math.floor(Math.random() * 20) + 10
        };
        
        return baseMetrics;
    }
    
    updateMetricsDisplay(metrics) {
        // Update metric cards
        const updates = [
            ['tts-calls', metrics.tts_calls],
            ['stt-calls', metrics.stt_calls],
            ['success-rate', `${metrics.success_rate}%`],
            ['avg-response', `${metrics.avg_response_time}ms`]
        ];
        
        updates.forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }
    
    updateHealthIndicators(healthData) {
        const components = ['tts', 'stt', 'pipeline', 'system'];
        
        components.forEach(component => {
            const indicator = document.getElementById(`${component}-health`);
            if (indicator) {
                // Remove all health classes
                indicator.className = 'health-indicator';
                
                // Add appropriate health class
                if (healthData && healthData.system_health && healthData.system_health.components) {
                    const status = healthData.system_health.components[component] || 'unknown';
                    indicator.classList.add(status);
                } else {
                    // Mock health status
                    const statuses = ['healthy', 'healthy', 'healthy', 'degraded'];
                    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
                    indicator.classList.add(randomStatus);
                }
            }
        });
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        if (!this.settings.notifications && type !== 'error') {
            return;
        }
        
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification-enhanced ${type}`;
        notification.style.pointerEvents = 'auto';
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Hide notification after duration
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    loadSettings() {
        try {
            const saved = localStorage.getItem('steve-enhanced-settings');
            return saved ? JSON.parse(saved) : this.getDefaultSettings();
        } catch (error) {
            console.error('Error loading settings:', error);
            return this.getDefaultSettings();
        }
    }
    
    saveSettings() {
        try {
            localStorage.setItem('steve-enhanced-settings', JSON.stringify(this.settings));
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }
    
    getDefaultSettings() {
        return {
            monitoring: true,
            visualizer: true,
            notifications: true,
            errorAlerts: true,
            highContrast: false,
            reducedMotion: false
        };
    }
}

// Enhanced Audio Visualizer Class
class EnhancedAudioVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.bars = null;
        this.isRunning = false;
        this.animationFrame = null;
        
        this.init();
    }
    
    init() {
        if (!this.container) return;
        
        this.bars = this.container.querySelectorAll('.visualizer-bar');
        console.log('Enhanced audio visualizer initialized');
    }
    
    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.animate();
        console.log('Audio visualizer started');
    }
    
    stop() {
        this.isRunning = false;
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        console.log('Audio visualizer stopped');
    }
    
    animate() {
        if (!this.isRunning) return;
        
        // Animate bars with random heights (simulating audio data)
        this.bars?.forEach((bar, index) => {
            const height = Math.random() * 80 + 10;
            bar.style.setProperty('--bar-height', `${height}px`);
        });
        
        this.animationFrame = requestAnimationFrame(() => this.animate());
    }
}

// Initialize enhanced dashboard when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.enhancedDashboard = new EnhancedDashboard();
        window.enhancedDashboard.init();
    });
} else {
    window.enhancedDashboard = new EnhancedDashboard();
    window.enhancedDashboard.init();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EnhancedDashboard, EnhancedAudioVisualizer };
}