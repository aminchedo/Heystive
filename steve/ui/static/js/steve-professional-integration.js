/**
 * STEVE PERSIAN VOICE ASSISTANT - PROFESSIONAL INTEGRATION
 * Complete integration of all UI/UX components
 * Coordinates voice visualizer, accessibility, error handling, and testing
 */

class SteveProfessionalIntegration {
    constructor() {
        this.components = {
            voiceVisualizer: null,
            accessibilityManager: null,
            errorHandler: null,
            uiTester: null,
            dashboard: null
        };
        
        this.state = {
            initialized: false,
            systemReady: false,
            voiceActive: false,
            currentEngine: 'kamtera_female',
            lastError: null,
            performance: {
                loadTime: 0,
                renderTime: 0,
                memoryUsage: 0
            }
        };
        
        this.config = {
            enableTesting: true,
            enableAccessibility: true,
            enableErrorHandling: true,
            autoInitialize: true,
            debugMode: false,
            persianFirst: true
        };
        
        this.eventHandlers = new Map();
        
        if (this.config.autoInitialize) {
            this.init();
        }
    }
    
    async init() {
        console.log('🚀 Initializing Steve Professional Integration...');
        
        const startTime = performance.now();
        
        try {
            // Initialize in dependency order
            await this.initializeCore();
            await this.initializeComponents();
            await this.setupIntegrations();
            await this.performHealthCheck();
            
            const loadTime = performance.now() - startTime;
            this.state.performance.loadTime = loadTime;
            this.state.initialized = true;
            
            console.log(`✅ Steve Professional Integration initialized in ${loadTime.toFixed(2)}ms`);
            
            // Announce readiness
            this.announceSystemReady();
            
        } catch (error) {
            console.error('❌ Integration initialization failed:', error);
            this.handleInitializationError(error);
        }
    }
    
    async initializeCore() {
        // Set up global error handling first
        if (this.config.enableErrorHandling && window.ErrorHandler) {
            this.components.errorHandler = window.errorHandler || new ErrorHandler();
            console.log('✓ Error Handler initialized');
        }
        
        // Initialize accessibility manager
        if (this.config.enableAccessibility && window.AccessibilityManager) {
            this.components.accessibilityManager = new AccessibilityManager();
            console.log('✓ Accessibility Manager initialized');
        }
        
        // Set up Persian-first configuration
        if (this.config.persianFirst) {
            this.configurePersianFirst();
        }
    }
    
    async initializeComponents() {
        // Initialize voice visualizer
        const visualizerContainer = document.getElementById('voice-visualizer');
        if (visualizerContainer && window.PersianVoiceVisualizer) {
            try {
                this.components.voiceVisualizer = new PersianVoiceVisualizer('voice-visualizer', {
                    width: 320,
                    height: 320,
                    accessibility: {
                        announcements: this.config.enableAccessibility,
                        visualFeedback: true
                    }
                });
                console.log('✓ Voice Visualizer initialized');
            } catch (error) {
                console.error('Voice Visualizer initialization failed:', error);
                this.handleComponentError('voiceVisualizer', error);
            }
        }
        
        // Initialize main dashboard
        if (window.SteveProfessionalDashboard) {
            try {
                this.components.dashboard = window.steveDashboard || new SteveProfessionalDashboard();
                console.log('✓ Professional Dashboard initialized');
            } catch (error) {
                console.error('Dashboard initialization failed:', error);
                this.handleComponentError('dashboard', error);
            }
        }
        
        // Initialize UI testing framework
        if (this.config.enableTesting && window.UITestingFramework) {
            try {
                this.components.uiTester = window.uiTester || new UITestingFramework();
                console.log('✓ UI Testing Framework initialized');
            } catch (error) {
                console.error('UI Testing Framework initialization failed:', error);
                this.handleComponentError('uiTester', error);
            }
        }
    }
    
