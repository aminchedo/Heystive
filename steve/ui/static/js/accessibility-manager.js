/**
 * STEVE PERSIAN VOICE ASSISTANT - ACCESSIBILITY MANAGER
 * WCAG 2.1 AA Compliance and Advanced Accessibility Features
 * Screen reader support, keyboard navigation, high contrast, and more
 */

class AccessibilityManager {
    constructor() {
        this.config = {
            announcements: true,
            keyboardNavigation: true,
            highContrast: false,
            reducedMotion: false,
            screenReaderMode: false,
            focusManagement: true,
            voiceDescriptions: true
        };
        
        this.announcer = null;
        this.focusHistory = [];
        this.currentFocusIndex = -1;
        this.keyboardShortcuts = new Map();
        
        this.init();
    }
    
    init() {
        this.createAnnouncer();
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.detectUserPreferences();
        this.setupFocusManagement();
        this.registerKeyboardShortcuts();
        this.setupARIALabels();
        
        console.log('Accessibility Manager initialized');
    }
    
    createAnnouncer() {
        // Create ARIA live region for announcements
        this.announcer = document.createElement('div');
        this.announcer.setAttribute('aria-live', 'polite');
        this.announcer.setAttribute('aria-atomic', 'true');
        this.announcer.setAttribute('class', 'sr-only');
        this.announcer.id = 'accessibility-announcer';
        document.body.appendChild(this.announcer);
        
        // Create assertive announcer for urgent messages
        this.assertiveAnnouncer = document.createElement('div');
        this.assertiveAnnouncer.setAttribute('aria-live', 'assertive');
        this.assertiveAnnouncer.setAttribute('aria-atomic', 'true');
        this.assertiveAnnouncer.setAttribute('class', 'sr-only');
        this.assertiveAnnouncer.id = 'accessibility-announcer-assertive';
        document.body.appendChild(this.assertiveAnnouncer);
    }
    
