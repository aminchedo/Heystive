#!/usr/bin/env python3
"""
HEYSTIVE VOICE SETTINGS USER INTERFACE
Interactive interface for managing Persian TTS settings and engine selection
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# Add workspace to path
sys.path.insert(0, '/workspace')

from heystive.voice.voice_config import VoiceConfigManager
from heystive.voice.persian_multi_tts_manager import PersianMultiTTSManager

logger = logging.getLogger(__name__)

class VoiceSettingsUI:
    """
    Interactive user interface for voice settings management
    Provides easy access to all voice configuration options
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = VoiceConfigManager(config_path)
        self.tts_manager = None
        self.running = False
        
        print("🎛️ Voice Settings UI Initialized")
    
    def start_ui(self):
        """Start the interactive voice settings interface"""
        print("\n🎛️ HEYSTIVE VOICE SETTINGS")
        print("=" * 50)
        
        self.running = True
        
        # Initialize TTS manager if voice is enabled
        if self.config_manager.get_voice_enabled():
            print("🔄 Initializing TTS manager...")
            try:
                self.tts_manager = PersianMultiTTSManager()
                print(f"✅ TTS manager ready with {len(self.tts_manager.engines)} engines")
            except Exception as e:
                print(f"⚠️ TTS manager initialization failed: {e}")
                self.tts_manager = None
        else:
            print("⚠️ Voice system is disabled")
        
        # Main UI loop
        while self.running:
            try:
                self._show_main_menu()
                choice = input("\nSelect option (1-9): ").strip()
                self._handle_menu_choice(choice)
                
            except KeyboardInterrupt:
                print("\n👋 Exiting Voice Settings...")
                break
            except Exception as e:
                logger.error(f"UI error: {e}")
                print(f"❌ Error: {e}")
        
        print("🏁 Voice Settings UI closed")
    
    def _show_main_menu(self):
        """Display the main menu options"""
        print("\n" + "=" * 50)
        print("🎤 VOICE SETTINGS MENU")
        print("=" * 50)
        
        # Show current status
        voice_enabled = self.config_manager.get_voice_enabled()
        default_engine = self.config_manager.get_default_engine()
        
        print(f"Status: {'🟢 ENABLED' if voice_enabled else '🔴 DISABLED'}")
        print(f"Default Engine: {default_engine}")
        
        if self.tts_manager and self.tts_manager.current_engine:
            current_info = self.tts_manager.get_current_engine_info()
            print(f"Current Engine: {current_info['name']} ({current_info['quality']})")
        
        print("\nOptions:")
        print("1. 🔊 Enable/Disable Voice System")
        print("2. 🎤 Manage TTS Engines")
        print("3. ⚙️ Audio Settings")
        print("4. 👤 User Preferences")
        print("5. 🧪 Test Voice System")
        print("6. 📁 Import/Export Settings")
        print("7. 🔄 Reset to Defaults")
        print("8. ℹ️ System Information")
        print("9. 🚪 Exit")
    
    def _handle_menu_choice(self, choice: str):
        """Handle user menu selection"""
        
        if choice == '1':
            self._toggle_voice_system()
        elif choice == '2':
            self._manage_tts_engines()
        elif choice == '3':
            self._configure_audio_settings()
        elif choice == '4':
            self._configure_user_preferences()
        elif choice == '5':
            self._test_voice_system()
        elif choice == '6':
            self._import_export_settings()
        elif choice == '7':
            self._reset_to_defaults()
        elif choice == '8':
            self._show_system_information()
        elif choice == '9':
            self.running = False
        else:
            print("❌ Invalid option. Please select 1-9.")
    
    def _toggle_voice_system(self):
        """Enable or disable the voice system"""
        print("\n🔊 VOICE SYSTEM TOGGLE")
        print("-" * 30)
        
        current_status = self.config_manager.get_voice_enabled()
        print(f"Current status: {'ENABLED' if current_status else 'DISABLED'}")
        
        new_status = not current_status
        action = "enable" if new_status else "disable"
        
        confirm = input(f"Do you want to {action} the voice system? (y/N): ").lower().startswith('y')
        
        if confirm:
            success = self.config_manager.set_voice_enabled(new_status)
            if success:
                print(f"✅ Voice system {'enabled' if new_status else 'disabled'}")
                
                if new_status and not self.tts_manager:
                    print("🔄 Initializing TTS manager...")
                    try:
                        self.tts_manager = PersianMultiTTSManager()
                        print(f"✅ TTS manager initialized with {len(self.tts_manager.engines)} engines")
                    except Exception as e:
                        print(f"❌ TTS manager initialization failed: {e}")
                elif not new_status:
                    self.tts_manager = None
                    print("🔄 TTS manager deactivated")
            else:
                print("❌ Failed to update voice system status")
        else:
            print("⚠️ Operation cancelled")
    
    def _manage_tts_engines(self):
        """Manage TTS engines"""
        if not self.config_manager.get_voice_enabled():
            print("❌ Voice system is disabled. Enable it first.")
            return
        
        if not self.tts_manager:
            print("❌ TTS manager not available")
            return
        
        print("\n🎤 TTS ENGINE MANAGEMENT")
        print("-" * 40)
        
        while True:
            # List available engines
            engines = self.tts_manager.engines
            print(f"\nAvailable Engines ({len(engines)}):")
            
            for i, (key, engine_info) in enumerate(engines.items(), 1):
                current = "✅" if key == self.tts_manager.current_engine else "  "
                print(f"{current} {i}. {engine_info['name']}")
                print(f"      Quality: {engine_info['quality']}, Voice: {engine_info['voice_type']}")
            
            print("\nOptions:")
            print("1. Switch to different engine")
            print("2. Test current engine")
            print("3. Test all engines")
            print("4. Set default engine")
            print("5. Back to main menu")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                self._switch_tts_engine()
            elif choice == '2':
                self._test_current_engine()
            elif choice == '3':
                self._test_all_engines()
            elif choice == '4':
                self._set_default_engine()
            elif choice == '5':
                break
            else:
                print("❌ Invalid option")
    
    def _switch_tts_engine(self):
        """Switch to a different TTS engine"""
        engines = list(self.tts_manager.engines.keys())
        
        print("\nSelect engine:")
        for i, engine_key in enumerate(engines, 1):
            engine_info = self.tts_manager.engines[engine_key]
            current = "✅" if engine_key == self.tts_manager.current_engine else "  "
            print(f"{current} {i}. {engine_info['name']}")
        
        try:
            choice = int(input("\nEnter engine number: ")) - 1
            if 0 <= choice < len(engines):
                selected_engine = engines[choice]
                success = self.tts_manager.switch_engine(selected_engine)
                
                if success:
                    print(f"✅ Switched to: {self.tts_manager.engines[selected_engine]['name']}")
                    
                    # Test the new engine
                    test_text = "تست موتور جدید TTS"
                    print(f"🔊 Testing with: '{test_text}'")
                    test_success = self.tts_manager.speak_persian(test_text)
                    
                    if test_success:
                        print("   ✅ Engine test successful")
                    else:
                        print("   ⚠️ Engine test failed")
                else:
                    print("❌ Failed to switch engine")
            else:
                print("❌ Invalid engine number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _test_current_engine(self):
        """Test the current TTS engine"""
        if not self.tts_manager.current_engine:
            print("❌ No engine selected")
            return
        
        current_info = self.tts_manager.get_current_engine_info()
        print(f"\n🧪 Testing: {current_info['name']}")
        
        test_texts = [
            "سلام! این یک تست است",
            "من می‌توانم به فارسی صحبت کنم",
            "کیفیت صدای من چطور است؟"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n{i}. Testing: '{text}'")
            success = self.tts_manager.speak_persian(text)
            print(f"   {'✅ Success' if success else '❌ Failed'}")
    
    def _test_all_engines(self):
        """Test all available TTS engines"""
        print("\n🧪 TESTING ALL ENGINES")
        print("-" * 30)
        
        results = self.tts_manager.test_all_engines()
        
        print(f"\n📊 Test Results:")
        successful = sum(results.values())
        total = len(results)
        
        print(f"Working engines: {successful}/{total}")
        print(f"Success rate: {(successful/total)*100:.1f}%")
        
        for engine_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            engine_info = self.tts_manager.engines[engine_name]
            print(f"  {engine_info['name']}: {status}")
    
    def _set_default_engine(self):
        """Set the default TTS engine"""
        engines = list(self.tts_manager.engines.keys())
        
        print("\nSelect default engine:")
        for i, engine_key in enumerate(engines, 1):
            engine_info = self.tts_manager.engines[engine_key]
            current_default = self.config_manager.get_default_engine()
            default_mark = "⭐" if engine_key == current_default else "  "
            print(f"{default_mark} {i}. {engine_info['name']}")
        
        try:
            choice = int(input("\nEnter engine number: ")) - 1
            if 0 <= choice < len(engines):
                selected_engine = engines[choice]
                success = self.config_manager.set_default_engine(selected_engine)
                
                if success:
                    engine_name = self.tts_manager.engines[selected_engine]['name']
                    print(f"✅ Default engine set to: {engine_name}")
                else:
                    print("❌ Failed to set default engine")
            else:
                print("❌ Invalid engine number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _configure_audio_settings(self):
        """Configure audio settings"""
        print("\n⚙️ AUDIO SETTINGS")
        print("-" * 30)
        
        current_settings = self.config_manager.get_audio_settings()
        
        print("Current settings:")
        print(f"  Sample Rate: {current_settings.get('sample_rate', 22050)}")
        print(f"  Volume: {current_settings.get('volume', 0.8)}")
        print(f"  Speed: {current_settings.get('speed', 1.0)}")
        print(f"  Output Format: {current_settings.get('output_format', 'wav')}")
        
        print("\nOptions:")
        print("1. Change volume (0.0 - 1.0)")
        print("2. Change speed (0.5 - 2.0)")
        print("3. Change sample rate")
        print("4. Back to main menu")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            try:
                volume = float(input("Enter volume (0.0 - 1.0): "))
                if 0.0 <= volume <= 1.0:
                    success = self.config_manager.set_audio_setting('volume', volume)
                    print(f"{'✅ Volume set to' if success else '❌ Failed to set volume:'} {volume}")
                else:
                    print("❌ Volume must be between 0.0 and 1.0")
            except ValueError:
                print("❌ Please enter a valid number")
        
        elif choice == '2':
            try:
                speed = float(input("Enter speed (0.5 - 2.0): "))
                if 0.5 <= speed <= 2.0:
                    success = self.config_manager.set_audio_setting('speed', speed)
                    print(f"{'✅ Speed set to' if success else '❌ Failed to set speed:'} {speed}")
                else:
                    print("❌ Speed must be between 0.5 and 2.0")
            except ValueError:
                print("❌ Please enter a valid number")
        
        elif choice == '3':
            print("Common sample rates: 16000, 22050, 44100, 48000")
            try:
                rate = int(input("Enter sample rate: "))
                if rate > 0:
                    success = self.config_manager.set_audio_setting('sample_rate', rate)
                    print(f"{'✅ Sample rate set to' if success else '❌ Failed to set sample rate:'} {rate}")
                else:
                    print("❌ Sample rate must be positive")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _configure_user_preferences(self):
        """Configure user preferences"""
        print("\n👤 USER PREFERENCES")
        print("-" * 30)
        
        current_prefs = self.config_manager.get_user_preferences()
        
        print("Current preferences:")
        print(f"  Auto Play: {current_prefs.get('auto_play', True)}")
        print(f"  Save Audio Files: {current_prefs.get('save_audio_files', True)}")
        print(f"  Preferred Voice: {current_prefs.get('preferred_voice', 'kamtera_female')}")
        
        print("\nOptions:")
        print("1. Toggle auto play")
        print("2. Toggle save audio files")
        print("3. Set preferred voice")
        print("4. Back to main menu")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            current = current_prefs.get('auto_play', True)
            new_value = not current
            success = self.config_manager.set_user_preference('auto_play', new_value)
            print(f"{'✅ Auto play' if success else '❌ Failed to set auto play:'} {'enabled' if new_value else 'disabled'}")
        
        elif choice == '2':
            current = current_prefs.get('save_audio_files', True)
            new_value = not current
            success = self.config_manager.set_user_preference('save_audio_files', new_value)
            print(f"{'✅ Save audio files' if success else '❌ Failed to set save audio files:'} {'enabled' if new_value else 'disabled'}")
        
        elif choice == '3':
            if self.tts_manager:
                engines = list(self.tts_manager.engines.keys())
                print("\nSelect preferred voice:")
                for i, engine_key in enumerate(engines, 1):
                    engine_info = self.tts_manager.engines[engine_key]
                    print(f"{i}. {engine_info['name']}")
                
                try:
                    choice = int(input("\nEnter voice number: ")) - 1
                    if 0 <= choice < len(engines):
                        selected_engine = engines[choice]
                        success = self.config_manager.set_user_preference('preferred_voice', selected_engine)
                        if success:
                            engine_name = self.tts_manager.engines[selected_engine]['name']
                            print(f"✅ Preferred voice set to: {engine_name}")
                        else:
                            print("❌ Failed to set preferred voice")
                    else:
                        print("❌ Invalid voice number")
                except ValueError:
                    print("❌ Please enter a valid number")
            else:
                print("❌ TTS manager not available")
    
    def _test_voice_system(self):
        """Test the voice system comprehensively"""
        print("\n🧪 VOICE SYSTEM TEST")
        print("-" * 30)
        
        if not self.config_manager.get_voice_enabled():
            print("❌ Voice system is disabled")
            return
        
        if not self.tts_manager:
            print("❌ TTS manager not available")
            return
        
        print("Running comprehensive voice system test...")
        
        # Test configuration
        config_validation = self.config_manager.validate_config()
        print(f"Configuration: {'✅ VALID' if config_validation['valid'] else '❌ INVALID'}")
        
        if config_validation['errors']:
            for error in config_validation['errors']:
                print(f"  ❌ {error}")
        
        if config_validation['warnings']:
            for warning in config_validation['warnings']:
                print(f"  ⚠️ {warning}")
        
        # Test TTS engines
        print("\nTesting TTS engines...")
        engine_results = self.tts_manager.test_all_engines()
        
        successful_engines = sum(engine_results.values())
        total_engines = len(engine_results)
        
        print(f"Working engines: {successful_engines}/{total_engines}")
        
        # Test current engine
        if self.tts_manager.current_engine:
            current_info = self.tts_manager.get_current_engine_info()
            print(f"\nCurrent engine: {current_info['name']}")
            
            test_text = "این یک تست سیستم صوتی HeyStive است"
            print(f"Testing with: '{test_text}'")
            
            success = self.tts_manager.speak_persian(test_text)
            print(f"Current engine test: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        print(f"\n📊 Overall system health: {(successful_engines/total_engines)*100:.1f}%")
    
    def _import_export_settings(self):
        """Import or export voice settings"""
        print("\n📁 IMPORT/EXPORT SETTINGS")
        print("-" * 30)
        
        print("Options:")
        print("1. Export current settings")
        print("2. Import settings from file")
        print("3. Back to main menu")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            filename = input("Enter export filename (or press Enter for default): ").strip()
            if not filename:
                filename = f"heystive_voice_settings_{int(datetime.now().timestamp())}.yaml"
            
            success = self.config_manager.export_config(filename)
            print(f"{'✅ Settings exported to' if success else '❌ Failed to export to:'} {filename}")
        
        elif choice == '2':
            filename = input("Enter import filename: ").strip()
            if filename and os.path.exists(filename):
                success = self.config_manager.import_config(filename)
                print(f"{'✅ Settings imported from' if success else '❌ Failed to import from:'} {filename}")
                
                if success:
                    print("🔄 Reinitializing TTS manager...")
                    try:
                        self.tts_manager = PersianMultiTTSManager()
                        print("✅ TTS manager reinitialized")
                    except Exception as e:
                        print(f"❌ TTS manager reinitialization failed: {e}")
            else:
                print("❌ File not found")
    
    def _reset_to_defaults(self):
        """Reset settings to defaults"""
        print("\n🔄 RESET TO DEFAULTS")
        print("-" * 30)
        
        print("⚠️ This will reset all voice settings to defaults!")
        confirm = input("Are you sure? Type 'RESET' to confirm: ")
        
        if confirm == 'RESET':
            success = self.config_manager.reset_to_defaults()
            
            if success:
                print("✅ Settings reset to defaults")
                print("🔄 Reinitializing TTS manager...")
                
                try:
                    self.tts_manager = PersianMultiTTSManager()
                    print("✅ TTS manager reinitialized")
                except Exception as e:
                    print(f"❌ TTS manager reinitialization failed: {e}")
            else:
                print("❌ Failed to reset settings")
        else:
            print("⚠️ Reset cancelled")
    
    def _show_system_information(self):
        """Show detailed system information"""
        print("\nℹ️ SYSTEM INFORMATION")
        print("-" * 30)
        
        # Configuration info
        print("Configuration:")
        print(f"  Voice Enabled: {self.config_manager.get_voice_enabled()}")
        print(f"  Default Engine: {self.config_manager.get_default_engine()}")
        print(f"  Config File: {self.config_manager.config_path}")
        
        # TTS Manager info
        if self.tts_manager:
            print(f"\nTTS Manager:")
            print(f"  Available Engines: {len(self.tts_manager.engines)}")
            print(f"  Current Engine: {self.tts_manager.current_engine}")
            print(f"  Output Directory: {self.tts_manager.output_dir}")
            
            # Engine details
            print(f"\nEngine Details:")
            for engine_key, engine_info in self.tts_manager.engines.items():
                print(f"  {engine_info['name']}:")
                print(f"    Quality: {engine_info['quality']}")
                print(f"    Voice Type: {engine_info['voice_type']}")
                print(f"    Accent: {engine_info['accent']}")
                print(f"    Offline: {engine_info['offline']}")
        else:
            print("\nTTS Manager: Not available")
        
        # Audio settings
        audio_settings = self.config_manager.get_audio_settings()
        print(f"\nAudio Settings:")
        for key, value in audio_settings.items():
            print(f"  {key}: {value}")
        
        # User preferences
        user_prefs = self.config_manager.get_user_preferences()
        print(f"\nUser Preferences:")
        for key, value in user_prefs.items():
            print(f"  {key}: {value}")

def main():
    """Main entry point for voice settings UI"""
    try:
        ui = VoiceSettingsUI()
        ui.start_ui()
    except KeyboardInterrupt:
        print("\n👋 Voice Settings UI interrupted")
    except Exception as e:
        logger.error(f"Voice Settings UI error: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()