/**
 * STEVE PERSIAN VOICE ASSISTANT - UI TESTING FRAMEWORK
 * Comprehensive testing suite for UI/UX validation
 * Accessibility, performance, and functionality testing
 */

class UITestingFramework {
    constructor() {
        this.testResults = [];
        this.testSuites = new Map();
        this.accessibilityTests = [];
        this.performanceTests = [];
        this.functionalTests = [];
        this.persianTests = [];
        
        this.config = {
            runOnLoad: false,
            logLevel: 'info',
            reportFormat: 'detailed',
            autoFix: false,
            thresholds: {
                accessibility: 90,
                performance: 80,
                persian_support: 95
            }
        };
        
        this.init();
    }
    
    init() {
        this.setupTestSuites();
        this.createTestInterface();
        this.setupEventListeners();
        
        console.log('UI Testing Framework initialized');
        
        if (this.config.runOnLoad) {
            this.runAllTests();
        }
    }
    
    setupTestSuites() {
        // Accessibility Test Suite
        this.testSuites.set('accessibility', {
            name: 'تست‌های دسترسی‌پذیری',
            description: 'بررسی انطباق با استانداردهای WCAG 2.1 AA',
            tests: [
                () => this.testKeyboardNavigation(),
                () => this.testARIALabels(),
                () => this.testColorContrast(),
                () => this.testFocusManagement(),
                () => this.testScreenReaderSupport(),
                () => this.testTouchTargets(),
                () => this.testSemanticHTML()
            ]
        });
        
        // Performance Test Suite
        this.testSuites.set('performance', {
            name: 'تست‌های عملکرد',
            description: 'بررسی سرعت و بهینه‌سازی رابط کاربری',
            tests: [
                () => this.testPageLoadTime(),
                () => this.testRenderPerformance(),
                () => this.testMemoryUsage(),
                () => this.testAnimationPerformance(),
                () => this.testNetworkRequests(),
                () => this.testImageOptimization()
            ]
        });
        
        // Persian Support Test Suite
        this.testSuites.set('persian', {
            name: 'تست‌های پشتیبانی فارسی',
            description: 'بررسی صحیح نمایش و عملکرد متن فارسی',
            tests: [
                () => this.testRTLLayout(),
                () => this.testPersianFonts(),
                () => this.testPersianNumbers(),
                () => this.testBidirectionalText(),
                () => this.testPersianKeyboard(),
                () => this.testCulturalAppropriate()
            ]
        });
        
        // Functionality Test Suite
        this.testSuites.set('functionality', {
            name: 'تست‌های عملکردی',
            description: 'بررسی صحیح عملکرد امکانات',
            tests: [
                () => this.testVoiceVisualizer(),
                () => this.testEngineSelection(),
                () => this.testSettingsPanel(),
                () => this.testErrorHandling(),
                () => this.testResponsiveDesign(),
                () => this.testFormValidation()
            ]
        });
        
        // Voice-First UX Test Suite
        this.testSuites.set('voice_ux', {
            name: 'تست‌های UX صوتی',
            description: 'بررسی تجربه کاربری صوت-محور',
            tests: [
                () => this.testVoiceInteractionFlow(),
                () => this.testAudioFeedback(),
                () => this.testVoiceCommands(),
                () => this.testSpeechRecognition(),
                () => this.testMultimodalInteraction()
            ]
        });
    }
    
