#!/usr/bin/env python3
"""
Heystive Persian Voice Assistant - Fully Functional Entry Point
نقطه ورود کاملاً فانکشنال دستیار صوتی فارسی هیستیو

A complete, functional entry point with integrated UI and TTS systems
نقطه ورود کامل و فانکشنال با سیستم‌های یکپارچه UI و TTS
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add heystive package to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "heystive"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HeystiveFunctionalLauncher:
    """راه‌انداز کاملاً فانکشنال هیستیو"""
    
    def __init__(self):
        self.modes = {
            'desktop': self._launch_desktop,
            'web': self._launch_web,
            'cli': self._launch_cli
        }
        
        print("🎤 Heystive Persian Voice Assistant - Functional System")
        print("دستیار صوتی فارسی هیستیو - سیستم کاملاً فانکشنال")
        print("=" * 70)
        
        # Test TTS system availability
        self._check_tts_system()
    
    def _check_tts_system(self):
        """بررسی در دسترس بودن سیستم TTS"""
        try:
            from models.intelligent_model_manager import IntelligentModelManager
            manager = IntelligentModelManager()
            print("✅ TTS system available and ready")
            
            # Show system status
            status = manager.get_system_status()
            hw = status['hardware']
            models = status['models']
            
            print(f"💻 Hardware: {hw['capability_level']} | RAM: {hw['ram_gb']:.1f}GB")
            print(f"📦 Models: {models['downloaded_count']} available")
            
            if models['active_model']:
                active = models['active_model']
                print(f"🎤 Active Model: {active['name']} ({active.get('quality', 'N/A')})")
            
        except Exception as e:
            print(f"⚠️ TTS system initialization: {e}")
            print("💡 System will run in simulation mode")
    
    def _launch_desktop(self, args):
        """راه‌اندازی اپلیکیشن دسکتاپ"""
        try:
            print("🖥️ Starting Modern Desktop Application...")
            print("راه‌اندازی اپلیکیشن دسکتاپ مدرن...")
            
            from ui.desktop.modern_desktop_app import HeystiveDesktopApp
            
            app = HeystiveDesktopApp()
            app.run()
            
        except ImportError as e:
            print(f"❌ Desktop app import failed: {e}")
            print("🔄 Trying fallback desktop interface...")
            
            # Fallback to console interface
            self._launch_console_desktop()
            
        except Exception as e:
            logger.error(f"❌ Desktop app failed: {e}")
            print("💡 Try: pip install tkinter")
            sys.exit(1)
    
    def _launch_web(self, args):
        """راه‌اندازی رابط وب"""
        try:
            print("🌐 Starting Functional Web Interface...")
            print("راه‌اندازی رابط وب فانکشنال...")
            
            from ui.web.functional_web_interface import HeystiveFunctionalWebInterface
            
            interface = HeystiveFunctionalWebInterface(port=args.port)
            interface.run(host='0.0.0.0', debug=args.debug)
            
        except ImportError as e:
            print(f"❌ Web interface import failed: {e}")
            print("💡 Try: pip install flask flask-cors")
            
            # Fallback to simple web interface
            self._launch_simple_web(args)
            
        except Exception as e:
            logger.error(f"❌ Web interface failed: {e}")
            sys.exit(1)
    
    def _launch_cli(self, args):
        """راه‌اندازی رابط CLI"""
        try:
            print("💻 Starting CLI Interface...")
            print("راه‌اندازی رابط خط فرمان...")
            
            self._run_cli_interface()
            
        except Exception as e:
            logger.error(f"❌ CLI interface failed: {e}")
            sys.exit(1)
    
    def _launch_console_desktop(self):
        """راه‌اندازی رابط دسکتاپ کنسولی"""
        print("🖥️ Console Desktop Interface")
        print("رابط دسکتاپ کنسولی")
        print("=" * 40)
        
        try:
            from models.intelligent_model_manager import IntelligentModelManager
            manager = IntelligentModelManager()
            
            while True:
                print(f"\n{'='*50}")
                print("🎤 هیستیو - دستیار صوتی فارسی")
                print("='*50}")
                print("1. تولید صوت فارسی")
                print("2. مشاهده مدل‌های موجود") 
                print("3. وضعیت سیستم")
                print("4. تست صوت نمونه")
                print("5. خروج")
                
                choice = input("\nانتخاب شما (1-5): ").strip()
                
                if choice == '1':
                    text = input("متن فارسی را وارد کنید: ").strip()
                    if text:
                        print(f"🎤 تولید صوت برای: {text}")
                        result = manager.generate_tts_audio(text)
                        if result:
                            print(f"✅ صوت تولید شد: {result}")
                        else:
                            print("❌ خطا در تولید صوت")
                    else:
                        print("❌ متن نمی‌تواند خالی باشد")
                
                elif choice == '2':
                    models = manager.model_downloader.get_downloaded_models()
                    print(f"\n📦 مدل‌های موجود ({len(models)}):")
                    for model in models:
                        print(f"   • {model['name']} ({model.get('quality', 'N/A')})")
                
                elif choice == '3':
                    status = manager.get_system_status()
                    print(f"\n📊 وضعیت سیستم:")
                    print(f"   Hardware: {status['hardware']['capability_level']}")
                    print(f"   RAM: {status['hardware']['ram_gb']:.1f}GB")
                    print(f"   Models: {status['models']['downloaded_count']}")
                    if status['models']['active_model']:
                        active = status['models']['active_model']
                        print(f"   Active: {active['name']}")
                
                elif choice == '4':
                    print("🎤 تست صوت نمونه: بله سرورم")
                    result = manager.generate_tts_audio("بله سرورم")
                    if result:
                        print(f"✅ صوت نمونه تولید شد: {result}")
                    else:
                        print("❌ خطا در تولید صوت نمونه")
                
                elif choice == '5':
                    print("خداحافظ! 👋")
                    break
                
                else:
                    print("❌ انتخاب نامعتبر")
        
        except Exception as e:
            print(f"❌ خطا در رابط کنسولی: {e}")
    
    def _launch_simple_web(self, args):
        """راه‌اندازی رابط وب ساده"""
        print("🌐 Simple Web Interface (Fallback)")
        print("رابط وب ساده (جایگزین)")
        
        # Simple HTTP server implementation
        try:
            from http.server import HTTPServer, SimpleHTTPRequestHandler
            import webbrowser
            
            class HeystiveHTTPHandler(SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        
                        html = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>هیستیو - دستیار صوتی فارسی</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #333; text-align: center; }
        .info { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .error { background: #ffe8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 هیستیو - دستیار صوتی فارسی</h1>
        
        <div class="info">
            <h3>✅ سیستم فعال است</h3>
            <p>رابط وب ساده در حال اجرا</p>
            <p>برای رابط کامل، Flask را نصب کنید:</p>
            <code>pip install flask flask-cors</code>
        </div>
        
        <div class="error">
            <h3>⚠️ محدودیت‌های رابط ساده</h3>
            <p>• عدم پشتیبانی از تولید صوت real-time</p>
            <p>• عدم دسترسی به API</p>
            <p>• عدم پشتیبانی از تعامل کامل</p>
        </div>
        
        <h3>🔧 راهنمای استفاده</h3>
        <ol>
            <li>برای رابط کامل: <code>pip install flask flask-cors</code></li>
            <li>سپس اجرا کنید: <code>python main_functional.py --mode web</code></li>
            <li>یا از رابط دسکتاپ استفاده کنید: <code>python main_functional.py --mode desktop</code></li>
        </ol>
        
        <h3>📱 سایر گزینه‌ها</h3>
        <ul>
            <li><strong>CLI:</strong> <code>python main_functional.py --mode cli</code></li>
            <li><strong>Desktop:</strong> <code>python main_functional.py --mode desktop</code></li>
        </ul>
    </div>
</body>
</html>
                        """
                        self.wfile.write(html.encode('utf-8'))
                    else:
                        super().do_GET()
            
            server = HTTPServer(('localhost', args.port), HeystiveHTTPHandler)
            print(f"🌐 Simple web server running on http://localhost:{args.port}")
            print("💡 For full functionality, install Flask: pip install flask flask-cors")
            
            # Try to open browser
            try:
                webbrowser.open(f"http://localhost:{args.port}")
            except:
                pass
            
            server.serve_forever()
            
        except Exception as e:
            print(f"❌ Simple web server failed: {e}")
    
    def _run_cli_interface(self):
        """اجرای رابط CLI"""
        print("💻 Heystive CLI Interface")
        print("رابط خط فرمان هیستیو")
        print("=" * 40)
        
        try:
            from models.intelligent_model_manager import IntelligentModelManager
            manager = IntelligentModelManager()
            
            # Interactive CLI
            print("🎤 برای تولید صوت، متن فارسی وارد کنید (یا 'exit' برای خروج)")
            
            while True:
                try:
                    text = input("\n📝 متن فارسی: ").strip()
                    
                    if text.lower() in ['exit', 'quit', 'خروج']:
                        print("خداحافظ! 👋")
                        break
                    
                    if not text:
                        print("❌ متن نمی‌تواند خالی باشد")
                        continue
                    
                    print(f"🎤 تولید صوت برای: {text}")
                    
                    # Generate TTS
                    result = manager.generate_tts_audio(text)
                    
                    if result:
                        print(f"✅ صوت تولید شد: {result}")
                        
                        # Ask if user wants to play
                        play = input("آیا می‌خواهید صوت را پخش کنید؟ (y/n): ").strip().lower()
                        if play in ['y', 'yes', 'بله']:
                            try:
                                import subprocess
                                import platform
                                
                                system = platform.system()
                                if system == "Windows":
                                    os.startfile(result)
                                elif system == "Darwin":  # macOS
                                    subprocess.call(["open", result])
                                else:  # Linux
                                    subprocess.call(["xdg-open", result])
                                
                                print("🔊 صوت در حال پخش...")
                            except Exception as e:
                                print(f"❌ خطا در پخش: {e}")
                    else:
                        print("❌ خطا در تولید صوت")
                
                except KeyboardInterrupt:
                    print("\n\nخداحافظ! 👋")
                    break
                except Exception as e:
                    print(f"❌ خطا: {e}")
        
        except Exception as e:
            print(f"❌ CLI interface failed: {e}")
            # Fallback to simple CLI
            self._run_simple_cli()
    
    def _run_simple_cli(self):
        """CLI ساده بدون وابستگی"""
        print("💻 Simple CLI (No Dependencies)")
        print("CLI ساده (بدون وابستگی)")
        
        while True:
            try:
                text = input("\n📝 متن فارسی (یا 'exit' برای خروج): ").strip()
                
                if text.lower() in ['exit', 'quit', 'خروج']:
                    print("خداحافظ! 👋")
                    break
                
                if text:
                    print(f"✅ متن دریافت شد: {text}")
                    print("💡 برای تولید صوت واقعی، سیستم TTS را راه‌اندازی کنید")
                    
                    # Save to file as simulation
                    output_dir = Path("audio_output")
                    output_dir.mkdir(exist_ok=True)
                    
                    output_file = output_dir / f"cli_simulation_{int(__import__('time').time())}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"CLI TTS Simulation\nText: {text}\nTime: {datetime.now()}\n")
                    
                    print(f"📄 شبیه‌سازی ذخیره شد: {output_file}")
                
            except KeyboardInterrupt:
                print("\n\nخداحافظ! 👋")
                break
            except Exception as e:
                print(f"❌ خطا: {e}")
    
    def launch(self, mode: str, args):
        """راه‌اندازی حالت مشخص شده"""
        if mode not in self.modes:
            print(f"❌ Unknown mode: {mode}")
            print(f"Available modes: {', '.join(self.modes.keys())}")
            sys.exit(1)
        
        print(f"🚀 Launching Heystive in {mode} mode...")
        print(f"راه‌اندازی هیستیو در حالت {mode}...")
        
        self.modes[mode](args)

