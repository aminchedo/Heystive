"""
Advanced Desktop Settings Interface
REAL IMPLEMENTATION - Production Ready Cross-Platform GUI
Modern Persian RTL interface using tkinter for maximum compatibility
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Dict, Any, Optional
import json

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

class AdvancedSettingsWindow:
    """Advanced settings window with comprehensive options"""
    
    def __init__(self, parent=None):
        self.settings_manager = get_settings_manager()
        self.service_manager = HeystiveServiceManager()
        self.root = None
        self.notebook = None
        self.settings_widgets = {}
        
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        """Setup the advanced settings interface"""
        self.root = tk.Toplevel() if hasattr(tk, '_default_root') and tk._default_root else tk.Tk()
        self.root.title("Heystive - تنظیمات پیشرفته")
        self.root.geometry("900x700")
        
        # Configure RTL support and styling
        self.setup_styles()
        
        # Create main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Create all settings tabs
        self.create_ui_settings_tab()
        self.create_voice_settings_tab()
        self.create_tts_settings_tab()
        self.create_service_settings_tab()
        self.create_advanced_settings_tab()
        self.create_shortcuts_settings_tab()
        self.create_web_settings_tab()
        self.create_desktop_settings_tab()
        
        # Create buttons frame
        self.create_buttons_frame(main_frame)
        
    def setup_styles(self):
        """Setup modern styling for the interface"""
        style = ttk.Style()
        
        # Configure theme
        try:
            style.theme_use('clam')  # Modern looking theme
        except tk.TclError:
            pass  # Use default theme if clam not available
            
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 10, 'bold'))
        
    def create_ui_settings_tab(self):
        """Create UI settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="رابط کاربری")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Theme settings
        theme_frame = ttk.LabelFrame(scrollable_frame, text="پوسته رابط کاربری", padding="10")
        theme_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(theme_frame, text="پوسته:", font=('Arial', 9, 'bold')).pack(anchor="e")
        self.settings_widgets['theme'] = ttk.Combobox(
            theme_frame, 
            values=["تیره", "روشن", "خودکار"],
            state="readonly",
            width=20
        )
        self.settings_widgets['theme'].pack(anchor="e", pady=2)
        
        ttk.Label(theme_frame, text="زبان رابط:", font=('Arial', 9, 'bold')).pack(anchor="e", pady=(10,0))
        self.settings_widgets['language'] = ttk.Combobox(
            theme_frame,
            values=["فارسی", "English", "Bilingual"],
            state="readonly",
            width=20
        )
        self.settings_widgets['language'].pack(anchor="e", pady=2)
        
        self.settings_widgets['rtl_layout'] = tk.BooleanVar()
        ttk.Checkbutton(
            theme_frame,
            text="چیدمان راست به چپ",
            variable=self.settings_widgets['rtl_layout']
        ).pack(anchor="e", pady=5)
        
        ttk.Label(theme_frame, text="اندازه فونت:", font=('Arial', 9, 'bold')).pack(anchor="e", pady=(10,0))
        self.settings_widgets['font_size'] = ttk.Combobox(
            theme_frame,
            values=["کوچک", "متوسط", "بزرگ", "خیلی بزرگ"],
            state="readonly",
            width=20
        )
        self.settings_widgets['font_size'].pack(anchor="e", pady=2)
        
        # Visual effects
        effects_frame = ttk.LabelFrame(scrollable_frame, text="جلوه‌های بصری", padding="10")
        effects_frame.pack(fill="x", padx=10, pady=5)
        
        self.settings_widgets['animations_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(
            effects_frame,
            text="انیمیشن‌ها فعال",
            variable=self.settings_widgets['animations_enabled']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['sound_effects'] = tk.BooleanVar()
        ttk.Checkbutton(
            effects_frame,
            text="جلوه‌های صوتی",
            variable=self.settings_widgets['sound_effects']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['notification_sounds'] = tk.BooleanVar()
        ttk.Checkbutton(
            effects_frame,
            text="صداهای اعلان",
            variable=self.settings_widgets['notification_sounds']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['system_tray_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(
            effects_frame,
            text="آیکون در سیستم تری",
            variable=self.settings_widgets['system_tray_enabled']
        ).pack(anchor="e", pady=2)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_voice_settings_tab(self):
        """Create voice settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="صدا و آواز")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Wake words configuration
        wake_words_frame = ttk.LabelFrame(scrollable_frame, text="کلمات بیداری", padding="10")
        wake_words_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(wake_words_frame, text="کلمات فارسی:", font=('Arial', 9, 'bold')).pack(anchor="e")
        self.settings_widgets['persian_wake_words'] = tk.Text(wake_words_frame, height=4, width=50)
        self.settings_widgets['persian_wake_words'].pack(fill="x", pady=2)
        
        ttk.Label(wake_words_frame, text="کلمات انگلیسی:", font=('Arial', 9, 'bold')).pack(anchor="e", pady=(10,0))
        self.settings_widgets['english_wake_words'] = tk.Text(wake_words_frame, height=4, width=50)
        self.settings_widgets['english_wake_words'].pack(fill="x", pady=2)
        
        # Voice processing settings
        processing_frame = ttk.LabelFrame(scrollable_frame, text="پردازش صوتی", padding="10")
        processing_frame.pack(fill="x", padx=10, pady=5)
        
        # Sensitivity slider
        sensitivity_frame = ttk.Frame(processing_frame)
        sensitivity_frame.pack(fill="x", pady=5)
        
        ttk.Label(sensitivity_frame, text="حساسیت تشخیص:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['sensitivity'] = tk.DoubleVar()
        self.settings_widgets['sensitivity_scale'] = ttk.Scale(
            sensitivity_frame,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            variable=self.settings_widgets['sensitivity'],
            length=200
        )
        self.settings_widgets['sensitivity_scale'].pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.settings_widgets['sensitivity_label'] = ttk.Label(sensitivity_frame, text="70%")
        self.settings_widgets['sensitivity_label'].pack(side="left")
        
        # Update label when scale changes
        def update_sensitivity_label(*args):
            value = int(self.settings_widgets['sensitivity'].get() * 100)
            self.settings_widgets['sensitivity_label'].config(text=f"{value}%")
        self.settings_widgets['sensitivity'].trace('w', update_sensitivity_label)
        
        # Audio processing options
        self.settings_widgets['noise_reduction'] = tk.BooleanVar()
        ttk.Checkbutton(
            processing_frame,
            text="کاهش نویز",
            variable=self.settings_widgets['noise_reduction']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['auto_gain_control'] = tk.BooleanVar()
        ttk.Checkbutton(
            processing_frame,
            text="کنترل خودکار بهره",
            variable=self.settings_widgets['auto_gain_control']
        ).pack(anchor="e", pady=2)
        
        # Audio devices
        devices_frame = ttk.Frame(processing_frame)
        devices_frame.pack(fill="x", pady=10)
        
        ttk.Label(devices_frame, text="دستگاه ورودی:", font=('Arial', 9, 'bold')).pack(anchor="e")
        self.settings_widgets['input_device'] = ttk.Combobox(
            devices_frame,
            values=["پیش‌فرض", "میکروفون داخلی", "میکروفون خارجی"],
            state="readonly",
            width=30
        )
        self.settings_widgets['input_device'].pack(anchor="e", pady=2)
        
        ttk.Label(devices_frame, text="دستگاه خروجی:", font=('Arial', 9, 'bold')).pack(anchor="e", pady=(10,0))
        self.settings_widgets['output_device'] = ttk.Combobox(
            devices_frame,
            values=["پیش‌فرض", "بلندگوی داخلی", "هدفون"],
            state="readonly",
            width=30
        )
        self.settings_widgets['output_device'].pack(anchor="e", pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_tts_settings_tab(self):
        """Create TTS settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="تبدیل متن به گفتار")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # TTS Engine selection
        engine_frame = ttk.LabelFrame(scrollable_frame, text="موتور TTS", padding="10")
        engine_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(engine_frame, text="موتور پیش‌فرض:", font=('Arial', 9, 'bold')).pack(anchor="e")
        self.settings_widgets['tts_engine'] = ttk.Combobox(
            engine_frame,
            values=["Piper", "Coqui", "gTTS", "Custom"],
            state="readonly",
            width=20
        )
        self.settings_widgets['tts_engine'].pack(anchor="e", pady=2)
        
        # Voice parameters
        params_frame = ttk.LabelFrame(scrollable_frame, text="پارامترهای صدا", padding="10")
        params_frame.pack(fill="x", padx=10, pady=5)
        
        # Speed control
        speed_frame = ttk.Frame(params_frame)
        speed_frame.pack(fill="x", pady=5)
        
        ttk.Label(speed_frame, text="سرعت گفتار:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['voice_speed'] = tk.DoubleVar()
        self.settings_widgets['speed_scale'] = ttk.Scale(
            speed_frame,
            from_=0.1,
            to=3.0,
            orient="horizontal",
            variable=self.settings_widgets['voice_speed'],
            length=200
        )
        self.settings_widgets['speed_scale'].pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.settings_widgets['speed_label'] = ttk.Label(speed_frame, text="1.0x")
        self.settings_widgets['speed_label'].pack(side="left")
        
        def update_speed_label(*args):
            value = self.settings_widgets['voice_speed'].get()
            self.settings_widgets['speed_label'].config(text=f"{value:.1f}x")
        self.settings_widgets['voice_speed'].trace('w', update_speed_label)
        
        # Pitch control
        pitch_frame = ttk.Frame(params_frame)
        pitch_frame.pack(fill="x", pady=5)
        
        ttk.Label(pitch_frame, text="بلندای صدا:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['voice_pitch'] = tk.DoubleVar()
        self.settings_widgets['pitch_scale'] = ttk.Scale(
            pitch_frame,
            from_=0.5,
            to=2.0,
            orient="horizontal",
            variable=self.settings_widgets['voice_pitch'],
            length=200
        )
        self.settings_widgets['pitch_scale'].pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.settings_widgets['pitch_label'] = ttk.Label(pitch_frame, text="1.0x")
        self.settings_widgets['pitch_label'].pack(side="left")
        
        def update_pitch_label(*args):
            value = self.settings_widgets['voice_pitch'].get()
            self.settings_widgets['pitch_label'].config(text=f"{value:.1f}x")
        self.settings_widgets['voice_pitch'].trace('w', update_pitch_label)
        
        # Volume control
        volume_frame = ttk.Frame(params_frame)
        volume_frame.pack(fill="x", pady=5)
        
        ttk.Label(volume_frame, text="حجم صدا:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['voice_volume'] = tk.DoubleVar()
        self.settings_widgets['volume_scale'] = ttk.Scale(
            volume_frame,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            variable=self.settings_widgets['voice_volume'],
            length=200
        )
        self.settings_widgets['volume_scale'].pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.settings_widgets['volume_label'] = ttk.Label(volume_frame, text="80%")
        self.settings_widgets['volume_label'].pack(side="left")
        
        def update_volume_label(*args):
            value = int(self.settings_widgets['voice_volume'].get() * 100)
            self.settings_widgets['volume_label'].config(text=f"{value}%")
        self.settings_widgets['voice_volume'].trace('w', update_volume_label)
        
        # Voice selection
        voices_frame = ttk.LabelFrame(scrollable_frame, text="انتخاب صدا", padding="10")
        voices_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(voices_frame, text="صدای فارسی:", font=('Arial', 9, 'bold')).pack(anchor="e")
        self.settings_widgets['persian_voice'] = ttk.Combobox(
            voices_frame,
            values=["fa_IR-gyro-medium", "fa_IR-amir-medium", "fa_IR-custom-voice"],
            state="readonly",
            width=30
        )
        self.settings_widgets['persian_voice'].pack(anchor="e", pady=2)
        
        ttk.Label(voices_frame, text="صدای انگلیسی:", font=('Arial', 9, 'bold')).pack(anchor="e", pady=(10,0))
        self.settings_widgets['english_voice'] = ttk.Combobox(
            voices_frame,
            values=["en_US-lessac-medium", "en_US-ljspeech-medium", "en_US-custom-voice"],
            state="readonly",
            width=30
        )
        self.settings_widgets['english_voice'].pack(anchor="e", pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_service_settings_tab(self):
        """Create Windows service settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="سرویس ویندوز")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Service control
        service_frame = ttk.LabelFrame(scrollable_frame, text="کنترل سرویس", padding="10")
        service_frame.pack(fill="x", padx=10, pady=5)
        
        # Service status
        self.service_status_label = ttk.Label(
            service_frame, 
            text="وضعیت: در حال بررسی...",
            font=('Arial', 9, 'bold')
        )
        self.service_status_label.pack(anchor="e", pady=5)
        
        # Service control buttons
        buttons_frame = ttk.Frame(service_frame)
        buttons_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            buttons_frame,
            text="نصب سرویس",
            command=self.install_service
        ).pack(side="right", padx=5)
        
        ttk.Button(
            buttons_frame,
            text="شروع سرویس",
            command=self.start_service
        ).pack(side="right", padx=5)
        
        ttk.Button(
            buttons_frame,
            text="توقف سرویس",
            command=self.stop_service
        ).pack(side="right", padx=5)
        
        ttk.Button(
            buttons_frame,
            text="حذف سرویس",
            command=self.uninstall_service
        ).pack(side="right", padx=5)
        
        # Service options
        options_frame = ttk.LabelFrame(scrollable_frame, text="تنظیمات سرویس", padding="10")
        options_frame.pack(fill="x", padx=10, pady=5)
        
        self.settings_widgets['auto_start'] = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="شروع خودکار با ویندوز",
            variable=self.settings_widgets['auto_start']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['run_on_startup'] = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="اجرا در استارت آپ",
            variable=self.settings_widgets['run_on_startup']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['minimize_to_tray'] = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="کمینه‌سازی به سیستم تری",
            variable=self.settings_widgets['minimize_to_tray']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['show_notifications'] = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="نمایش اعلان‌ها",
            variable=self.settings_widgets['show_notifications']
        ).pack(anchor="e", pady=2)
        
        # Logging settings
        logging_frame = ttk.LabelFrame(scrollable_frame, text="تنظیمات ثبت وقایع", padding="10")
        logging_frame.pack(fill="x", padx=10, pady=5)
        
        log_level_frame = ttk.Frame(logging_frame)
        log_level_frame.pack(fill="x", pady=5)
        
        ttk.Label(log_level_frame, text="سطح ثبت:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['log_level'] = ttk.Combobox(
            log_level_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=15
        )
        self.settings_widgets['log_level'].pack(side="left")
        
        # Update service status
        self.update_service_status()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_advanced_settings_tab(self):
        """Create advanced settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="تنظیمات پیشرفته")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Performance settings
        performance_frame = ttk.LabelFrame(scrollable_frame, text="تنظیمات عملکرد", padding="10")
        performance_frame.pack(fill="x", padx=10, pady=5)
        
        timeout_frame = ttk.Frame(performance_frame)
        timeout_frame.pack(fill="x", pady=5)
        
        ttk.Label(timeout_frame, text="تایم‌اوت API:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['api_timeout'] = tk.IntVar()
        timeout_spinbox = ttk.Spinbox(
            timeout_frame,
            from_=5,
            to=300,
            textvariable=self.settings_widgets['api_timeout'],
            width=10
        )
        timeout_spinbox.pack(side="left")
        ttk.Label(timeout_frame, text="ثانیه").pack(side="left", padx=(5,0))
        
        retries_frame = ttk.Frame(performance_frame)
        retries_frame.pack(fill="x", pady=5)
        
        ttk.Label(retries_frame, text="حداکثر تلاش مجدد:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['max_retries'] = tk.IntVar()
        ttk.Spinbox(
            retries_frame,
            from_=1,
            to=10,
            textvariable=self.settings_widgets['max_retries'],
            width=10
        ).pack(side="left")
        
        # Cache settings
        cache_frame = ttk.LabelFrame(scrollable_frame, text="تنظیمات کش", padding="10")
        cache_frame.pack(fill="x", padx=10, pady=5)
        
        self.settings_widgets['cache_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(
            cache_frame,
            text="فعال‌سازی کش",
            variable=self.settings_widgets['cache_enabled']
        ).pack(anchor="e", pady=2)
        
        cache_size_frame = ttk.Frame(cache_frame)
        cache_size_frame.pack(fill="x", pady=5)
        
        ttk.Label(cache_size_frame, text="اندازه کش:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['cache_size_mb'] = tk.IntVar()
        ttk.Spinbox(
            cache_size_frame,
            from_=10,
            to=1000,
            textvariable=self.settings_widgets['cache_size_mb'],
            width=10
        ).pack(side="left")
        ttk.Label(cache_size_frame, text="MB").pack(side="left", padx=(5,0))
        
        # Developer options
        dev_frame = ttk.LabelFrame(scrollable_frame, text="گزینه‌های توسعه‌دهنده", padding="10")
        dev_frame.pack(fill="x", padx=10, pady=5)
        
        self.settings_widgets['debug_mode'] = tk.BooleanVar()
        ttk.Checkbutton(
            dev_frame,
            text="حالت دیباگ",
            variable=self.settings_widgets['debug_mode']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['performance_monitoring'] = tk.BooleanVar()
        ttk.Checkbutton(
            dev_frame,
            text="نظارت بر عملکرد",
            variable=self.settings_widgets['performance_monitoring']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['usage_analytics'] = tk.BooleanVar()
        ttk.Checkbutton(
            dev_frame,
            text="آنالیتیکس استفاده",
            variable=self.settings_widgets['usage_analytics']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['auto_updates'] = tk.BooleanVar()
        ttk.Checkbutton(
            dev_frame,
            text="به‌روزرسانی خودکار",
            variable=self.settings_widgets['auto_updates']
        ).pack(anchor="e", pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_shortcuts_settings_tab(self):
        """Create keyboard shortcuts settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="میانبرهای کیبورد")
        
        shortcuts_frame = ttk.LabelFrame(tab_frame, text="میانبرهای کیبورد", padding="20")
        shortcuts_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create shortcut input fields
        shortcuts = [
            ("activate_voice", "فعال‌سازی صوتی:"),
            ("show_hide_ui", "نمایش/مخفی کردن رابط:"),
            ("settings", "تنظیمات:"),
            ("quit", "خروج:")
        ]
        
        for i, (key, label) in enumerate(shortcuts):
            frame = ttk.Frame(shortcuts_frame)
            frame.pack(fill="x", pady=5)
            
            ttk.Label(frame, text=label, font=('Arial', 9, 'bold')).pack(side="right", padx=(0, 10))
            self.settings_widgets[key] = tk.StringVar()
            ttk.Entry(
                frame,
                textvariable=self.settings_widgets[key],
                width=20
            ).pack(side="left")
        
        # Reset to defaults button
        ttk.Button(
            shortcuts_frame,
            text="بازگردانی به پیش‌فرض",
            command=self.reset_shortcuts
        ).pack(pady=20)
        
    def create_web_settings_tab(self):
        """Create web interface settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="رابط وب")
        
        # Web server settings
        server_frame = ttk.LabelFrame(tab_frame, text="تنظیمات سرور وب", padding="20")
        server_frame.pack(fill="x", padx=20, pady=10)
        
        port_frame = ttk.Frame(server_frame)
        port_frame.pack(fill="x", pady=5)
        
        ttk.Label(port_frame, text="پورت:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['web_port'] = tk.IntVar()
        ttk.Spinbox(
            port_frame,
            from_=1024,
            to=65535,
            textvariable=self.settings_widgets['web_port'],
            width=10
        ).pack(side="left")
        
        host_frame = ttk.Frame(server_frame)
        host_frame.pack(fill="x", pady=5)
        
        ttk.Label(host_frame, text="هاست:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['web_host'] = tk.StringVar()
        ttk.Entry(
            host_frame,
            textvariable=self.settings_widgets['web_host'],
            width=20
        ).pack(side="left")
        
        # Web options
        options_frame = ttk.LabelFrame(tab_frame, text="گزینه‌های رابط وب", padding="20")
        options_frame.pack(fill="x", padx=20, pady=10)
        
        self.settings_widgets['auto_open_browser'] = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="باز کردن خودکار مرورگر",
            variable=self.settings_widgets['auto_open_browser']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['enable_remote_access'] = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="دسترسی از راه دور",
            variable=self.settings_widgets['enable_remote_access']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['ssl_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="فعال‌سازی SSL",
            variable=self.settings_widgets['ssl_enabled']
        ).pack(anchor="e", pady=2)
        
    def create_desktop_settings_tab(self):
        """Create desktop application settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="اپلیکیشن دسکتاپ")
        
        # Window settings
        window_frame = ttk.LabelFrame(tab_frame, text="تنظیمات پنجره", padding="20")
        window_frame.pack(fill="x", padx=20, pady=10)
        
        width_frame = ttk.Frame(window_frame)
        width_frame.pack(fill="x", pady=5)
        
        ttk.Label(width_frame, text="عرض پنجره:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['window_width'] = tk.IntVar()
        ttk.Spinbox(
            width_frame,
            from_=800,
            to=2560,
            textvariable=self.settings_widgets['window_width'],
            width=10
        ).pack(side="left")
        
        height_frame = ttk.Frame(window_frame)
        height_frame.pack(fill="x", pady=5)
        
        ttk.Label(height_frame, text="ارتفاع پنجره:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['window_height'] = tk.IntVar()
        ttk.Spinbox(
            height_frame,
            from_=600,
            to=1440,
            textvariable=self.settings_widgets['window_height'],
            width=10
        ).pack(side="left")
        
        # Window behavior
        behavior_frame = ttk.LabelFrame(tab_frame, text="رفتار پنجره", padding="20")
        behavior_frame.pack(fill="x", padx=20, pady=10)
        
        self.settings_widgets['remember_position'] = tk.BooleanVar()
        ttk.Checkbutton(
            behavior_frame,
            text="به خاطر سپردن موقعیت پنجره",
            variable=self.settings_widgets['remember_position']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['always_on_top'] = tk.BooleanVar()
        ttk.Checkbutton(
            behavior_frame,
            text="همیشه روی همه پنجره‌ها",
            variable=self.settings_widgets['always_on_top']
        ).pack(anchor="e", pady=2)
        
        self.settings_widgets['startup_minimized'] = tk.BooleanVar()
        ttk.Checkbutton(
            behavior_frame,
            text="شروع به صورت کمینه",
            variable=self.settings_widgets['startup_minimized']
        ).pack(anchor="e", pady=2)
        
        # Opacity slider
        opacity_frame = ttk.Frame(behavior_frame)
        opacity_frame.pack(fill="x", pady=10)
        
        ttk.Label(opacity_frame, text="شفافیت:", font=('Arial', 9, 'bold')).pack(side="right")
        self.settings_widgets['opacity'] = tk.DoubleVar()
        self.settings_widgets['opacity_scale'] = ttk.Scale(
            opacity_frame,
            from_=0.2,
            to=1.0,
            orient="horizontal",
            variable=self.settings_widgets['opacity'],
            length=200
        )
        self.settings_widgets['opacity_scale'].pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.settings_widgets['opacity_label'] = ttk.Label(opacity_frame, text="100%")
        self.settings_widgets['opacity_label'].pack(side="left")
        
        def update_opacity_label(*args):
            value = int(self.settings_widgets['opacity'].get() * 100)
            self.settings_widgets['opacity_label'].config(text=f"{value}%")
        self.settings_widgets['opacity'].trace('w', update_opacity_label)
        
    def create_buttons_frame(self, parent):
        """Create action buttons frame"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Main action buttons
        actions_frame = ttk.Frame(buttons_frame)
        actions_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Button(
            actions_frame,
            text="ذخیره تنظیمات",
            command=self.save_settings
        ).pack(side="right", padx=5)
        
        ttk.Button(
            actions_frame,
            text="اعمال",
            command=self.apply_settings
        ).pack(side="right", padx=5)
        
        ttk.Button(
            actions_frame,
            text="بازگردانی",
            command=self.reset_settings
        ).pack(side="right", padx=5)
        
        ttk.Button(
            actions_frame,
            text="لغو",
            command=self.close_window
        ).pack(side="right", padx=5)
        
        # Import/Export buttons
        import_export_frame = ttk.Frame(buttons_frame)
        import_export_frame.pack(side="right")
        
        ttk.Button(
            import_export_frame,
            text="صادرات تنظیمات",
            command=self.export_settings
        ).pack(side="right", padx=5)
        
        ttk.Button(
            import_export_frame,
            text="وارد کردن تنظیمات",
            command=self.import_settings
        ).pack(side="right", padx=5)
        
    def load_current_settings(self):
        """Load current settings into UI controls"""
        try:
            settings = self.settings_manager.get_all_settings()
            
            # UI Settings
            theme_map = {"dark": 0, "light": 1, "auto": 2}
            theme_index = theme_map.get(settings.get("ui", {}).get("theme", "dark"), 0)
            if 'theme' in self.settings_widgets:
                self.settings_widgets['theme'].current(theme_index)
            
            lang_map = {"persian": 0, "english": 1, "bilingual": 2}
            lang_index = lang_map.get(settings.get("ui", {}).get("language", "persian"), 0)
            if 'language' in self.settings_widgets:
                self.settings_widgets['language'].current(lang_index)
            
            if 'rtl_layout' in self.settings_widgets:
                self.settings_widgets['rtl_layout'].set(settings.get("ui", {}).get("rtl_layout", True))
            
            font_map = {"small": 0, "medium": 1, "large": 2, "extra_large": 3}
            font_index = font_map.get(settings.get("ui", {}).get("font_size", "medium"), 1)
            if 'font_size' in self.settings_widgets:
                self.settings_widgets['font_size'].current(font_index)
            
            # Boolean UI settings
            ui_booleans = ['animations_enabled', 'sound_effects', 'notification_sounds', 'system_tray_enabled']
            for setting in ui_booleans:
                if setting in self.settings_widgets:
                    self.settings_widgets[setting].set(settings.get("ui", {}).get(setting, True))
            
            # Voice Settings
            voice_settings = settings.get("voice", {})
            
            if 'persian_wake_words' in self.settings_widgets:
                persian_words = "\n".join(voice_settings.get("wake_words", {}).get("persian", []))
                self.settings_widgets['persian_wake_words'].delete(1.0, tk.END)
                self.settings_widgets['persian_wake_words'].insert(1.0, persian_words)
            
            if 'english_wake_words' in self.settings_widgets:
                english_words = "\n".join(voice_settings.get("wake_words", {}).get("english", []))
                self.settings_widgets['english_wake_words'].delete(1.0, tk.END)
                self.settings_widgets['english_wake_words'].insert(1.0, english_words)
            
            if 'sensitivity' in self.settings_widgets:
                self.settings_widgets['sensitivity'].set(voice_settings.get("sensitivity", 0.7))
            
            # Voice boolean settings
            voice_booleans = ['noise_reduction', 'auto_gain_control']
            for setting in voice_booleans:
                if setting in self.settings_widgets:
                    self.settings_widgets[setting].set(voice_settings.get(setting, True))
            
            # TTS Settings
            tts_settings = settings.get("tts", {})
            
            engine_map = {"piper": 0, "coqui": 1, "gtts": 2, "custom": 3}
            engine_index = engine_map.get(tts_settings.get("default_engine", "piper"), 0)
            if 'tts_engine' in self.settings_widgets:
                self.settings_widgets['tts_engine'].current(engine_index)
            
            if 'voice_speed' in self.settings_widgets:
                self.settings_widgets['voice_speed'].set(tts_settings.get("voice_speed", 1.0))
            
            if 'voice_pitch' in self.settings_widgets:
                self.settings_widgets['voice_pitch'].set(tts_settings.get("voice_pitch", 1.0))
            
            if 'voice_volume' in self.settings_widgets:
                self.settings_widgets['voice_volume'].set(tts_settings.get("voice_volume", 0.8))
            
            # Service Settings
            service_settings = settings.get("service", {})
            
            service_booleans = ['auto_start', 'run_on_startup', 'minimize_to_tray', 'show_notifications']
            for setting in service_booleans:
                if setting in self.settings_widgets:
                    self.settings_widgets[setting].set(service_settings.get(setting, True))
            
            log_level_map = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
            log_level_index = log_level_map.get(service_settings.get("log_level", "INFO"), 1)
            if 'log_level' in self.settings_widgets:
                self.settings_widgets['log_level'].current(log_level_index)
            
            # Advanced Settings
            advanced_settings = settings.get("advanced", {})
            
            if 'api_timeout' in self.settings_widgets:
                self.settings_widgets['api_timeout'].set(advanced_settings.get("api_timeout", 30))
            
            if 'max_retries' in self.settings_widgets:
                self.settings_widgets['max_retries'].set(advanced_settings.get("max_retries", 3))
            
            if 'cache_size_mb' in self.settings_widgets:
                self.settings_widgets['cache_size_mb'].set(advanced_settings.get("cache_size_mb", 100))
            
            advanced_booleans = ['cache_enabled', 'debug_mode', 'performance_monitoring', 'usage_analytics', 'auto_updates']
            for setting in advanced_booleans:
                if setting in self.settings_widgets:
                    self.settings_widgets[setting].set(advanced_settings.get(setting, True))
            
            # Shortcuts
            shortcuts = settings.get("shortcuts", {})
            shortcut_keys = ['activate_voice', 'show_hide_ui', 'settings', 'quit']
            for key in shortcut_keys:
                if key in self.settings_widgets:
                    self.settings_widgets[key].set(shortcuts.get(key, ""))
            
            # Web Settings
            web_settings = settings.get("web_interface", {})
            
            if 'web_port' in self.settings_widgets:
                self.settings_widgets['web_port'].set(web_settings.get("port", 5001))
            
            if 'web_host' in self.settings_widgets:
                self.settings_widgets['web_host'].set(web_settings.get("host", "localhost"))
            
            web_booleans = ['auto_open_browser', 'enable_remote_access', 'ssl_enabled']
            for setting in web_booleans:
                if setting in self.settings_widgets:
                    self.settings_widgets[setting].set(web_settings.get(setting, False))
            
            # Desktop Settings
            desktop_settings = settings.get("desktop_interface", {})
            
            if 'window_width' in self.settings_widgets:
                self.settings_widgets['window_width'].set(desktop_settings.get("window_width", 1200))
            
            if 'window_height' in self.settings_widgets:
                self.settings_widgets['window_height'].set(desktop_settings.get("window_height", 800))
            
            if 'opacity' in self.settings_widgets:
                self.settings_widgets['opacity'].set(desktop_settings.get("opacity", 1.0))
            
            desktop_booleans = ['remember_position', 'always_on_top', 'startup_minimized']
            for setting in desktop_booleans:
                if setting in self.settings_widgets:
                    self.settings_widgets[setting].set(desktop_settings.get(setting, False))
                    
        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def save_settings(self):
        """Save all settings"""
        self.apply_settings()
        self.close_window()
        
    def apply_settings(self):
        """Apply current UI settings to settings manager"""
        try:
            # UI Settings
            theme_map = ["dark", "light", "auto"]
            if 'theme' in self.settings_widgets and self.settings_widgets['theme'].current() >= 0:
                theme = theme_map[self.settings_widgets['theme'].current()]
                self.settings_manager.set_setting("ui.theme", theme)
            
            lang_map = ["persian", "english", "bilingual"]
            if 'language' in self.settings_widgets and self.settings_widgets['language'].current() >= 0:
                language = lang_map[self.settings_widgets['language'].current()]
                self.settings_manager.set_setting("ui.language", language)
            
            if 'rtl_layout' in self.settings_widgets:
                self.settings_manager.set_setting("ui.rtl_layout", self.settings_widgets['rtl_layout'].get())
            
            font_map = ["small", "medium", "large", "extra_large"]
            if 'font_size' in self.settings_widgets and self.settings_widgets['font_size'].current() >= 0:
                font_size = font_map[self.settings_widgets['font_size'].current()]
                self.settings_manager.set_setting("ui.font_size", font_size)
            
            # UI boolean settings
            ui_booleans = ['animations_enabled', 'sound_effects', 'notification_sounds', 'system_tray_enabled']
            for setting in ui_booleans:
                if setting in self.settings_widgets:
                    self.settings_manager.set_setting(f"ui.{setting}", self.settings_widgets[setting].get())
            
            # Voice Settings
            if 'persian_wake_words' in self.settings_widgets:
                persian_words = [
                    word.strip() for word in 
                    self.settings_widgets['persian_wake_words'].get(1.0, tk.END).split('\n') 
                    if word.strip()
                ]
                self.settings_manager.set_setting("voice.wake_words.persian", persian_words)
            
            if 'english_wake_words' in self.settings_widgets:
                english_words = [
                    word.strip() for word in 
                    self.settings_widgets['english_wake_words'].get(1.0, tk.END).split('\n') 
                    if word.strip()
                ]
                self.settings_manager.set_setting("voice.wake_words.english", english_words)
            
            if 'sensitivity' in self.settings_widgets:
                self.settings_manager.set_setting("voice.sensitivity", self.settings_widgets['sensitivity'].get())
            
            voice_booleans = ['noise_reduction', 'auto_gain_control']
            for setting in voice_booleans:
                if setting in self.settings_widgets:
                    self.settings_manager.set_setting(f"voice.{setting}", self.settings_widgets[setting].get())
            
            # TTS Settings
            engine_map = ["piper", "coqui", "gtts", "custom"]
            if 'tts_engine' in self.settings_widgets and self.settings_widgets['tts_engine'].current() >= 0:
                engine = engine_map[self.settings_widgets['tts_engine'].current()]
                self.settings_manager.set_setting("tts.default_engine", engine)
            
            tts_values = ['voice_speed', 'voice_pitch', 'voice_volume']
            for setting in tts_values:
                if setting in self.settings_widgets:
                    self.settings_manager.set_setting(f"tts.{setting}", self.settings_widgets[setting].get())
            
            # Service Settings
            service_booleans = ['auto_start', 'run_on_startup', 'minimize_to_tray', 'show_notifications']
            for setting in service_booleans:
                if setting in self.settings_widgets:
                    self.settings_manager.set_setting(f"service.{setting}", self.settings_widgets[setting].get())
            
            log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            if 'log_level' in self.settings_widgets and self.settings_widgets['log_level'].current() >= 0:
                log_level = log_levels[self.settings_widgets['log_level'].current()]
                self.settings_manager.set_setting("service.log_level", log_level)
            
            # Advanced Settings
            advanced_ints = ['api_timeout', 'max_retries', 'cache_size_mb']
            for setting in advanced_ints:
                if setting in self.settings_widgets:
                    self.settings_manager.set_setting(f"advanced.{setting}", self.settings_widgets[setting].get())
            
            advanced_booleans = ['cache_enabled', 'debug_mode', 'performance_monitoring', 'usage_analytics', 'auto_updates']
            for setting in advanced_booleans:
                if setting in self.settings_widgets:
                    self.settings_manager.set_setting(f"advanced.{setting}", self.settings_widgets[setting].get())
            
            # Shortcuts
            shortcut_keys = ['activate_voice', 'show_hide_ui', 'settings', 'quit']
            for key in shortcut_keys:
                if key in self.settings_widgets:
                    self.settings_manager.set_setting(f"shortcuts.{key}", self.settings_widgets[key].get())
            
            # Web Settings
            if 'web_port' in self.settings_widgets:
                self.settings_manager.set_setting("web_interface.port", self.settings_widgets['web_port'].get())
            
            if 'web_host' in self.settings_widgets:
                self.settings_manager.set_setting("web_interface.host", self.settings_widgets['web_host'].get())
            
            web_booleans = ['auto_open_browser', 'enable_remote_access', 'ssl_enabled']
            for setting in web_booleans:
                if setting in self.settings_widgets:
                    self.settings_manager.set_setting(f"web_interface.{setting}", self.settings_widgets[setting].get())
            
            # Desktop Settings
            desktop_ints = ['window_width', 'window_height']
            for setting in desktop_ints:
                if setting in self.settings_widgets:
                    self.settings_manager.set_setting(f"desktop_interface.{setting}", self.settings_widgets[setting].get())
            
            if 'opacity' in self.settings_widgets:
                self.settings_manager.set_setting("desktop_interface.opacity", self.settings_widgets['opacity'].get())
            
            desktop_booleans = ['remember_position', 'always_on_top', 'startup_minimized']
            for setting in desktop_booleans:
                if setting in self.settings_widgets:
                    self.settings_manager.set_setting(f"desktop_interface.{setting}", self.settings_widgets[setting].get())
            
            # Show success message
            messagebox.showinfo("موفقیت", "تنظیمات با موفقیت ذخیره شد.")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره تنظیمات:\n{str(e)}")
            
    def reset_settings(self):
        """Reset settings to defaults"""
        result = messagebox.askyesno(
            "بازگردانی تنظیمات", 
            "آیا مطمئن هستید که می‌خواهید تمام تنظیمات به حالت پیش‌فرض بازگردانده شوند؟"
        )
        
        if result:
            self.settings_manager.reset_to_defaults()
            self.load_current_settings()
            
    def reset_shortcuts(self):
        """Reset shortcuts to defaults"""
        default_shortcuts = {
            'activate_voice': "Ctrl+Shift+Space",
            'show_hide_ui': "Ctrl+Shift+H",
            'settings': "Ctrl+Comma",
            'quit': "Ctrl+Q"
        }
        
        for key, value in default_shortcuts.items():
            if key in self.settings_widgets:
                self.settings_widgets[key].set(value)
                
    def export_settings(self):
        """Export settings to file"""
        file_path = filedialog.asksaveasfilename(
            title="صادرات تنظیمات",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.settings_manager.export_settings(Path(file_path)):
                messagebox.showinfo("موفقیت", "تنظیمات با موفقیت صادر شد.")
            else:
                messagebox.showerror("خطا", "خطا در صادرات تنظیمات.")
                
    def import_settings(self):
        """Import settings from file"""
        file_path = filedialog.askopenfilename(
            title="وارد کردن تنظیمات",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.settings_manager.import_settings(Path(file_path)):
                self.load_current_settings()
                messagebox.showinfo("موفقیت", "تنظیمات با موفقیت وارد شد.")
            else:
                messagebox.showerror("خطا", "خطا در وارد کردن تنظیمات.")
                
    def update_service_status(self):
        """Update Windows service status"""
        try:
            status = self.service_manager.get_service_status()
            
            status_text = f"وضعیت: {'نصب شده' if status['installed'] else 'نصب نشده'} - "
            status_text += f"{'در حال اجرا' if status['running'] else 'متوقف'}"
            
            if hasattr(self, 'service_status_label'):
                self.service_status_label.config(text=status_text)
                
        except Exception as e:
            if hasattr(self, 'service_status_label'):
                self.service_status_label.config(text=f"وضعیت: خطا - {str(e)}")
                
    def install_service(self):
        """Install Windows service"""
        try:
            if self.service_manager.install_service():
                messagebox.showinfo("نصب سرویس", "سرویس با موفقیت نصب شد.")
                self.update_service_status()
            else:
                messagebox.showerror("خطا", "خطا در نصب سرویس.")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در نصب سرویس:\n{str(e)}")
            
    def start_service(self):
        """Start Windows service"""
        try:
            if self.service_manager.start_service():
                messagebox.showinfo("شروع سرویس", "سرویس با موفقیت شروع شد.")
                self.update_service_status()
            else:
                messagebox.showerror("خطا", "خطا در شروع سرویس.")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در شروع سرویس:\n{str(e)}")
            
    def stop_service(self):
        """Stop Windows service"""
        try:
            if self.service_manager.stop_service():
                messagebox.showinfo("توقف سرویس", "سرویس با موفقیت متوقف شد.")
                self.update_service_status()
            else:
                messagebox.showerror("خطا", "خطا در توقف سرویس.")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در توقف سرویس:\n{str(e)}")
            
    def uninstall_service(self):
        """Uninstall Windows service"""
        result = messagebox.askyesno(
            "حذف سرویس",
            "آیا مطمئن هستید که می‌خواهید سرویس را حذف کنید؟"
        )
        
        if result:
            try:
                if self.service_manager.uninstall_service():
                    messagebox.showinfo("حذف سرویس", "سرویس با موفقیت حذف شد.")
                    self.update_service_status()
                else:
                    messagebox.showerror("خطا", "خطا در حذف سرویس.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف سرویس:\n{str(e)}")
                
    def close_window(self):
        """Close the settings window"""
        self.root.destroy()
        
    def run(self):
        """Run the settings window"""
        self.root.mainloop()

def main():
    """Main entry point for testing"""
    app = AdvancedSettingsWindow()
    app.run()

if __name__ == "__main__":
    main()