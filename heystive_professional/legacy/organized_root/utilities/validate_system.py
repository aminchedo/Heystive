#!/usr/bin/env python3
"""
System Validation Script for Persian Voice Assistant
Quick validation of all critical components
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def validate_imports():
    """Validate all critical imports"""
    print("📦 Validating imports...")
    
    try:
        # Core components
        from steve.core.voice_pipeline import SteveVoiceAssistant
        from steve.core.persian_tts import ElitePersianTTS
        from steve.core.wake_word_detector import PersianWakeWordDetector
        from steve.core.persian_stt import AdaptivePersianSTT
        
        # Intelligence components
        from steve.intelligence.llm_manager import PersianLLMManager
        
        # Smart home components
        from steve.smart_home.device_controller import SmartHomeController
        
        # Utility components
        from steve.utils.system_monitor import SystemPerformanceMonitor
        
        # Web interface
        from steve.ui.web_interface import SteveWebInterface
        
        # Main application
        from main import CompleteVoiceAssistant
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def validate_file_structure():
    """Validate file structure"""
    print("📁 Validating file structure...")
    
    required_files = [
        "main.py",
        "steve/__init__.py",
        "steve/core/__init__.py",
        "steve/core/voice_pipeline.py",
        "steve/core/persian_tts.py",
        "steve/core/wake_word_detector.py",
        "steve/core/persian_stt.py",
        "steve/intelligence/__init__.py",
        "steve/intelligence/llm_manager.py",
        "steve/smart_home/__init__.py",
        "steve/smart_home/device_controller.py",
        "steve/utils/__init__.py",
        "steve/utils/system_monitor.py",
        "steve/ui/__init__.py",
        "steve/ui/web_interface.py",
        "steve/ui/templates/dashboard.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

async def validate_basic_functionality():
    """Validate basic functionality"""
    print("⚙️ Validating basic functionality...")
    
    try:
        # Test system monitor
        from steve.utils.system_monitor import SystemPerformanceMonitor
        monitor = SystemPerformanceMonitor()
        config = await monitor.assess_system_capabilities()
        
        if not config or 'hardware_tier' not in config:
            print("❌ System monitor failed")
            return False
        
        print(f"✅ System monitor: {config['hardware_tier']} tier")
        
        # Test voice assistant creation
        from steve.core.voice_pipeline import SteveVoiceAssistant
        voice_assistant = SteveVoiceAssistant(config)
        
        if not voice_assistant:
            print("❌ Voice assistant creation failed")
            return False
        
        print("✅ Voice assistant created")
        
        # Test smart home controller
        from steve.smart_home.device_controller import SmartHomeController
        controller = SmartHomeController()
        
        if not controller:
            print("❌ Smart home controller creation failed")
            return False
        
        print("✅ Smart home controller created")
        
        # Test web interface
        from steve.ui.web_interface import SteveWebInterface
        web_interface = SteveWebInterface(voice_assistant)
        
        if not web_interface:
            print("❌ Web interface creation failed")
            return False
        
        print("✅ Web interface created")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality validation failed: {e}")
        return False

def validate_dependencies():
    """Validate critical dependencies"""
    print("🔧 Validating dependencies...")
    
    critical_deps = [
        'asyncio',
        'logging',
        'numpy',
        'flask',
        'threading',
        'datetime',
        'pathlib',
        'typing'
    ]
    
    missing_deps = []
    for dep in critical_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {missing_deps}")
        return False
    else:
        print("✅ All critical dependencies available")
        return True

async def main():
    """Main validation function"""
    print("🔍 Persian Voice Assistant System Validation")
    print("=" * 50)
    
    validation_results = []
    
    # Run all validations
    validation_results.append(validate_dependencies())
    validation_results.append(validate_file_structure())
    validation_results.append(validate_imports())
    validation_results.append(await validate_basic_functionality())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(validation_results)
    total = len(validation_results)
    
    if passed == total:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ System is ready to run")
        print("\n🚀 To start the system:")
        print("   python3 main.py")
        print("\n🌐 Web interface will be available at:")
        print("   http://localhost:5000")
        return True
    else:
        print(f"❌ {total - passed} validations failed")
        print("🔧 Please fix the issues above before running the system")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Validation interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Validation error: {e}")
        sys.exit(1)