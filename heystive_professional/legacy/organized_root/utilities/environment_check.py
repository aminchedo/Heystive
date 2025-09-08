#!/usr/bin/env python3
"""
Environment Check Script for Heystive Persian Voice Assistant
Diagnoses Python environment and dependency issues
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Python Version Check")
    print("-" * 30)
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    
    if version < (3, 8):
        print("❌ ERROR: Python 3.8+ required")
        return False
    elif version >= (3, 8):
        print("✅ Python version compatible")
        return True

def check_stdlib_modules():
    """Check standard library modules"""
    print("\n📚 Standard Library Check")
    print("-" * 30)
    
    stdlib_modules = {
        'select': 'System I/O multiplexing',
        'asyncio': 'Asynchronous programming',
        'sqlite3': 'Database interface', 
        'threading': 'Thread-based parallelism',
        'tempfile': 'Temporary file handling',
        'base64': 'Base64 encoding/decoding',
        'pathlib': 'Object-oriented filesystem paths',
        'json': 'JSON encoder/decoder'
    }
    
    all_available = True
    for module, description in stdlib_modules.items():
        try:
            __import__(module)
            print(f"✅ {module}: Available ({description})")
        except ImportError as e:
            print(f"❌ {module}: Missing - {e}")
            all_available = False
    
    return all_available

def check_environment_type():
    """Check if we're in a virtual environment"""
    print("\n📦 Environment Type Check")
    print("-" * 30)
    
    in_venv = False
    
    # Check for virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        print(f"   Virtual env path: {sys.prefix}")
        in_venv = True
    else:
        print("🌍 System Python detected")
        print("   Recommendation: Create virtual environment")
    
    # Check for externally managed environment
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if 'externally-managed-environment' in result.stderr.lower():
            print("⚠️ Externally-managed environment detected (PEP 668)")
            if not in_venv:
                print("   SOLUTION: Must use virtual environment")
                print("   Command: python3 -m venv .venv && source .venv/bin/activate")
    except Exception as e:
        print(f"⚠️ Could not check pip status: {e}")
    
    return in_venv

def check_dependencies():
    """Check for required dependencies"""
    print("\n🔧 Dependency Check")
    print("-" * 30)
    
    # Core dependencies for TTS functionality
    required_deps = {
        'numpy': 'Numerical computing',
        'pyttsx3': 'Text-to-speech engine',
        'gtts': 'Google Text-to-Speech',
        'requests': 'HTTP library',
        'pygame': 'Audio playback',
    }
    
    optional_deps = {
        'torch': 'Machine learning framework',
        'librosa': 'Audio analysis',
        'transformers': 'NLP models',
        'pyaudio': 'Audio I/O',
        'soundfile': 'Audio file I/O'
    }
    
    available_count = 0
    total_count = len(required_deps)
    
    print("Required dependencies:")
    for package, description in required_deps.items():
        try:
            __import__(package)
            print(f"✅ {package}: Available ({description})")
            available_count += 1
        except ImportError:
            print(f"❌ {package}: Missing ({description})")
    
    print(f"\nOptional dependencies:")
    optional_available = 0
    for package, description in optional_deps.items():
        try:
            __import__(package)
            print(f"✅ {package}: Available ({description})")
            optional_available += 1
        except ImportError:
            print(f"⚠️ {package}: Missing ({description})")
    
    print(f"\nDependency Summary:")
    print(f"Required: {available_count}/{total_count}")
    print(f"Optional: {optional_available}/{len(optional_deps)}")
    
    return available_count == total_count

def check_audio_system():
    """Check audio system availability"""
    print("\n🔊 Audio System Check")
    print("-" * 30)
    
    audio_working = True
    
    # Check PyAudio
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        p.terminate()
        print(f"✅ PyAudio: {device_count} audio devices available")
    except ImportError:
        print("❌ PyAudio: Not installed")
        audio_working = False
    except Exception as e:
        print(f"⚠️ PyAudio: Error - {e}")
        audio_working = False
    
    # Check pygame audio
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.quit()
        print("✅ Pygame audio: Available")
    except ImportError:
        print("❌ Pygame: Not installed")
    except Exception as e:
        print(f"⚠️ Pygame audio: Error - {e}")
    
    return audio_working

def check_file_permissions():
    """Check file system permissions"""
    print("\n📁 File System Check")
    print("-" * 30)
    
    project_root = Path(__file__).parent
    
    # Check read permissions
    key_files = ['requirements.txt', 'test_tts_real.py', 'steve/core/tts_engine.py']
    for file_path in key_files:
        full_path = project_root / file_path
        if full_path.exists():
            if os.access(full_path, os.R_OK):
                print(f"✅ {file_path}: Readable")
            else:
                print(f"❌ {file_path}: Not readable")
        else:
            print(f"⚠️ {file_path}: File not found")
    
    # Check write permissions in project directory
    try:
        test_file = project_root / '.permission_test'
        test_file.write_text('test')
        test_file.unlink()
        print("✅ Project directory: Writable")
        return True
    except Exception as e:
        print(f"❌ Project directory: Not writable - {e}")
        return False

def generate_recommendations():
    """Generate recommendations based on checks"""
    print("\n💡 Recommendations")
    print("-" * 30)
    
    recommendations = []
    
    # Check if in virtual environment
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        recommendations.append("1. Create and activate virtual environment:")
        recommendations.append("   python3 -m venv .venv")
        recommendations.append("   source .venv/bin/activate  # Linux/macOS")
        recommendations.append("   .venv\\Scripts\\activate     # Windows")
        recommendations.append("")
    
    # Check for missing dependencies
    try:
        import numpy, pyttsx3, gtts, requests
    except ImportError:
        recommendations.append("2. Install core dependencies:")
        recommendations.append("   python -m pip install numpy pyttsx3 gtts requests pygame")
        recommendations.append("")
    
    # Check for audio system
    try:
        import pyaudio
    except ImportError:
        recommendations.append("3. Install audio system dependencies:")
        recommendations.append("   # Ubuntu/Debian:")
        recommendations.append("   sudo apt-get install portaudio19-dev")
        recommendations.append("   python -m pip install pyaudio")
        recommendations.append("   # macOS:")
        recommendations.append("   brew install portaudio")
        recommendations.append("   python -m pip install pyaudio")
        recommendations.append("")
    
    recommendations.append("4. Test the installation:")
    recommendations.append("   python3 test_tts_real.py")
    recommendations.append("")
    recommendations.append("5. Use the safe installation script:")
    recommendations.append("   chmod +x install_safe.sh")
    recommendations.append("   ./install_safe.sh")
    
    for rec in recommendations:
        print(rec)

def main():
    """Main diagnostic function"""
    print("🔍 Heystive Environment Diagnostic Tool")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Standard Library", check_stdlib_modules), 
        ("Environment Type", check_environment_type),
        ("Dependencies", check_dependencies),
        ("Audio System", check_audio_system),
        ("File Permissions", check_file_permissions)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results[check_name] = False
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Environment is ready for Heystive!")
    else:
        print("🔧 Environment needs setup. See recommendations below:")
        generate_recommendations()

if __name__ == "__main__":
    main()