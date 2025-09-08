#!/usr/bin/env python3
"""
Setup Script for Heystive Modern Interfaces
Installs dependencies and prepares the system for running
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def install_requirements():
    """Install requirements for all interfaces"""
    project_root = Path(__file__).parent
    
    # Basic requirements first
    basic_requirements = [
        "requests>=2.31.0",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "jinja2>=3.1.2",
        "python-multipart>=0.0.6",
        "websockets>=12.0",
        "psutil>=5.9.6"
    ]
    
    print("📦 Installing basic requirements...")
    for req in basic_requirements:
        if not run_command(f"pip3 install '{req}'", f"Installing {req}"):
            print(f"⚠️ Failed to install {req}, continuing...")
    
    # Web interface requirements
    web_req_file = project_root / "ui_modern_web" / "requirements-web.txt"
    if web_req_file.exists():
        run_command(f"pip3 install -r '{web_req_file}'", "Installing web interface requirements")
    
    # Desktop interface requirements (optional)
    desktop_req_file = project_root / "ui_modern_desktop" / "requirements-desktop.txt"
    if desktop_req_file.exists():
        print("📱 Installing desktop interface requirements (optional)...")
        if not run_command(f"pip3 install -r '{desktop_req_file}'", "Installing desktop requirements"):
            print("⚠️ Desktop requirements failed - desktop interface may not work")
            print("   This is normal if you only want the web interface")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip
    try:
        subprocess.run(["pip3", "--version"], check=True, capture_output=True)
        print("✅ pip3 is available")
    except subprocess.CalledProcessError:
        print("❌ pip3 not found")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    project_root = Path(__file__).parent
    
    directories = [
        "ui_modern_web/static/audio",
        "ui_modern_web/logs",
        "ui_modern_desktop/logs",
        "logs"
    ]
    
    for dir_path in directories:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")

def create_startup_scripts():
    """Create convenient startup scripts"""
    project_root = Path(__file__).parent
    
    # Web interface startup script
    web_script = project_root / "start_web.py"
    web_script.write_text("""#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# Start web interface
web_path = Path(__file__).parent / "ui_modern_web" / "app.py"
subprocess.run([sys.executable, str(web_path)])
""")
    
    # Desktop interface startup script
    desktop_script = project_root / "start_desktop.py"
    desktop_script.write_text("""#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# Start desktop interface
desktop_path = Path(__file__).parent / "ui_modern_desktop" / "main_desktop.py"
subprocess.run([sys.executable, str(desktop_path)])
""")
    
    # Make scripts executable on Unix-like systems
    try:
        os.chmod(web_script, 0o755)
        os.chmod(desktop_script, 0o755)
    except:
        pass  # Windows doesn't need chmod
    
    print("✅ Created startup scripts: start_web.py, start_desktop.py")

def test_installation():
    """Test if installation was successful"""
    print("🧪 Testing installation...")
    
    try:
        # Test basic imports
        import requests
        import fastapi
        import uvicorn
        import jinja2
        print("✅ Basic web dependencies available")
        
        # Test PySide6 (optional)
        try:
            import PySide6
            print("✅ PySide6 available - desktop interface will work")
        except ImportError:
            print("⚠️ PySide6 not available - desktop interface disabled")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🎤 Heystive Modern Interfaces - Setup")
    print("=" * 50)
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System requirements not met")
        return False
    
    # Create directories
    create_directories()
    
    # Install requirements
    install_requirements()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Test installation
    if test_installation():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the launcher: python3 modern_launcher/launcher.py")
        print("2. Or start web interface directly: python3 start_web.py")
        print("3. Or start desktop interface: python3 start_desktop.py")
        print("\nFor the complete experience:")
        print("• First start the existing backend: cd heystive_professional && python3 main.py --mode web")
        print("• Then start a modern interface")
        
        return True
    else:
        print("\n❌ Setup completed with errors")
        print("Some components may not work correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)