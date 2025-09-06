#!/usr/bin/env python3
"""
Core Phase 1 Test - Demonstrates working functionality
Tests the essential components that are available
"""

import asyncio
import sys
import logging
from pathlib import Path
import time
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_system_assessment():
    """Test comprehensive system assessment"""
    try:
        from steve.utils.system_monitor import SystemPerformanceMonitor
        
        print("🔍 Testing System Assessment...")
        monitor = SystemPerformanceMonitor()
        system_profile = await monitor.assess_system_capabilities()
        
        # Validate system profile
        required_fields = ["hardware_tier", "ram_gb", "cpu_cores", "gpu_available", "os_type"]
        for field in required_fields:
            if field not in system_profile:
                print(f"❌ Missing field: {field}")
                return False
        
        print(f"✅ Hardware Tier: {system_profile['hardware_tier']}")
        print(f"✅ RAM: {system_profile['ram_gb']}GB")
        print(f"✅ CPU Cores: {system_profile['cpu_cores']}")
        print(f"✅ GPU Available: {system_profile['gpu_available']}")
        print(f"✅ OS: {system_profile['os_type']}")
        
        # Test performance monitoring
        current_metrics = await monitor.monitor_performance()
        print(f"✅ Performance Monitoring: CPU {current_metrics.get('cpu_usage', 0):.1f}%")
        
        # Test system summary
        summary = monitor.get_system_summary()
        print(f"✅ System Summary Generated: {len(summary)} characters")
        
        return True
    except Exception as e:
        print(f"❌ System Assessment Failed: {e}")
        return False

async def test_persian_language_processing():
    """Test Persian language processing components"""
    try:
        print("\n🔍 Testing Persian Language Processing...")
        
        # Test Persian text normalization
        from steve.core.persian_stt import PersianTextNormalizer
        
        normalizer = PersianTextNormalizer()
        
        # Test cases
        test_cases = [
            "سلام، من استیو هستم",
            "ساعت ۱۲:۳۰ است",
            "چراغ را روشن کن",
            "هوا چطور است؟"
        ]
        
        for test_text in test_cases:
            normalized = normalizer.normalize(test_text)
            print(f"✅ Normalized: '{test_text}' -> '{normalized}'")
        
        # Test Persian text processing for TTS
        from steve.core.persian_tts import PersianTextNormalizer as TTSNormalizer
        
        tts_normalizer = TTSNormalizer()
        
        for test_text in test_cases:
            normalized = tts_normalizer.normalize(test_text)
            print(f"✅ TTS Normalized: '{test_text}' -> '{normalized}'")
        
        return True
    except Exception as e:
        print(f"❌ Persian Language Processing Failed: {e}")
        return False

async def test_voice_pipeline_architecture():
    """Test voice pipeline architecture without heavy dependencies"""
    try:
        print("\n🔍 Testing Voice Pipeline Architecture...")
        
        from steve.core.voice_pipeline import SteveVoiceAssistant
        
        # Create hardware config
        hardware_config = {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False,
            "os_type": "Linux",
            "architecture": "x86_64"
        }
        
        # Test Steve initialization
        steve = SteveVoiceAssistant(hardware_config)
        
        # Test status
        status = steve.get_status()
        print(f"✅ Steve Status - Initialized: {status['is_initialized']}")
        print(f"✅ Hardware Config: {status['hardware_config']['hardware_tier']}")
        print(f"✅ Configuration: {len(status['config'])} settings")
        
        # Test performance report
        report = steve.get_performance_report()
        print(f"✅ Performance Report: {len(report)} characters")
        
        # Test response generation (without audio)
        test_responses = [
            "سلام",
            "کمک",
            "ساعت",
            "چراغ را روشن کن"
        ]
        
        for user_input in test_responses:
            response = await steve._generate_response(user_input)
            print(f"✅ Response to '{user_input}': '{response}'")
        
        return True
    except Exception as e:
        print(f"❌ Voice Pipeline Architecture Failed: {e}")
        return False

