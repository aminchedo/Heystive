#!/usr/bin/env python3
"""
Heystive Modern Launcher - Unified Interface Selector
Allows users to choose between different interface options
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
import threading
import time
import requests
from typing import Dict, Any, Optional

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "heystive_professional" / "heystive"))

class HeystiveLauncher:
    """
    Modern launcher for Heystive Persian Voice Assistant
    Provides interface selection and system management
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # State
        self.backend_process = None
        self.interface_process = None
        self.backend_status = "stopped"
        self.selected_interface = tk.StringVar(value="modern_web")
        
        # Paths
        self.project_root = project_root
        self.backend_path = self.project_root / "heystive_professional" / "main.py"
        self.web_path = self.project_root / "ui_modern_web" / "app.py"
        self.desktop_path = self.project_root / "ui_modern_desktop" / "main_desktop.py"
        
        # UI Components
        self.status_label = None
        self.launch_button = None
        self.stop_button = None
        self.backend_status_label = None
        
        self.create_ui()
        self.start_status_monitor()
        
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Heystive Modern Launcher - انتخاب رابط کاربری")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Persian font support
        try:
            self.root.option_add('*Font', 'Arial 10')
        except:
            pass
    
    def create_ui(self):
        """Create user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🎤 Heystive Persian Voice Assistant",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="دستیار صوتی فارسی - انتخاب رابط کاربری",
            font=('Arial', 10)
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Interface Selection
        interface_frame = ttk.LabelFrame(main_frame, text="انتخاب رابط کاربری", padding="15")
        interface_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Modern Web Interface
        web_radio = ttk.Radiobutton(
            interface_frame,
            text="🌐 رابط وب مدرن (Modern Web Interface)",
            variable=self.selected_interface,
            value="modern_web"
        )
        web_radio.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        web_desc = ttk.Label(
            interface_frame,
            text="   • رابط کاربری وب با طراحی مدرن و پشتیبانی PWA\n   • دسترسی از هر مرورگر، طراحی ریسپانسیو\n   • WebSocket برای ارتباط بلادرنگ",
            font=('Arial', 9),
            foreground='gray'
        )
        web_desc.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Modern Desktop Interface
        desktop_radio = ttk.Radiobutton(
            interface_frame,
            text="🖥️ رابط دسکتاپ مدرن (Modern Desktop Interface)",
            variable=self.selected_interface,
            value="modern_desktop"
        )
        desktop_radio.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        desktop_desc = ttk.Label(
            interface_frame,
            text="   • رابط کاربری بومی با PySide6 و Material Design\n   • یکپارچگی با سیستم، System Tray، Hotkeys\n   • عملکرد بهتر و دسترسی آفلاین",
            font=('Arial', 9),
            foreground='gray'
        )
        desktop_desc.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Existing Interfaces
        existing_radio = ttk.Radiobutton(
            interface_frame,
            text="📱 رابط‌های موجود (Existing Interfaces)",
            variable=self.selected_interface,
            value="existing"
        )
        existing_radio.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        existing_desc = ttk.Label(
            interface_frame,
            text="   • رابط‌های قبلی Heystive (Desktop و Web)\n   • سازگاری کامل با نسخه فعلی\n   • گزینه‌ای برای کاربران فعلی",
            font=('Arial', 9),
            foreground='gray'
        )
        existing_desc.grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="وضعیت سیستم", padding="15")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Backend Status
        backend_frame = ttk.Frame(status_frame)
        backend_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(backend_frame, text="Backend:").grid(row=0, column=0, sticky=tk.W)
        self.backend_status_label = ttk.Label(
            backend_frame, 
            text="🔴 متوقف", 
            foreground='red'
        )
        self.backend_status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # System Status
        self.status_label = ttk.Label(
            status_frame,
            text="آماده برای راه‌اندازی",
            font=('Arial', 10)
        )
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 20))
        
        self.launch_button = ttk.Button(
            button_frame,
            text="🚀 راه‌اندازی سیستم",
            command=self.launch_system
        )
        self.launch_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ توقف سیستم",
            command=self.stop_system,
            state='disabled'
        )
        self.stop_button.grid(row=0, column=1, padx=(10, 0))
        
        # Advanced Options
        advanced_frame = ttk.LabelFrame(main_frame, text="گزینه‌های پیشرفته", padding="10")
        advanced_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(
            advanced_frame,
            text="⚙️ تنظیمات",
            command=self.show_settings
        ).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(
            advanced_frame,
            text="📊 داشبورد سیستم",
            command=self.open_dashboard
        ).grid(row=0, column=1, padx=(10, 0))
        
        ttk.Button(
            advanced_frame,
            text="📝 گزارش‌ها",
            command=self.show_logs
        ).grid(row=0, column=2, padx=(10, 0))
        
        ttk.Button(
            advanced_frame,
            text="❓ راهنما",
            command=self.show_help
        ).grid(row=0, column=3, padx=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        interface_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
        backend_frame.columnconfigure(1, weight=1)
    
    def launch_system(self):
        """Launch the selected system"""
        try:
            self.update_status("در حال راه‌اندازی...")
            self.launch_button.config(state='disabled')
            
            # Start backend first
            if not self.start_backend():
                self.update_status("خطا در راه‌اندازی Backend")
                self.launch_button.config(state='normal')
                return
            
            # Wait for backend to be ready
            self.update_status("انتظار برای آماده شدن Backend...")
            if not self.wait_for_backend():
                self.update_status("Backend آماده نشد")
                self.stop_backend()
                self.launch_button.config(state='normal')
                return
            
            # Start selected interface
            interface = self.selected_interface.get()
            if interface == "modern_web":
                self.start_modern_web()
            elif interface == "modern_desktop":
                self.start_modern_desktop()
            elif interface == "existing":
                self.start_existing_interface()
            
            self.update_status("سیستم با موفقیت راه‌اندازی شد")
            self.stop_button.config(state='normal')
            
        except Exception as e:
            self.update_status(f"خطا در راه‌اندازی: {str(e)}")
            self.launch_button.config(state='normal')
            messagebox.showerror("خطا", f"خطا در راه‌اندازی سیستم:\n{str(e)}")
    
    def stop_system(self):
        """Stop all running components"""
        try:
            self.update_status("در حال توقف سیستم...")
            
            # Stop interface
            if self.interface_process:
                self.interface_process.terminate()
                self.interface_process = None
            
            # Stop backend
            self.stop_backend()
            
            self.update_status("سیستم متوقف شد")
            self.launch_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
        except Exception as e:
            self.update_status(f"خطا در توقف: {str(e)}")
            messagebox.showerror("خطا", f"خطا در توقف سیستم:\n{str(e)}")
    
    def start_backend(self) -> bool:
        """Start Heystive backend"""
        try:
            if not self.backend_path.exists():
                messagebox.showerror("خطا", f"فایل Backend یافت نشد:\n{self.backend_path}")
                return False
            
            # Start backend process
            self.backend_process = subprocess.Popen([
                sys.executable, str(self.backend_path), "--mode", "web", "--port", "8000"
            ], cwd=str(self.backend_path.parent))
            
            self.backend_status = "starting"
            self.update_backend_status()
            
            return True
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در راه‌اندازی Backend:\n{str(e)}")
            return False
    
    def stop_backend(self):
        """Stop backend process"""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            finally:
                self.backend_process = None
                self.backend_status = "stopped"
                self.update_backend_status()
    
    def wait_for_backend(self, timeout: int = 30) -> bool:
        """Wait for backend to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    self.backend_status = "running"
                    self.update_backend_status()
                    return True
            except:
                pass
            
            time.sleep(2)
        
        return False
    
    def start_modern_web(self):
        """Start modern web interface"""
        try:
            if not self.web_path.exists():
                messagebox.showerror("خطا", f"رابط وب مدرن یافت نشد:\n{self.web_path}")
                return
            
            self.interface_process = subprocess.Popen([
                sys.executable, str(self.web_path)
            ], cwd=str(self.web_path.parent))
            
            # Open browser after a delay
            def open_browser():
                time.sleep(3)
                import webbrowser
                webbrowser.open("http://localhost:5001")
            
            threading.Thread(target=open_browser, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در راه‌اندازی رابط وب:\n{str(e)}")
    
    def start_modern_desktop(self):
        """Start modern desktop interface"""
        try:
            if not self.desktop_path.exists():
                messagebox.showerror("خطا", f"رابط دسکتاپ مدرن یافت نشد:\n{self.desktop_path}")
                return
            
            self.interface_process = subprocess.Popen([
                sys.executable, str(self.desktop_path)
            ], cwd=str(self.desktop_path.parent))
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در راه‌اندازی رابط دسکتاپ:\n{str(e)}")
    
    def start_existing_interface(self):
        """Start existing Heystive interface"""
        try:
            # Show selection dialog for existing interfaces
            choice = messagebox.askyesnocancel(
                "انتخاب رابط موجود",
                "کدام رابط موجود را می‌خواهید راه‌اندازی کنید؟\n\n"
                "بله: رابط دسکتاپ موجود\n"
                "خیر: رابط وب موجود\n"
                "لغو: انصراف"
            )
            
            if choice is None:  # Cancel
                return
            elif choice:  # Yes - Desktop
                self.interface_process = subprocess.Popen([
                    sys.executable, str(self.backend_path), "--mode", "desktop"
                ], cwd=str(self.backend_path.parent))
            else:  # No - Web
                # Web interface is already running with backend
                import webbrowser
                webbrowser.open("http://localhost:8000")
                
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در راه‌اندازی رابط موجود:\n{str(e)}")
    
    def update_status(self, status: str):
        """Update status label"""
        if self.status_label:
            self.status_label.config(text=status)
        self.root.update_idletasks()
    
    def update_backend_status(self):
        """Update backend status display"""
        if not self.backend_status_label:
            return
            
        if self.backend_status == "running":
            self.backend_status_label.config(text="🟢 در حال اجرا", foreground='green')
        elif self.backend_status == "starting":
            self.backend_status_label.config(text="🟡 در حال راه‌اندازی", foreground='orange')
        else:
            self.backend_status_label.config(text="🔴 متوقف", foreground='red')
    
    def start_status_monitor(self):
        """Start background status monitoring"""
        def monitor():
            while True:
                try:
                    if self.backend_process and self.backend_process.poll() is not None:
                        # Backend process died
                        self.backend_status = "stopped"
                        self.root.after(0, self.update_backend_status)
                        
                    if self.backend_status == "running":
                        # Check if backend is still responsive
                        try:
                            requests.get("http://localhost:8000/health", timeout=2)
                        except:
                            self.backend_status = "error"
                            self.root.after(0, self.update_backend_status)
                    
                    time.sleep(5)
                    
                except Exception:
                    pass
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("تنظیمات")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        
        ttk.Label(
            settings_window,
            text="تنظیمات سیستم",
            font=('Arial', 14, 'bold')
        ).pack(pady=20)
        
        # Backend URL
        url_frame = ttk.Frame(settings_window)
        url_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(url_frame, text="آدرس Backend:").pack(anchor='w')
        url_entry = ttk.Entry(url_frame, width=40)
        url_entry.pack(fill='x', pady=5)
        url_entry.insert(0, "http://localhost:8000")
        
        # Auto-start option
        auto_start = tk.BooleanVar()
        ttk.Checkbutton(
            settings_window,
            text="راه‌اندازی خودکار هنگام اجرا",
            variable=auto_start
        ).pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="ذخیره",
            command=settings_window.destroy
        ).pack(side='left', padx=10)
        
        ttk.Button(
            button_frame,
            text="لغو",
            command=settings_window.destroy
        ).pack(side='left')
    
    def open_dashboard(self):
        """Open system dashboard in browser"""
        try:
            import webbrowser
            if self.backend_status == "running":
                webbrowser.open("http://localhost:5001/dashboard")
            else:
                messagebox.showwarning("هشدار", "ابتدا سیستم را راه‌اندازی کنید")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در باز کردن داشبورد:\n{str(e)}")
    
    def show_logs(self):
        """Show system logs"""
        logs_window = tk.Toplevel(self.root)
        logs_window.title("گزارش‌های سیستم")
        logs_window.geometry("600x400")
        logs_window.transient(self.root)
        
        # Text widget for logs
        text_widget = tk.Text(logs_window, wrap='word')
        scrollbar = ttk.Scrollbar(logs_window, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load logs
        try:
            log_file = self.project_root / "heystive_professional" / "heystive.log"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = f.read()
                text_widget.insert('1.0', logs)
            else:
                text_widget.insert('1.0', "فایل گزارش یافت نشد")
        except Exception as e:
            text_widget.insert('1.0', f"خطا در خواندن گزارش‌ها: {str(e)}")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
🎤 راهنمای Heystive Modern Launcher

رابط‌های موجود:
• رابط وب مدرن: رابط کاربری وب با طراحی مدرن
• رابط دسکتاپ مدرن: رابط بومی با PySide6
• رابط‌های موجود: نسخه‌های قبلی Heystive

مراحل راه‌اندازی:
1. رابط مورد نظر را انتخاب کنید
2. روی "راه‌اندازی سیستم" کلیک کنید
3. منتظر بمانید تا Backend آماده شود
4. رابط انتخابی باز خواهد شد

نکات مهم:
• Backend باید قبل از رابط‌ها اجرا شود
• پورت‌های 8000 و 5001 باید آزاد باشند
• برای رابط دسکتاپ، PySide6 نصب باشد

در صورت بروز مشکل، گزارش‌ها را بررسی کنید.
        """
        
        messagebox.showinfo("راهنما", help_text)
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("خروج", "آیا می‌خواهید از برنامه خارج شوید؟"):
            self.stop_system()
            self.root.destroy()
    
    def run(self):
        """Run the launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        launcher = HeystiveLauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ Launcher failed to start: {e}")
        messagebox.showerror("خطا", f"خطا در راه‌اندازی Launcher:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()