    async setupIntegrations() {
        // Connect voice visualizer to dashboard
        if (this.components.voiceVisualizer && this.components.dashboard) {
            this.connectVoiceVisualizerToDashboard();
        }
        
        // Connect error handler to all components
        if (this.components.errorHandler) {
            this.connectErrorHandling();
        }
        
        // Connect accessibility manager
        if (this.components.accessibilityManager) {
            this.connectAccessibilityFeatures();
        }
        
        // Set up global event listeners
        this.setupGlobalEventListeners();
        
        // Set up keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Set up performance monitoring
        this.setupPerformanceMonitoring();
    }
    
    connectVoiceVisualizerToDashboard() {
        const visualizer = this.components.voiceVisualizer;
        const dashboard = this.components.dashboard;
        
        // Listen for visualizer events
        document.getElementById('voice-visualizer').addEventListener('voiceVisualizerClick', (e) => {
            dashboard.handleVoiceInteraction();
        });
        
        // Connect state changes
        const originalSetState = dashboard.voiceVisualizer?.setState;
        if (originalSetState) {
            dashboard.voiceVisualizer.setState = (state, options) => {
                originalSetState.call(dashboard.voiceVisualizer, state, options);
                this.state.voiceActive = state === 'listening' || state === 'speaking';
                this.broadcastStateChange('voice', { state, options });
            };
        }
        
        console.log('✓ Voice Visualizer connected to Dashboard');
    }
    
    connectErrorHandling() {
        const errorHandler = this.components.errorHandler;
        
        // Override component error methods to use integrated error handler
        Object.values(this.components).forEach(component => {
            if (component && typeof component.handleError !== 'function') {
                component.handleError = (error, context) => {
                    return errorHandler.handleError(error, context);
                };
            }
        });
        
        // Set up error recovery callbacks
        errorHandler.setRecoveryCallback('voice_engine', () => {
            return this.recoverVoiceEngine();
        });
        
        errorHandler.setRecoveryCallback('network', () => {
            return this.recoverNetworkConnection();
        });
        
        console.log('✓ Error Handling connected');
    }
    
    connectAccessibilityFeatures() {
        const accessibility = this.components.accessibilityManager;
        
        // Connect voice state announcements
        if (this.components.voiceVisualizer) {
            const originalSetState = this.components.voiceVisualizer.setState;
            this.components.voiceVisualizer.setState = (state, options) => {
                originalSetState.call(this.components.voiceVisualizer, state, options);
                accessibility.announceVoiceState(state, options?.message);
            };
        }
        
        // Connect dashboard announcements
        if (this.components.dashboard) {
            this.components.dashboard.announce = (message, priority) => {
                accessibility.announce(message, priority);
            };
        }
        
        console.log('✓ Accessibility Features connected');
    }
    
