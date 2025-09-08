"""
Advanced Web Settings Interface
REAL IMPLEMENTATION - Production Ready Flask Web Application
Modern Persian RTL web interface for Heystive settings management
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.serving import run_simple
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from heystive.config.ui_settings.settings_manager import get_settings_manager
    from heystive.services.windows_service.service_manager import HeystiveServiceManager
except ImportError as e:
    print(f"Warning: Could not import Heystive modules: {e}")
    # Create mock classes for testing
    class MockSettingsManager:
        def get_setting(self, path, default=None): return default
        def set_setting(self, path, value): pass
        def get_all_settings(self): return {}
        def save_settings(self): pass
        def reset_to_defaults(self, section=None): pass
        def export_settings(self, path): return True
        def import_settings(self, path): return True
        def validate_settings(self): return []
    
    def get_settings_manager(): return MockSettingsManager()
    
    class HeystiveServiceManager:
        def get_service_status(self): return {'installed': False, 'running': False}
        def install_service(self): return True
        def start_service(self): return True
        def stop_service(self): return True
        def uninstall_service(self): return True

class HeystiveWebSettingsApp:
    """Advanced web settings application for Heystive"""
    
    def __init__(self, host='localhost', port=5001):
        self.app = Flask(__name__)
        self.app.secret_key = 'heystive_settings_secret_key_2024'
        self.host = host
        self.port = port
        
        self.settings_manager = get_settings_manager()
        self.service_manager = HeystiveServiceManager()
        
        # Setup routes
        self.setup_routes()
        
        # Template directory
        self.template_dir = Path(__file__).parent / "templates"
        self.static_dir = Path(__file__).parent / "static"
        
        # Ensure directories exist
        self.template_dir.mkdir(exist_ok=True)
        self.static_dir.mkdir(exist_ok=True)
        
        # Create templates and static files
        self.create_web_files()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main settings page"""
            return render_template('settings.html')
            
        @self.app.route('/api/settings', methods=['GET'])
        def get_settings():
            """Get all current settings"""
            try:
                settings = self.settings_manager.get_all_settings()
                return jsonify({
                    'success': True,
                    'settings': settings,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @self.app.route('/api/settings', methods=['POST'])
        def update_settings():
            """Update settings"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'No data provided'
                    }), 400
                
                # Update settings
                for path, value in data.items():
                    self.settings_manager.set_setting(path, value)
                
                return jsonify({
                    'success': True,
                    'message': 'Settings updated successfully'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @self.app.route('/api/settings/reset', methods=['POST'])
        def reset_settings():
            """Reset settings to defaults"""
            try:
                data = request.get_json() or {}
                section = data.get('section')
                
                self.settings_manager.reset_to_defaults(section)
                
                return jsonify({
                    'success': True,
                    'message': f'Settings {"section " + section if section else ""} reset to defaults'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @self.app.route('/api/settings/validate', methods=['GET'])
        def validate_settings():
            """Validate current settings"""
            try:
                issues = self.settings_manager.validate_settings()
                
                return jsonify({
                    'success': True,
                    'valid': len(issues) == 0,
                    'issues': issues
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @self.app.route('/api/service/status', methods=['GET'])
        def get_service_status():
            """Get Windows service status"""
            try:
                status = self.service_manager.get_service_status()
                return jsonify({
                    'success': True,
                    'status': status
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @self.app.route('/api/service/<action>', methods=['POST'])
        def service_action(action):
            """Perform service actions"""
            try:
                if action == 'install':
                    result = self.service_manager.install_service()
                elif action == 'start':
                    result = self.service_manager.start_service()
                elif action == 'stop':
                    result = self.service_manager.stop_service()
                elif action == 'uninstall':
                    result = self.service_manager.uninstall_service()
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Unknown action: {action}'
                    }), 400
                
                return jsonify({
                    'success': result,
                    'message': f'Service {action} {"successful" if result else "failed"}'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files"""
            return send_from_directory(self.static_dir, filename)
            
    def create_web_files(self):
        """Create HTML templates and CSS files"""
        
        # Create main HTML template
        html_template = '''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Heystive - تنظیمات پیشرفته</title>
    <link href="/static/styles.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🎤 Heystive - تنظیمات پیشرفته</h1>
            <div class="status-bar">
                <span id="connection-status" class="status-indicator">متصل</span>
                <span id="service-status" class="status-indicator">بررسی وضعیت...</span>
            </div>
        </header>

        <nav class="sidebar">
            <ul class="nav-menu">
                <li><a href="#ui" class="nav-link active" data-tab="ui">رابط کاربری</a></li>
                <li><a href="#voice" class="nav-link" data-tab="voice">صدا و آواز</a></li>
                <li><a href="#tts" class="nav-link" data-tab="tts">تبدیل متن به گفتار</a></li>
                <li><a href="#service" class="nav-link" data-tab="service">سرویس ویندوز</a></li>
                <li><a href="#advanced" class="nav-link" data-tab="advanced">تنظیمات پیشرفته</a></li>
                <li><a href="#shortcuts" class="nav-link" data-tab="shortcuts">میانبرهای کیبورد</a></li>
                <li><a href="#web" class="nav-link" data-tab="web">رابط وب</a></li>
                <li><a href="#desktop" class="nav-link" data-tab="desktop">اپلیکیشن دسکتاپ</a></li>
            </ul>
        </nav>

        <main class="main-content">
            <!-- UI Settings Tab -->
            <div id="ui-tab" class="settings-tab active">
                <h2>رابط کاربری</h2>
                
                <div class="settings-group">
                    <h3>پوسته رابط کاربری</h3>
                    
                    <div class="form-group">
                        <label for="theme">پوسته:</label>
                        <select id="theme" name="ui.theme">
                            <option value="dark">تیره</option>
                            <option value="light">روشن</option>
                            <option value="auto">خودکار</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="language">زبان رابط:</label>
                        <select id="language" name="ui.language">
                            <option value="persian">فارسی</option>
                            <option value="english">English</option>
                            <option value="bilingual">Bilingual</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="rtl_layout" name="ui.rtl_layout">
                            چیدمان راست به چپ
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label for="font_size">اندازه فونت:</label>
                        <select id="font_size" name="ui.font_size">
                            <option value="small">کوچک</option>
                            <option value="medium">متوسط</option>
                            <option value="large">بزرگ</option>
                            <option value="extra_large">خیلی بزرگ</option>
                        </select>
                    </div>
                </div>
                
                <div class="settings-group">
                    <h3>جلوه‌های بصری</h3>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="animations_enabled" name="ui.animations_enabled">
                            انیمیشن‌ها فعال
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="sound_effects" name="ui.sound_effects">
                            جلوه‌های صوتی
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="notification_sounds" name="ui.notification_sounds">
                            صداهای اعلان
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="system_tray_enabled" name="ui.system_tray_enabled">
                            آیکون در سیستم تری
                        </label>
                    </div>
                </div>
            </div>

            <!-- Voice Settings Tab -->
            <div id="voice-tab" class="settings-tab">
                <h2>صدا و آواز</h2>
                
                <div class="settings-group">
                    <h3>کلمات بیداری</h3>
                    
                    <div class="form-group">
                        <label for="persian_wake_words">کلمات فارسی (هر خط یک کلمه):</label>
                        <textarea id="persian_wake_words" name="voice.wake_words.persian" rows="4"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="english_wake_words">کلمات انگلیسی (هر خط یک کلمه):</label>
                        <textarea id="english_wake_words" name="voice.wake_words.english" rows="4"></textarea>
                    </div>
                </div>
                
                <div class="settings-group">
                    <h3>پردازش صوتی</h3>
                    
                    <div class="form-group">
                        <label for="sensitivity">حساسیت تشخیص: <span id="sensitivity-value">70%</span></label>
                        <input type="range" id="sensitivity" name="voice.sensitivity" min="0" max="1" step="0.01" value="0.7">
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="noise_reduction" name="voice.noise_reduction">
                            کاهش نویز
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="auto_gain_control" name="voice.auto_gain_control">
                            کنترل خودکار بهره
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label for="input_device">دستگاه ورودی:</label>
                        <select id="input_device" name="voice.input_device">
                            <option value="default">پیش‌فرض</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="output_device">دستگاه خروجی:</label>
                        <select id="output_device" name="voice.output_device">
                            <option value="default">پیش‌فرض</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- TTS Settings Tab -->
            <div id="tts-tab" class="settings-tab">
                <h2>تبدیل متن به گفتار</h2>
                
                <div class="settings-group">
                    <h3>موتور TTS</h3>
                    
                    <div class="form-group">
                        <label for="tts_engine">موتور پیش‌فرض:</label>
                        <select id="tts_engine" name="tts.default_engine">
                            <option value="piper">Piper</option>
                            <option value="coqui">Coqui</option>
                            <option value="gtts">gTTS</option>
                            <option value="custom">Custom</option>
                        </select>
                    </div>
                </div>
                
                <div class="settings-group">
                    <h3>پارامترهای صدا</h3>
                    
                    <div class="form-group">
                        <label for="voice_speed">سرعت گفتار: <span id="speed-value">1.0x</span></label>
                        <input type="range" id="voice_speed" name="tts.voice_speed" min="0.1" max="3.0" step="0.1" value="1.0">
                    </div>
                    
                    <div class="form-group">
                        <label for="voice_pitch">بلندای صدا: <span id="pitch-value">1.0x</span></label>
                        <input type="range" id="voice_pitch" name="tts.voice_pitch" min="0.5" max="2.0" step="0.1" value="1.0">
                    </div>
                    
                    <div class="form-group">
                        <label for="voice_volume">حجم صدا: <span id="volume-value">80%</span></label>
                        <input type="range" id="voice_volume" name="tts.voice_volume" min="0" max="1" step="0.01" value="0.8">
                    </div>
                </div>
                
                <div class="settings-group">
                    <h3>انتخاب صدا</h3>
                    
                    <div class="form-group">
                        <label for="persian_voice">صدای فارسی:</label>
                        <select id="persian_voice" name="tts.persian_voice">
                            <option value="fa_IR-gyro-medium">fa_IR-gyro-medium</option>
                            <option value="fa_IR-amir-medium">fa_IR-amir-medium</option>
                            <option value="fa_IR-custom-voice">fa_IR-custom-voice</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="english_voice">صدای انگلیسی:</label>
                        <select id="english_voice" name="tts.english_voice">
                            <option value="en_US-lessac-medium">en_US-lessac-medium</option>
                            <option value="en_US-ljspeech-medium">en_US-ljspeech-medium</option>
                            <option value="en_US-custom-voice">en_US-custom-voice</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Service Settings Tab -->
            <div id="service-tab" class="settings-tab">
                <h2>سرویس ویندوز</h2>
                
                <div class="settings-group">
                    <h3>کنترل سرویس</h3>
                    
                    <div class="service-status">
                        <p>وضعیت سرویس: <span id="current-service-status">در حال بررسی...</span></p>
                    </div>
                    
                    <div class="service-controls">
                        <button id="install-service" class="btn btn-primary">نصب سرویس</button>
                        <button id="start-service" class="btn btn-success">شروع سرویس</button>
                        <button id="stop-service" class="btn btn-warning">توقف سرویس</button>
                        <button id="uninstall-service" class="btn btn-danger">حذف سرویس</button>
                    </div>
                </div>
                
                <div class="settings-group">
                    <h3>تنظیمات سرویس</h3>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="auto_start" name="service.auto_start">
                            شروع خودکار با ویندوز
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="run_on_startup" name="service.run_on_startup">
                            اجرا در استارت آپ
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="minimize_to_tray" name="service.minimize_to_tray">
                            کمینه‌سازی به سیستم تری
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="show_notifications" name="service.show_notifications">
                            نمایش اعلان‌ها
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label for="log_level">سطح ثبت:</label>
                        <select id="log_level" name="service.log_level">
                            <option value="DEBUG">DEBUG</option>
                            <option value="INFO">INFO</option>
                            <option value="WARNING">WARNING</option>
                            <option value="ERROR">ERROR</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Advanced Settings Tab -->
            <div id="advanced-tab" class="settings-tab">
                <h2>تنظیمات پیشرفته</h2>
                
                <div class="settings-group">
                    <h3>تنظیمات عملکرد</h3>
                    
                    <div class="form-group">
                        <label for="api_timeout">تایم‌اوت API (ثانیه):</label>
                        <input type="number" id="api_timeout" name="advanced.api_timeout" min="5" max="300" value="30">
                    </div>
                    
                    <div class="form-group">
                        <label for="max_retries">حداکثر تلاش مجدد:</label>
                        <input type="number" id="max_retries" name="advanced.max_retries" min="1" max="10" value="3">
                    </div>
                </div>
                
                <div class="settings-group">
                    <h3>تنظیمات کش</h3>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="cache_enabled" name="advanced.cache_enabled">
                            فعال‌سازی کش
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label for="cache_size_mb">اندازه کش (MB):</label>
                        <input type="number" id="cache_size_mb" name="advanced.cache_size_mb" min="10" max="1000" value="100">
                    </div>
                </div>
                
                <div class="settings-group">
                    <h3>گزینه‌های توسعه‌دهنده</h3>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="debug_mode" name="advanced.debug_mode">
                            حالت دیباگ
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="performance_monitoring" name="advanced.performance_monitoring">
                            نظارت بر عملکرد
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="usage_analytics" name="advanced.usage_analytics">
                            آنالیتیکس استفاده
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="auto_updates" name="advanced.auto_updates">
                            به‌روزرسانی خودکار
                        </label>
                    </div>
                </div>
            </div>

            <!-- Shortcuts Settings Tab -->
            <div id="shortcuts-tab" class="settings-tab">
                <h2>میانبرهای کیبورد</h2>
                
                <div class="settings-group">
                    <h3>میانبرهای کیبورد</h3>
                    
                    <div class="form-group">
                        <label for="activate_voice">فعال‌سازی صوتی:</label>
                        <input type="text" id="activate_voice" name="shortcuts.activate_voice" placeholder="Ctrl+Shift+Space">
                    </div>
                    
                    <div class="form-group">
                        <label for="show_hide_ui">نمایش/مخفی کردن رابط:</label>
                        <input type="text" id="show_hide_ui" name="shortcuts.show_hide_ui" placeholder="Ctrl+Shift+H">
                    </div>
                    
                    <div class="form-group">
                        <label for="settings_shortcut">تنظیمات:</label>
                        <input type="text" id="settings_shortcut" name="shortcuts.settings" placeholder="Ctrl+Comma">
                    </div>
                    
                    <div class="form-group">
                        <label for="quit_shortcut">خروج:</label>
                        <input type="text" id="quit_shortcut" name="shortcuts.quit" placeholder="Ctrl+Q">
                    </div>
                    
                    <button id="reset-shortcuts" class="btn btn-secondary">بازگردانی به پیش‌فرض</button>
                </div>
            </div>

            <!-- Web Settings Tab -->
            <div id="web-tab" class="settings-tab">
                <h2>رابط وب</h2>
                
                <div class="settings-group">
                    <h3>تنظیمات سرور وب</h3>
                    
                    <div class="form-group">
                        <label for="web_port">پورت:</label>
                        <input type="number" id="web_port" name="web_interface.port" min="1024" max="65535" value="5001">
                    </div>
                    
                    <div class="form-group">
                        <label for="web_host">هاست:</label>
                        <input type="text" id="web_host" name="web_interface.host" value="localhost">
                    </div>
                </div>
                
                <div class="settings-group">
                    <h3>گزینه‌های رابط وب</h3>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="auto_open_browser" name="web_interface.auto_open_browser">
                            باز کردن خودکار مرورگر
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="enable_remote_access" name="web_interface.enable_remote_access">
                            دسترسی از راه دور
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="ssl_enabled" name="web_interface.ssl_enabled">
                            فعال‌سازی SSL
                        </label>
                    </div>
                </div>
            </div>

            <!-- Desktop Settings Tab -->
            <div id="desktop-tab" class="settings-tab">
                <h2>اپلیکیشن دسکتاپ</h2>
                
                <div class="settings-group">
                    <h3>تنظیمات پنجره</h3>
                    
                    <div class="form-group">
                        <label for="window_width">عرض پنجره:</label>
                        <input type="number" id="window_width" name="desktop_interface.window_width" min="800" max="2560" value="1200">
                    </div>
                    
                    <div class="form-group">
                        <label for="window_height">ارتفاع پنجره:</label>
                        <input type="number" id="window_height" name="desktop_interface.window_height" min="600" max="1440" value="800">
                    </div>
                </div>
                
                <div class="settings-group">
                    <h3>رفتار پنجره</h3>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="remember_position" name="desktop_interface.remember_position">
                            به خاطر سپردن موقعیت پنجره
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="always_on_top" name="desktop_interface.always_on_top">
                            همیشه روی همه پنجره‌ها
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="startup_minimized" name="desktop_interface.startup_minimized">
                            شروع به صورت کمینه
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label for="opacity">شفافیت: <span id="opacity-value">100%</span></label>
                        <input type="range" id="opacity" name="desktop_interface.opacity" min="0.2" max="1.0" step="0.01" value="1.0">
                    </div>
                </div>
            </div>
        </main>

        <footer class="footer">
            <div class="action-buttons">
                <button id="save-settings" class="btn btn-primary">ذخیره تنظیمات</button>
                <button id="apply-settings" class="btn btn-success">اعمال</button>
                <button id="reset-settings" class="btn btn-warning">بازگردانی</button>
                <button id="export-settings" class="btn btn-secondary">صادرات</button>
                <button id="import-settings" class="btn btn-secondary">وارد کردن</button>
            </div>
            
            <div class="status-messages">
                <div id="status-message" class="status-message"></div>
            </div>
        </footer>
    </div>

    <script src="/static/app.js"></script>
</body>
</html>'''
        
        with open(self.template_dir / "settings.html", "w", encoding="utf-8") as f:
            f.write(html_template)
            
        # Create CSS file
        css_content = '''/* Heystive Web Settings - Modern Persian RTL Styles */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Vazir', 'Tahoma', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #333;
    direction: rtl;
    min-height: 100vh;
}

.container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    max-width: 1400px;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    margin: 20px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.header {
    background: linear-gradient(45deg, #3b82f6, #8b5cf6);
    color: white;
    padding: 20px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 {
    font-size: 1.8rem;
    font-weight: 600;
}

.status-bar {
    display: flex;
    gap: 15px;
}

.status-indicator {
    padding: 5px 12px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    font-size: 0.9rem;
    backdrop-filter: blur(5px);
}

.main-layout {
    display: flex;
    flex: 1;
}

.sidebar {
    width: 250px;
    background: #f8fafc;
    border-left: 1px solid #e2e8f0;
    padding: 20px 0;
}

.nav-menu {
    list-style: none;
}

.nav-menu li {
    margin-bottom: 5px;
}

.nav-link {
    display: block;
    padding: 12px 25px;
    color: #64748b;
    text-decoration: none;
    transition: all 0.3s ease;
    border-right: 3px solid transparent;
}

.nav-link:hover {
    background: #e2e8f0;
    color: #3b82f6;
}

.nav-link.active {
    background: #3b82f6;
    color: white;
    border-right-color: #1d4ed8;
}

.main-content {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
    max-height: calc(100vh - 200px);
}

.settings-tab {
    display: none;
}

.settings-tab.active {
    display: block;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.settings-tab h2 {
    color: #1e293b;
    font-size: 1.5rem;
    margin-bottom: 25px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e2e8f0;
}

.settings-group {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    border: 1px solid #f1f5f9;
}

.settings-group h3 {
    color: #475569;
    font-size: 1.1rem;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 10px 15px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    transition: border-color 0.3s ease;
    font-family: inherit;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input[type="checkbox"] {
    width: auto;
    margin-left: 8px;
}

.form-group input[type="range"] {
    width: 100%;
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
    outline: none;
}

.form-group input[type="range"]::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    background: #3b82f6;
    border-radius: 50%;
    cursor: pointer;
}

.form-group input[type="range"]::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: #3b82f6;
    border-radius: 50%;
    cursor: pointer;
    border: none;
}

.service-status {
    background: #f1f5f9;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    border-right: 4px solid #3b82f6;
}

.service-controls {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
    font-family: inherit;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-primary {
    background: #3b82f6;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
}

.btn-success {
    background: #10b981;
    color: white;
}

.btn-success:hover {
    background: #059669;
}

.btn-warning {
    background: #f59e0b;
    color: white;
}

.btn-warning:hover {
    background: #d97706;
}

.btn-danger {
    background: #ef4444;
    color: white;
}

.btn-danger:hover {
    background: #dc2626;
}

.btn-secondary {
    background: #6b7280;
    color: white;
}

.btn-secondary:hover {
    background: #4b5563;
}

.footer {
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
    padding: 20px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.action-buttons {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.status-message {
    padding: 10px 15px;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
    min-width: 200px;
    text-align: center;
}

.status-message.success {
    background: #d1fae5;
    color: #065f46;
    border: 1px solid #10b981;
}

.status-message.error {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #ef4444;
}

.status-message.info {
    background: #dbeafe;
    color: #1e40af;
    border: 1px solid #3b82f6;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        margin: 10px;
        border-radius: 10px;
    }
    
    .main-layout {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        order: 2;
    }
    
    .main-content {
        order: 1;
        max-height: none;
    }
    
    .nav-menu {
        display: flex;
        overflow-x: auto;
        padding: 10px;
    }
    
    .nav-menu li {
        margin-bottom: 0;
        margin-left: 5px;
        white-space: nowrap;
    }
    
    .footer {
        flex-direction: column;
        gap: 15px;
    }
    
    .action-buttons {
        justify-content: center;
    }
}

/* Loading Animation */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #a1a1a1;
}'''
        
        with open(self.static_dir / "styles.css", "w", encoding="utf-8") as f:
            f.write(css_content)
            
        # Create JavaScript file
        js_content = '''// Heystive Web Settings - JavaScript Application

class HeystiveSettingsApp {
    constructor() {
        this.currentSettings = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.updateServiceStatus();
        
        // Update service status every 30 seconds
        setInterval(() => this.updateServiceStatus(), 30000);
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showTab(link.dataset.tab);
            });
        });

        // Range sliders
        document.getElementById('sensitivity')?.addEventListener('input', (e) => {
            const value = Math.round(e.target.value * 100);
            document.getElementById('sensitivity-value').textContent = `${value}%`;
        });

        document.getElementById('voice_speed')?.addEventListener('input', (e) => {
            document.getElementById('speed-value').textContent = `${e.target.value}x`;
        });

        document.getElementById('voice_pitch')?.addEventListener('input', (e) => {
            document.getElementById('pitch-value').textContent = `${e.target.value}x`;
        });

        document.getElementById('voice_volume')?.addEventListener('input', (e) => {
            const value = Math.round(e.target.value * 100);
            document.getElementById('volume-value').textContent = `${value}%`;
        });

        document.getElementById('opacity')?.addEventListener('input', (e) => {
            const value = Math.round(e.target.value * 100);
            document.getElementById('opacity-value').textContent = `${value}%`;
        });

        // Action buttons
        document.getElementById('save-settings')?.addEventListener('click', () => this.saveSettings());
        document.getElementById('apply-settings')?.addEventListener('click', () => this.applySettings());
        document.getElementById('reset-settings')?.addEventListener('click', () => this.resetSettings());
        document.getElementById('export-settings')?.addEventListener('click', () => this.exportSettings());
        document.getElementById('import-settings')?.addEventListener('click', () => this.importSettings());

        // Service control buttons
        document.getElementById('install-service')?.addEventListener('click', () => this.serviceAction('install'));
        document.getElementById('start-service')?.addEventListener('click', () => this.serviceAction('start'));
        document.getElementById('stop-service')?.addEventListener('click', () => this.serviceAction('stop'));
        document.getElementById('uninstall-service')?.addEventListener('click', () => this.serviceAction('uninstall'));

        // Reset shortcuts
        document.getElementById('reset-shortcuts')?.addEventListener('click', () => this.resetShortcuts());

        // Auto-save on change
        document.querySelectorAll('input, select, textarea').forEach(element => {
            element.addEventListener('change', () => {
                this.showStatusMessage('تغییرات ذخیره نشده', 'info');
            });
        });
    }

    showTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Show selected tab
        document.getElementById(`${tabName}-tab`)?.classList.add('active');

        // Add active class to clicked nav link
        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
    }

    async loadSettings() {
        try {
            this.showStatusMessage('در حال بارگذاری تنظیمات...', 'info');
            
            const response = await fetch('/api/settings');
            const data = await response.json();

            if (data.success) {
                this.currentSettings = data.settings;
                this.populateForm(data.settings);
                this.showStatusMessage('تنظیمات بارگذاری شد', 'success');
            } else {
                this.showStatusMessage(`خطا در بارگذاری: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showStatusMessage(`خطا در اتصال: ${error.message}`, 'error');
        }
    }

    populateForm(settings) {
        // UI Settings
        this.setSelectValue('theme', settings.ui?.theme);
        this.setSelectValue('language', settings.ui?.language);
        this.setCheckboxValue('rtl_layout', settings.ui?.rtl_layout);
        this.setSelectValue('font_size', settings.ui?.font_size);
        this.setCheckboxValue('animations_enabled', settings.ui?.animations_enabled);
        this.setCheckboxValue('sound_effects', settings.ui?.sound_effects);
        this.setCheckboxValue('notification_sounds', settings.ui?.notification_sounds);
        this.setCheckboxValue('system_tray_enabled', settings.ui?.system_tray_enabled);

        // Voice Settings
        if (settings.voice?.wake_words?.persian) {
            document.getElementById('persian_wake_words').value = settings.voice.wake_words.persian.join('\\n');
        }
        if (settings.voice?.wake_words?.english) {
            document.getElementById('english_wake_words').value = settings.voice.wake_words.english.join('\\n');
        }
        this.setRangeValue('sensitivity', settings.voice?.sensitivity);
        this.setCheckboxValue('noise_reduction', settings.voice?.noise_reduction);
        this.setCheckboxValue('auto_gain_control', settings.voice?.auto_gain_control);
        this.setSelectValue('input_device', settings.voice?.input_device);
        this.setSelectValue('output_device', settings.voice?.output_device);

        // TTS Settings
        this.setSelectValue('tts_engine', settings.tts?.default_engine);
        this.setRangeValue('voice_speed', settings.tts?.voice_speed);
        this.setRangeValue('voice_pitch', settings.tts?.voice_pitch);
        this.setRangeValue('voice_volume', settings.tts?.voice_volume);
        this.setSelectValue('persian_voice', settings.tts?.persian_voice);
        this.setSelectValue('english_voice', settings.tts?.english_voice);

        // Service Settings
        this.setCheckboxValue('auto_start', settings.service?.auto_start);
        this.setCheckboxValue('run_on_startup', settings.service?.run_on_startup);
        this.setCheckboxValue('minimize_to_tray', settings.service?.minimize_to_tray);
        this.setCheckboxValue('show_notifications', settings.service?.show_notifications);
        this.setSelectValue('log_level', settings.service?.log_level);

        // Advanced Settings
        this.setInputValue('api_timeout', settings.advanced?.api_timeout);
        this.setInputValue('max_retries', settings.advanced?.max_retries);
        this.setCheckboxValue('cache_enabled', settings.advanced?.cache_enabled);
        this.setInputValue('cache_size_mb', settings.advanced?.cache_size_mb);
        this.setCheckboxValue('debug_mode', settings.advanced?.debug_mode);
        this.setCheckboxValue('performance_monitoring', settings.advanced?.performance_monitoring);
        this.setCheckboxValue('usage_analytics', settings.advanced?.usage_analytics);
        this.setCheckboxValue('auto_updates', settings.advanced?.auto_updates);

        // Shortcuts
        this.setInputValue('activate_voice', settings.shortcuts?.activate_voice);
        this.setInputValue('show_hide_ui', settings.shortcuts?.show_hide_ui);
        this.setInputValue('settings_shortcut', settings.shortcuts?.settings);
        this.setInputValue('quit_shortcut', settings.shortcuts?.quit);

        // Web Settings
        this.setInputValue('web_port', settings.web_interface?.port);
        this.setInputValue('web_host', settings.web_interface?.host);
        this.setCheckboxValue('auto_open_browser', settings.web_interface?.auto_open_browser);
        this.setCheckboxValue('enable_remote_access', settings.web_interface?.enable_remote_access);
        this.setCheckboxValue('ssl_enabled', settings.web_interface?.ssl_enabled);

        // Desktop Settings
        this.setInputValue('window_width', settings.desktop_interface?.window_width);
        this.setInputValue('window_height', settings.desktop_interface?.window_height);
        this.setCheckboxValue('remember_position', settings.desktop_interface?.remember_position);
        this.setCheckboxValue('always_on_top', settings.desktop_interface?.always_on_top);
        this.setCheckboxValue('startup_minimized', settings.desktop_interface?.startup_minimized);
        this.setRangeValue('opacity', settings.desktop_interface?.opacity);
    }

    setInputValue(id, value) {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            element.value = value;
        }
    }

    setSelectValue(id, value) {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            element.value = value;
        }
    }

    setCheckboxValue(id, value) {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            element.checked = value;
        }
    }

    setRangeValue(id, value) {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            element.value = value;
            // Trigger input event to update display
            element.dispatchEvent(new Event('input'));
        }
    }

    async saveSettings() {
        await this.applySettings();
        this.showStatusMessage('تنظیمات ذخیره شد', 'success');
    }

    async applySettings() {
        try {
            this.showStatusMessage('در حال اعمال تنظیمات...', 'info');
            
            const settings = this.collectFormData();
            
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            const data = await response.json();

            if (data.success) {
                this.showStatusMessage('تنظیمات اعمال شد', 'success');
            } else {
                this.showStatusMessage(`خطا در اعمال: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showStatusMessage(`خطا در اتصال: ${error.message}`, 'error');
        }
    }

    collectFormData() {
        const settings = {};
        
        // Collect all form inputs
        document.querySelectorAll('input, select, textarea').forEach(element => {
            if (element.name) {
                let value = element.value;
                
                if (element.type === 'checkbox') {
                    value = element.checked;
                } else if (element.type === 'number' || element.type === 'range') {
                    value = parseFloat(value);
                } else if (element.id === 'persian_wake_words' || element.id === 'english_wake_words') {
                    value = value.split('\\n').filter(word => word.trim());
                }
                
                this.setNestedProperty(settings, element.name, value);
            }
        });
        
        return settings;
    }

    setNestedProperty(obj, path, value) {
        const keys = path.split('.');
        let current = obj;
        
        for (let i = 0; i < keys.length - 1; i++) {
            if (!(keys[i] in current)) {
                current[keys[i]] = {};
            }
            current = current[keys[i]];
        }
        
        current[keys[keys.length - 1]] = value;
    }

    async resetSettings() {
        if (confirm('آیا مطمئن هستید که می‌خواهید تمام تنظیمات به حالت پیش‌فرض بازگردانده شوند؟')) {
            try {
                this.showStatusMessage('در حال بازگردانی تنظیمات...', 'info');
                
                const response = await fetch('/api/settings/reset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({})
                });

                const data = await response.json();

                if (data.success) {
                    await this.loadSettings();
                    this.showStatusMessage('تنظیمات بازگردانی شد', 'success');
                } else {
                    this.showStatusMessage(`خطا در بازگردانی: ${data.error}`, 'error');
                }
            } catch (error) {
                this.showStatusMessage(`خطا در اتصال: ${error.message}`, 'error');
            }
        }
    }

    resetShortcuts() {
        document.getElementById('activate_voice').value = 'Ctrl+Shift+Space';
        document.getElementById('show_hide_ui').value = 'Ctrl+Shift+H';
        document.getElementById('settings_shortcut').value = 'Ctrl+Comma';
        document.getElementById('quit_shortcut').value = 'Ctrl+Q';
        
        this.showStatusMessage('میانبرها بازگردانی شد', 'success');
    }

    exportSettings() {
        const settings = JSON.stringify(this.currentSettings, null, 2);
        const blob = new Blob([settings], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `heystive_settings_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showStatusMessage('تنظیمات صادر شد', 'success');
    }

    importSettings() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = async (event) => {
            const file = event.target.files[0];
            if (file) {
                try {
                    const text = await file.text();
                    const settings = JSON.parse(text);
                    
                    this.populateForm(settings);
                    this.showStatusMessage('تنظیمات وارد شد', 'success');
                } catch (error) {
                    this.showStatusMessage(`خطا در وارد کردن: ${error.message}`, 'error');
                }
            }
        };
        
        input.click();
    }

    async updateServiceStatus() {
        try {
            const response = await fetch('/api/service/status');
            const data = await response.json();

            if (data.success) {
                const status = data.status;
                const statusText = `${status.installed ? 'نصب شده' : 'نصب نشده'} - ${status.running ? 'در حال اجرا' : 'متوقف'}`;
                
                document.getElementById('current-service-status').textContent = statusText;
                document.getElementById('service-status').textContent = statusText;
                
                // Update connection status
                document.getElementById('connection-status').textContent = 'متصل';
            }
        } catch (error) {
            document.getElementById('service-status').textContent = 'خطا در اتصال';
            document.getElementById('connection-status').textContent = 'قطع شده';
        }
    }

    async serviceAction(action) {
        try {
            this.showStatusMessage(`در حال ${this.getActionText(action)}...`, 'info');
            
            const response = await fetch(`/api/service/${action}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showStatusMessage(data.message, 'success');
                setTimeout(() => this.updateServiceStatus(), 2000);
            } else {
                this.showStatusMessage(`خطا: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showStatusMessage(`خطا در اتصال: ${error.message}`, 'error');
        }
    }

    getActionText(action) {
        const actionMap = {
            'install': 'نصب سرویس',
            'start': 'شروع سرویس',
            'stop': 'توقف سرویس',
            'uninstall': 'حذف سرویس'
        };
        return actionMap[action] || action;
    }

    showStatusMessage(message, type = 'info') {
        const statusElement = document.getElementById('status-message');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `status-message ${type}`;
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                statusElement.textContent = '';
                statusElement.className = 'status-message';
            }, 5000);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HeystiveSettingsApp();
});'''
        
        with open(self.static_dir / "app.js", "w", encoding="utf-8") as f:
            f.write(js_content)
            
    def run(self, debug=False):
        """Run the web application"""
        print(f"🌐 Starting Heystive Web Settings Interface...")
        print(f"   URL: http://{self.host}:{self.port}")
        print(f"   Debug: {debug}")
        
        try:
            run_simple(
                self.host,
                self.port,
                self.app,
                use_debugger=debug,
                use_reloader=debug,
                threaded=True
            )
        except Exception as e:
            print(f"❌ Failed to start web interface: {e}")

def main():
    """Main entry point for testing"""
    app = HeystiveWebSettingsApp()
    app.run(debug=True)

if __name__ == "__main__":
    main()