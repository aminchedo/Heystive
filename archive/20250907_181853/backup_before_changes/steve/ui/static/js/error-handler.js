/**
 * STEVE PERSIAN VOICE ASSISTANT - ERROR HANDLER
 * Advanced error handling and recovery patterns
 * User-friendly error messages in Persian with recovery suggestions
 */

class ErrorHandler {
    constructor() {
        this.errorLog = [];
        this.maxLogSize = 100;
        this.retryAttempts = new Map();
        this.maxRetries = 3;
        this.errorPatterns = new Map();
        this.recoveryStrategies = new Map();
        
        this.init();
    }
    
    init() {
        this.setupErrorPatterns();
        this.setupRecoveryStrategies();
        this.setupGlobalErrorHandlers();
        this.createErrorUI();
        
        console.log('Error Handler initialized');
    }
    
    setupErrorPatterns() {
        // Define error patterns and their classifications
        this.errorPatterns.set('network', {
            patterns: [
                /fetch.*failed/i,
                /network.*error/i,
                /connection.*refused/i,
                /timeout/i,
                /cors/i
            ],
            severity: 'medium',
            category: 'network',
            persianMessage: 'خطا در ارتباط با سرور',
            recoverable: true
        });
        
        this.errorPatterns.set('audio', {
            patterns: [
                /audio.*error/i,
                /microphone.*not.*found/i,
                /permission.*denied.*audio/i,
                /web.*audio.*context/i,
                /media.*stream/i
            ],
            severity: 'high',
            category: 'audio',
            persianMessage: 'خطا در سیستم صوتی',
            recoverable: true
        });
        
        this.errorPatterns.set('voice_engine', {
            patterns: [
                /tts.*error/i,
                /stt.*error/i,
                /engine.*not.*found/i,
                /voice.*synthesis.*failed/i,
                /speech.*recognition.*error/i
            ],
            severity: 'high',
            category: 'voice_engine',
            persianMessage: 'خطا در موتور صوتی',
            recoverable: true
        });
        
        this.errorPatterns.set('permission', {
            patterns: [
                /permission.*denied/i,
                /not.*allowed/i,
                /access.*denied/i,
                /unauthorized/i
            ],
            severity: 'high',
            category: 'permission',
            persianMessage: 'عدم دسترسی لازم',
            recoverable: true
        });
        
        this.errorPatterns.set('system', {
            patterns: [
                /out.*of.*memory/i,
                /system.*error/i,
                /internal.*error/i,
                /500/,
                /503/
            ],
            severity: 'critical',
            category: 'system',
            persianMessage: 'خطای سیستمی',
            recoverable: false
        });
        
        this.errorPatterns.set('validation', {
            patterns: [
                /validation.*error/i,
                /invalid.*input/i,
                /bad.*request/i,
                /400/
            ],
            severity: 'low',
            category: 'validation',
            persianMessage: 'خطا در اعتبارسنجی داده‌ها',
            recoverable: true
        });
    }
    
    setupRecoveryStrategies() {
        // Define recovery strategies for different error types
        this.recoveryStrategies.set('network', {
            immediate: [
                () => this.checkNetworkConnection(),
                () => this.retryWithBackoff()
            ],
            delayed: [
                () => this.switchToOfflineMode(),
                () => this.cacheLastKnownGoodState()
            ],
            manual: [
                () => this.showNetworkTroubleshooting()
            ]
        });
        
        this.recoveryStrategies.set('audio', {
            immediate: [
                () => this.requestAudioPermission(),
                () => this.reinitializeAudioContext()
            ],
            delayed: [
                () => this.switchToTextMode(),
                () => this.showAudioSetupGuide()
            ],
            manual: [
                () => this.showAudioTroubleshooting()
            ]
        });
        
        this.recoveryStrategies.set('voice_engine', {
            immediate: [
                () => this.switchToFallbackEngine(),
                () => this.reinitializeVoiceEngine()
            ],
            delayed: [
                () => this.downloadAlternativeEngine(),
                () => this.resetVoiceConfiguration()
            ],
            manual: [
                () => this.showEngineSelectionPanel()
            ]
        });
        
        this.recoveryStrategies.set('permission', {
            immediate: [
                () => this.requestPermissions()
            ],
            delayed: [
                () => this.showPermissionGuide()
            ],
            manual: [
                () => this.showBrowserSettingsGuide()
            ]
        });
        
        this.recoveryStrategies.set('system', {
            immediate: [
                () => this.clearCache(),
                () => this.reduceSystemLoad()
            ],
            delayed: [
                () => this.suggestPageRefresh(),
                () => this.enableLowResourceMode()
            ],
            manual: [
                () => this.showSystemRequirements()
            ]
        });
    }
    
