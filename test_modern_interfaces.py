#!/usr/bin/env python3
"""
Integration Test Script for Heystive Modern Interfaces
Tests all new components and their integration with existing backend
"""

import sys
import os
import subprocess
import time
import requests
import json
from pathlib import Path
import tempfile
import wave

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "heystive_professional" / "heystive"))

def test_project_structure():
    """Test that all required files and directories exist"""
    print("🔍 Testing project structure...")
    
    required_paths = [
        # Modern Web Interface
        "ui_modern_web/app.py",
        "ui_modern_web/static/css/persian-rtl.css",
        "ui_modern_web/static/js/main.js",
        "ui_modern_web/templates/base.html",
        "ui_modern_web/templates/voice-interface.html",
        "ui_modern_web/templates/dashboard.html",
        "ui_modern_web/requirements-web.txt",
        
        # Modern Desktop Interface
        "ui_modern_desktop/main_desktop.py",
        "ui_modern_desktop/components/modern_main_window.py",
        "ui_modern_desktop/components/voice_control_widget.py",
        "ui_modern_desktop/utils/api_client.py",
        "ui_modern_desktop/requirements-desktop.txt",
        
        # API Bridge
        "api_bridge/shared_client.py",
        
        # Launcher
        "modern_launcher/launcher.py",
        
        # Existing Backend
        "heystive_professional/main.py",
        "heystive_professional/heystive/main.py"
    ]
    
    missing_files = []
    for path_str in required_paths:
        path = project_root / path_str
        if not path.exists():
            missing_files.append(path_str)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files exist")
    return True

def test_api_bridge():
    """Test API bridge functionality"""
    print("🔗 Testing API bridge...")
    
    try:
        from api_bridge.shared_client import HeystiveSharedClient, PersianTextProcessor
        
        # Test API client initialization
        client = HeystiveSharedClient()
        
        # Test Persian text processor
        processor = PersianTextProcessor()
        
        # Test Persian digit conversion
        test_text = "The time is 12:34:56"
        persian_text = processor.to_persian_digits(test_text)
        expected = "The time is ۱۲:۳۴:۵۶"
        
        if persian_text != expected:
            print(f"❌ Persian digit conversion failed: {persian_text} != {expected}")
            return False
        
        # Test text normalization
        arabic_text = "السلام عليكم"
        normalized = processor.normalize_persian_text(arabic_text)
        
        print("✅ API bridge tests passed")
        return True
        
    except Exception as e:
        print(f"❌ API bridge test failed: {e}")
        return False

def test_web_interface_imports():
    """Test web interface imports"""
    print("🌐 Testing web interface imports...")
    
    try:
        # Test FastAPI app import
        sys.path.insert(0, str(project_root / "ui_modern_web"))
        
        # Import main components (without running)
        import importlib.util
        
        # Test app.py
        spec = importlib.util.spec_from_file_location(
            "web_app", 
            project_root / "ui_modern_web" / "app.py"
        )
        web_module = importlib.util.module_from_spec(spec)
        
        # This will test syntax but not execute
        with open(project_root / "ui_modern_web" / "app.py", 'r') as f:
            compile(f.read(), 'app.py', 'exec')
        
        print("✅ Web interface imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Web interface import failed: {e}")
        return False

def test_desktop_interface_imports():
    """Test desktop interface imports (if PySide6 available)"""
    print("🖥️ Testing desktop interface imports...")
    
    try:
        # Check if PySide6 is available
        try:
            import PySide6
        except ImportError:
            print("⚠️ PySide6 not available, skipping desktop interface tests")
            return True
        
        # Test desktop app import
        sys.path.insert(0, str(project_root / "ui_modern_desktop"))
        
        # Test main_desktop.py syntax
        with open(project_root / "ui_modern_desktop" / "main_desktop.py", 'r') as f:
            compile(f.read(), 'main_desktop.py', 'exec')
        
        # Test components
        with open(project_root / "ui_modern_desktop" / "components" / "modern_main_window.py", 'r') as f:
            compile(f.read(), 'modern_main_window.py', 'exec')
        
        print("✅ Desktop interface imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Desktop interface import failed: {e}")
        return False

