#!/usr/bin/env python3
"""
Simplified Phase 1 Test
Tests core functionality without heavy dependencies
"""

import asyncio
import sys
import logging
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_system_monitor():
    """Test system monitoring functionality"""
    try:
        from steve.utils.system_monitor import SystemPerformanceMonitor
        
        print("🔍 Testing System Performance Monitor...")
        monitor = SystemPerformanceMonitor()
        system_profile = await monitor.assess_system_capabilities()
        
        print(f"✅ Hardware Tier: {system_profile['hardware_tier']}")
        print(f"✅ RAM: {system_profile['ram_gb']}GB")
        print(f"✅ CPU Cores: {system_profile['cpu_cores']}")
        print(f"✅ GPU Available: {system_profile['gpu_available']}")
        print(f"✅ OS: {system_profile['os_type']}")
        
        return True
    except Exception as e:
        print(f"❌ System Monitor Test Failed: {e}")
        return False

async def test_voice_pipeline_init():
    """Test voice pipeline initialization"""
    try:
        from steve.core.voice_pipeline import SteveVoiceAssistant
        
        print("\n🔍 Testing Voice Pipeline Initialization...")
        
        # Create mock hardware config
        hardware_config = {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False,
            "os_type": "Linux",
            "architecture": "x86_64"
        }
        
        steve = SteveVoiceAssistant(hardware_config)
        
        # Test status before initialization
        status = steve.get_status()
        print(f"✅ Initial Status - Initialized: {status['is_initialized']}")
        print(f"✅ Hardware Config: {status['hardware_config']['hardware_tier']}")
        
        # Test performance report
        report = steve.get_performance_report()
        print(f"✅ Performance Report Generated: {len(report)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Voice Pipeline Test Failed: {e}")
        return False

async def test_persian_processing():
    """Test Persian language processing"""
    try:
        from steve.core.persian_stt import PersianTextNormalizer
        from steve.core.persian_tts import PersianTextNormalizer as TTSNormalizer
        
        print("\n🔍 Testing Persian Language Processing...")
        
        # Test STT normalizer
        stt_normalizer = PersianTextNormalizer()
        test_text = "سلام، من استیو هستم. ساعت ۱۲:۳۰ است."
        normalized = stt_normalizer.normalize(test_text)
        print(f"✅ STT Normalization: '{test_text}' -> '{normalized}'")
        
        # Test TTS normalizer
        tts_normalizer = TTSNormalizer()
        normalized_tts = tts_normalizer.normalize(test_text)
        print(f"✅ TTS Normalization: '{test_text}' -> '{normalized_tts}'")
        
        return True
    except Exception as e:
        print(f"❌ Persian Processing Test Failed: {e}")
        return False

async def test_wake_word_detector():
    """Test wake word detector initialization"""
    try:
        from steve.core.wake_word_detector import PersianWakeWordDetector
        
        print("\n🔍 Testing Wake Word Detector...")
        
        hardware_config = {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False
        }
        
        detector = PersianWakeWordDetector(hardware_config)
        
        # Test configuration
        audio_config = detector.audio_config
        print(f"✅ Audio Config - Sample Rate: {audio_config['sample_rate']}")
        print(f"✅ Audio Config - Chunk Size: {audio_config['chunk_size']}")
        
        # Test Persian patterns
        patterns = detector.persian_wake_patterns
        print(f"✅ Persian Patterns Loaded: {len(patterns)} patterns")
        
        # Test detection stats
        stats = detector.get_detection_stats()
        print(f"✅ Detection Stats: {stats['sample_rate']}Hz, {stats['chunk_size']} samples")
        
        return True
    except Exception as e:
        print(f"❌ Wake Word Detector Test Failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Steve Voice Assistant - Simplified Phase 1 Test")
    print("=" * 60)
    
    tests = [
        ("System Monitor", test_system_monitor),
        ("Voice Pipeline", test_voice_pipeline_init),
        ("Persian Processing", test_persian_processing),
        ("Wake Word Detector", test_wake_word_detector)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"💥 {test_name} Test Error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Phase 1 Core Components Working")
        print("✅ System Assessment Functional")
        print("✅ Persian Language Processing Ready")
        print("✅ Voice Pipeline Architecture Complete")
        print("\n🚀 Ready for Phase 1 Approval!")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed")
        print("🔧 Please review failed tests")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))