async def test_hardware_adaptation():
    """Test hardware adaptation logic"""
    try:
        print("\n🔍 Testing Hardware Adaptation...")
        
        # Test different hardware tiers
        hardware_configs = [
            {"ram_gb": 16, "cpu_cores": 8, "gpu_available": True, "hardware_tier": "high"},
            {"ram_gb": 8, "cpu_cores": 4, "gpu_available": False, "hardware_tier": "medium"},
            {"ram_gb": 4, "cpu_cores": 2, "gpu_available": False, "hardware_tier": "low"}
        ]
        
        for config in hardware_configs:
            from steve.core.persian_stt import AdaptivePersianSTT
            
            stt = AdaptivePersianSTT(config)
            tier = stt._assess_hardware_tier()
            model_config = stt._select_optimal_model_config()
            
            print(f"✅ Hardware: {config['ram_gb']}GB RAM, {config['cpu_cores']} cores")
            print(f"   Tier: {tier}, Model: {model_config['primary_model']}")
        
        return True
    except Exception as e:
        print(f"❌ Hardware Adaptation Failed: {e}")
        return False

async def test_persian_wake_word_logic():
    """Test Persian wake word detection logic"""
    try:
        print("\n🔍 Testing Persian Wake Word Logic...")
        
        from steve.core.wake_word_detector import PersianWakeWordDetector
        
        hardware_config = {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False
        }
        
        detector = PersianWakeWordDetector(hardware_config)
        
        # Test Persian patterns
        patterns = detector.persian_wake_patterns
        print(f"✅ Persian Patterns: {len(patterns)} patterns loaded")
        
        for pattern_name, pattern_data in patterns.items():
            print(f"   - {pattern_name}: '{pattern_data['persian_text']}'")
            print(f"     Phonemes: {pattern_data['phonemes']}")
            print(f"     Duration: {pattern_data['duration_range']} seconds")
        
        # Test audio configuration
        audio_config = detector.audio_config
        print(f"✅ Audio Config: {audio_config['sample_rate']}Hz, {audio_config['chunk_size']} samples")
        
        # Test detection stats
        stats = detector.get_detection_stats()
        print(f"✅ Detection Stats: {stats['sample_rate']}Hz, threshold: {stats['detection_threshold']}")
        
        return True
    except Exception as e:
        print(f"❌ Persian Wake Word Logic Failed: {e}")
        return False

async def test_performance_metrics():
    """Test performance metrics collection"""
    try:
        print("\n🔍 Testing Performance Metrics...")
        
        from steve.utils.system_monitor import SystemPerformanceMonitor
        
        monitor = SystemPerformanceMonitor()
        
        # Test system assessment
        system_profile = await monitor.assess_system_capabilities()
        
        # Test performance monitoring
        metrics = await monitor.monitor_performance()
        
        print(f"✅ System Profile: {len(system_profile)} fields")
        print(f"✅ Performance Metrics: {len(metrics)} metrics")
        print(f"✅ CPU Usage: {metrics.get('cpu_usage', 0):.1f}%")
        print(f"✅ Memory Usage: {metrics.get('memory_usage', 0):.1f}%")
        
        # Test system summary
        summary = monitor.get_system_summary()
        print(f"✅ System Summary: {len(summary)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Performance Metrics Failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Steve Voice Assistant - Core Phase 1 Test")
    print("=" * 60)
    
    tests = [
        ("System Assessment", test_system_assessment),
        ("Persian Language Processing", test_persian_language_processing),
        ("Voice Pipeline Architecture", test_voice_pipeline_architecture),
        ("Hardware Adaptation", test_hardware_adaptation),
        ("Persian Wake Word Logic", test_persian_wake_word_logic),
        ("Performance Metrics", test_performance_metrics)
    ]
    
    passed = 0
    total = len(tests)
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"💥 {test_name} Test Error: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL CORE TESTS PASSED!")
        print("✅ System Assessment: Working")
        print("✅ Persian Language Processing: Working")
        print("✅ Voice Pipeline Architecture: Working")
        print("✅ Hardware Adaptation: Working")
        print("✅ Persian Wake Word Logic: Working")
        print("✅ Performance Metrics: Working")
        print("\n🚀 PHASE 1 CORE COMPONENTS VALIDATED!")
        print("✅ Ready for Phase 1 Approval")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed")
        print("🔧 Please review failed tests")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))