    setupGlobalErrorHandlers() {
        // Global error handler
        window.addEventListener('error', (e) => {
            this.handleGlobalError(e.error, e.filename, e.lineno, e.colno);
        });
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (e) => {
            this.handlePromiseRejection(e.reason);
        });
        
        // Network error handler
        window.addEventListener('offline', () => {
            this.handleNetworkError('شما آفلاین هستید');
        });
        
        window.addEventListener('online', () => {
            this.handleNetworkRecovery();
        });
    }
    
    createErrorUI() {
        // Create error notification container
        this.errorContainer = document.createElement('div');
        this.errorContainer.id = 'error-container';
        this.errorContainer.className = 'error-container';
        this.errorContainer.setAttribute('aria-live', 'assertive');
        this.errorContainer.setAttribute('aria-atomic', 'true');
        
        // Add error container styles
        const style = document.createElement('style');
        style.textContent = `
            .error-container {
                position: fixed;
                top: var(--space-4);
                right: var(--space-4);
                z-index: var(--z-toast);
                max-width: 400px;
                pointer-events: none;
            }
            
            .error-notification {
                background: var(--color-accent-100);
                color: var(--color-accent-900);
                padding: var(--space-4);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-xl);
                margin-bottom: var(--space-2);
                border: 2px solid var(--color-accent);
                pointer-events: auto;
                animation: slideInRight 0.3s ease-out;
                direction: rtl;
                text-align: right;
            }
            
            .error-notification.warning {
                background: var(--color-warning-100);
                color: var(--color-warning-900);
                border-color: var(--color-warning);
            }
            
            .error-notification.info {
                background: var(--color-primary-100);
                color: var(--color-primary-900);
                border-color: var(--color-primary);
            }
            
            .error-notification.success {
                background: var(--color-secondary-100);
                color: var(--color-secondary-900);
                border-color: var(--color-secondary);
            }
            
            .error-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: var(--space-2);
            }
            
            .error-title {
                font-weight: 600;
                font-size: var(--text-base);
                display: flex;
                align-items: center;
                gap: var(--space-2);
            }
            
            .error-close {
                background: none;
                border: none;
                font-size: var(--text-lg);
                cursor: pointer;
                color: inherit;
                opacity: 0.7;
                padding: var(--space-1);
                border-radius: var(--radius-sm);
            }
            
            .error-close:hover {
                opacity: 1;
                background: rgba(0, 0, 0, 0.1);
            }
            
            .error-message {
                margin-bottom: var(--space-3);
                line-height: var(--leading-relaxed);
            }
            
            .error-actions {
                display: flex;
                gap: var(--space-2);
                flex-wrap: wrap;
            }
            
            .error-action-btn {
                background: currentColor;
                color: var(--bg-primary);
                border: none;
                padding: var(--space-2) var(--space-3);
                border-radius: var(--radius-md);
                font-size: var(--text-sm);
                font-weight: 500;
                cursor: pointer;
                transition: all var(--duration-normal);
                opacity: 0.9;
            }
            
            .error-action-btn:hover {
                opacity: 1;
                transform: translateY(-1px);
            }
            
            .error-action-btn.secondary {
                background: transparent;
                color: currentColor;
                border: 1px solid currentColor;
            }
            
            .error-details {
                margin-top: var(--space-3);
                padding: var(--space-3);
                background: rgba(0, 0, 0, 0.1);
                border-radius: var(--radius-md);
                font-size: var(--text-sm);
                font-family: var(--font-mono);
            }
            
            .error-details summary {
                cursor: pointer;
                font-weight: 500;
                margin-bottom: var(--space-2);
            }
            
            .error-recovery-progress {
                margin-top: var(--space-3);
            }
            
            .error-recovery-step {
                display: flex;
                align-items: center;
                gap: var(--space-2);
                margin-bottom: var(--space-1);
                font-size: var(--text-sm);
            }
            
            .error-recovery-step.completed {
                color: var(--color-secondary);
            }
            
            .error-recovery-step.failed {
                color: var(--color-accent);
            }
            
            .error-recovery-step.pending {
                color: var(--text-muted);
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            
            .error-notification.removing {
                animation: slideOutRight 0.3s ease-in forwards;
            }
            
            /* Mobile styles */
            @media (max-width: 768px) {
                .error-container {
                    top: var(--space-2);
                    right: var(--space-2);
                    left: var(--space-2);
                    max-width: none;
                }
                
                .error-notification {
                    padding: var(--space-3);
                }
                
                .error-actions {
                    justify-content: center;
                }
                
                .error-action-btn {
                    flex: 1;
                    min-width: 80px;
                }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(this.errorContainer);
    }
    
    // Public API methods
    handleError(error, context = {}) {
        console.error('Error handled:', error, context);
        
        const errorInfo = this.classifyError(error);
        const errorId = this.generateErrorId();
        
        // Log error
        this.logError({
            id: errorId,
            error,
            context,
            classification: errorInfo,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href
        });
        
        // Show error notification
        this.showErrorNotification(errorInfo, errorId, context);
        
        // Attempt automatic recovery
        this.attemptRecovery(errorInfo, errorId, context);
        
        return errorId;
    }
    
    classifyError(error) {
        const errorString = error.toString().toLowerCase();
        
        for (const [type, pattern] of this.errorPatterns) {
            if (pattern.patterns.some(regex => regex.test(errorString))) {
                return {
                    type,
                    ...pattern,
                    originalError: error
                };
            }
        }
        
        // Default classification
        return {
            type: 'unknown',
            severity: 'medium',
            category: 'unknown',
            persianMessage: 'خطای نامشخص',
            recoverable: false,
            originalError: error
        };
    }
    
    showErrorNotification(errorInfo, errorId, context) {
        const notification = document.createElement('div');
        notification.className = `error-notification ${errorInfo.severity}`;
        notification.id = `error-${errorId}`;
        
        const icon = this.getErrorIcon(errorInfo.severity);
        const actions = this.getErrorActions(errorInfo, errorId, context);
        
        notification.innerHTML = `
            <div class="error-header">
                <div class="error-title">
                    <i class="${icon}" aria-hidden="true"></i>
                    <span>${errorInfo.persianMessage}</span>
                </div>
                <button class="error-close" onclick="this.closest('.error-notification').remove()" aria-label="بستن">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="error-message">
                ${this.getDetailedErrorMessage(errorInfo, context)}
            </div>
            ${actions.length > 0 ? `<div class="error-actions">${actions.join('')}</div>` : ''}
            ${this.shouldShowDetails(errorInfo) ? this.createErrorDetails(errorInfo, errorId) : ''}
        `;
        
        this.errorContainer.appendChild(notification);
        
        // Auto-remove after delay (except for critical errors)
        if (errorInfo.severity !== 'critical') {
            setTimeout(() => {
                this.removeNotification(notification);
            }, this.getNotificationDuration(errorInfo.severity));
        }
        
        // Announce error for screen readers
        if (window.accessibilityManager) {
            window.accessibilityManager.announce(
                `${errorInfo.persianMessage}. ${this.getDetailedErrorMessage(errorInfo, context)}`,
                'assertive'
            );
        }
    }
    
    getErrorIcon(severity) {
        const icons = {
            low: 'fas fa-info-circle',
            medium: 'fas fa-exclamation-triangle',
            high: 'fas fa-exclamation-circle',
            critical: 'fas fa-skull-crossbones'
        };
        return icons[severity] || 'fas fa-exclamation-triangle';
    }
    
    getDetailedErrorMessage(errorInfo, context) {
        const messages = {
            network: 'ارتباط با سرور برقرار نشد. لطفاً اتصال اینترنت خود را بررسی کنید.',
            audio: 'دسترسی به میکروفن یا سیستم صوتی امکان‌پذیر نیست. لطفاً مجوزهای مرورگر را بررسی کنید.',
            voice_engine: 'موتور صوتی دچار مشکل شده است. در حال تلاش برای تعویض به موتور جایگزین...',
            permission: 'دسترسی لازم برای عملکرد صحیح وجود ندارد. لطفاً مجوزهای مرورگر را بررسی کنید.',
            system: 'خطای سیستمی رخ داده است. لطفاً صفحه را بازنشانی کنید.',
            validation: 'اطلاعات ورودی نامعتبر است. لطفاً دوباره تلاش کنید.',
            unknown: 'خطای غیرمنتظره‌ای رخ داده است.'
        };
        
        let message = messages[errorInfo.category] || messages.unknown;
        
        // Add context-specific information
        if (context.operation) {
            message += ` (در حین ${context.operation})`;
        }
        
        return message;
    }
    
    getErrorActions(errorInfo, errorId, context) {
        const actions = [];
        
        if (errorInfo.recoverable) {
            actions.push(`
                <button class="error-action-btn" onclick="errorHandler.retryOperation('${errorId}', ${JSON.stringify(context).replace(/"/g, '&quot;')})">
                    <i class="fas fa-redo"></i> تلاش مجدد
                </button>
            `);
        }
        
        // Category-specific actions
        switch (errorInfo.category) {
            case 'network':
                actions.push(`
                    <button class="error-action-btn secondary" onclick="errorHandler.showNetworkTroubleshooting()">
                        <i class="fas fa-wifi"></i> راهنمای شبکه
                    </button>
                `);
                break;
                
            case 'audio':
                actions.push(`
                    <button class="error-action-btn secondary" onclick="errorHandler.showAudioSetupGuide()">
                        <i class="fas fa-microphone"></i> راهنمای صوت
                    </button>
                `);
                break;
                
            case 'voice_engine':
                actions.push(`
                    <button class="error-action-btn secondary" onclick="errorHandler.showEngineSelectionPanel()">
                        <i class="fas fa-cogs"></i> تغییر موتور
                    </button>
                `);
                break;
                
            case 'permission':
                actions.push(`
                    <button class="error-action-btn secondary" onclick="errorHandler.showPermissionGuide()">
                        <i class="fas fa-shield-alt"></i> راهنمای مجوزها
                    </button>
                `);
                break;
        }
        
        return actions;
    }
    
    createErrorDetails(errorInfo, errorId) {
        return `
            <details class="error-details">
                <summary>جزئیات فنی</summary>
                <div>
                    <strong>شناسه خطا:</strong> ${errorId}<br>
                    <strong>نوع:</strong> ${errorInfo.type}<br>
                    <strong>دسته‌بندی:</strong> ${errorInfo.category}<br>
                    <strong>زمان:</strong> ${new Date().toLocaleString('fa-IR')}<br>
                    <strong>پیام اصلی:</strong> ${errorInfo.originalError.message || errorInfo.originalError.toString()}
                </div>
            </details>
        `;
    }
    
    shouldShowDetails(errorInfo) {
        return errorInfo.severity === 'critical' || errorInfo.category === 'system';
    }
    
    getNotificationDuration(severity) {
        const durations = {
            low: 3000,
            medium: 5000,
            high: 8000,
            critical: 0 // Don't auto-remove
        };
        return durations[severity] || 5000;
    }
    
    async attemptRecovery(errorInfo, errorId, context) {
        if (!errorInfo.recoverable) return;
        
        const strategies = this.recoveryStrategies.get(errorInfo.category);
        if (!strategies) return;
        
        // Show recovery progress
        this.showRecoveryProgress(errorId);
        
        try {
            // Try immediate recovery strategies
            for (const strategy of strategies.immediate) {
                const success = await this.executeRecoveryStrategy(strategy, errorId);
                if (success) {
                    this.showRecoverySuccess(errorId);
                    return;
                }
            }
            
            // Try delayed recovery strategies
            setTimeout(async () => {
                for (const strategy of strategies.delayed) {
                    const success = await this.executeRecoveryStrategy(strategy, errorId);
                    if (success) {
                        this.showRecoverySuccess(errorId);
                        return;
                    }
                }
                
                // Show manual recovery options
                this.showManualRecoveryOptions(strategies.manual, errorId);
            }, 2000);
            
        } catch (recoveryError) {
            console.error('Recovery failed:', recoveryError);
            this.showRecoveryFailure(errorId);
        }
    }
    
    async executeRecoveryStrategy(strategy, errorId) {
        try {
            this.updateRecoveryProgress(errorId, strategy.name, 'pending');
            const result = await strategy();
            this.updateRecoveryProgress(errorId, strategy.name, result ? 'completed' : 'failed');
            return result;
        } catch (error) {
            this.updateRecoveryProgress(errorId, strategy.name, 'failed');
            return false;
        }
    }
    
    showRecoveryProgress(errorId) {
        const notification = document.getElementById(`error-${errorId}`);
        if (!notification) return;
        
        const progressDiv = document.createElement('div');
        progressDiv.className = 'error-recovery-progress';
        progressDiv.innerHTML = `
            <div style="font-weight: 500; margin-bottom: var(--space-2);">
                <i class="fas fa-cog fa-spin"></i> در حال تلاش برای بازیابی...
            </div>
            <div id="recovery-steps-${errorId}"></div>
        `;
        
        notification.appendChild(progressDiv);
    }
    
    updateRecoveryProgress(errorId, stepName, status) {
        const stepsContainer = document.getElementById(`recovery-steps-${errorId}`);
        if (!stepsContainer) return;
        
        const step = document.createElement('div');
        step.className = `error-recovery-step ${status}`;
        
        const icon = {
            pending: 'fas fa-clock',
            completed: 'fas fa-check',
            failed: 'fas fa-times'
        }[status] || 'fas fa-clock';
        
        step.innerHTML = `
            <i class="${icon}"></i>
            <span>${stepName}</span>
        `;
        
        stepsContainer.appendChild(step);
    }
    
    showRecoverySuccess(errorId) {
        const notification = document.getElementById(`error-${errorId}`);
        if (!notification) return;
        
        notification.className = 'error-notification success';
        notification.querySelector('.error-title span').textContent = 'مشکل برطرف شد';
        notification.querySelector('.error-message').textContent = 'سیستم با موفقیت بازیابی شد و آماده استفاده است.';
        
        setTimeout(() => {
            this.removeNotification(notification);
        }, 3000);
    }
    
    showRecoveryFailure(errorId) {
        const notification = document.getElementById(`error-${errorId}`);
        if (!notification) return;
        
        const progressDiv = notification.querySelector('.error-recovery-progress');
        if (progressDiv) {
            progressDiv.innerHTML = `
                <div style="color: var(--color-accent); font-weight: 500;">
                    <i class="fas fa-exclamation-triangle"></i> بازیابی خودکار ناموفق بود
                </div>
            `;
        }
    }
    
    showManualRecoveryOptions(strategies, errorId) {
        const notification = document.getElementById(`error-${errorId}`);
        if (!notification) return;
        
        const actionsDiv = notification.querySelector('.error-actions');
        if (actionsDiv) {
            actionsDiv.innerHTML += strategies.map(strategy => `
                <button class="error-action-btn secondary" onclick="errorHandler.executeManualRecovery('${strategy.name}', '${errorId}')">
                    ${strategy.name}
                </button>
            `).join('');
        }
    }
    
    // Recovery strategy implementations
    async checkNetworkConnection() {
        try {
            const response = await fetch('/api/health', { 
                method: 'HEAD',
                cache: 'no-cache'
            });
            return response.ok;
        } catch {
            return false;
        }
    }
    
    async retryWithBackoff() {
        // Implement exponential backoff retry logic
        return new Promise(resolve => {
            setTimeout(() => resolve(true), 1000);
        });
    }
    
    async requestAudioPermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
            return true;
        } catch {
            return false;
        }
    }
    
    async reinitializeAudioContext() {
        try {
            if (window.voiceVisualizer) {
                await window.voiceVisualizer.initializeAudioVisualization();
                return true;
            }
            return false;
        } catch {
            return false;
        }
    }
    
    async switchToFallbackEngine() {
        try {
            if (window.steveDashboard) {
                // Switch to a known working engine
                window.steveDashboard.selectEngine('google_tts');
                return true;
            }
            return false;
        } catch {
            return false;
        }
    }
    
    // UI interaction methods
    retryOperation(errorId, context) {
        // Retry the original operation that failed
        const errorLog = this.errorLog.find(log => log.id === errorId);
        if (errorLog && context.retryFunction) {
            context.retryFunction();
        }
    }
    
    showNetworkTroubleshooting() {
        this.showHelpDialog('راهنمای رفع مشکلات شبکه', `
            <div class="help-content">
                <h3>راهنمای رفع مشکلات شبکه</h3>
                <ol>
                    <li>اتصال اینترنت خود را بررسی کنید</li>
                    <li>مرورگر را بازنشانی کنید</li>
                    <li>فایروال یا آنتی‌ویروس را موقتاً غیرفعال کنید</li>
                    <li>از VPN استفاده می‌کنید؟ آن را غیرفعال کنید</li>
                    <li>DNS را به 8.8.8.8 تغییر دهید</li>
                </ol>
            </div>
        `);
    }
    
    showAudioSetupGuide() {
        this.showHelpDialog('راهنمای تنظیم صوت', `
            <div class="help-content">
                <h3>راهنمای تنظیم سیستم صوتی</h3>
                <ol>
                    <li>مجوز دسترسی به میکروفن را بررسی کنید</li>
                    <li>میکروفن را در تنظیمات سیستم فعال کنید</li>
                    <li>مرورگر را بازنشانی کنید</li>
                    <li>از مرورگر دیگری امتحان کنید</li>
                    <li>درایورهای صوتی را به‌روزرسانی کنید</li>
                </ol>
            </div>
        `);
    }
    
    showEngineSelectionPanel() {
        // Focus on engine selection panel
        const enginePanel = document.querySelector('.engine-selector');
        if (enginePanel) {
            enginePanel.scrollIntoView({ behavior: 'smooth' });
            const firstEngine = enginePanel.querySelector('.engine-option');
            if (firstEngine) {
                firstEngine.focus();
            }
        }
    }
    
    showPermissionGuide() {
        this.showHelpDialog('راهنمای مجوزها', `
            <div class="help-content">
                <h3>راهنمای تنظیم مجوزهای مرورگر</h3>
                <ol>
                    <li>روی آیکون قفل کنار آدرس کلیک کنید</li>
                    <li>مجوز میکروفن را "اجازه دادن" کنید</li>
                    <li>صفحه را بازنشانی کنید</li>
                    <li>در صورت لزوم مرورگر را بازنشانی کنید</li>
                </ol>
            </div>
        `);
    }
    
    showHelpDialog(title, content) {
        // Create and show help dialog
        const dialog = document.createElement('div');
        dialog.className = 'error-help-dialog';
        dialog.innerHTML = `
            <div class="error-help-overlay" onclick="this.parentElement.remove()"></div>
            <div class="error-help-content">
                <div class="error-help-header">
                    <h3>${title}</h3>
                    <button onclick="this.closest('.error-help-dialog').remove()" aria-label="بستن">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="error-help-body">${content}</div>
            </div>
        `;
        
        document.body.appendChild(dialog);
    }
    
    // Utility methods
    removeNotification(notification) {
        notification.classList.add('removing');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
    
    generateErrorId() {
        return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    logError(errorData) {
        this.errorLog.push(errorData);
        
        // Keep log size manageable
        if (this.errorLog.length > this.maxLogSize) {
            this.errorLog.shift();
        }
        
        // Send to server if available
        this.sendErrorToServer(errorData);
    }
    
    async sendErrorToServer(errorData) {
        try {
            await fetch('/api/errors', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(errorData)
            });
        } catch {
            // Silently fail - don't create error loops
        }
    }
    
    handleGlobalError(error, filename, lineno, colno) {
        this.handleError(error, {
            type: 'global',
            filename,
            lineno,
            colno
        });
    }
    
    handlePromiseRejection(reason) {
        this.handleError(reason, {
            type: 'promise_rejection'
        });
    }
    
    handleNetworkError(message) {
        this.handleError(new Error(message), {
            type: 'network',
            operation: 'network_connectivity'
        });
    }
    
    handleNetworkRecovery() {
        // Show recovery notification
        this.showSuccessNotification('اتصال اینترنت برقرار شد', 'سیستم مجدداً آنلاین است');
    }
    
    showSuccessNotification(title, message) {
        const notification = document.createElement('div');
        notification.className = 'error-notification success';
        notification.innerHTML = `
            <div class="error-header">
                <div class="error-title">
                    <i class="fas fa-check-circle"></i>
                    <span>${title}</span>
                </div>
                <button class="error-close" onclick="this.closest('.error-notification').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="error-message">${message}</div>
        `;
        
        this.errorContainer.appendChild(notification);
        
        setTimeout(() => {
            this.removeNotification(notification);
        }, 3000);
    }
    
    getErrorReport() {
        return {
            totalErrors: this.errorLog.length,
            recentErrors: this.errorLog.slice(-10),
            errorsByCategory: this.getErrorsByCategory(),
            retryAttempts: Object.fromEntries(this.retryAttempts)
        };
    }
    
    getErrorsByCategory() {
        const categories = {};
        this.errorLog.forEach(log => {
            const category = log.classification.category;
            categories[category] = (categories[category] || 0) + 1;
        });
        return categories;
    }
}

// Create global error handler instance
window.errorHandler = new ErrorHandler();

// Export for module use
window.ErrorHandler = ErrorHandler;