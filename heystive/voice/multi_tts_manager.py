import os
import warnings
warnings.filterwarnings("ignore")

class MultiTTSManager:
    """
    Multiple TTS engines manager - User can choose preferred option
    IMPLEMENT ALL ENGINES AS WORKING ALTERNATIVES
    """
    
    def __init__(self):
        self.available_engines = {}
        self.current_engine = None
        self.output_dir = "heystive_audio_output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize all available engines
        self._initialize_all_engines()
        
        # Auto-select best available engine
        self._auto_select_best_engine()
    
    def _initialize_all_engines(self):
        """Initialize ALL TTS engines - test each one immediately"""
        
        print("🔄 Initializing Multiple TTS Engines...")
        
        # ENGINE 1: pyttsx3 (System TTS - Optimized)
        self._init_pyttsx3()
        
        # ENGINE 2: Coqui TTS (Neural TTS - High Quality)
        self._init_coqui_tts()
        
        # ENGINE 3: Google TTS (Online - Natural)
        self._init_google_tts()
        
        # ENGINE 4: eSpeak Direct (Simple Offline)
        self._init_espeak_direct()
        
        # ENGINE 5: Azure TTS (Online - Premium)
        self._init_azure_tts()
        
        print(f"\n✅ Initialized {len(self.available_engines)} TTS engines")
        
    def _init_pyttsx3(self):
        """Initialize optimized pyttsx3 engine"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Apply basic settings without voice selection that might fail
            try:
                engine.setProperty('rate', 150)  # Slower rate for better clarity
                engine.setProperty('volume', 1.0)
                
                # Try to set a voice, but don't fail if it doesn't work
                voices = engine.getProperty('voices')
                if voices and len(voices) > 0:
                    # Just use the first available voice
                    engine.setProperty('voice', voices[0].id)
            except:
                print("⚠️ pyttsx3: Voice settings failed, using defaults")
            
            # Test the engine with English text (more reliable)
            test_file = f"{self.output_dir}/test_pyttsx3.wav"
            test_text = "pyttsx3 TTS engine test"
            
            try:
                engine.save_to_file(test_text, test_file)
                engine.runAndWait()
                
                if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
                    self.available_engines['pyttsx3'] = {
                        'engine': engine,
                        'name': 'pyttsx3 (System TTS)',
                        'quality': 'Medium',
                        'speed': 'Fast',
                        'offline': True,
                        'status': 'Working'
                    }
                    print("✅ pyttsx3: Initialized and tested")
                else:
                    print("❌ pyttsx3: Test file creation failed")
            except Exception as test_error:
                print(f"❌ pyttsx3: Test failed - {test_error}")
                
        except Exception as e:
            print(f"❌ pyttsx3: Failed - {e}")
    
    def _init_coqui_tts(self):
        """Initialize Coqui TTS (XTTS-v2)"""
        try:
            from TTS.api import TTS
            import torch
            import torchaudio
            
            # Use XTTS-v2 model for Persian
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            # Test the engine
            test_text = "تست موتور Coqui TTS"
            test_file = f"{self.output_dir}/test_coqui.wav"
            
            wav = tts.tts(text=test_text, language="fa")
            torchaudio.save(test_file, torch.tensor(wav).unsqueeze(0), 22050)
            
            if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
                self.available_engines['coqui'] = {
                    'engine': tts,
                    'name': 'Coqui TTS (Neural)',
                    'quality': 'High',
                    'speed': 'Medium',
                    'offline': True,
                    'status': 'Working'
                }
                print("✅ Coqui TTS: Initialized and tested")
            else:
                print("❌ Coqui TTS: Test failed")
                
        except ImportError:
            print("⚠️ Coqui TTS: Not available (requires Python 3.9-3.11, current: Python 3.13)")
        except Exception as e:
            print(f"❌ Coqui TTS: Failed - {e}")
    
    def _init_google_tts(self):
        """Initialize Google TTS (gTTS)"""
        try:
            from gtts import gTTS
            import pygame
            
            # Try Persian first, then Arabic as fallback for Persian text
            test_text = "تست موتور Google TTS"
            test_file = f"{self.output_dir}/test_gtts.mp3"
            
            # Try Persian language code
            try:
                tts = gTTS(text=test_text, lang='fa', slow=False)
                tts.save(test_file)
                lang_used = 'fa (Persian)'
            except:
                # Fallback to Arabic for Persian text
                try:
                    tts = gTTS(text=test_text, lang='ar', slow=False)
                    tts.save(test_file)
                    lang_used = 'ar (Arabic - Persian fallback)'
                except:
                    # Final fallback to English
                    test_text = "Google TTS Test"
                    tts = gTTS(text=test_text, lang='en', slow=False)
                    tts.save(test_file)
                    lang_used = 'en (English - fallback)'
            
            if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
                self.available_engines['gtts'] = {
                    'engine': 'gtts',
                    'name': f'Google TTS ({lang_used})',
                    'quality': 'High',
                    'speed': 'Medium',
                    'offline': False,
                    'status': 'Working'
                }
                print(f"✅ Google TTS: Initialized and tested with {lang_used}")
            else:
                print("❌ Google TTS: Test failed")
                
        except ImportError:
            print("⚠️ Google TTS: Not installed (pip install gtts pygame)")
        except Exception as e:
            print(f"❌ Google TTS: Failed - {e}")
    
    def _init_espeak_direct(self):
        """Initialize direct eSpeak engine"""
        try:
            import subprocess
            
            # Test eSpeak directly
            test_text = "eSpeak TTS engine test"
            test_file = f"{self.output_dir}/test_espeak.wav"
            
            # Try eSpeak command
            cmd = ["espeak", "-w", test_file, "-s", "150", test_text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(test_file) and os.path.getsize(test_file) > 0:
                self.available_engines['espeak'] = {
                    'engine': 'espeak',
                    'name': 'eSpeak (Direct)',
                    'quality': 'Basic',
                    'speed': 'Very Fast',
                    'offline': True,
                    'status': 'Working'
                }
                print("✅ eSpeak: Initialized and tested")
            else:
                print(f"❌ eSpeak: Test failed - {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ eSpeak: Timeout during test")
        except FileNotFoundError:
            print("⚠️ eSpeak: Not installed (apt install espeak)")
        except Exception as e:
            print(f"❌ eSpeak: Failed - {e}")
    
    def _init_azure_tts(self):
        """Initialize Azure TTS"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Note: Requires Azure API key
            print("ℹ️ Azure TTS: Requires API key (skipping for offline setup)")
            
        except ImportError:
            print("⚠️ Azure TTS: Not installed (pip install azure-cognitiveservices-speech)")
        except Exception as e:
            print(f"❌ Azure TTS: Failed - {e}")
    
    def _select_best_voice(self, voices):
        """Select best voice for Persian"""
        for voice in voices:
            voice_name = voice.name.lower()
            if any(lang in voice_name for lang in ['persian', 'farsi', 'arabic']):
                return voice
        
        # Fallback to female voices
        for voice in voices:
            if 'female' in voice.name.lower():
                return voice
        
        return voices[0] if voices else None
    
    def _auto_select_best_engine(self):
        """Auto-select the best available engine"""
        
        # Priority order: Coqui > eSpeak > pyttsx3 > Google TTS
        priority_order = ['coqui', 'espeak', 'pyttsx3', 'gtts']
        
        for engine_name in priority_order:
            if engine_name in self.available_engines:
                self.current_engine = engine_name
                print(f"🎯 Auto-selected: {self.available_engines[engine_name]['name']}")
                return
        
        print("❌ No TTS engines available!")
    
    def list_available_engines(self):
        """List all available TTS engines"""
        print("\n🎤 AVAILABLE TTS ENGINES:")
        print("=" * 50)
        
        for i, (key, engine_info) in enumerate(self.available_engines.items(), 1):
            current = "✅ CURRENT" if key == self.current_engine else ""
            print(f"{i}. {engine_info['name']} {current}")
            print(f"   Quality: {engine_info['quality']}")
            print(f"   Speed: {engine_info['speed']}")
            print(f"   Offline: {'Yes' if engine_info['offline'] else 'No'}")
            print(f"   Status: {engine_info['status']}")
            print()
        
        return list(self.available_engines.keys())
    
    def switch_engine(self, engine_name):
        """Switch to a different TTS engine"""
        if engine_name in self.available_engines:
            self.current_engine = engine_name
            print(f"🔄 Switched to: {self.available_engines[engine_name]['name']}")
            return True
        else:
            print(f"❌ Engine '{engine_name}' not available")
            return False
    
    def speak_with_current_engine(self, text, output_file=None):
        """Speak using currently selected engine"""
        
        if not self.current_engine:
            print("❌ No TTS engine selected")
            return False
        
        engine_info = self.available_engines[self.current_engine]
        
        try:
            if self.current_engine == 'pyttsx3':
                return self._speak_pyttsx3(text, output_file, engine_info['engine'])
            
            elif self.current_engine == 'coqui':
                return self._speak_coqui(text, output_file, engine_info['engine'])
            
            elif self.current_engine == 'gtts':
                return self._speak_gtts(text, output_file)
            
            elif self.current_engine == 'espeak':
                return self._speak_espeak(text, output_file)
            
        except Exception as e:
            print(f"❌ TTS Error ({self.current_engine}): {e}")
            return False
    
    def _speak_pyttsx3(self, text, output_file, engine):
        """Speak with pyttsx3"""
        try:
            if output_file:
                engine.save_to_file(text, output_file)
                engine.runAndWait()
                print(f"📁 Audio saved to: {output_file}")
            else:
                engine.say(text)
                engine.runAndWait()
            return True
        except Exception as e:
            print(f"❌ pyttsx3 playback error: {e}")
            return False
    
    def _speak_coqui(self, text, output_file, tts_engine):
        """Speak with Coqui TTS"""
        import torch
        import torchaudio
        
        wav = tts_engine.tts(text=text, language="fa")
        
        if output_file:
            torchaudio.save(output_file, torch.tensor(wav).unsqueeze(0), 22050)
        else:
            # Play directly
            import sounddevice as sd
            sd.play(wav, 22050)
            sd.wait()
        return True
    
    def _speak_gtts(self, text, output_file):
        """Speak with Google TTS"""
        from gtts import gTTS
        
        if not output_file:
            output_file = f"{self.output_dir}/temp_gtts.mp3"
        
        # Try Persian first, then Arabic, then English
        try:
            tts = gTTS(text=text, lang='fa', slow=False)
        except:
            try:
                tts = gTTS(text=text, lang='ar', slow=False)
            except:
                tts = gTTS(text=text, lang='en', slow=False)
        
        tts.save(output_file)
        
        # Try to play the file, but don't fail if no audio device
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pass
        except:
            print(f"📁 Audio saved to: {output_file} (no audio device for playback)")
        
        return True
    
    def _speak_espeak(self, text, output_file):
        """Speak with direct eSpeak"""
        import subprocess
        
        if not output_file:
            output_file = f"{self.output_dir}/temp_espeak.wav"
        
        try:
            # Use eSpeak directly
            cmd = ["espeak", "-w", output_file, "-s", "150", text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(output_file):
                print(f"📁 Audio saved to: {output_file}")
                return True
            else:
                print(f"❌ eSpeak error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ eSpeak failed: {e}")
            return False
    
    def test_all_engines(self):
        """Test all available engines with the same text"""
        
        test_text = "سلام! این تست کیفیت صدای موتورهای مختلف TTS است."
        
        print("\n🧪 TESTING ALL TTS ENGINES:")
        print("=" * 50)
        
        for engine_name, engine_info in self.available_engines.items():
            print(f"\n🔊 Testing: {engine_info['name']}")
            
            # Switch to this engine
            original_engine = self.current_engine
            self.current_engine = engine_name
            
            # Test
            test_file = f"{self.output_dir}/comparison_test_{engine_name}.wav"
            success = self.speak_with_current_engine(test_text, test_file)
            
            if success and os.path.exists(test_file):
                file_size = os.path.getsize(test_file)
                print(f"✅ Success: {test_file} ({file_size} bytes)")
            else:
                print(f"❌ Failed: Could not generate audio")
            
            # Restore original engine
            self.current_engine = original_engine
        
        print(f"\n🎵 Audio comparison files saved in: {self.output_dir}/")
        print("Listen to all files and choose your preferred TTS engine!")

# IMMEDIATE EXECUTION AND TESTING
if __name__ == "__main__":
    print("🚀 INITIALIZING MULTI-TTS SYSTEM...")
    
    tts_manager = MultiTTSManager()
    
    # Show available engines
    available_engines = tts_manager.list_available_engines()
    
    if available_engines:
        # Test all engines
        tts_manager.test_all_engines()
        
        # Interactive engine selection
        print("\n🎯 INTERACTIVE ENGINE SELECTION:")
        for i, engine in enumerate(available_engines, 1):
            print(f"{i}. {engine}")
        
        try:
            choice = input("\nSelect engine number (or press Enter for auto): ").strip()
            if choice and choice.isdigit():
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(available_engines):
                    selected_engine = available_engines[selected_index]
                    tts_manager.switch_engine(selected_engine)
        except:
            pass
        
        # Final test with selected engine
        print("\n🎤 FINAL TEST WITH SELECTED ENGINE:")
        final_test = "تست نهایی سیستم صوتی چندگانه استیو"
        final_file = f"{tts_manager.output_dir}/final_test.wav"
        
        success = tts_manager.speak_with_current_engine(final_test, final_file)
        if success:
            print(f"✅ Final test successful: {final_file}")
        else:
            print("❌ Final test failed")
    
    else:
        print("❌ No TTS engines available. Check dependencies!")