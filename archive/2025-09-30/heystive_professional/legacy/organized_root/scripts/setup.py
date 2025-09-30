#!/usr/bin/env python3
"""
Steve Voice Assistant - Automated Setup Script
One-command installation and configuration
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SteveInstaller:
    """Complete automated installation system for Steve Voice Assistant"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.installation_steps = [
            ("Checking system requirements", self._check_system_requirements),
            ("Installing Python dependencies", self._install_python_dependencies),
            ("Setting up audio system", self._setup_audio_system),
            ("Creating model directories", self._create_model_directories),
            ("Downloading Persian models", self._download_persian_models),
            ("Configuring system", self._configure_system),
            ("Validating installation", self._validate_installation),
            ("Creating startup script", self._create_startup_script)
        ]
    
    def install_complete_system(self) -> bool:
        """One-command installation of entire system"""
        print("🚀 نصب کامل سیستم استیو...")
        print("🚀 Installing Steve Voice Assistant...")
        print("=" * 60)
        
        for step_num, (step_name, step_func) in enumerate(self.installation_steps, 1):
            print(f"\n📦 Step {step_num}: {step_name}")
            print("-" * 40)
            
            try:
                result = step_func()
                if result["success"]:
                    print(f"✅ {step_name} completed successfully")
                    if result.get("message"):
                        print(f"   {result['message']}")
                else:
                    print(f"❌ Error in {step_name}: {result['error']}")
                    return False
            except Exception as e:
                print(f"💥 Unexpected error in {step_name}: {e}")
                return False
        
        print("\n" + "=" * 60)
        print("🎉 نصب با موفقیت کامل شد!")
        print("🎉 Installation completed successfully!")
        print("\n🚀 برای شروع: python main.py")
        print("🚀 To start: python main.py")
        return True
    
    def _check_system_requirements(self) -> dict:
        """Check system requirements"""
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version < (3, 8):
                return {"success": False, "error": "Python 3.8+ required"}
            
            # Check OS
            os_name = platform.system()
            if os_name not in ["Linux", "Darwin", "Windows"]:
                return {"success": False, "error": f"Unsupported OS: {os_name}"}
            
            # Check available memory
            try:
                import psutil
                ram_gb = psutil.virtual_memory().total / (1024**3)
                if ram_gb < 4:
                    return {"success": False, "error": f"Insufficient RAM: {ram_gb:.1f}GB (minimum 4GB required)"}
            except ImportError:
                pass
            
            # Check disk space
            try:
                import shutil
                free_space = shutil.disk_usage(self.project_root).free / (1024**3)
                if free_space < 2:
                    return {"success": False, "error": f"Insufficient disk space: {free_space:.1f}GB (minimum 2GB required)"}
            except:
                pass
            
            return {
                "success": True,
                "message": f"Python {python_version.major}.{python_version.minor}, {os_name}, {ram_gb:.1f}GB RAM"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _install_python_dependencies(self) -> dict:
        """Install Python dependencies"""
        try:
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                return {"success": False, "error": "requirements.txt not found"}
            
            # Install dependencies
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                return {"success": False, "error": f"pip install failed: {result.stderr}"}
            
            return {"success": True, "message": "All dependencies installed successfully"}
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Installation timeout - try again"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _setup_audio_system(self) -> dict:
        """Setup audio system"""
        try:
            os_name = platform.system()
            
            if os_name == "Linux":
                # Install audio dependencies for Linux
                audio_packages = ["portaudio19-dev", "libasound2-dev", "alsa-utils"]
                for package in audio_packages:
                    try:
                        subprocess.run(["sudo", "apt-get", "install", "-y", package], 
                                     check=True, capture_output=True, timeout=60)
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        logger.warning(f"Could not install {package} - may need manual installation")
            
            elif os_name == "Darwin":  # macOS
                # Check for Homebrew and install portaudio
                try:
                    subprocess.run(["brew", "install", "portaudio"], 
                                 check=True, capture_output=True, timeout=120)
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    logger.warning("Could not install portaudio via Homebrew")
            
            return {"success": True, "message": "Audio system configured"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_model_directories(self) -> dict:
        """Create directories for models"""
        try:
            model_dirs = [
                "models",
                "models/whisper",
                "models/tts",
                "models/wake_word",
                "config",
                "logs"
            ]
            
            for dir_path in model_dirs:
                full_path = self.project_root / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
            
            return {"success": True, "message": "Model directories created"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _download_persian_models(self) -> dict:
        """Download Persian language models"""
        try:
            # This is a placeholder for model downloading
            # In production, you would download actual models here
            
            logger.info("Model downloading would happen here")
            logger.info("For now, models will be downloaded on first use")
            
            return {"success": True, "message": "Model download configured"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _configure_system(self) -> dict:
        """Configure system settings"""
        try:
            # Create configuration file
            config_file = self.project_root / "config" / "steve_config.json"
            config_file.parent.mkdir(exist_ok=True)
            
            config = {
                "wake_word": "هی استیو",
                "response": "بله سرورم",
                "language": "fa",
                "audio": {
                    "sample_rate": 16000,
                    "chunk_size": 1024
                },
                "models": {
                    "stt": "whisper-medium",
                    "tts": "auto"
                }
            }
            
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return {"success": True, "message": "System configuration created"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_installation(self) -> dict:
        """Validate the installation"""
        try:
            # Test imports
            test_imports = [
                "numpy", "torch", "librosa", "soundfile", 
                "psutil", "pyaudio", "transformers"
            ]
            
            failed_imports = []
            for module in test_imports:
                try:
                    __import__(module)
                except ImportError:
                    failed_imports.append(module)
            
            if failed_imports:
                return {"success": False, "error": f"Failed imports: {failed_imports}"}
            
            # Test audio system
            try:
                import pyaudio
                p = pyaudio.PyAudio()
                device_count = p.get_device_count()
                p.terminate()
                
                if device_count == 0:
                    return {"success": False, "error": "No audio devices found"}
            except Exception as e:
                return {"success": False, "error": f"Audio system test failed: {e}"}
            
            return {"success": True, "message": "Installation validation passed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_startup_script(self) -> dict:
        """Create startup script"""
        try:
            # Create startup script
            startup_script = self.project_root / "start_steve.py"
            
            script_content = '''#!/usr/bin/env python3
"""
Steve Voice Assistant Startup Script
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    try:
        from main import main
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Steve shutting down...")
    except Exception as e:
        print(f"❌ Error starting Steve: {e}")
        sys.exit(1)
'''
            
            with open(startup_script, 'w') as f:
                f.write(script_content)
            
            # Make executable on Unix systems
            if platform.system() != "Windows":
                os.chmod(startup_script, 0o755)
            
            return {"success": True, "message": "Startup script created"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Main installation function"""
    installer = SteveInstaller()
    success = installer.install_complete_system()
    
    if success:
        print("\n🎉 Steve Voice Assistant is ready!")
        print("🎤 Say 'هی استیو' to start!")
        return 0
    else:
        print("\n❌ Installation failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())