    setupGlobalEventListeners() {
        // Window events
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        window.addEventListener('online', () => {
            this.handleNetworkReconnection();
        });
        
        window.addEventListener('offline', () => {
            this.handleNetworkDisconnection();
        });
        
        // Visibility change
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });
        
        // Orientation change for mobile
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.handleOrientationChange(), 100);
        });
        
        // Resize for responsive updates
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
        
        console.log('✓ Global Event Listeners set up');
    }
    
    setupKeyboardShortcuts() {
        const shortcuts = {
            'ctrl+space': () => this.toggleVoice(),
            'ctrl+shift+t': () => this.runTests(),
            'ctrl+shift+a': () => this.toggleAccessibilityMode(),
            'ctrl+shift+d': () => this.toggleDebugMode(),
            'ctrl+shift+r': () => this.resetSystem(),
            'ctrl+h': () => this.showHelp(),
            'escape': () => this.handleEscape()
        };
        
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyString(e);
            if (shortcuts[key]) {
                e.preventDefault();
                shortcuts[key]();
            }
        });
        
        console.log('✓ Keyboard Shortcuts set up');
    }
    
    setupPerformanceMonitoring() {
        // Monitor performance metrics
        if (window.PerformanceObserver) {
            // Largest Contentful Paint
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    if (entry.entryType === 'largest-contentful-paint') {
                        this.state.performance.renderTime = entry.startTime;
                    }
                });
            }).observe({ entryTypes: ['largest-contentful-paint'] });
            
            // Memory usage
            if (performance.memory) {
                setInterval(() => {
                    this.state.performance.memoryUsage = performance.memory.usedJSHeapSize;
                }, 5000);
            }
        }
        
        console.log('✓ Performance Monitoring set up');
    }
    
    async performHealthCheck() {
        const healthChecks = [
            () => this.checkComponentHealth(),
            () => this.checkAccessibilityCompliance(),
            () => this.checkPerformanceThresholds(),
            () => this.checkPersianSupport()
        ];
        
        const results = await Promise.all(
            healthChecks.map(check => this.safeExecute(check))
        );
        
        const overallHealth = results.every(result => result.passed);
        this.state.systemReady = overallHealth;
        
        if (!overallHealth) {
            console.warn('⚠️ Health check issues detected:', results.filter(r => !r.passed));
        }
        
        console.log(`✓ Health Check completed: ${overallHealth ? 'HEALTHY' : 'ISSUES DETECTED'}`);
    }
    
    // Health Check Methods
    async checkComponentHealth() {
        const components = Object.entries(this.components);
        const healthyComponents = components.filter(([name, component]) => component !== null);
        
        return {
            passed: healthyComponents.length >= components.length * 0.8, // 80% threshold
            message: `${healthyComponents.length}/${components.length} components healthy`,
            details: { healthy: healthyComponents.length, total: components.length }
        };
    }
    
    async checkAccessibilityCompliance() {
        if (!this.components.accessibilityManager) {
            return { passed: false, message: 'Accessibility Manager not available' };
        }
        
        const report = this.components.accessibilityManager.getAccessibilityReport();
        const score = Object.values(report.config).filter(Boolean).length;
        
        return {
            passed: score >= 4, // Minimum accessibility features
            message: `Accessibility score: ${score}/6`,
            details: report
        };
    }
    
    async checkPerformanceThresholds() {
        const thresholds = {
            loadTime: 3000, // 3 seconds
            renderTime: 1000, // 1 second
            memoryUsage: 50 * 1024 * 1024 // 50MB
        };
        
        const performance = this.state.performance;
        const issues = [];
        
        if (performance.loadTime > thresholds.loadTime) {
            issues.push(`Load time: ${performance.loadTime}ms > ${thresholds.loadTime}ms`);
        }
        
        if (performance.renderTime > thresholds.renderTime) {
            issues.push(`Render time: ${performance.renderTime}ms > ${thresholds.renderTime}ms`);
        }
        
        if (performance.memoryUsage > thresholds.memoryUsage) {
            issues.push(`Memory usage: ${Math.round(performance.memoryUsage / 1024 / 1024)}MB > ${Math.round(thresholds.memoryUsage / 1024 / 1024)}MB`);
        }
        
        return {
            passed: issues.length === 0,
            message: issues.length === 0 ? 'Performance within thresholds' : `Performance issues: ${issues.length}`,
            details: { issues, performance, thresholds }
        };
    }
    
    async checkPersianSupport() {
        const checks = [
            () => document.dir === 'rtl' || document.body.dir === 'rtl',
            () => document.documentElement.lang === 'fa',
            () => getComputedStyle(document.body).fontFamily.toLowerCase().includes('vazir'),
            () => document.querySelector('.persian-text') !== null
        ];
        
        const passed = checks.filter(check => check()).length;
        
        return {
            passed: passed >= 3, // At least 3 out of 4 Persian support features
            message: `Persian support: ${passed}/4 features`,
            details: { passed, total: checks.length }
        };
    }
    
    // Event Handlers
    handleNetworkReconnection() {
        console.log('📡 Network reconnected');
        
        if (this.components.errorHandler) {
            this.components.errorHandler.handleNetworkRecovery();
        }
        
        if (this.components.accessibilityManager) {
            this.components.accessibilityManager.announce('اتصال اینترنت برقرار شد', 'polite');
        }
        
        // Retry failed operations
        this.retryFailedOperations();
    }
    
    handleNetworkDisconnection() {
        console.log('📡 Network disconnected');
        
        if (this.components.errorHandler) {
            this.components.errorHandler.handleNetworkError('اتصال اینترنت قطع شد');
        }
        
        // Switch to offline mode
        this.enableOfflineMode();
    }
    
    handleVisibilityChange() {
        if (document.hidden) {
            // Page hidden - reduce resource usage
            this.pauseNonEssentialOperations();
        } else {
            // Page visible - resume operations
            this.resumeOperations();
        }
    }
    
    handleOrientationChange() {
        console.log('📱 Orientation changed');
        
        // Update responsive layout
        if (this.components.dashboard) {
            this.components.dashboard.updateLayout();
        }
        
        // Recalculate voice visualizer size
        if (this.components.voiceVisualizer) {
            this.components.voiceVisualizer.updateSize();
        }
    }
    
    handleResize() {
        const viewport = { width: window.innerWidth, height: window.innerHeight };
        console.log('📐 Viewport resized:', viewport);
        
        // Update components for new size
        this.updateComponentsForViewport(viewport);
    }
    
    handleInitializationError(error) {
        console.error('Initialization Error:', error);
        
        // Show user-friendly error message
        this.showCriticalError('خطا در راه‌اندازی سیستم', 'لطفاً صفحه را بازنشانی کنید');
        
        // Attempt graceful degradation
        this.enableFallbackMode();
    }
    
    handleComponentError(componentName, error) {
        console.error(`Component Error (${componentName}):`, error);
        
        if (this.components.errorHandler) {
            this.components.errorHandler.handleError(error, {
                component: componentName,
                operation: 'initialization'
            });
        }
        
        // Mark component as failed
        this.components[componentName] = null;
    }
    
    // Action Methods
    toggleVoice() {
        if (this.components.dashboard) {
            this.components.dashboard.handleVoiceInteraction();
        } else if (this.components.voiceVisualizer) {
            // Fallback to direct visualizer control
            const currentState = this.components.voiceVisualizer.getState();
            const newState = currentState === 'idle' ? 'listening' : 'idle';
            this.components.voiceVisualizer.setState(newState);
        }
    }
    
    runTests() {
        if (this.components.uiTester) {
            this.components.uiTester.runAllTests();
        } else {
            console.warn('UI Tester not available');
        }
    }
    
    toggleAccessibilityMode() {
        if (this.components.accessibilityManager) {
            const currentMode = this.components.accessibilityManager.config.highContrast;
            if (currentMode) {
                this.components.accessibilityManager.disableHighContrast();
            } else {
                this.components.accessibilityManager.enableHighContrast();
            }
        }
    }
    
    toggleDebugMode() {
        this.config.debugMode = !this.config.debugMode;
        
        if (this.config.debugMode) {
            console.log('🐛 Debug mode enabled');
            document.body.classList.add('debug-mode');
        } else {
            console.log('🐛 Debug mode disabled');
            document.body.classList.remove('debug-mode');
        }
    }
    
    async resetSystem() {
        console.log('🔄 Resetting system...');
        
        if (this.components.accessibilityManager) {
            this.components.accessibilityManager.announce('در حال بازنشانی سیستم...', 'assertive');
        }
        
        try {
            // Reset all components
            await this.resetComponents();
            
            // Re-initialize
            await this.init();
            
            if (this.components.accessibilityManager) {
                this.components.accessibilityManager.announce('سیستم بازنشانی شد', 'polite');
            }
            
        } catch (error) {
            console.error('Reset failed:', error);
            this.handleComponentError('system', error);
        }
    }
    
    showHelp() {
        const helpContent = `
            <div class="help-content persian-text">
                <h2>راهنمای استفاده از دستیار صوتی استیو</h2>
                
                <h3>کلیدهای میانبر:</h3>
                <ul>
                    <li><kbd>Ctrl + Space</kbd>: فعال/غیرفعال کردن صوت</li>
                    <li><kbd>Ctrl + Shift + T</kbd>: اجرای تست‌های رابط کاربری</li>
                    <li><kbd>Ctrl + Shift + A</kbd>: تغییر حالت دسترسی‌پذیری</li>
                    <li><kbd>Ctrl + H</kbd>: نمایش راهنما</li>
                    <li><kbd>Escape</kbd>: بستن پنجره‌ها</li>
                </ul>
                
                <h3>استفاده از صوت:</h3>
                <ul>
                    <li>روی دایره آبی کلیک کنید تا شنیدن شروع شود</li>
                    <li>"هی استیو" بگویید تا دستیار فعال شود</li>
                    <li>فرمان خود را بگویید</li>
                    <li>منتظر پاسخ دستیار باشید</li>
                </ul>
                
                <h3>انتخاب موتور صوتی:</h3>
                <ul>
                    <li>از پنل سمت راست موتور مناسب را انتخاب کنید</li>
                    <li>دکمه "تست" را برای آزمایش صدا فشار دهید</li>
                    <li>بهترین موتور را بر اساس کیفیت انتخاب کنید</li>
                </ul>
            </div>
        `;
        
        this.showModal('راهنمای استفاده', helpContent);
    }
    
    handleEscape() {
        // Close any open modals or panels
        const modals = document.querySelectorAll('.modal.active, .mobile-modal.active');
        modals.forEach(modal => {
            modal.classList.remove('active');
        });
        
        // Collapse test panel if expanded
        const testPanel = document.getElementById('ui-test-panel');
        if (testPanel && testPanel.classList.contains('expanded')) {
            testPanel.classList.remove('expanded');
        }
    }
    
    // Recovery Methods
    async recoverVoiceEngine() {
        console.log('🔧 Attempting voice engine recovery...');
        
        try {
            // Switch to fallback engine
            if (this.components.dashboard) {
                this.components.dashboard.selectEngine('google_tts');
            }
            
            // Reinitialize voice visualizer
            if (this.components.voiceVisualizer) {
                await this.components.voiceVisualizer.initializeAudioVisualization();
            }
            
            return true;
        } catch (error) {
            console.error('Voice engine recovery failed:', error);
            return false;
        }
    }
    
    async recoverNetworkConnection() {
        console.log('🌐 Attempting network recovery...');
        
        try {
            // Test network connectivity
            const response = await fetch('/api/health', { 
                method: 'HEAD',
                cache: 'no-cache' 
            });
            
            if (response.ok) {
                this.disableOfflineMode();
                return true;
            }
        } catch (error) {
            console.error('Network recovery failed:', error);
        }
        
        return false;
    }
    
    // Utility Methods
    configurePersianFirst() {
        // Set document direction and language
        document.documentElement.dir = 'rtl';
        document.documentElement.lang = 'fa';
        
        // Add Persian-first CSS class
        document.body.classList.add('persian-first');
        
        // Configure number formatting
        if (Intl && Intl.NumberFormat) {
            this.persianNumberFormatter = new Intl.NumberFormat('fa-IR');
        }
        
        console.log('✓ Persian-first configuration applied');
    }
    
    broadcastStateChange(type, data) {
        const event = new CustomEvent('steveStateChange', {
            detail: { type, data, timestamp: Date.now() }
        });
        document.dispatchEvent(event);
    }
    
    safeExecute(fn) {
        return new Promise((resolve) => {
            try {
                const result = fn();
                resolve(Promise.resolve(result));
            } catch (error) {
                resolve({ passed: false, message: error.message, error });
            }
        });
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    getKeyString(e) {
        const parts = [];
        if (e.ctrlKey) parts.push('ctrl');
        if (e.altKey) parts.push('alt');
        if (e.shiftKey) parts.push('shift');
        if (e.metaKey) parts.push('meta');
        parts.push(e.key.toLowerCase());
        return parts.join('+');
    }
    
    showModal(title, content) {
        // Create modal if it doesn't exist
        let modal = document.getElementById('steve-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'steve-modal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-overlay" onclick="this.parentElement.classList.remove('active')"></div>
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 class="modal-title"></h3>
                        <button class="modal-close" onclick="this.closest('.modal').classList.remove('active')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body"></div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        modal.querySelector('.modal-title').textContent = title;
        modal.querySelector('.modal-body').innerHTML = content;
        modal.classList.add('active');
    }
    
    showCriticalError(title, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'critical-error';
        errorDiv.innerHTML = `
            <div class="critical-error-content">
                <h2><i class="fas fa-exclamation-triangle"></i> ${title}</h2>
                <p>${message}</p>
                <button onclick="location.reload()" class="error-action-btn">
                    <i class="fas fa-redo"></i> بازنشانی صفحه
                </button>
            </div>
        `;
        
        document.body.appendChild(errorDiv);
    }
    
    enableOfflineMode() {
        document.body.classList.add('offline-mode');
        console.log('📴 Offline mode enabled');
    }
    
    disableOfflineMode() {
        document.body.classList.remove('offline-mode');
        console.log('📶 Online mode restored');
    }
    
    enableFallbackMode() {
        document.body.classList.add('fallback-mode');
        console.log('⚠️ Fallback mode enabled');
    }
    
    pauseNonEssentialOperations() {
        // Pause animations and timers when page is hidden
        if (this.components.voiceVisualizer) {
            this.components.voiceVisualizer.stopAnimation();
        }
    }
    
    resumeOperations() {
        // Resume operations when page becomes visible
        if (this.components.voiceVisualizer) {
            this.components.voiceVisualizer.startAnimation();
        }
    }
    
    updateComponentsForViewport(viewport) {
        // Update components for new viewport size
        if (this.components.voiceVisualizer) {
            // Adjust visualizer size based on viewport
            const size = viewport.width < 768 ? 200 : 320;
            this.components.voiceVisualizer.updateSize(size, size);
        }
    }
    
    retryFailedOperations() {
        // Retry any operations that failed due to network issues
        console.log('🔄 Retrying failed operations...');
    }
    
    async resetComponents() {
        // Reset all components to initial state
        Object.keys(this.components).forEach(key => {
            if (this.components[key] && typeof this.components[key].destroy === 'function') {
                this.components[key].destroy();
            }
            this.components[key] = null;
        });
    }
    
    announceSystemReady() {
        if (this.components.accessibilityManager) {
            this.components.accessibilityManager.announce(
                'سیستم دستیار صوتی استیو آماده است. برای شروع روی میکروفون کلیک کنید',
                'polite'
            );
        }
        
        // Show ready notification
        setTimeout(() => {
            this.showNotification('سیستم آماده است', 'استیو آماده خدمت‌رسانی به شما است', 'success');
        }, 1000);
    }
    
    showNotification(title, message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <h4>${title}</h4>
                <p>${message}</p>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    cleanup() {
        console.log('🧹 Cleaning up Steve Professional Integration...');
        
        // Clean up all components
        Object.values(this.components).forEach(component => {
            if (component && typeof component.destroy === 'function') {
                component.destroy();
            }
        });
        
        // Remove event listeners
        this.eventHandlers.forEach((handler, event) => {
            document.removeEventListener(event, handler);
        });
        
        console.log('✓ Cleanup completed');
    }
    
    // Public API
    getState() {
        return { ...this.state };
    }
    
    getComponents() {
        return { ...this.components };
    }
    
    isReady() {
        return this.state.initialized && this.state.systemReady;
    }
    
    getPerformanceReport() {
        return {
            ...this.state.performance,
            components: Object.keys(this.components).filter(key => this.components[key] !== null),
            timestamp: Date.now()
        };
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.steveIntegration = new SteveProfessionalIntegration();
});

// Export for module use
window.SteveProfessionalIntegration = SteveProfessionalIntegration;