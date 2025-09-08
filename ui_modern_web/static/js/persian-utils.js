/**
 * Persian Language Utilities for Heystive Voice Assistant
 * Text processing, formatting, and localization utilities
 */

class PersianUtils {
    constructor() {
        // Persian digits mapping
        this.persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
        this.arabicDigits = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
        this.englishDigits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
        
        // Persian months
        this.persianMonths = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];
        
        // Persian weekdays
        this.persianWeekdays = [
            'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه'
        ];
        
        // Common Persian phrases for voice assistant
        this.commonPhrases = {
            greeting: ['سلام', 'درود', 'صبح بخیر', 'عصر بخیر', 'شب بخیر'],
            thanks: ['ممنون', 'متشکرم', 'سپاس', 'مرسی'],
            goodbye: ['خداحافظ', 'بدرود', 'تا بعد', 'فعلا'],
            yes: ['بله', 'آره', 'بلی', 'درسته'],
            no: ['نه', 'خیر', 'نخیر', 'اشتباهه'],
            help: ['کمک', 'راهنمایی', 'یاری', 'همکاری']
        };
        
        // Persian keyboard layout
        this.persianKeyboard = {
            'q': 'ض', 'w': 'ص', 'e': 'ث', 'r': 'ق', 't': 'ف', 'y': 'غ', 'u': 'ع', 'i': 'ه', 'o': 'خ', 'p': 'ح',
            'a': 'ش', 's': 'س', 'd': 'ی', 'f': 'ب', 'g': 'ل', 'h': 'ا', 'j': 'ت', 'k': 'ن', 'l': 'م', ';': 'ک',
            'z': 'ظ', 'x': 'ط', 'c': 'ز', 'v': 'ر', 'b': 'ذ', 'n': 'د', 'm': 'پ', ',': 'و', '.': '.'
        };
    }
    
    // Convert English digits to Persian
    toPersianDigits(text) {
        if (typeof text !== 'string') {
            text = String(text);
        }
        
        return text.replace(/[0-9]/g, (digit) => {
            return this.persianDigits[parseInt(digit)];
        });
    }
    
    // Convert Persian digits to English
    toEnglishDigits(text) {
        if (typeof text !== 'string') {
            text = String(text);
        }
        
        // Convert Persian digits
        text = text.replace(/[۰-۹]/g, (digit) => {
            return this.englishDigits[this.persianDigits.indexOf(digit)];
        });
        
        // Convert Arabic digits
        text = text.replace(/[٠-٩]/g, (digit) => {
            return this.englishDigits[this.arabicDigits.indexOf(digit)];
        });
        
        return text;
    }
    
    // Normalize Persian text
    normalizeText(text) {
        if (typeof text !== 'string') {
            text = String(text);
        }
        
        // Replace Arabic characters with Persian equivalents
        const arabicToPersian = {
            'ي': 'ی',  // Arabic yeh to Persian yeh
            'ك': 'ک',  // Arabic kaf to Persian kaf
            'ء': 'ٔ',  // Arabic hamza to Persian hamza
            'ة': 'ه',  // Arabic teh marbuta to Persian heh
            'ؤ': 'و',  // Arabic waw with hamza to Persian waw
            'إ': 'ا',  // Arabic alef with hamza below to Persian alef
            'أ': 'ا',  // Arabic alef with hamza above to Persian alef
            'آ': 'آ'   // Keep Persian alef with madda
        };
        
        Object.keys(arabicToPersian).forEach(arabic => {
            text = text.replace(new RegExp(arabic, 'g'), arabicToPersian[arabic]);
        });
        
        // Remove extra spaces
        text = text.replace(/\s+/g, ' ').trim();
        
        return text;
    }
    
    // Check if text is Persian
    isPersian(text) {
        if (typeof text !== 'string') return false;
        
        const persianRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
        return persianRegex.test(text);
    }
    
    // Check if text contains Persian
    containsPersian(text) {
        return this.isPersian(text);
    }
    
    // Format Persian number with thousand separators
    formatNumber(number) {
        const numStr = this.toEnglishDigits(String(number));
        const formatted = parseInt(numStr).toLocaleString('fa-IR');
        return this.toPersianDigits(formatted);
    }
    
    // Convert Gregorian date to Persian (Jalali)
    toJalaliDate(date = new Date()) {
        const gy = date.getFullYear();
        const gm = date.getMonth() + 1;
        const gd = date.getDate();
        
        // Simple Jalali conversion (approximate)
        const jy = gy - 621;
        const jm = gm;
        const jd = gd;
        
        // This is a simplified conversion - for production use a proper library
        return {
            year: jy,
            month: jm,
            day: jd,
            monthName: this.persianMonths[jm - 1],
            formatted: `${this.toPersianDigits(jd)} ${this.persianMonths[jm - 1]} ${this.toPersianDigits(jy)}`
        };
    }
    
    // Format time in Persian
    formatTime(date = new Date()) {
        const hours = this.toPersianDigits(date.getHours().toString().padStart(2, '0'));
        const minutes = this.toPersianDigits(date.getMinutes().toString().padStart(2, '0'));
        const seconds = this.toPersianDigits(date.getSeconds().toString().padStart(2, '0'));
        
        return `${hours}:${minutes}:${seconds}`;
    }
    
    // Get Persian weekday
    getPersianWeekday(date = new Date()) {
        return this.persianWeekdays[date.getDay()];
    }
    
    // Clean text for voice processing
    cleanForVoice(text) {
        if (typeof text !== 'string') return '';
        
        // Normalize text
        text = this.normalizeText(text);
        
        // Remove HTML tags
        text = text.replace(/<[^>]*>/g, '');
        
        // Remove special characters except Persian punctuation
        text = text.replace(/[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s\.\!\?\،\؛\؟]/g, '');
        
        // Replace multiple spaces with single space
        text = text.replace(/\s+/g, ' ').trim();
        
        return text;
    }
    
    // Detect text direction
    getTextDirection(text) {
        if (!text) return 'ltr';
        
        const rtlRegex = /[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]/;
        const ltrRegex = /[A-Za-z]/;
        
        const rtlCount = (text.match(rtlRegex) || []).length;
        const ltrCount = (text.match(ltrRegex) || []).length;
        
        return rtlCount > ltrCount ? 'rtl' : 'ltr';
    }
    
    // Convert English keyboard input to Persian
    convertToPersian(englishText) {
        return englishText.split('').map(char => {
            return this.persianKeyboard[char.toLowerCase()] || char;
        }).join('');
    }
    
    // Text similarity for voice recognition
    calculateSimilarity(text1, text2) {
        if (!text1 || !text2) return 0;
        
        text1 = this.normalizeText(text1.toLowerCase());
        text2 = this.normalizeText(text2.toLowerCase());
        
        if (text1 === text2) return 1;
        
        const longer = text1.length > text2.length ? text1 : text2;
        const shorter = text1.length > text2.length ? text2 : text1;
        
        if (longer.length === 0) return 1;
        
        const distance = this.levenshteinDistance(longer, shorter);
        return (longer.length - distance) / longer.length;
    }
    
    // Levenshtein distance for text similarity
    levenshteinDistance(str1, str2) {
        const matrix = [];
        
        for (let i = 0; i <= str2.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str1.length; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= str2.length; i++) {
            for (let j = 1; j <= str1.length; j++) {
                if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }
        
        return matrix[str2.length][str1.length];
    }
    
    // Extract Persian words
    extractWords(text) {
        if (!text) return [];
        
        const normalized = this.normalizeText(text);
        const words = normalized.match(/[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+/g);
        
        return words || [];
    }
    
    // Count Persian words
    countWords(text) {
        return this.extractWords(text).length;
    }
    
    // Truncate Persian text
    truncate(text, maxLength, suffix = '...') {
        if (!text || text.length <= maxLength) return text;
        
        const truncated = text.substring(0, maxLength - suffix.length);
        const lastSpace = truncated.lastIndexOf(' ');
        
        if (lastSpace > maxLength * 0.5) {
            return truncated.substring(0, lastSpace) + suffix;
        }
        
        return truncated + suffix;
    }
    
    // Validate Persian text input
    validatePersianInput(text, options = {}) {
        const {
            minLength = 0,
            maxLength = Infinity,
            allowNumbers = true,
            allowPunctuation = true,
            allowEnglish = false
        } = options;
        
        if (!text) return { valid: false, error: 'متن خالی است' };
        
        const normalized = this.normalizeText(text);
        
        if (normalized.length < minLength) {
            return { valid: false, error: `متن باید حداقل ${this.toPersianDigits(minLength)} کاراکتر باشد` };
        }
        
        if (normalized.length > maxLength) {
            return { valid: false, error: `متن نباید بیش از ${this.toPersianDigits(maxLength)} کاراکتر باشد` };
        }
        
        if (!allowNumbers && /[0-9۰-۹٠-٩]/.test(normalized)) {
            return { valid: false, error: 'استفاده از اعداد مجاز نیست' };
        }
        
        if (!allowPunctuation && /[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s]/.test(normalized)) {
            return { valid: false, error: 'استفاده از علائم نگارشی مجاز نیست' };
        }
        
        if (!allowEnglish && /[A-Za-z]/.test(normalized)) {
            return { valid: false, error: 'استفاده از حروف انگلیسی مجاز نیست' };
        }
        
        return { valid: true, text: normalized };
    }
    
    // Format Persian currency
    formatCurrency(amount, currency = 'ریال') {
        const formatted = this.formatNumber(amount);
        return `${formatted} ${currency}`;
    }
    
    // Get appropriate Persian greeting based on time
    getTimeBasedGreeting() {
        const hour = new Date().getHours();
        
        if (hour < 5) return 'شب بخیر';
        if (hour < 12) return 'صبح بخیر';
        if (hour < 17) return 'ظهر بخیر';
        if (hour < 20) return 'عصر بخیر';
        return 'شب بخیر';
    }
    
    // Check if text contains common Persian voice commands
    containsVoiceCommand(text) {
        const normalized = this.normalizeText(text.toLowerCase());
        const commands = [
            'سلام', 'استیو', 'کمک', 'بگو', 'بخوان', 'پخش کن', 'توقف',
            'صدا', 'موسیقی', 'خبر', 'هوا', 'ساعت', 'تاریخ', 'محاسبه'
        ];
        
        return commands.some(command => normalized.includes(command));
    }
}

// Persian Text Formatter
class PersianFormatter {
    constructor() {
        this.utils = new PersianUtils();
    }
    
    // Format text for display in UI
    formatForDisplay(text, options = {}) {
        const {
            convertDigits = true,
            normalizeText = true,
            truncateLength = null,
            direction = 'auto'
        } = options;
        
        if (!text) return '';
        
        let formatted = text;
        
        if (normalizeText) {
            formatted = this.utils.normalizeText(formatted);
        }
        
        if (convertDigits) {
            formatted = this.utils.toPersianDigits(formatted);
        }
        
        if (truncateLength) {
            formatted = this.utils.truncate(formatted, truncateLength);
        }
        
        return formatted;
    }
    
    // Format text for voice synthesis
    formatForVoice(text) {
        if (!text) return '';
        
        let formatted = this.utils.cleanForVoice(text);
        
        // Convert numbers to Persian digits for better pronunciation
        formatted = this.utils.toPersianDigits(formatted);
        
        // Add pronunciation hints for common abbreviations
        formatted = formatted.replace(/ص\.ب/g, 'صبح');
        formatted = formatted.replace(/ظ\.ه/g, 'ظهر');
        formatted = formatted.replace(/ع\.ص/g, 'عصر');
        formatted = formatted.replace(/ش\.ب/g, 'شب');
        
        return formatted;
    }
}

// Persian Input Handler
class PersianInputHandler {
    constructor(inputElement) {
        this.input = inputElement;
        this.utils = new PersianUtils();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        if (!this.input) return;
        
        // Auto-convert English to Persian
        this.input.addEventListener('input', (e) => {
            const cursorPosition = e.target.selectionStart;
            const convertedText = this.utils.convertToPersian(e.target.value);
            
            if (convertedText !== e.target.value) {
                e.target.value = convertedText;
                e.target.setSelectionRange(cursorPosition, cursorPosition);
            }
        });
        
        // Set RTL direction for Persian content
        this.input.addEventListener('input', (e) => {
            const direction = this.utils.getTextDirection(e.target.value);
            e.target.style.direction = direction;
            e.target.style.textAlign = direction === 'rtl' ? 'right' : 'left';
        });
    }
}

// Export for global use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PersianUtils, PersianFormatter, PersianInputHandler };
} else {
    window.PersianUtils = PersianUtils;
    window.PersianFormatter = PersianFormatter;
    window.PersianInputHandler = PersianInputHandler;
}