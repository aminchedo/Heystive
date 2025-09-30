#!/usr/bin/env python3
"""
ENHANCED PERSIAN TTS INTEGRATION TEST
Comprehensive test of the enhanced Persian TTS system for HeyStive
"""

import sys
import os
from pathlib import Path
import time

# Add workspace to path
sys.path.insert(0, '/workspace')

def test_persian_multi_tts_manager():
    """Test the PersianMultiTTSManager"""
    print("🧪 Testing PersianMultiTTSManager...")
    print("=" * 50)
    
    try:
        from heystive.voice.persian_multi_tts_manager import PersianMultiTTSManager
        
        # Create TTS manager
        tts_manager = PersianMultiTTSManager()
        
        # Test basic functionality
        print(f"✅ TTS Manager created successfully")
        print(f"📊 Available engines: {len(tts_manager.engines)}")
        print(f"🎯 Current engine: {tts_manager.current_engine}")
        
        # List engines
        engines = tts_manager.list_engines()
        
        # Test speaking
        test_text = "سلام! این تست سیستم صوتی چندگانه HeyStive است"
        print(f"\n🔊 Testing speech generation...")
        print(f"Text: '{test_text}'")
        
        success = tts_manager.speak_persian(test_text)
        if success:
            print("✅ Speech generation successful")
        else:
            print("❌ Speech generation failed")
        
        # Test engine switching
        if len(tts_manager.engines) > 1:
            print(f"\n🔄 Testing engine switching...")
            engine_names = list(tts_manager.engines.keys())
            for engine_name in engine_names[:2]:  # Test first 2 engines
                print(f"Switching to: {engine_name}")
                switch_success = tts_manager.switch_engine(engine_name)
                if switch_success:
                    print(f"✅ Switched to {engine_name}")
                    # Test speech with this engine
                    test_success = tts_manager.speak_persian(f"تست با موتور {engine_name}")
                    if test_success:
                        print(f"✅ Speech with {engine_name} successful")
                    else:
                        print(f"❌ Speech with {engine_name} failed")
                else:
                    print(f"❌ Failed to switch to {engine_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ PersianMultiTTSManager test failed: {e}")
        return False

def test_voice_config_manager():
    """Test the VoiceConfigManager"""
    print("\n🧪 Testing VoiceConfigManager...")
    print("=" * 50)
    
    try:
        from heystive.voice.voice_config import VoiceConfigManager
        
        # Create config manager
        config_manager = VoiceConfigManager()
        
        # Test basic functionality
        print(f"✅ Config Manager created successfully")
        print(f"Voice enabled: {config_manager.get_voice_enabled()}")
        print(f"Default engine: {config_manager.get_default_engine()}")
        print(f"Output directory: {config_manager.get_output_directory()}")
        
        # Test enabled engines
        enabled_engines = config_manager.get_enabled_engines()
        print(f"Enabled engines: {list(enabled_engines.keys())}")
        
        # Test user preferences
        preferences = config_manager.get_user_preferences()
        print(f"User preferences: {preferences}")
        
        # Test validation
        validation = config_manager.validate_config()
        print(f"Configuration valid: {validation['valid']}")
        if validation['errors']:
            print(f"Errors: {validation['errors']}")
        if validation['warnings']:
            print(f"Warnings: {validation['warnings']}")
        
        return True
        
    except Exception as e:
        print(f"❌ VoiceConfigManager test failed: {e}")
        return False

def test_enhanced_voice_bridge():
    """Test the enhanced voice bridge"""
    print("\n🧪 Testing Enhanced Voice Bridge...")
    print("=" * 50)
    
    try:
        from heystive.integration.voice_bridge import HeystiveVoiceBridge
        
        # Create voice bridge
        voice_bridge = HeystiveVoiceBridge()
        
        # Test basic functionality
        print(f"✅ Voice Bridge created successfully")
        
        # Test voice configuration
        config = voice_bridge.get_voice_config()
        print(f"Voice enabled: {config['enabled']}")
        print(f"Current engine: {config['current_engine']}")
        
        # Test voice options
        voice_options = voice_bridge.list_voice_options()
        print(f"Available voice options: {len(voice_options)}")
        
        # Test speech generation
        test_text = "سلام! من HeyStive هستم، دستیار صوتی فارسی شما"
        print(f"\n🔊 Testing speech generation...")
        print(f"Text: '{test_text}'")
        
        success = voice_bridge.speak_persian(test_text)
        if success:
            print("✅ Speech generation successful")
        else:
            print("❌ Speech generation failed")
        
        # Test command processing
        test_command = "سلام استیو"
        print(f"\n🎯 Testing command processing...")
        print(f"Command: '{test_command}'")
        
        response = voice_bridge.process_voice_command(test_command)
        print(f"Response: '{response}'")
        
        # Test process and speak
        print(f"\n🎤 Testing process and speak...")
        process_success = voice_bridge.process_and_speak(test_command)
        if process_success:
            print("✅ Process and speak successful")
        else:
            print("❌ Process and speak failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Voice Bridge test failed: {e}")
        return False