def main():
    """تابع اصلی"""
    parser = argparse.ArgumentParser(
        description="Heystive Persian Voice Assistant - Fully Functional System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎤 هیستیو - دستیار صوتی فارسی
Heystive Persian Voice Assistant - Fully Functional

Examples / نمونه‌ها:
  python main_functional.py                           # Desktop mode
  python main_functional.py --mode desktop            # Desktop GUI
  python main_functional.py --mode web --port 8080    # Web interface
  python main_functional.py --mode cli                # CLI interface

Features / ویژگی‌ها:
  🎤 Advanced Persian TTS with multiple engines
  🖥️ Modern desktop GUI with full functionality
  🌐 Professional web interface with real-time features
  💻 Interactive CLI interface
  🧠 Intelligent model management
  🔧 Automatic hardware detection and optimization
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["desktop", "web", "cli"], 
        default="desktop",
        help="Interface mode (default: desktop)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=5000,
        help="Port for web interface (default: 5000)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--config", 
        help="Configuration file path"
    )
    
    args = parser.parse_args()
    
    try:
        launcher = HeystiveFunctionalLauncher()
        launcher.launch(args.mode, args)
        
    except KeyboardInterrupt:
        print("\n\nبرنامه متوقف شد. خداحافظ! 👋")
    except Exception as e:
        logger.error(f"❌ Heystive failed to start: {e}")
        print(f"❌ خطا در راه‌اندازی هیستیو: {e}")
        print("💡 برای کمک، فایل PERSIAN_TTS_SETUP_REPORT.md را مطالعه کنید")
        sys.exit(1)

if __name__ == "__main__":
    main()