    setupKeyboardNavigation() {
        // Create keyboard navigation manager
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });
        
        // Track focus changes
        document.addEventListener('focusin', (e) => {
            this.handleFocusChange(e);
        });
        
        // Skip links for keyboard users
        this.createSkipLinks();
    }
    
    createSkipLinks() {
        const skipLinks = document.createElement('div');
        skipLinks.className = 'skip-links';
        skipLinks.innerHTML = `
            <a href="#main-content" class="skip-link">پرش به محتوای اصلی</a>
            <a href="#voice-visualizer" class="skip-link">پرش به کنترل صوتی</a>
            <a href="#engine-selector" class="skip-link">پرش به انتخاب موتور</a>
            <a href="#system-metrics" class="skip-link">پرش به آمار سیستم</a>
        `;
        
        // Add skip link styles
        const style = document.createElement('style');
        style.textContent = `
            .skip-links {
                position: absolute;
                top: -100px;
                left: 0;
                z-index: 10000;
            }
            
            .skip-link {
                position: absolute;
                top: -100px;
                left: 10px;
                background: var(--color-primary);
                color: white;
                padding: var(--space-2) var(--space-4);
                border-radius: var(--radius-md);
                text-decoration: none;
                font-weight: 500;
                transition: top 0.2s ease;
            }
            
            .skip-link:focus {
                top: 10px;
            }
        `;
        document.head.appendChild(style);
        document.body.insertBefore(skipLinks, document.body.firstChild);
    }
    
    setupScreenReaderSupport() {
        // Enhance all interactive elements with proper ARIA labels
        this.enhanceInteractiveElements();
        
        // Setup live regions for dynamic content
        this.setupLiveRegions();
        
        // Add screen reader instructions
        this.addScreenReaderInstructions();
    }
    
    enhanceInteractiveElements() {
        // Voice visualizer
        const visualizer = document.getElementById('voice-visualizer');
        if (visualizer) {
            visualizer.setAttribute('role', 'button');
            visualizer.setAttribute('aria-label', 'دکمه کنترل صوتی - برای شروع یا توقف شنیدن کلیک کنید');
            visualizer.setAttribute('aria-describedby', 'voice-status-description');
            visualizer.setAttribute('tabindex', '0');
        }
        
        // Engine options
        document.querySelectorAll('.engine-option').forEach((option, index) => {
            option.setAttribute('role', 'radio');
            option.setAttribute('tabindex', index === 0 ? '0' : '-1');
            option.setAttribute('aria-describedby', `engine-description-${index}`);
            
            // Add description element
            const description = document.createElement('div');
            description.id = `engine-description-${index}`;
            description.className = 'sr-only';
            description.textContent = this.getEngineDescription(option);
            option.appendChild(description);
        });
        
        // Toggle switches
        document.querySelectorAll('.toggle-switch').forEach(toggle => {
            toggle.setAttribute('role', 'switch');
            toggle.setAttribute('tabindex', '0');
            
            const label = toggle.closest('.setting-item').querySelector('.setting-label');
            if (label) {
                const labelId = `toggle-label-${Date.now()}-${Math.random()}`;
                label.id = labelId;
                toggle.setAttribute('aria-labelledby', labelId);
            }
        });
        
        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            const label = btn.querySelector('.quick-action-label');
            if (label) {
                btn.setAttribute('aria-label', `${label.textContent} - دکمه عملیات سریع`);
            }
        });
    }
    
    setupLiveRegions() {
        // Conversation display
        const conversationDisplay = document.querySelector('.conversation-display');
        if (conversationDisplay) {
            conversationDisplay.setAttribute('aria-live', 'polite');
            conversationDisplay.setAttribute('aria-label', 'تاریخچه گفتگو');
            conversationDisplay.setAttribute('role', 'log');
        }
        
        // System metrics
        const metricsGrid = document.querySelector('.metrics-grid');
        if (metricsGrid) {
            metricsGrid.setAttribute('aria-live', 'polite');
            metricsGrid.setAttribute('aria-label', 'آمار عملکرد سیستم');
        }
    }
    
    addScreenReaderInstructions() {
        const instructions = document.createElement('div');
        instructions.className = 'sr-only';
        instructions.setAttribute('aria-label', 'راهنمای استفاده برای صفحه‌خوان');
        instructions.innerHTML = `
            <h2>راهنمای استفاده از دستیار صوتی استیو</h2>
            <p>این صفحه شامل دستیار صوتی فارسی با قابلیت‌های زیر است:</p>
            <ul>
                <li>کنترل صوتی: برای فعال‌سازی یا غیرفعال‌سازی شنیدن از دکمه کنترل صوتی استفاده کنید</li>
                <li>انتخاب موتور: موتور TTS مناسب را از لیست موتورهای موجود انتخاب کنید</li>
                <li>تنظیمات: تنظیمات دسترسی‌پذیری و صوتی را تغییر دهید</li>
                <li>آمار سیستم: عملکرد سیستم را مشاهده کنید</li>
            </ul>
            <p>برای استفاده از کلیدهای میانبر، کلید Tab را برای حرکت بین عناصر و Enter یا Space را برای فعال‌سازی استفاده کنید.</p>
        `;
        document.body.appendChild(instructions);
    }
    
    detectUserPreferences() {
        // Detect user preferences from browser/system
        
        // High contrast
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            this.enableHighContrast();
        }
        
        // Reduced motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.enableReducedMotion();
        }
        
        // Color scheme
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.enableDarkMode();
        }
        
        // Listen for preference changes
        window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
            if (e.matches) {
                this.enableHighContrast();
            } else {
                this.disableHighContrast();
            }
        });
        
        window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
            if (e.matches) {
                this.enableReducedMotion();
            } else {
                this.disableReducedMotion();
            }
        });
    }
    
    setupFocusManagement() {
        // Focus trap for modals
        this.setupFocusTraps();
        
        // Focus indicators
        this.enhanceFocusIndicators();
        
        // Focus restoration
        this.setupFocusRestoration();
    }
    
    setupFocusTraps() {
        // Create focus trap utility
        this.focusTraps = new Map();
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.handleTabNavigation(e);
            }
        });
    }
    
    enhanceFocusIndicators() {
        const style = document.createElement('style');
        style.textContent = `
            /* Enhanced focus indicators */
            *:focus-visible {
                outline: 3px solid var(--color-primary) !important;
                outline-offset: 2px !important;
                border-radius: 2px;
            }
            
            /* High contrast focus indicators */
            @media (prefers-contrast: high) {
                *:focus-visible {
                    outline: 4px solid #000 !important;
                    outline-offset: 3px !important;
                    background: #ffff00 !important;
                    color: #000 !important;
                }
            }
            
            /* Remove default focus styles */
            *:focus:not(:focus-visible) {
                outline: none;
            }
        `;
        document.head.appendChild(style);
    }
    
    setupFocusRestoration() {
        // Track focus history for restoration
        document.addEventListener('focusin', (e) => {
            this.focusHistory.push(e.target);
            if (this.focusHistory.length > 10) {
                this.focusHistory.shift();
            }
        });
    }
    
    registerKeyboardShortcuts() {
        // Register keyboard shortcuts
        this.keyboardShortcuts.set('ctrl+space', () => {
            this.activateVoiceControl();
        });
        
        this.keyboardShortcuts.set('ctrl+h', () => {
            this.showHelp();
        });
        
        this.keyboardShortcuts.set('ctrl+/', () => {
            this.showKeyboardShortcuts();
        });
        
        this.keyboardShortcuts.set('escape', () => {
            this.handleEscape();
        });
        
        this.keyboardShortcuts.set('ctrl+1', () => {
            this.selectEngine(0);
        });
        
        this.keyboardShortcuts.set('ctrl+2', () => {
            this.selectEngine(1);
        });
        
        this.keyboardShortcuts.set('ctrl+3', () => {
            this.selectEngine(2);
        });
        
        this.keyboardShortcuts.set('ctrl+4', () => {
            this.selectEngine(3);
        });
    }
    
    handleKeyboardNavigation(e) {
        const key = this.getKeyString(e);
        
        // Handle keyboard shortcuts
        if (this.keyboardShortcuts.has(key)) {
            e.preventDefault();
            this.keyboardShortcuts.get(key)();
            return;
        }
        
        // Handle arrow key navigation for radio groups
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            this.handleArrowNavigation(e);
        }
        
        // Handle Enter/Space for activation
        if (e.key === 'Enter' || e.key === ' ') {
            this.handleActivation(e);
        }
    }
    
    handleArrowNavigation(e) {
        const radioGroup = e.target.closest('[role="radiogroup"]');
        if (!radioGroup) return;
        
        const radios = Array.from(radioGroup.querySelectorAll('[role="radio"]'));
        const currentIndex = radios.indexOf(e.target);
        
        if (currentIndex === -1) return;
        
        e.preventDefault();
        
        let nextIndex;
        if (e.key === 'ArrowDown') {
            nextIndex = (currentIndex + 1) % radios.length;
        } else {
            nextIndex = (currentIndex - 1 + radios.length) % radios.length;
        }
        
        // Update focus and selection
        radios[currentIndex].setAttribute('tabindex', '-1');
        radios[currentIndex].setAttribute('aria-checked', 'false');
        
        radios[nextIndex].setAttribute('tabindex', '0');
        radios[nextIndex].setAttribute('aria-checked', 'true');
        radios[nextIndex].focus();
        
        // Trigger selection
        radios[nextIndex].click();
    }
    
    handleActivation(e) {
        const element = e.target;
        
        // Handle toggle switches
        if (element.getAttribute('role') === 'switch') {
            e.preventDefault();
            this.toggleSwitch(element);
        }
        
        // Handle buttons without default behavior
        if (element.getAttribute('role') === 'button' && !element.tagName.match(/button|a/i)) {
            e.preventDefault();
            element.click();
        }
    }
    
    handleTabNavigation(e) {
        // Handle focus trapping in modals
        const modal = document.querySelector('.modal.active, .mobile-modal.active');
        if (modal) {
            this.trapFocusInModal(e, modal);
        }
    }
    
    trapFocusInModal(e, modal) {
        const focusableElements = modal.querySelectorAll(
            'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
        }
    }
    
    handleFocusChange(e) {
        // Announce focus changes for screen readers
        if (this.config.voiceDescriptions) {
            this.announceFocusChange(e.target);
        }
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
    
    // Public API methods
    announce(message, priority = 'polite') {
        if (!this.config.announcements) return;
        
        const announcer = priority === 'assertive' ? this.assertiveAnnouncer : this.announcer;
        announcer.textContent = message;
        
        // Clear after announcement
        setTimeout(() => {
            announcer.textContent = '';
        }, 1000);
    }
    
    announceVoiceState(state, details = '') {
        const messages = {
            idle: 'دستیار صوتی آماده است',
            listening: 'در حال شنیدن صدای شما',
            speaking: 'دستیار در حال پاسخ دادن است',
            processing: 'در حال پردازش درخواست شما',
            error: 'خطا رخ داده است، لطفاً دوباره تلاش کنید'
        };
        
        const message = messages[state] || state;
        const fullMessage = details ? `${message}. ${details}` : message;
        
        this.announce(fullMessage, state === 'error' ? 'assertive' : 'polite');
    }
    
    announceFocusChange(element) {
        const label = this.getElementLabel(element);
        if (label) {
            this.announce(`فوکوس روی ${label}`, 'polite');
        }
    }
    
    getElementLabel(element) {
        // Get the best label for an element
        return element.getAttribute('aria-label') ||
               element.getAttribute('title') ||
               element.textContent?.trim() ||
               element.getAttribute('placeholder') ||
               'عنصر بدون برچسب';
    }
    
    getEngineDescription(option) {
        const name = option.querySelector('.engine-name')?.textContent || '';
        const details = option.querySelector('.engine-details')?.textContent || '';
        return `${name}. ${details}`;
    }
    
    enableHighContrast() {
        this.config.highContrast = true;
        document.body.classList.add('high-contrast');
        this.announce('حالت کنتراست بالا فعال شد', 'polite');
    }
    
    disableHighContrast() {
        this.config.highContrast = false;
        document.body.classList.remove('high-contrast');
        this.announce('حالت کنتراست بالا غیرفعال شد', 'polite');
    }
    
    enableReducedMotion() {
        this.config.reducedMotion = true;
        document.body.classList.add('reduced-motion');
        this.announce('حرکت کاهش‌یافته فعال شد', 'polite');
    }
    
    disableReducedMotion() {
        this.config.reducedMotion = false;
        document.body.classList.remove('reduced-motion');
        this.announce('حرکت کاهش‌یافته غیرفعال شد', 'polite');
    }
    
    enableDarkMode() {
        document.body.classList.add('dark-mode');
        this.announce('حالت تاریک فعال شد', 'polite');
    }
    
    activateVoiceControl() {
        const voiceButton = document.getElementById('voice-visualizer');
        if (voiceButton) {
            voiceButton.focus();
            voiceButton.click();
            this.announce('کنترل صوتی فعال شد', 'assertive');
        }
    }
    
    selectEngine(index) {
        const engines = document.querySelectorAll('.engine-option');
        if (engines[index]) {
            engines[index].focus();
            engines[index].click();
        }
    }
    
    showHelp() {
        this.announce('نمایش راهنما', 'polite');
        // Trigger help display
        const helpEvent = new CustomEvent('showHelp');
        document.dispatchEvent(helpEvent);
    }
    
    showKeyboardShortcuts() {
        const shortcuts = `
            کلیدهای میانبر:
            Ctrl + Space: فعال‌سازی کنترل صوتی
            Ctrl + H: نمایش راهنما
            Ctrl + /: نمایش کلیدهای میانبر
            Escape: بستن پنجره‌ها
            Ctrl + 1-4: انتخاب موتور صوتی
            Tab: حرکت بین عناصر
            Enter/Space: فعال‌سازی عنصر
            فلش‌های بالا/پایین: حرکت در گروه‌های رادیویی
        `;
        
        this.announce(shortcuts, 'polite');
    }
    
    handleEscape() {
        // Close modals, dropdowns, etc.
        const modal = document.querySelector('.modal.active, .mobile-modal.active');
        if (modal) {
            modal.classList.remove('active');
            this.restoreFocus();
        }
    }
    
    toggleSwitch(element) {
        const isActive = element.classList.contains('active');
        element.classList.toggle('active');
        element.setAttribute('aria-checked', !isActive);
        
        const label = element.getAttribute('aria-labelledby');
        const labelElement = label ? document.getElementById(label) : null;
        const labelText = labelElement ? labelElement.textContent : 'تنظیم';
        
        this.announce(`${labelText} ${isActive ? 'غیرفعال' : 'فعال'} شد`, 'polite');
    }
    
    restoreFocus() {
        if (this.focusHistory.length > 1) {
            const previousElement = this.focusHistory[this.focusHistory.length - 2];
            if (previousElement && document.contains(previousElement)) {
                previousElement.focus();
            }
        }
    }
    
    setupARIALabels() {
        // Add comprehensive ARIA labels
        const style = document.createElement('style');
        style.textContent = `
            /* Screen reader only class */
            .sr-only {
                position: absolute !important;
                width: 1px !important;
                height: 1px !important;
                padding: 0 !important;
                margin: -1px !important;
                overflow: hidden !important;
                clip: rect(0, 0, 0, 0) !important;
                white-space: nowrap !important;
                border: 0 !important;
            }
            
            .sr-only-focusable:focus {
                position: static !important;
                width: auto !important;
                height: auto !important;
                padding: inherit !important;
                margin: inherit !important;
                overflow: visible !important;
                clip: auto !important;
                white-space: normal !important;
            }
            
            /* High contrast styles */
            .high-contrast {
                --color-primary: #0000FF;
                --color-secondary: #008000;
                --color-accent: #FF0000;
                --text-primary: #000000;
                --bg-primary: #FFFFFF;
            }
            
            .high-contrast .voice-visualizer-container {
                border: 4px solid #000000;
            }
            
            .high-contrast .btn {
                border: 3px solid currentColor;
                font-weight: 700;
            }
            
            /* Reduced motion styles */
            .reduced-motion *,
            .reduced-motion *::before,
            .reduced-motion *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Utility methods
    isScreenReaderActive() {
        // Detect if screen reader is likely active
        return this.config.screenReaderMode || 
               window.navigator.userAgent.includes('NVDA') ||
               window.navigator.userAgent.includes('JAWS') ||
               window.speechSynthesis?.speaking === false;
    }
    
    getAccessibilityReport() {
        return {
            config: this.config,
            highContrast: this.config.highContrast,
            reducedMotion: this.config.reducedMotion,
            screenReaderActive: this.isScreenReaderActive(),
            keyboardNavigationEnabled: this.config.keyboardNavigation,
            announcementsEnabled: this.config.announcements,
            focusManagementActive: this.config.focusManagement
        };
    }
}

// Export for global use
window.AccessibilityManager = AccessibilityManager;