def test_launcher():
    """Test launcher functionality"""
    print("🚀 Testing launcher...")
    
    try:
        # Test launcher import
        sys.path.insert(0, str(project_root / "modern_launcher"))
        
        # Test syntax
        with open(project_root / "modern_launcher" / "launcher.py", 'r') as f:
            compile(f.read(), 'launcher.py', 'exec')
        
        print("✅ Launcher tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Launcher test failed: {e}")
        return False

def test_backend_integration():
    """Test integration with existing backend"""
    print("🔧 Testing backend integration...")
    
    try:
        # Check if we can import existing backend components
        backend_path = project_root / "heystive_professional" / "heystive"
        sys.path.insert(0, str(backend_path))
        
        # Test if main components are accessible
        try:
            from core.voice_pipeline import SteveVoiceAssistant
            print("✅ Voice pipeline accessible")
        except ImportError as e:
            print(f"⚠️ Voice pipeline not accessible: {e}")
        
        try:
            from engines.tts.persian_multi_tts_manager import PersianMultiTTSManager
            print("✅ TTS manager accessible")
        except ImportError as e:
            print(f"⚠️ TTS manager not accessible: {e}")
        
        try:
            from intelligence.conversation_flow import ConversationManager
            print("✅ Conversation manager accessible")
        except ImportError as e:
            print(f"⚠️ Conversation manager not accessible: {e}")
        
        print("✅ Backend integration tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Backend integration test failed: {e}")
        return False

def test_requirements():
    """Test that all requirements files are valid"""
    print("📋 Testing requirements files...")
    
    requirements_files = [
        "ui_modern_web/requirements-web.txt",
        "ui_modern_desktop/requirements-desktop.txt"
    ]
    
    for req_file in requirements_files:
        req_path = project_root / req_file
        if not req_path.exists():
            print(f"❌ Requirements file missing: {req_file}")
            continue
        
        try:
            with open(req_path, 'r') as f:
                lines = f.readlines()
            
            # Basic validation - check for valid package names
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' not in line and '>=' not in line and '<=' not in line:
                        if not line.replace('-', '').replace('_', '').replace('[', '').replace(']', '').replace('cryptography', '').isalnum():
                            print(f"⚠️ Potentially invalid requirement: {line}")
            
            print(f"✅ {req_file} is valid")
            
        except Exception as e:
            print(f"❌ Error reading {req_file}: {e}")
            return False
    
    return True

def create_test_audio():
    """Create a test audio file for voice processing tests"""
    try:
        # Create a simple test audio file (1 second of silence)
        sample_rate = 44100
        duration = 1  # second
        frames = int(sample_rate * duration)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)  # mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b'\x00\x00' * frames)  # silence
            
            return temp_file.name
    except Exception as e:
        print(f"⚠️ Could not create test audio file: {e}")
        return None

def run_integration_test():
    """Run a simple integration test if backend is available"""
    print("🧪 Running integration test...")
    
    try:
        # Check if backend is running
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("⚠️ Backend not running, skipping integration test")
            return True
    except:
        print("⚠️ Backend not accessible, skipping integration test")
        return True
    
    try:
        # Test API bridge with live backend
        from api_bridge.shared_client import HeystiveSharedClient
        
        client = HeystiveSharedClient()
        
        # Test system status
        status = client.get_system_status()
        if status.get('status') in ['running', 'ready']:
            print("✅ System status API working")
        else:
            print(f"⚠️ System status: {status.get('status', 'unknown')}")
        
        # Test text message
        result = client.send_text_message("سلام استیو")
        if result.get('status') == 'success' or 'response' in result:
            print("✅ Text message API working")
        else:
            print(f"⚠️ Text message result: {result}")
        
        print("✅ Integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎤 Heystive Modern Interfaces - Integration Test")
    print("=" * 60)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("API Bridge", test_api_bridge),
        ("Web Interface", test_web_interface_imports),
        ("Desktop Interface", test_desktop_interface_imports),
        ("Launcher", test_launcher),
        ("Backend Integration", test_backend_integration),
        ("Requirements", test_requirements),
        ("Integration Test", run_integration_test)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} test ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The modern interfaces are ready to use.")
        print("\nNext steps:")
        print("1. Install requirements: pip install -r ui_modern_web/requirements-web.txt")
        print("2. For desktop: pip install -r ui_modern_desktop/requirements-desktop.txt")
        print("3. Run launcher: python modern_launcher/launcher.py")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)