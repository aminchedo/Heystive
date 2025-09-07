#!/usr/bin/env python3
"""
HEYSTIVE VOICE SETTINGS UI
Interactive interface for managing multiple TTS engines
"""

import sys
import os
sys.path.insert(0, '/workspace')

from heystive.voice.multi_tts_manager import MultiTTSManager

class VoiceSettings:
    """Interactive voice engine selection and testing interface"""
    
    def __init__(self, tts_manager=None):
        self.tts_manager = tts_manager or MultiTTSManager()
        
    def show_voice_menu(self):
        """Interactive voice engine selection menu"""
        
        while True:
            print("\n🎛️ HEYSTIVE VOICE SETTINGS")
            print("=" * 40)
            
            current_engine = self.tts_manager.current_engine
            if current_engine:
                current_info = self.tts_manager.available_engines[current_engine]
                print(f"🎯 Current Engine: {current_info['name']}")
            else:
                print("❌ No engine selected")
            
            print("\nOptions:")
            print("1. List all engines")
            print("2. Switch engine") 
            print("3. Test current engine")
            print("4. Test all engines")
            print("5. Engine comparison")
            print("6. Back to main")
            
            try:
                choice = input("\nSelect option (1-6): ").strip()
                
                if choice == "1":
                    self._list_engines()
                elif choice == "2":
                    self._switch_engine_interactive()
                elif choice == "3":
                    self._test_current_engine()
                elif choice == "4":
                    self._test_all_engines()
                elif choice == "5":
                    self._engine_comparison()
                elif choice == "6":
                    print("👋 Returning to main menu...")
                    break
                else:
                    print("❌ Invalid option. Please select 1-6.")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting voice settings...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _list_engines(self):
        """List all available engines with details"""
        print("\n🎤 AVAILABLE TTS ENGINES:")
        print("=" * 50)
        
        if not self.tts_manager.available_engines:
            print("❌ No TTS engines available")
            return
            
        for i, (key, engine_info) in enumerate(self.tts_manager.available_engines.items(), 1):
            current = "✅ CURRENT" if key == self.tts_manager.current_engine else ""
            print(f"\n{i}. {engine_info['name']} {current}")
            print(f"   Quality: {engine_info['quality']}")
            print(f"   Speed: {engine_info['speed']}")
            print(f"   Offline: {'Yes' if engine_info['offline'] else 'No'}")
            print(f"   Status: {engine_info['status']}")
        
        input("\nPress Enter to continue...")
    
    def _switch_engine_interactive(self):
        """Interactive engine switching"""
        engines = list(self.tts_manager.available_engines.keys())
        
        if not engines:
            print("❌ No engines available to switch to")
            return
            
        print("\n🔄 SWITCH TTS ENGINE:")
        print("=" * 30)
        
        for i, engine in enumerate(engines, 1):
            engine_info = self.tts_manager.available_engines[engine]
            current = " (CURRENT)" if engine == self.tts_manager.current_engine else ""
            print(f"{i}. {engine_info['name']}{current}")
        
        try:
            choice = input(f"\nSelect engine (1-{len(engines)}): ").strip()
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(engines):
                    selected_engine = engines[choice_idx]
                    success = self.tts_manager.switch_engine(selected_engine)
                    if success:
                        print(f"✅ Switched to: {self.tts_manager.available_engines[selected_engine]['name']}")
                        
                        # Test the new engine
                        test_choice = input("\nTest new engine? (y/n): ").strip().lower()
                        if test_choice in ['y', 'yes']:
                            self._test_current_engine()
                    else:
                        print("❌ Failed to switch engine")
                else:
                    print("❌ Invalid selection")
            else:
                print("❌ Please enter a number")
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error switching engine: {e}")
    
    def _test_current_engine(self):
        """Test currently selected engine"""
        if not self.tts_manager.current_engine:
            print("❌ No engine selected")
            return
            
        current_engine = self.tts_manager.current_engine
        engine_info = self.tts_manager.available_engines[current_engine]
        
        print(f"\n🔊 TESTING: {engine_info['name']}")
        print("=" * 40)
        
        # Get test text from user
        print("Choose test text:")
        print("1. Persian text (default)")
        print("2. English text")
        print("3. Custom text")
        
        text_choice = input("Select (1-3, or Enter for default): ").strip()
        
        if text_choice == "2":
            test_text = "This is a test of the current TTS engine"
        elif text_choice == "3":
            test_text = input("Enter custom text: ").strip()
            if not test_text:
                test_text = "تست موتور صوتی فعلی"
        else:
            test_text = "این تست موتور صوتی فعلی استیو است"
        
        # Generate test file
        test_file = f"{self.tts_manager.output_dir}/current_engine_test_{current_engine}.wav"
        
        print(f"\n🎵 Generating audio: '{test_text}'")
        success = self.tts_manager.speak_with_current_engine(test_text, test_file)
        
        if success and os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            print(f"✅ Test successful!")
            print(f"📁 File: {test_file}")
            print(f"📊 Size: {file_size} bytes")
        else:
            print("❌ Test failed")
        
        input("\nPress Enter to continue...")
    
    def _test_all_engines(self):
        """Test all available engines"""
        if not self.tts_manager.available_engines:
            print("❌ No engines available to test")
            return
            
        print("\n🧪 TESTING ALL ENGINES:")
        print("=" * 40)
        
        test_text = input("Enter test text (or press Enter for default): ").strip()
        if not test_text:
            test_text = "سلام! این تست همه موتورهای TTS است."
        
        print(f"\n🎵 Testing with: '{test_text}'")
        print("-" * 40)
        
        results = []
        
        for engine_name, engine_info in self.tts_manager.available_engines.items():
            print(f"\n🔊 Testing: {engine_info['name']}")
            
            # Switch to this engine temporarily
            original_engine = self.tts_manager.current_engine
            self.tts_manager.current_engine = engine_name
            
            # Test
            test_file = f"{self.tts_manager.output_dir}/test_all_{engine_name}.wav"
            success = self.tts_manager.speak_with_current_engine(test_text, test_file)
            
            if success and os.path.exists(test_file):
                file_size = os.path.getsize(test_file)
                print(f"   ✅ Success: {file_size} bytes")
                results.append((engine_name, engine_info['name'], test_file, file_size, True))
            else:
                print(f"   ❌ Failed")
                results.append((engine_name, engine_info['name'], None, 0, False))
            
            # Restore original engine
            self.tts_manager.current_engine = original_engine
        
        # Show results summary
        print(f"\n📊 TEST RESULTS SUMMARY:")
        print("=" * 50)
        for engine_key, engine_name, file_path, size, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{engine_name}: {status}")
            if success:
                print(f"   📁 {file_path} ({size} bytes)")
        
        print(f"\n🎵 All test files saved in: {self.tts_manager.output_dir}/")
        input("\nPress Enter to continue...")
    
    def _engine_comparison(self):
        """Compare engines side by side"""
        if len(self.tts_manager.available_engines) < 2:
            print("❌ Need at least 2 engines for comparison")
            return
            
        print("\n⚖️ ENGINE COMPARISON:")
        print("=" * 50)
        
        # Show comparison table
        print(f"{'Engine':<25} {'Quality':<10} {'Speed':<12} {'Offline':<8} {'Status':<10}")
        print("-" * 70)
        
        for engine_key, engine_info in self.tts_manager.available_engines.items():
            current = " (CURRENT)" if engine_key == self.tts_manager.current_engine else ""
            engine_name = engine_info['name'][:20] + current
            quality = engine_info['quality']
            speed = engine_info['speed']
            offline = "Yes" if engine_info['offline'] else "No"
            status = engine_info['status']
            
            print(f"{engine_name:<25} {quality:<10} {speed:<12} {offline:<8} {status:<10}")
        
        print("\n📋 RECOMMENDATIONS:")
        print("-" * 30)
        
        # Find best engines for different use cases
        offline_engines = [k for k, v in self.tts_manager.available_engines.items() if v['offline']]
        high_quality = [k for k, v in self.tts_manager.available_engines.items() if v['quality'] == 'High']
        fast_engines = [k for k, v in self.tts_manager.available_engines.items() if 'Fast' in v['speed']]
        
        if offline_engines:
            best_offline = offline_engines[0]
            print(f"🔒 Best Offline: {self.tts_manager.available_engines[best_offline]['name']}")
        
        if high_quality:
            best_quality = high_quality[0]
            print(f"⭐ Best Quality: {self.tts_manager.available_engines[best_quality]['name']}")
        
        if fast_engines:
            best_speed = fast_engines[0]
            print(f"⚡ Fastest: {self.tts_manager.available_engines[best_speed]['name']}")
        
        input("\nPress Enter to continue...")

def main():
    """Main function for standalone voice settings"""
    print("🚀 HEYSTIVE VOICE SETTINGS")
    print("=" * 40)
    
    try:
        # Initialize TTS manager
        print("🔧 Initializing TTS engines...")
        tts_manager = MultiTTSManager()
        
        if not tts_manager.available_engines:
            print("❌ No TTS engines available!")
            print("Please install dependencies and try again.")
            return
        
        # Create and run voice settings
        settings = VoiceSettings(tts_manager)
        settings.show_voice_menu()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()