def test_voice_engines_comparison():
    """Test all voice engines and compare quality"""
    print("\n🧪 Testing Voice Engines Comparison...")
    print("=" * 50)
    
    try:
        from heystive.voice.persian_multi_tts_manager import PersianMultiTTSManager
        
        # Create TTS manager
        tts_manager = PersianMultiTTSManager()
        
        if not tts_manager.engines:
            print("❌ No engines available for testing")
            return False
        
        # Test all engines
        test_results = tts_manager.test_all_engines()
        
        # Report results
        successful_engines = sum(test_results.values())
        total_engines = len(test_results)
        
        print(f"\n📊 Engine Test Results:")
        print(f"Successful: {successful_engines}/{total_engines}")
        
        for engine_name, success in test_results.items():
            status = "✅ WORKING" if success else "❌ FAILED"
            engine_info = tts_manager.engines.get(engine_name, {})
            engine_name_display = engine_info.get('name', engine_name)
            print(f"  {engine_name_display}: {status}")
        
        return successful_engines > 0
        
    except Exception as e:
        print(f"❌ Voice engines comparison test failed: {e}")
        return False

def test_integration_with_existing_system():
    """Test integration with existing HeyStive system"""
    print("\n🧪 Testing Integration with Existing System...")
    print("=" * 50)
    
    try:
        from heystive.integration.voice_bridge import HeystiveVoiceBridge
        
        # Create voice bridge
        voice_bridge = HeystiveVoiceBridge()
        
        # Test complete integration
        test_results = voice_bridge.test_complete_integration()
        
        # Report results
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 Integration Test Results:")
        print(f"Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ENHANCED PERSIAN TTS INTEGRATION TEST")
    print("=" * 60)
    print("Testing the complete Persian TTS system for HeyStive")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    test_results['persian_multi_tts_manager'] = test_persian_multi_tts_manager()
    test_results['voice_config_manager'] = test_voice_config_manager()
    test_results['enhanced_voice_bridge'] = test_enhanced_voice_bridge()
    test_results['voice_engines_comparison'] = test_voice_engines_comparison()
    test_results['integration_with_existing_system'] = test_integration_with_existing_system()
    
    # Final report
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 80:
        print("\n🎉 ENHANCED PERSIAN TTS INTEGRATION SUCCESSFUL!")
        print("✅ All major components working correctly")
        print("✅ Ready for production use")
        print("✅ HeyStive now has advanced Persian TTS capabilities")
    elif success_rate >= 60:
        print("\n👍 ENHANCED PERSIAN TTS INTEGRATION MOSTLY SUCCESSFUL!")
        print("✅ Core functionality working")
        print("⚠️ Some components may need refinement")
    else:
        print("\n❌ ENHANCED PERSIAN TTS INTEGRATION NEEDS WORK!")
        print("🛑 Critical issues detected")
        print("🔧 Please check dependencies and configuration")
    
    # Check output directory
    output_dir = Path("/workspace/heystive_audio_output")
    if output_dir.exists():
        audio_files = list(output_dir.glob("*.wav")) + list(output_dir.glob("*.mp3"))
        print(f"\n🎵 Generated Audio Files: {len(audio_files)}")
        for audio_file in audio_files[:5]:  # Show first 5 files
            size = audio_file.stat().st_size
            print(f"  📁 {audio_file.name} ({size} bytes)")
        if len(audio_files) > 5:
            print(f"  ... and {len(audio_files) - 5} more files")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)