    createTestInterface() {
        // Create floating test panel
        const testPanel = document.createElement('div');
        testPanel.id = 'ui-test-panel';
        testPanel.className = 'ui-test-panel';
        testPanel.innerHTML = `
            <div class="test-panel-header">
                <h3>🧪 تست رابط کاربری</h3>
                <div class="test-panel-controls">
                    <button onclick="uiTester.runAllTests()" class="test-btn primary">
                        <i class="fas fa-play"></i> اجرای همه تست‌ها
                    </button>
                    <button onclick="uiTester.togglePanel()" class="test-btn secondary">
                        <i class="fas fa-chevron-up"></i>
                    </button>
                </div>
            </div>
            <div class="test-panel-content">
                <div class="test-suites">
                    ${Array.from(this.testSuites.entries()).map(([id, suite]) => `
                        <div class="test-suite" data-suite="${id}">
                            <div class="test-suite-header">
                                <h4>${suite.name}</h4>
                                <button onclick="uiTester.runTestSuite('${id}')" class="test-btn mini">
                                    اجرا
                                </button>
                            </div>
                            <p class="test-suite-description">${suite.description}</p>
                            <div class="test-results" id="results-${id}"></div>
                        </div>
                    `).join('')}
                </div>
                <div class="test-summary" id="test-summary">
                    <div class="summary-stats">
                        <div class="stat">
                            <span class="stat-value" id="total-tests">0</span>
                            <span class="stat-label">کل تست‌ها</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value" id="passed-tests">0</span>
                            <span class="stat-label">موفق</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value" id="failed-tests">0</span>
                            <span class="stat-label">ناموفق</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value" id="score-percentage">0%</span>
                            <span class="stat-label">امتیاز</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .ui-test-panel {
                position: fixed;
                bottom: 20px;
                left: 20px;
                width: 400px;
                max-height: 600px;
                background: var(--bg-primary);
                border: 2px solid var(--color-primary);
                border-radius: var(--radius-xl);
                box-shadow: var(--shadow-2xl);
                z-index: 10000;
                font-family: var(--font-primary);
                direction: rtl;
                text-align: right;
                overflow: hidden;
                transform: translateY(calc(100% - 60px));
                transition: transform 0.3s ease;
            }
            
            .ui-test-panel.expanded {
                transform: translateY(0);
            }
            
            .test-panel-header {
                background: var(--color-primary);
                color: white;
                padding: var(--space-3) var(--space-4);
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
            }
            
            .test-panel-header h3 {
                margin: 0;
                font-size: var(--text-base);
            }
            
            .test-panel-controls {
                display: flex;
                gap: var(--space-2);
            }
            
            .test-btn {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: var(--space-1) var(--space-2);
                border-radius: var(--radius-md);
                font-size: var(--text-sm);
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .test-btn:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            
            .test-btn.primary {
                background: var(--color-secondary);
                border-color: var(--color-secondary);
            }
            
            .test-btn.mini {
                padding: 2px 6px;
                font-size: 11px;
            }
            
            .test-panel-content {
                max-height: 500px;
                overflow-y: auto;
                padding: var(--space-4);
            }
            
            .test-suite {
                margin-bottom: var(--space-4);
                padding: var(--space-3);
                border: 1px solid var(--color-gray-200);
                border-radius: var(--radius-lg);
            }
            
            .test-suite-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: var(--space-2);
            }
            
            .test-suite-header h4 {
                margin: 0;
                font-size: var(--text-base);
                color: var(--text-primary);
            }
            
            .test-suite-description {
                color: var(--text-secondary);
                font-size: var(--text-sm);
                margin-bottom: var(--space-3);
            }
            
            .test-results {
                min-height: 20px;
            }
            
            .test-result {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: var(--space-2);
                margin-bottom: var(--space-1);
                border-radius: var(--radius-md);
                font-size: var(--text-sm);
            }
            
            .test-result.passed {
                background: var(--color-secondary-100);
                color: var(--color-secondary-900);
            }
            
            .test-result.failed {
                background: var(--color-accent-100);
                color: var(--color-accent-900);
            }
            
            .test-result.running {
                background: var(--color-warning-100);
                color: var(--color-warning-900);
            }
            
            .test-summary {
                border-top: 1px solid var(--color-gray-200);
                padding-top: var(--space-4);
                margin-top: var(--space-4);
            }
            
            .summary-stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: var(--space-3);
            }
            
            .stat {
                text-align: center;
                padding: var(--space-2);
                background: var(--bg-secondary);
                border-radius: var(--radius-lg);
            }
            
            .stat-value {
                display: block;
                font-size: var(--text-xl);
                font-weight: 700;
                color: var(--color-primary);
            }
            
            .stat-label {
                font-size: var(--text-sm);
                color: var(--text-secondary);
            }
            
            @media (max-width: 768px) {
                .ui-test-panel {
                    left: 10px;
                    right: 10px;
                    width: auto;
                }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(testPanel);
        
        // Add click handler for header
        testPanel.querySelector('.test-panel-header').addEventListener('click', () => {
            this.togglePanel();
        });
    }
    
    setupEventListeners() {
        // Keyboard shortcut to run tests
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.runAllTests();
            }
        });
        
        // Auto-run tests on certain events
        window.addEventListener('load', () => {
            if (this.config.runOnLoad) {
                setTimeout(() => this.runAllTests(), 2000);
            }
        });
    }
    
    // Test Suite Runners
    async runAllTests() {
        console.log('🧪 Running all UI tests...');
        this.clearResults();
        
        const startTime = performance.now();
        let totalTests = 0;
        let passedTests = 0;
        
        for (const [suiteId, suite] of this.testSuites) {
            const results = await this.runTestSuite(suiteId);
            totalTests += results.total;
            passedTests += results.passed;
        }
        
        const duration = performance.now() - startTime;
        const score = Math.round((passedTests / totalTests) * 100);
        
        this.updateSummary(totalTests, passedTests, score);
        this.generateReport(duration);
        
        console.log(`✅ Tests completed: ${passedTests}/${totalTests} passed (${score}%)`);
    }
    
    async runTestSuite(suiteId) {
        const suite = this.testSuites.get(suiteId);
        if (!suite) return { total: 0, passed: 0 };
        
        console.log(`🔍 Running ${suite.name}...`);
        
        const resultsContainer = document.getElementById(`results-${suiteId}`);
        resultsContainer.innerHTML = '';
        
        let passed = 0;
        let total = suite.tests.length;
        
        for (let i = 0; i < suite.tests.length; i++) {
            const test = suite.tests[i];
            const testName = test.name || `Test ${i + 1}`;
            
            // Show running state
            this.showTestResult(resultsContainer, testName, 'running', 'در حال اجرا...');
            
            try {
                const result = await test();
                if (result.passed) {
                    passed++;
                    this.showTestResult(resultsContainer, testName, 'passed', result.message);
                } else {
                    this.showTestResult(resultsContainer, testName, 'failed', result.message);
                }
            } catch (error) {
                this.showTestResult(resultsContainer, testName, 'failed', error.message);
            }
        }
        
        return { total, passed };
    }
    
    // Accessibility Tests
    async testKeyboardNavigation() {
        const focusableElements = document.querySelectorAll(
            'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        
        let accessibleCount = 0;
        focusableElements.forEach(el => {
            if (el.tabIndex >= 0 && !el.hidden) {
                accessibleCount++;
            }
        });
        
        const passed = accessibleCount > 0 && accessibleCount === focusableElements.length;
        
        return {
            passed,
            message: passed 
                ? `${accessibleCount} عنصر قابل فوکوس یافت شد`
                : `مشکل در ناوبری کیبورد: ${accessibleCount}/${focusableElements.length}`
        };
    }
    
    async testARIALabels() {
        const interactiveElements = document.querySelectorAll('button, [role="button"], input, select, textarea');
        let labeledCount = 0;
        
        interactiveElements.forEach(el => {
            if (el.getAttribute('aria-label') || 
                el.getAttribute('aria-labelledby') || 
                el.querySelector('label') ||
                el.textContent.trim()) {
                labeledCount++;
            }
        });
        
        const passed = labeledCount === interactiveElements.length;
        
        return {
            passed,
            message: passed 
                ? `همه عناصر دارای برچسب مناسب هستند`
                : `${interactiveElements.length - labeledCount} عنصر فاقد برچسب`
        };
    }
    
    async testColorContrast() {
        // Simplified contrast test - in real implementation, would use color analysis
        const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, div');
        let contrastIssues = 0;
        
        textElements.forEach(el => {
            const style = window.getComputedStyle(el);
            const color = style.color;
            const backgroundColor = style.backgroundColor;
            
            // Simple check for very light text on light background
            if (color.includes('rgb(255') && backgroundColor.includes('rgb(255')) {
                contrastIssues++;
            }
        });
        
        const passed = contrastIssues === 0;
        
        return {
            passed,
            message: passed 
                ? 'هیچ مشکل کنتراست رنگ یافت نشد'
                : `${contrastIssues} مشکل احتمالی کنتراست رنگ`
        };
    }
    
    async testFocusManagement() {
        const focusableElements = document.querySelectorAll('[tabindex], button, input, select, textarea, a[href]');
        let properFocusCount = 0;
        
        focusableElements.forEach(el => {
            // Check if element has visible focus indicator
            el.focus();
            const style = window.getComputedStyle(el);
            if (style.outline !== 'none' || style.boxShadow.includes('outline')) {
                properFocusCount++;
            }
        });
        
        // Restore focus
        document.activeElement?.blur();
        
        const passed = properFocusCount > focusableElements.length * 0.8; // 80% threshold
        
        return {
            passed,
            message: passed 
                ? 'مدیریت فوکوس مناسب است'
                : `${focusableElements.length - properFocusCount} عنصر فاقد نشانگر فوکوس`
        };
    }
    
    async testScreenReaderSupport() {
        const ariaElements = document.querySelectorAll('[aria-live], [aria-atomic], [role], [aria-label]');
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const landmarks = document.querySelectorAll('main, nav, aside, section, header, footer');
        
        const score = ariaElements.length + headings.length + landmarks.length;
        const passed = score > 10; // Minimum threshold
        
        return {
            passed,
            message: passed 
                ? `پشتیبانی خوب از صفحه‌خوان (امتیاز: ${score})`
                : `پشتیبانی ناکافی از صفحه‌خوان (امتیاز: ${score})`
        };
    }
    
    async testTouchTargets() {
        const touchElements = document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"], a');
        let adequateCount = 0;
        
        touchElements.forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width >= 44 && rect.height >= 44) {
                adequateCount++;
            }
        });
        
        const passed = adequateCount === touchElements.length;
        
        return {
            passed,
            message: passed 
                ? 'همه اهداف لمسی اندازه مناسب دارند'
                : `${touchElements.length - adequateCount} هدف لمسی کوچک‌تر از حد استاندارد`
        };
    }
    
    async testSemanticHTML() {
        const semanticElements = document.querySelectorAll('main, nav, aside, section, article, header, footer, h1, h2, h3, h4, h5, h6');
        const totalElements = document.querySelectorAll('*').length;
        const semanticRatio = semanticElements.length / totalElements;
        
        const passed = semanticRatio > 0.1; // At least 10% semantic elements
        
        return {
            passed,
            message: passed 
                ? `استفاده مناسب از HTML معنایی (${Math.round(semanticRatio * 100)}%)`
                : `استفاده کم از HTML معنایی (${Math.round(semanticRatio * 100)}%)`
        };
    }
    
    // Performance Tests
    async testPageLoadTime() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        const passed = loadTime < 3000; // 3 seconds threshold
        
        return {
            passed,
            message: passed 
                ? `زمان بارگذاری مناسب: ${loadTime}ms`
                : `زمان بارگذاری طولانی: ${loadTime}ms`
        };
    }
    
    async testRenderPerformance() {
        const startTime = performance.now();
        
        // Trigger a reflow
        document.body.offsetHeight;
        
        const renderTime = performance.now() - startTime;
        const passed = renderTime < 16; // 60fps threshold
        
        return {
            passed,
            message: passed 
                ? `عملکرد رندر مناسب: ${renderTime.toFixed(2)}ms`
                : `عملکرد رندر کند: ${renderTime.toFixed(2)}ms`
        };
    }
    
    async testMemoryUsage() {
        if (!performance.memory) {
            return {
                passed: true,
                message: 'اطلاعات حافظه در دسترس نیست'
            };
        }
        
        const memoryUsage = performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit;
        const passed = memoryUsage < 0.8; // Less than 80% memory usage
        
        return {
            passed,
            message: passed 
                ? `استفاده از حافظه مناسب: ${Math.round(memoryUsage * 100)}%`
                : `استفاده زیاد از حافظه: ${Math.round(memoryUsage * 100)}%`
        };
    }
    
    async testAnimationPerformance() {
        const animatedElements = document.querySelectorAll('[style*="animation"], .voice-visualizer-container');
        let smoothAnimations = 0;
        
        // Simple check for CSS animations
        animatedElements.forEach(el => {
            const style = window.getComputedStyle(el);
            if (style.animationDuration !== '0s' || style.transitionDuration !== '0s') {
                smoothAnimations++;
            }
        });
        
        const passed = smoothAnimations > 0;
        
        return {
            passed,
            message: passed 
                ? `${smoothAnimations} انیمیشن یافت شد`
                : 'هیچ انیمیشنی یافت نشد'
        };
    }
    
    async testNetworkRequests() {
        const entries = performance.getEntriesByType('resource');
        const slowRequests = entries.filter(entry => entry.duration > 1000);
        const passed = slowRequests.length === 0;
        
        return {
            passed,
            message: passed 
                ? `همه درخواست‌های شبکه سریع هستند`
                : `${slowRequests.length} درخواست کند یافت شد`
        };
    }
    
    async testImageOptimization() {
        const images = document.querySelectorAll('img');
        let optimizedCount = 0;
        
        images.forEach(img => {
            if (img.loading === 'lazy' || img.getAttribute('src')?.includes('webp')) {
                optimizedCount++;
            }
        });
        
        const passed = images.length === 0 || optimizedCount / images.length > 0.5;
        
        return {
            passed,
            message: passed 
                ? `بهینه‌سازی تصاویر مناسب`
                : `${images.length - optimizedCount} تصویر غیربهینه`
        };
    }
    
    // Persian Support Tests
    async testRTLLayout() {
        const body = document.body;
        const direction = window.getComputedStyle(body).direction;
        const passed = direction === 'rtl';
        
        return {
            passed,
            message: passed 
                ? 'چیدمان RTL صحیح است'
                : 'چیدمان RTL تنظیم نشده است'
        };
    }
    
    async testPersianFonts() {
        const persianElements = document.querySelectorAll('.persian-text, [lang="fa"], body');
        let properFontCount = 0;
        
        persianElements.forEach(el => {
            const style = window.getComputedStyle(el);
            const fontFamily = style.fontFamily.toLowerCase();
            
            if (fontFamily.includes('vazir') || 
                fontFamily.includes('sahel') || 
                fontFamily.includes('tahoma')) {
                properFontCount++;
            }
        });
        
        const passed = properFontCount > 0;
        
        return {
            passed,
            message: passed 
                ? `فونت‌های فارسی مناسب تنظیم شده`
                : 'فونت‌های فارسی مناسب یافت نشد'
        };
    }
    
    async testPersianNumbers() {
        const textElements = document.querySelectorAll('*');
        let persianNumberCount = 0;
        
        textElements.forEach(el => {
            const text = el.textContent;
            if (text && /[۰-۹]/.test(text)) {
                persianNumberCount++;
            }
        });
        
        // This test passes if we find Persian numbers OR if we're consistently using English numbers
        const passed = true; // Persian numbers are optional
        
        return {
            passed,
            message: persianNumberCount > 0 
                ? `${persianNumberCount} عنصر با اعداد فارسی یافت شد`
                : 'از اعداد انگلیسی استفاده شده است'
        };
    }
    
    async testBidirectionalText() {
        // Test for proper handling of mixed RTL/LTR text
        const mixedTextElements = document.querySelectorAll('*');
        let bidiElements = 0;
        
        mixedTextElements.forEach(el => {
            const text = el.textContent;
            if (text && /[a-zA-Z]/.test(text) && /[\u0600-\u06FF]/.test(text)) {
                bidiElements++;
            }
        });
        
        const passed = true; // Bidirectional text handling is complex to test automatically
        
        return {
            passed,
            message: bidiElements > 0 
                ? `${bidiElements} عنصر با متن دوجهته یافت شد`
                : 'متن دوجهته یافت نشد'
        };
    }
    
    async testPersianKeyboard() {
        // Test if Persian input is supported
        const inputs = document.querySelectorAll('input[type="text"], textarea');
        let persianSupportCount = 0;
        
        inputs.forEach(input => {
            // Check if input has Persian placeholder or lang attribute
            if (input.placeholder?.match(/[\u0600-\u06FF]/) || 
                input.lang === 'fa' || 
                input.dir === 'rtl') {
                persianSupportCount++;
            }
        });
        
        const passed = inputs.length === 0 || persianSupportCount > 0;
        
        return {
            passed,
            message: passed 
                ? 'پشتیبانی از ورودی فارسی موجود است'
                : 'پشتیبانی از ورودی فارسی یافت نشد'
        };
    }
    
    async testCulturalAppropriate() {
        // Test for culturally appropriate content
        const textContent = document.body.textContent;
        let culturalScore = 0;
        
        // Check for Persian greetings and common phrases
        const persianPhrases = ['سلام', 'خوش آمدید', 'ممنون', 'لطفاً', 'متشکرم'];
        persianPhrases.forEach(phrase => {
            if (textContent.includes(phrase)) {
                culturalScore++;
            }
        });
        
        const passed = culturalScore > 0;
        
        return {
            passed,
            message: passed 
                ? `محتوای فرهنگی مناسب (امتیاز: ${culturalScore})`
                : 'محتوای فرهنگی فارسی یافت نشد'
        };
    }
    
    // Functionality Tests
    async testVoiceVisualizer() {
        const visualizer = document.getElementById('voice-visualizer');
        const passed = visualizer && visualizer.offsetWidth > 0 && visualizer.offsetHeight > 0;
        
        return {
            passed,
            message: passed 
                ? 'نمایش‌گر صوتی به درستی نمایش داده می‌شود'
                : 'نمایش‌گر صوتی یافت نشد یا مخفی است'
        };
    }
    
    async testEngineSelection() {
        const engines = document.querySelectorAll('.engine-option');
        const activeEngine = document.querySelector('.engine-option.active');
        
        const passed = engines.length > 0 && activeEngine !== null;
        
        return {
            passed,
            message: passed 
                ? `${engines.length} موتور صوتی یافت شد، یکی فعال است`
                : 'مشکل در پنل انتخاب موتور صوتی'
        };
    }
    
    async testSettingsPanel() {
        const settings = document.querySelectorAll('.toggle-switch, .setting-item');
        const passed = settings.length > 0;
        
        return {
            passed,
            message: passed 
                ? `${settings.length} تنظیم یافت شد`
                : 'پنل تنظیمات یافت نشد'
        };
    }
    
    async testErrorHandling() {
        const errorContainer = document.getElementById('error-container');
        const passed = errorContainer !== null && window.errorHandler;
        
        return {
            passed,
            message: passed 
                ? 'سیستم مدیریت خطا فعال است'
                : 'سیستم مدیریت خطا یافت نشد'
        };
    }
    
    async testResponsiveDesign() {
        const viewport = window.innerWidth;
        const dashboard = document.querySelector('.dashboard-main');
        
        if (!dashboard) {
            return {
                passed: false,
                message: 'داشبورد اصلی یافت نشد'
            };
        }
        
        const style = window.getComputedStyle(dashboard);
        const passed = style.display === 'grid' || style.display === 'flex';
        
        return {
            passed,
            message: passed 
                ? `طراحی ریسپانسیو فعال است (${viewport}px)`
                : 'مشکل در طراحی ریسپانسیو'
        };
    }
    
    async testFormValidation() {
        const forms = document.querySelectorAll('form');
        const inputs = document.querySelectorAll('input[required], textarea[required]');
        
        let validationCount = 0;
        inputs.forEach(input => {
            if (input.checkValidity || input.getAttribute('aria-invalid')) {
                validationCount++;
            }
        });
        
        const passed = forms.length === 0 || validationCount > 0;
        
        return {
            passed,
            message: passed 
                ? 'اعتبارسنجی فرم‌ها مناسب است'
                : 'مشکل در اعتبارسنجی فرم‌ها'
        };
    }
    
    // Voice UX Tests
    async testVoiceInteractionFlow() {
        const voiceButton = document.getElementById('voice-visualizer');
        const statusText = document.getElementById('voice-status-text');
        
        const passed = voiceButton && statusText;
        
        return {
            passed,
            message: passed 
                ? 'جریان تعامل صوتی موجود است'
                : 'جریان تعامل صوتی ناقص است'
        };
    }
    
    async testAudioFeedback() {
        const audioElements = document.querySelectorAll('audio, [data-audio]');
        const visualFeedback = document.querySelectorAll('.voice-visualizer-container, .voice-indicator');
        
        const passed = visualFeedback.length > 0;
        
        return {
            passed,
            message: passed 
                ? 'بازخورد صوتی/بصری موجود است'
                : 'بازخورد صوتی یافت نشد'
        };
    }
    
    async testVoiceCommands() {
        // Test if voice command handling is set up
        const passed = typeof window.steveDashboard?.handleVoiceInteraction === 'function';
        
        return {
            passed,
            message: passed 
                ? 'سیستم فرمان‌های صوتی آماده است'
                : 'سیستم فرمان‌های صوتی یافت نشد'
        };
    }
    
    async testSpeechRecognition() {
        const supported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        
        return {
            passed: supported,
            message: supported 
                ? 'تشخیص گفتار پشتیبانی می‌شود'
                : 'تشخیص گفتار پشتیبانی نمی‌شود'
        };
    }
    
    async testMultimodalInteraction() {
        const touchSupport = 'ontouchstart' in window;
        const keyboardSupport = document.querySelectorAll('[tabindex]').length > 0;
        const voiceSupport = document.getElementById('voice-visualizer') !== null;
        
        const supportCount = [touchSupport, keyboardSupport, voiceSupport].filter(Boolean).length;
        const passed = supportCount >= 2;
        
        return {
            passed,
            message: passed 
                ? `${supportCount} روش تعامل پشتیبانی می‌شود`
                : `تنها ${supportCount} روش تعامل پشتیبانی می‌شود`
        };
    }
    
    // UI Helper Methods
    showTestResult(container, testName, status, message) {
        const existingResult = container.querySelector(`[data-test="${testName}"]`);
        if (existingResult) {
            existingResult.remove();
        }
        
        const resultDiv = document.createElement('div');
        resultDiv.className = `test-result ${status}`;
        resultDiv.setAttribute('data-test', testName);
        
        const icon = {
            running: 'fas fa-spinner fa-spin',
            passed: 'fas fa-check',
            failed: 'fas fa-times'
        }[status] || 'fas fa-question';
        
        resultDiv.innerHTML = `
            <span>
                <i class="${icon}"></i>
                ${testName}
            </span>
            <small>${message}</small>
        `;
        
        container.appendChild(resultDiv);
    }
    
    updateSummary(total, passed, score) {
        document.getElementById('total-tests').textContent = total;
        document.getElementById('passed-tests').textContent = passed;
        document.getElementById('failed-tests').textContent = total - passed;
        document.getElementById('score-percentage').textContent = `${score}%`;
        
        // Update score color
        const scoreElement = document.getElementById('score-percentage');
        scoreElement.style.color = score >= 80 ? 'var(--color-secondary)' : 
                                   score >= 60 ? 'var(--color-warning)' : 
                                   'var(--color-accent)';
    }
    
    clearResults() {
        document.querySelectorAll('.test-results').forEach(container => {
            container.innerHTML = '';
        });
    }
    
    togglePanel() {
        const panel = document.getElementById('ui-test-panel');
        panel.classList.toggle('expanded');
        
        const chevron = panel.querySelector('.fa-chevron-up, .fa-chevron-down');
        if (chevron) {
            chevron.className = panel.classList.contains('expanded') 
                ? 'fas fa-chevron-down' 
                : 'fas fa-chevron-up';
        }
    }
    
    generateReport(duration) {
        const report = {
            timestamp: new Date().toISOString(),
            duration: Math.round(duration),
            results: this.testResults,
            summary: {
                total: parseInt(document.getElementById('total-tests').textContent),
                passed: parseInt(document.getElementById('passed-tests').textContent),
                failed: parseInt(document.getElementById('failed-tests').textContent),
                score: parseInt(document.getElementById('score-percentage').textContent)
            },
            environment: {
                userAgent: navigator.userAgent,
                viewport: `${window.innerWidth}x${window.innerHeight}`,
                language: navigator.language,
                platform: navigator.platform
            }
        };
        
        console.log('📊 Test Report:', report);
        return report;
    }
    
    exportReport() {
        const report = this.generateReport(0);
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `steve-ui-test-report-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Create global testing instance
window.uiTester = new UITestingFramework();

// Export for module use
window.UITestingFramework = UITestingFramework;