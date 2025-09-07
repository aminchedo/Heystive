#!/usr/bin/env python3
"""
COMPREHENSIVE HEYSTIVE PERSIAN TTS INTEGRATION TEST
Tests all components of the enhanced Persian voice system
Validates production readiness and functionality
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Add workspace to path
sys.path.insert(0, '/workspace')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 TESTING MODULE IMPORTS")
    print("=" * 50)
    
    test_results = {}
    
    # Core modules
    modules_to_test = [
        ('heystive.voice.persian_multi_tts_manager', 'PersianMultiTTSManager'),
        ('heystive.voice.voice_config', 'VoiceConfigManager'),
        ('heystive.integration.voice_bridge', 'HeystiveVoiceBridge'),
        ('heystive.ui.voice_settings_ui', 'VoiceSettingsUI'),
        ('heystive_main_app', 'HeyStiveApp'),
    ]
    
    for module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            test_results[f"{module_path}.{class_name}"] = True
            print(f"✅ {module_path}.{class_name}")
        except Exception as e:
            test_results[f"{module_path}.{class_name}"] = False
            print(f"❌ {module_path}.{class_name}: {e}")
    
    # External dependencies
    external_deps = [
        'gtts',
        'pyttsx3',
        'sounddevice',
        'soundfile',
        'pygame',
        'yaml',
        'numpy',
        'scipy',
        'speech_recognition'
    ]
    
    print(f"\n📦 External Dependencies:")
    for dep in external_deps:
        try:
            __import__(dep)
            test_results[f"external.{dep}"] = True
            print(f"✅ {dep}")
        except ImportError as e:
            test_results[f"external.{dep}"] = False
            print(f"❌ {dep}: {e}")
    
    passed = sum(test_results.values())
    total = len(test_results)
    print(f"\n📊 Import Test Results: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return test_results

def test_tts_manager():
    """Test the Persian Multi-TTS Manager"""
    print("\n🎤 TESTING PERSIAN MULTI-TTS MANAGER")
    print("=" * 50)
    
    test_results = {}
    
    try:
        from heystive.voice.persian_multi_tts_manager import PersianMultiTTSManager
        
        # Initialize TTS manager
        print("🔄 Initializing TTS Manager...")
        tts_manager = PersianMultiTTSManager()
        
        # Test 1: Engine availability
        available_engines = len(tts_manager.engines)
        test_results['engines_available'] = available_engines >= 3  # At least 3 engines
        print(f"Available engines: {available_engines} ({'✅' if test_results['engines_available'] else '❌'})")
        
        # Test 2: Current engine selection
        has_current_engine = tts_manager.current_engine is not None
        test_results['current_engine_selected'] = has_current_engine
        print(f"Current engine selected: {'✅' if has_current_engine else '❌'}")
        
        if has_current_engine:
            current_info = tts_manager.get_current_engine_info()
            print(f"  Current: {current_info['name']} ({current_info['quality']})")
        
        # Test 3: Engine listing
        engines_info = tts_manager.list_engines()
        test_results['engine_listing'] = len(engines_info) > 0
        print(f"Engine listing: {'✅' if test_results['engine_listing'] else '❌'}")
        
        # Test 4: Engine switching
        if len(tts_manager.engines) > 1:
            engine_keys = list(tts_manager.engines.keys())
            original_engine = tts_manager.current_engine
            test_engine = engine_keys[1] if engine_keys[0] == original_engine else engine_keys[0]
            
            switch_success = tts_manager.switch_engine(test_engine)
            test_results['engine_switching'] = switch_success
            print(f"Engine switching: {'✅' if switch_success else '❌'}")
            
            # Switch back
            tts_manager.switch_engine(original_engine)
        else:
            test_results['engine_switching'] = False
            print("Engine switching: ❌ (insufficient engines)")
        
        # Test 5: Audio generation
        print("🔊 Testing audio generation...")
        test_text = "تست سیستم صوتی HeyStive"
        
        # Test each engine
        engine_test_results = {}
        for engine_name in tts_manager.engines.keys():
            print(f"  Testing {engine_name}...")
            success = tts_manager.speak_persian(test_text, engine_name)
            engine_test_results[engine_name] = success
            print(f"    {'✅' if success else '❌'}")
        
        working_engines = sum(engine_test_results.values())
        test_results['audio_generation'] = working_engines > 0
        print(f"Audio generation: {'✅' if test_results['audio_generation'] else '❌'} ({working_engines}/{len(engine_test_results)} engines working)")
        
        # Test 6: Text normalization
        test_texts = [
            "سلام ۱۲۳ دنیا",  # Persian digits
            "صبح بخیر!",      # Simple text
            "ضصثظطق",         # Difficult Persian chars
        ]
        
        normalization_success = 0
        for text in test_texts:
            try:
                normalized = tts_manager._normalize_persian_text(text)
                if normalized != text:  # Should be different after normalization
                    normalization_success += 1
            except Exception as e:
                print(f"    Normalization error for '{text}': {e}")
        
        test_results['text_normalization'] = normalization_success > 0
        print(f"Text normalization: {'✅' if test_results['text_normalization'] else '❌'}")
        
    except Exception as e:
        print(f"❌ TTS Manager test failed: {e}")
        test_results = {
            'engines_available': False,
            'current_engine_selected': False,
            'engine_listing': False,
            'engine_switching': False,
            'audio_generation': False,
            'text_normalization': False
        }
    
    passed = sum(test_results.values())
    total = len(test_results)
    print(f"\n📊 TTS Manager Test Results: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return test_results

def test_voice_bridge():
    """Test the Voice Bridge integration"""
    print("\n🌉 TESTING VOICE BRIDGE INTEGRATION")
    print("=" * 50)
    
    test_results = {}
    
    try:
        from heystive.integration.voice_bridge import HeystiveVoiceBridge
        
        # Initialize voice bridge
        print("🔄 Initializing Voice Bridge...")
        bridge = HeystiveVoiceBridge()
        
        # Test 1: Initialization
        test_results['bridge_initialization'] = bridge.tts_manager is not None
        print(f"Bridge initialization: {'✅' if test_results['bridge_initialization'] else '❌'}")
        
        # Test 2: Voice configuration
        voice_config = bridge.get_voice_config()
        test_results['voice_config'] = voice_config.get('enabled', False)
        print(f"Voice configuration: {'✅' if test_results['voice_config'] else '❌'}")
        
        # Test 3: Engine listing
        engines = bridge.list_voice_options()
        test_results['engine_listing'] = len(engines) > 0
        print(f"Engine listing: {'✅' if test_results['engine_listing'] else '❌'} ({len(engines)} engines)")
        
        # Test 4: Command processing
        test_commands = [
            "سلام استیو",
            "ساعت چنده؟",
            "کمک",
            "تست"
        ]
        
        command_successes = 0
        for command in test_commands:
            try:
                response = bridge.process_voice_command(command)
                if response and len(response) > 0:
                    command_successes += 1
                    print(f"    '{command}' → '{response[:50]}...' ✅")
                else:
                    print(f"    '{command}' → No response ❌")
            except Exception as e:
                print(f"    '{command}' → Error: {e} ❌")
        
        test_results['command_processing'] = command_successes == len(test_commands)
        print(f"Command processing: {'✅' if test_results['command_processing'] else '❌'} ({command_successes}/{len(test_commands)})")
        
        # Test 5: Voice response generation
        try:
            test_response = "این یک تست پاسخ صوتی است"
            voice_success = bridge.speak_persian(test_response)
            test_results['voice_response'] = voice_success
            print(f"Voice response: {'✅' if voice_success else '❌'}")
        except Exception as e:
            test_results['voice_response'] = False
            print(f"Voice response: ❌ ({e})")
        
        # Test 6: Engine switching
        if len(engines) > 1:
            engine_keys = list(engines.keys())
            test_engine = engine_keys[1] if len(engine_keys) > 1 else engine_keys[0]
            
            switch_success = bridge.change_voice_engine(test_engine)
            test_results['engine_switching'] = switch_success
            print(f"Engine switching: {'✅' if switch_success else '❌'}")
        else:
            test_results['engine_switching'] = False
            print("Engine switching: ❌ (insufficient engines)")
        
        # Test 7: Existing system integration
        existing_components = len(bridge.existing_heystive)
        test_results['existing_integration'] = existing_components > 0
        print(f"Existing integration: {'✅' if test_results['existing_integration'] else '❌'} ({existing_components} components)")
        
    except Exception as e:
        print(f"❌ Voice Bridge test failed: {e}")
        test_results = {
            'bridge_initialization': False,
            'voice_config': False,
            'engine_listing': False,
            'command_processing': False,
            'voice_response': False,
            'engine_switching': False,
            'existing_integration': False
        }
    
    passed = sum(test_results.values())
    total = len(test_results)
    print(f"\n📊 Voice Bridge Test Results: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return test_results

def test_main_application():
    """Test the main HeyStive application"""
    print("\n🚀 TESTING MAIN APPLICATION")
    print("=" * 50)
    
    test_results = {}
    
    try:
        from heystive_main_app import HeyStiveApp
        
        # Test 1: Application initialization
        print("🔄 Initializing Main Application...")
        app = HeyStiveApp()
        
        test_results['app_initialization'] = app.voice_bridge is not None
        print(f"App initialization: {'✅' if test_results['app_initialization'] else '❌'}")
        
        # Test 2: Configuration management
        config_valid = app.config_manager.validate_config()
        test_results['config_validation'] = config_valid['valid']
        print(f"Configuration validation: {'✅' if test_results['config_validation'] else '❌'}")
        
        if config_valid['errors']:
            for error in config_valid['errors']:
                print(f"    ❌ {error}")
        
        # Test 3: Voice system status
        if app.voice_bridge:
            voice_config = app.voice_bridge.get_voice_config()
            test_results['voice_system'] = voice_config.get('enabled', False)
            print(f"Voice system: {'✅' if test_results['voice_system'] else '❌'}")
            
            current_engine = voice_config.get('current_engine')
            if current_engine:
                print(f"    Current engine: {current_engine['name']}")
        else:
            test_results['voice_system'] = False
            print("Voice system: ❌")
        
        # Test 4: Conversation history
        test_results['conversation_history'] = hasattr(app, 'conversation_history')
        print(f"Conversation history: {'✅' if test_results['conversation_history'] else '❌'}")
        
        # Test 5: Signal handling
        test_results['signal_handling'] = hasattr(app, '_signal_handler')
        print(f"Signal handling: {'✅' if test_results['signal_handling'] else '❌'}")
        
    except Exception as e:
        print(f"❌ Main Application test failed: {e}")
        test_results = {
            'app_initialization': False,
            'config_validation': False,
            'voice_system': False,
            'conversation_history': False,
            'signal_handling': False
        }
    
    passed = sum(test_results.values())
    total = len(test_results)
    print(f"\n📊 Main Application Test Results: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return test_results

def test_voice_settings_ui():
    """Test the Voice Settings UI"""
    print("\n🎛️ TESTING VOICE SETTINGS UI")
    print("=" * 50)
    
    test_results = {}
    
    try:
        from heystive.ui.voice_settings_ui import VoiceSettingsUI
        
        # Test 1: UI initialization
        print("🔄 Initializing Voice Settings UI...")
        ui = VoiceSettingsUI()
        
        test_results['ui_initialization'] = ui.config_manager is not None
        print(f"UI initialization: {'✅' if test_results['ui_initialization'] else '❌'}")
        
        # Test 2: Configuration access
        voice_enabled = ui.config_manager.get_voice_enabled()
        test_results['config_access'] = isinstance(voice_enabled, bool)
        print(f"Configuration access: {'✅' if test_results['config_access'] else '❌'}")
        
        # Test 3: Menu methods
        menu_methods = [
            '_show_main_menu',
            '_handle_menu_choice',
            '_toggle_voice_system',
            '_manage_tts_engines',
            '_test_voice_system'
        ]
        
        method_success = 0
        for method_name in menu_methods:
            if hasattr(ui, method_name):
                method_success += 1
        
        test_results['ui_methods'] = method_success == len(menu_methods)
        print(f"UI methods: {'✅' if test_results['ui_methods'] else '❌'} ({method_success}/{len(menu_methods)})")
        
    except Exception as e:
        print(f"❌ Voice Settings UI test failed: {e}")
        test_results = {
            'ui_initialization': False,
            'config_access': False,
            'ui_methods': False
        }
    
    passed = sum(test_results.values())
    total = len(test_results)
    print(f"\n📊 Voice Settings UI Test Results: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return test_results

def test_file_system():
    """Test file system components"""
    print("\n📁 TESTING FILE SYSTEM")
    print("=" * 50)
    
    test_results = {}
    
    # Test 1: Configuration file
    config_file = Path("/workspace/heystive/config/voice_settings.yaml")
    test_results['config_file'] = config_file.exists()
    print(f"Configuration file: {'✅' if test_results['config_file'] else '❌'} ({config_file})")
    
    # Test 2: Output directory
    output_dir = Path("/workspace/heystive_audio_output")
    test_results['output_directory'] = output_dir.exists()
    print(f"Output directory: {'✅' if test_results['output_directory'] else '❌'} ({output_dir})")
    
    # Test 3: Audio files
    if output_dir.exists():
        audio_files = list(output_dir.glob("*.wav")) + list(output_dir.glob("*.mp3"))
        test_results['audio_files'] = len(audio_files) > 0
        print(f"Audio files: {'✅' if test_results['audio_files'] else '❌'} ({len(audio_files)} files)")
    else:
        test_results['audio_files'] = False
        print("Audio files: ❌ (directory not found)")
    
    # Test 4: Module structure
    required_modules = [
        "/workspace/heystive/voice/persian_multi_tts_manager.py",
        "/workspace/heystive/voice/voice_config.py",
        "/workspace/heystive/integration/voice_bridge.py",
        "/workspace/heystive/ui/voice_settings_ui.py",
        "/workspace/heystive_main_app.py"
    ]
    
    module_success = 0
    for module_path in required_modules:
        if Path(module_path).exists():
            module_success += 1
        else:
            print(f"    ❌ Missing: {module_path}")
    
    test_results['module_structure'] = module_success == len(required_modules)
    print(f"Module structure: {'✅' if test_results['module_structure'] else '❌'} ({module_success}/{len(required_modules)})")
    
    passed = sum(test_results.values())
    total = len(test_results)
    print(f"\n📊 File System Test Results: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return test_results

def generate_comprehensive_report(all_results: Dict[str, Dict[str, bool]]):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    
    total_tests = 0
    total_passed = 0
    
    for test_category, results in all_results.items():
        passed = sum(results.values())
        total = len(results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        total_tests += total
        total_passed += passed
        
        status = "✅ PASS" if percentage >= 80 else "⚠️ PARTIAL" if percentage >= 60 else "❌ FAIL"
        print(f"{test_category:25} {passed:2}/{total:2} ({percentage:5.1f}%) {status}")
    
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print("-" * 80)
    print(f"{'OVERALL RESULTS':25} {total_passed:2}/{total_tests:2} ({overall_percentage:5.1f}%)")
    
    if overall_percentage >= 90:
        print("\n🎉 EXCELLENT! System is production ready")
        status = "PRODUCTION_READY"
    elif overall_percentage >= 80:
        print("\n👍 GOOD! System is mostly functional with minor issues")
        status = "MOSTLY_FUNCTIONAL"
    elif overall_percentage >= 60:
        print("\n⚠️ PARTIAL! System has significant issues that need attention")
        status = "NEEDS_ATTENTION"
    else:
        print("\n❌ CRITICAL! System has major issues and is not ready for use")
        status = "CRITICAL_ISSUES"
    
    print(f"\n📊 FINAL ASSESSMENT: {status}")
    print(f"🔊 Persian TTS Integration: {'SUCCESSFUL' if overall_percentage >= 80 else 'NEEDS WORK'}")
    print(f"🎤 Voice System: {'READY FOR PRODUCTION' if overall_percentage >= 80 else 'REQUIRES FIXES'}")
    print(f"🚀 HeyStive Enhancement: {'COMPLETE' if overall_percentage >= 80 else 'INCOMPLETE'}")
    
    # Detailed recommendations
    print(f"\n📋 RECOMMENDATIONS:")
    
    if overall_percentage >= 90:
        print("✅ System is ready for production deployment")
        print("✅ All major components are functional")
        print("✅ Voice capabilities successfully integrated")
    elif overall_percentage >= 80:
        print("⚠️ Review and fix any failing tests")
        print("✅ Core functionality is working")
        print("✅ Voice system is operational")
    else:
        print("❌ Address critical issues before deployment")
        print("❌ Review system architecture")
        print("❌ Fix major component failures")
    
    return {
        'overall_percentage': overall_percentage,
        'status': status,
        'total_passed': total_passed,
        'total_tests': total_tests,
        'ready_for_production': overall_percentage >= 80
    }

def main():
    """Run comprehensive integration tests"""
    print("🚀 HEYSTIVE PERSIAN TTS COMPREHENSIVE INTEGRATION TEST")
    print("=" * 80)
    print("Testing all components of the enhanced Persian voice system")
    print("Validating production readiness and functionality")
    print()
    
    start_time = time.time()
    
    # Run all tests
    all_results = {}
    
    try:
        all_results['Import Tests'] = test_imports()
        all_results['TTS Manager'] = test_tts_manager()
        all_results['Voice Bridge'] = test_voice_bridge()
        all_results['Main Application'] = test_main_application()
        all_results['Voice Settings UI'] = test_voice_settings_ui()
        all_results['File System'] = test_file_system()
        
    except Exception as e:
        logger.error(f"Test execution error: {e}")
        print(f"❌ Test execution failed: {e}")
    
    # Generate comprehensive report
    final_report = generate_comprehensive_report(all_results)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n⏱️ Test Duration: {duration:.2f} seconds")
    print(f"📅 Test Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🏁 COMPREHENSIVE INTEGRATION TEST COMPLETE")
    print("=" * 80)
    
    return final_report

if __name__ == "__main__":
    main()