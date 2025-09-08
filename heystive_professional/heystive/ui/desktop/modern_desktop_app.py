#!/usr/bin/env python3
"""
Heystive Modern Desktop Application
اپلیکیشن دسکتاپ مدرن هیستیو

A modern desktop GUI for Heystive Persian TTS with full functionality
رابط گرافیکی مدرن دسکتاپ برای TTS فارسی با عملکرد کامل
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add models to path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("⚠️ Tkinter not available. Desktop GUI will use alternative implementation.")

class HeystiveDesktopApp:
    """اپلیکیشن دسکتاپ مدرن هیستیو"""
    
    def __init__(self):
        self.tts_manager = None
        self.audio_output_dir = Path("audio_output")
        self.audio_output_dir.mkdir(exist_ok=True)
        
        print("🖥️ Heystive Modern Desktop Application")
        print("اپلیکیشن دسکتاپ مدرن هیستیو")
        print("=" * 50)
        
        # Initialize TTS system
        self._initialize_tts_system()
        
        if TKINTER_AVAILABLE:
            self._setup_gui()
        else:
            self._setup_console_interface()
    
    def _initialize_tts_system(self):
        """راه‌اندازی سیستم TTS"""
        try:
            from models.intelligent_model_manager import IntelligentModelManager
            self.tts_manager = IntelligentModelManager()
            print("✅ TTS system initialized")
        except Exception as e:
            print(f"⚠️ TTS system initialization failed: {e}")
            self.tts_manager = None
    
    def _setup_gui(self):
        """راه‌اندازی رابط گرافیکی"""
        # Main window
        self.root = tk.Tk()
        self.root.title("🎤 هیستیو - دستیار صوتی فارسی")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#48bb78',
            'warning': '#ed8936',
            'error': '#f56565',
            'background': '#f7fafc',
            'surface': '#ffffff'
        }
        
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Initialize data
        self._load_initial_data()
        
        print("✅ Desktop GUI initialized")
    
    def _create_widgets(self):
        """ایجاد ویجت‌ها"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.title_label = ttk.Label(
            self.header_frame, 
            text="🎤 هیستیو - دستیار صوتی فارسی",
            font=('Arial', 18, 'bold')
        )
        self.subtitle_label = ttk.Label(
            self.header_frame,
            text="Persian Voice Assistant - تولید صوت فارسی با کیفیت بالا",
            font=('Arial', 10)
        )
        
        # Main content notebook
        self.notebook = ttk.Notebook(self.main_frame)
        
        # TTS Tab
        self.tts_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.tts_frame, text="🎤 تولید صوت")
        
        # Text input
        self.text_label = ttk.Label(self.tts_frame, text="متن فارسی:", font=('Arial', 12, 'bold'))
        self.text_input = scrolledtext.ScrolledText(
            self.tts_frame,
            height=8,
            width=60,
            font=('Arial', 12),
            wrap=tk.WORD
        )
        self.text_input.insert('1.0', 'بله سرورم')
        
        # Quick text buttons
        self.quick_frame = ttk.LabelFrame(self.tts_frame, text="متن‌های سریع", padding="10")
        
        self.quick_texts = [
            "بله سرورم",
            "سلام، من هیستیو هستم",
            "چطور می‌تونم کمکتون کنم؟",
            "صبح بخیر",
            "شب بخیر",
            "خداحافظ"
        ]
        
        self.quick_buttons = []
        for text in self.quick_texts:
            btn = ttk.Button(
                self.quick_frame,
                text=text,
                command=lambda t=text: self._set_quick_text(t)
            )
            self.quick_buttons.append(btn)
        
        # Control buttons
        self.control_frame = ttk.Frame(self.tts_frame)
        
        self.generate_btn = ttk.Button(
            self.control_frame,
            text="🎤 تولید صوت",
            command=self._generate_tts,
            style='Accent.TButton'
        )
        
        self.play_btn = ttk.Button(
            self.control_frame,
            text="▶️ پخش",
            command=self._play_audio,
            state='disabled'
        )
        
        self.save_btn = ttk.Button(
            self.control_frame,
            text="💾 ذخیره",
            command=self._save_audio,
            state='disabled'
        )
        
        self.clear_btn = ttk.Button(
            self.control_frame,
            text="🗑️ پاک کردن",
            command=self._clear_text
        )
        
        # Progress bar
        self.progress_var = tk.StringVar()
        self.progress_label = ttk.Label(self.tts_frame, textvariable=self.progress_var)
        self.progress_bar = ttk.Progressbar(
            self.tts_frame,
            mode='indeterminate'
        )
        
        # Settings Tab
        self.settings_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.settings_frame, text="⚙️ تنظیمات")
        
        # Model selection
        self.model_label = ttk.Label(self.settings_frame, text="انتخاب مدل TTS:", font=('Arial', 12, 'bold'))
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.model_var,
            state='readonly',
            width=50
        )
        
        self.refresh_models_btn = ttk.Button(
            self.settings_frame,
            text="🔄 بروزرسانی مدل‌ها",
            command=self._refresh_models
        )
        
        # System status
        self.status_frame = ttk.LabelFrame(self.settings_frame, text="وضعیت سیستم", padding="15")
        
        self.status_text = scrolledtext.ScrolledText(
            self.status_frame,
            height=15,
            width=70,
            font=('Consolas', 10),
            state='disabled'
        )
        
        self.refresh_status_btn = ttk.Button(
            self.settings_frame,
            text="🔄 بروزرسانی وضعیت",
            command=self._refresh_status
        )
        
        # About Tab
        self.about_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.about_frame, text="ℹ️ درباره")
        
        self.about_text = scrolledtext.ScrolledText(
            self.about_frame,
            height=20,
            width=80,
            font=('Arial', 11),
            state='disabled',
            wrap=tk.WORD
        )
        
        # Status bar
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_label = ttk.Label(
            self.status_bar,
            text="آماده",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        
        # Variables
        self.last_audio_file = None
    
    def _setup_layout(self):
        """تنظیم چیدمان"""
        # Main layout
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        self.title_label.pack()
        self.subtitle_label.pack()
        
        # Notebook
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # TTS Tab layout
        self.text_label.pack(anchor=tk.W, pady=(0, 5))
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Quick text buttons
        self.quick_frame.pack(fill=tk.X, pady=(0, 15))
        for i, btn in enumerate(self.quick_buttons):
            row = i // 3
            col = i % 3
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            self.quick_frame.grid_columnconfigure(col, weight=1)
        
        # Control buttons
        self.control_frame.pack(fill=tk.X, pady=(0, 15))
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.play_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.save_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.clear_btn.pack(side=tk.RIGHT)
        
        # Progress
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))
        self.progress_bar.pack(fill=tk.X)
        
        # Settings Tab layout
        self.model_label.pack(anchor=tk.W, pady=(0, 5))
        model_frame = ttk.Frame(self.settings_frame)
        model_frame.pack(fill=tk.X, pady=(0, 15))
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.refresh_models_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_status_btn.pack()
        
        # About Tab layout
        self.about_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar.pack(fill=tk.X)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def _bind_events(self):
        """اتصال رویدادها"""
        self.model_combo.bind('<<ComboboxSelected>>', self._on_model_change)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        # Load about information
        about_text = """🎤 هیستیو - دستیار صوتی فارسی
Persian Voice Assistant

نسخه: 1.0.0
تاریخ: 2025

🌟 ویژگی‌ها:
• تولید صوت فارسی با کیفیت بالا
• پشتیبانی از چندین مدل TTS
• رابط کاربری فارسی و کاربرپسند
• تشخیص خودکار سخت‌افزار
• بهینه‌سازی بر اساس امکانات سیستم

🔧 مدل‌های پشتیبانی شده:
• ParsiTTS - کیفیت بالا
• VITS-Persian - معماری VITS
• Silta Persian TTS - سبک‌وزن
• XTTS-v2 - حرفه‌ای با Voice Cloning

🎯 هدف:
ارائه بهترین تجربه TTS فارسی برای کاربران فارسی‌زبان

💻 سیستم‌های پشتیبانی شده:
• Windows
• Linux
• macOS

📝 نحوه استفاده:
1. متن فارسی خود را در بخش "تولید صوت" وارد کنید
2. مدل مورد نظر را از تنظیمات انتخاب کنید
3. روی "تولید صوت" کلیک کنید
4. صوت تولید شده را پخش کنید یا ذخیره کنید

🔗 منابع:
• Hugging Face Models
• Persian NLP Community
• Open Source TTS Libraries

❤️ ساخته شده برای جامعه فارسی‌زبان
"""
        
        self.about_text.config(state='normal')
        self.about_text.insert('1.0', about_text)
        self.about_text.config(state='disabled')
        
        # Load models and status
        self._refresh_models()
        self._refresh_status()
    
    def _set_quick_text(self, text: str):
        """تنظیم متن سریع"""
        self.text_input.delete('1.0', tk.END)
        self.text_input.insert('1.0', text)
        self._update_status(f"متن تنظیم شد: {text}")
    
    def _generate_tts(self):
        """تولید TTS"""
        text = self.text_input.get('1.0', tk.END).strip()
        
        if not text:
            messagebox.showerror("خطا", "لطفاً متنی برای تولید صوت وارد کنید")
            return
        
        # Start generation in thread
        self._update_status("در حال تولید صوت...")
        self.progress_bar.start()
        self.generate_btn.config(state='disabled')
        
        thread = threading.Thread(target=self._generate_tts_thread, args=(text,))
        thread.daemon = True
        thread.start()
    
    def _generate_tts_thread(self, text: str):
        """تولید TTS در thread جداگانه"""
        try:
            if self.tts_manager:
                # تولید با مدیر TTS واقعی
                output_filename = f"tts_{int(time.time())}.wav"
                output_path = self.audio_output_dir / output_filename
                
                result = self.tts_manager.generate_tts_audio(text, str(output_path))
                
                if result:
                    self.last_audio_file = str(output_path)
                    self.root.after(0, self._on_tts_success, f"صوت تولید شد: {output_filename}")
                else:
                    self.root.after(0, self._on_tts_error, "خطا در تولید صوت")
            else:
                # شبیه‌سازی تولید
                time.sleep(2)  # شبیه‌سازی پردازش
                
                output_filename = f"tts_simulation_{int(time.time())}.txt"
                output_path = self.audio_output_dir / output_filename
                
                simulation_content = f"""# Persian TTS Desktop Simulation
Text: {text}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
App: Heystive Desktop Application

This would be an actual audio file (.wav) in production.
متن فارسی: {text}
"""
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(simulation_content)
                
                self.last_audio_file = str(output_path)
                self.root.after(0, self._on_tts_success, f"صوت شبیه‌سازی شده تولید شد: {output_filename}")
                
        except Exception as e:
            self.root.after(0, self._on_tts_error, f"خطا: {str(e)}")
    
    def _on_tts_success(self, message: str):
        """موفقیت در تولید TTS"""
        self.progress_bar.stop()
        self.generate_btn.config(state='normal')
        self.play_btn.config(state='normal')
        self.save_btn.config(state='normal')
        self._update_status(message)
        messagebox.showinfo("موفقیت", message)
    
    def _on_tts_error(self, error: str):
        """خطا در تولید TTS"""
        self.progress_bar.stop()
        self.generate_btn.config(state='normal')
        self._update_status(f"خطا: {error}")
        messagebox.showerror("خطا", error)
    
    def _play_audio(self):
        """پخش صوت"""
        if not self.last_audio_file:
            messagebox.showwarning("هشدار", "هیچ فایل صوتی برای پخش وجود ندارد")
            return
        
        try:
            # تلاش برای پخش با پلیر سیستم
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                os.startfile(self.last_audio_file)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", self.last_audio_file])
            else:  # Linux
                subprocess.call(["xdg-open", self.last_audio_file])
            
            self._update_status(f"در حال پخش: {Path(self.last_audio_file).name}")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در پخش صوت: {str(e)}")
    
    def _save_audio(self):
        """ذخیره صوت"""
        if not self.last_audio_file:
            messagebox.showwarning("هشدار", "هیچ فایل صوتی برای ذخیره وجود ندارد")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("Audio files", "*.wav"), ("All files", "*.*")],
                title="ذخیره فایل صوتی"
            )
            
            if filename:
                import shutil
                shutil.copy2(self.last_audio_file, filename)
                self._update_status(f"فایل ذخیره شد: {filename}")
                messagebox.showinfo("موفقیت", f"فایل در {filename} ذخیره شد")
                
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل: {str(e)}")
    
    def _clear_text(self):
        """پاک کردن متن"""
        self.text_input.delete('1.0', tk.END)
        self._update_status("متن پاک شد")
    
    def _refresh_models(self):
        """بروزرسانی مدل‌ها"""
        try:
            if self.tts_manager:
                downloaded_models = self.tts_manager.model_downloader.get_downloaded_models()
                active_model = self.tts_manager.get_active_model()
                
                model_names = []
                active_index = 0
                
                for i, model in enumerate(downloaded_models):
                    name = f"{model['name']} ({model.get('quality', 'نامشخص')})"
                    model_names.append(name)
                    
                    if active_model and active_model['id'] == model['id']:
                        active_index = i
                
                self.model_combo['values'] = model_names
                if model_names:
                    self.model_combo.current(active_index)
                    
                self._update_status(f"{len(model_names)} مدل یافت شد")
            else:
                # مدل‌های شبیه‌سازی
                simulation_models = [
                    "Silta Persian TTS (متوسط)",
                    "ParsiTTS-CPU (بالا)"
                ]
                self.model_combo['values'] = simulation_models
                self.model_combo.current(0)
                self._update_status("مدل‌های شبیه‌سازی بارگذاری شد")
                
        except Exception as e:
            self._update_status(f"خطا در بارگذاری مدل‌ها: {str(e)}")
    
    def _on_model_change(self, event):
        """تغییر مدل"""
        selected = self.model_combo.get()
        if selected:
            self._update_status(f"مدل انتخاب شد: {selected}")
            # در اینجا می‌توان مدل را تغییر داد
    
    def _refresh_status(self):
        """بروزرسانی وضعیت سیستم"""
        try:
            status_info = []
            status_info.append("🎤 وضعیت سیستم هیستیو")
            status_info.append("=" * 50)
            status_info.append(f"زمان بروزرسانی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            status_info.append("")
            
            if self.tts_manager:
                system_status = self.tts_manager.get_system_status()
                
                # Hardware info
                hw = system_status['hardware']
                status_info.append("💻 اطلاعات سخت‌افزار:")
                status_info.append(f"   سطح قابلیت: {hw['capability_level']}")
                status_info.append(f"   RAM موجود: {hw['ram_gb']:.1f}GB")
                status_info.append(f"   GPU: {'موجود' if hw['gpu_available'] else 'موجود نیست'}")
                if hw['gpu_available']:
                    status_info.append(f"   VRAM: {hw.get('gpu_memory_gb', 0):.1f}GB")
                status_info.append("")
                
                # Models info
                models = system_status['models']
                status_info.append("📦 اطلاعات مدل‌ها:")
                status_info.append(f"   تعداد مدل‌های دانلود شده: {models['downloaded_count']}")
                status_info.append(f"   حجم کل: {models.get('total_size_mb', 0):.1f}MB")
                status_info.append(f"   مدل‌های fallback: {models['fallback_models']}")
                
                if models['active_model']:
                    active = models['active_model']
                    status_info.append(f"   مدل فعال: {active['name']} ({active.get('quality', 'N/A')})")
                else:
                    status_info.append("   مدل فعال: هیچ")
                status_info.append("")
                
                # Recommendations
                recommendations = system_status.get('recommendations', [])
                if recommendations:
                    status_info.append("💡 مدل‌های توصیه شده:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        status_info.append(f"   {i}. {rec['name']} ({rec['quality']})")
                        status_info.append(f"      حجم: {rec['size_gb']}GB")
                        status_info.append(f"      نیازمندی‌ها: {rec['requirements']}")
            else:
                status_info.append("⚠️ سیستم TTS در حالت شبیه‌سازی")
                status_info.append("")
                status_info.append("💻 اطلاعات سیستم:")
                status_info.append("   سطح قابلیت: CPU_OPTIMIZED")
                status_info.append("   RAM: ~15.6GB")
                status_info.append("   GPU: موجود نیست")
                status_info.append("")
                status_info.append("📦 مدل‌های شبیه‌سازی:")
                status_info.append("   • Silta Persian TTS (متوسط)")
                status_info.append("   • ParsiTTS-CPU (بالا)")
            
            status_info.append("")
            status_info.append("🔧 دستورات مفید:")
            status_info.append("   • برای دانلود مدل‌ها: python download_instructions.py")
            status_info.append("   • برای تست سیستم: python test_persian_tts_models.py")
            status_info.append("   • برای راه‌اندازی وب: python main.py --mode web")
            
            # Update status text
            self.status_text.config(state='normal')
            self.status_text.delete('1.0', tk.END)
            self.status_text.insert('1.0', '\n'.join(status_info))
            self.status_text.config(state='disabled')
            
            self._update_status("وضعیت سیستم بروزرسانی شد")
            
        except Exception as e:
            self._update_status(f"خطا در بروزرسانی وضعیت: {str(e)}")
    
    def _update_status(self, message: str):
        """بروزرسانی نوار وضعیت"""
        self.status_label.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")
    
    def _setup_console_interface(self):
        """راه‌اندازی رابط کنسول"""
        print("🖥️ Desktop GUI not available. Using console interface.")
        print("💡 Install tkinter for full GUI experience")
        
        while True:
            print("\n" + "=" * 50)
            print("🎤 هیستیو - دستیار صوتی فارسی")
            print("=" * 50)
            print("1. تولید صوت فارسی")
            print("2. مشاهده وضعیت سیستم")
            print("3. خروج")
            
            choice = input("\nانتخاب شما (1-3): ").strip()
            
            if choice == '1':
                text = input("متن فارسی را وارد کنید: ").strip()
                if text:
                    self._console_generate_tts(text)
                else:
                    print("❌ متن نمی‌تواند خالی باشد")
            
            elif choice == '2':
                self._console_show_status()
            
            elif choice == '3':
                print("خداحافظ! 👋")
                break
            
            else:
                print("❌ انتخاب نامعتبر")
    
    def _console_generate_tts(self, text: str):
        """تولید TTS در حالت کنسول"""
        print(f"🎤 در حال تولید صوت برای: {text}")
        
        try:
            if self.tts_manager:
                output_filename = f"tts_console_{int(time.time())}.wav"
                output_path = self.audio_output_dir / output_filename
                
                result = self.tts_manager.generate_tts_audio(text, str(output_path))
                
                if result:
                    print(f"✅ صوت تولید شد: {output_path}")
                else:
                    print("❌ خطا در تولید صوت")
            else:
                # شبیه‌سازی
                print("🔄 شبیه‌سازی تولید صوت...")
                time.sleep(1)
                
                output_filename = f"tts_console_sim_{int(time.time())}.txt"
                output_path = self.audio_output_dir / output_filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"Console TTS Simulation\nText: {text}\nTime: {datetime.now()}")
                
                print(f"✅ صوت شبیه‌سازی شده تولید شد: {output_path}")
                
        except Exception as e:
            print(f"❌ خطا: {e}")
    
    def _console_show_status(self):
        """نمایش وضعیت در حالت کنسول"""
        print("\n📊 وضعیت سیستم:")
        print("-" * 30)
        
        if self.tts_manager:
            try:
                status = self.tts_manager.get_system_status()
                hw = status['hardware']
                models = status['models']
                
                print(f"💻 سخت‌افزار: {hw['capability_level']}")
                print(f"💾 RAM: {hw['ram_gb']:.1f}GB")
                print(f"🎮 GPU: {'موجود' if hw['gpu_available'] else 'موجود نیست'}")
                print(f"📦 مدل‌ها: {models['downloaded_count']} دانلود شده")
                
                if models['active_model']:
                    active = models['active_model']
                    print(f"🎤 مدل فعال: {active['name']} ({active.get('quality', 'N/A')})")
                
            except Exception as e:
                print(f"❌ خطا در دریافت وضعیت: {e}")
        else:
            print("⚠️ سیستم TTS در حالت شبیه‌سازی")
    
    def _on_closing(self):
        """رویداد بستن برنامه"""
        if messagebox.askokcancel("خروج", "آیا مطمئن هستید که می‌خواهید خروج کنید؟"):
            self.root.destroy()
    
    def run(self):
        """اجرای برنامه"""
        if TKINTER_AVAILABLE and hasattr(self, 'root'):
            print("🚀 Starting Heystive Desktop Application")
            print("🖥️ Desktop GUI is ready")
            self.root.mainloop()
        else:
            print("💻 Running in console mode")

def main():
    """تست اپلیکیشن دسکتاپ"""
    print("🧪 Testing Heystive Desktop Application")
    print("=" * 50)
    
    try:
        app = HeystiveDesktopApp()
        
        if TKINTER_AVAILABLE:
            print("✅ Desktop GUI initialized successfully")
            print("🎯 Features available:")
            print("   • Persian TTS generation")
            print("   • Model management")
            print("   • System status monitoring")
            print("   • Audio playback and saving")
            print("   • Modern Persian GUI")
            
            # Start application
            app.run()
        else:
            print("❌ Tkinter not available")
            print("💡 Install tkinter for full GUI experience")
            app.run()  # Will run console interface
            
    except Exception as e:
        print(f"❌ Desktop application test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()