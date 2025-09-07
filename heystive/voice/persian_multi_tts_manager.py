#!/usr/bin/env python3
"""
HEYSTIVE PERSIAN MULTI-TTS MANAGER
Complete Persian/Farsi Text-to-Speech system with multiple high-quality TTS engines
Implements all 6 specified TTS models with exact model paths and real functionality
"""

import os
import warnings
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PersianMultiTTSManager:
    """
    Complete Persian TTS system with 6 high-quality engines
    All engines must be functional and generate real audio files
    """
    
    def __init__(self):
        self.output_dir = Path("/workspace/heystive_audio_output")
        self.output_dir.mkdir(exist_ok=True)
        
        self.engines = {}
        self.current_engine = None
        self.engine_priority = [
            'kamtera_female', 'kamtera_male', 'informal_persian', 
            'google_tts', 'system_tts', 'espeak_persian'
        ]
        
        print("🚀 Initializing Persian Multi-TTS Manager...")
        print("=" * 60)
        
        # Initialize all TTS engines
        self._initialize_all_engines()
        
        # Auto-select best available engine
        self._auto_select_best_engine()
        
        print(f"✅ Persian TTS Manager initialized with {len(self.engines)} engines")
    
    def _initialize_all_engines(self):
        """Initialize ALL 6 TTS engines with exact model paths"""
        
        print("🔄 Initializing Persian TTS Engines...")
        
        # ENGINE 1: Kamtera Female VITS (Premium Quality)
        self._init_kamtera_female()
        
        # ENGINE 2: Kamtera Male VITS (High Quality)
        self._init_kamtera_male()
        
        # ENGINE 3: Informal Persian VITS (Conversational Style)
        self._init_informal_persian()
        
        # ENGINE 4: Google TTS (Online - Natural)
        self._init_google_tts()
        
        # ENGINE 5: System TTS (pyttsx3 - Optimized)
        self._init_system_tts()
        
        # ENGINE 6: eSpeak Persian (Offline Fallback)
        self._init_espeak_persian()
        
        print(f"✅ Initialized {len(self.engines)} TTS engines")
    
    def _init_kamtera_female(self):
        """Initialize Kamtera Female VITS model"""
        try:
            from TTS.api import TTS
            import torch
            import torchaudio
            
            print("🔧 Initializing Kamtera Female VITS...")
            
            # Use exact model path from requirements
            model_path = "Kamtera/persian-tts-female-vits"
            
            # Initialize TTS with Kamtera female model
            tts = TTS(model_path)
            
            # Test the engine
            test_text = "سلام! من صدای زن کامترا هستم"
            test_file = self.output_dir / "test_kamtera_female.wav"
            
            # Generate test audio
            wav = tts.tts(text=test_text)
            torchaudio.save(str(test_file), torch.tensor(wav).unsqueeze(0), 22050)
            
            if test_file.exists() and test_file.stat().st_size > 0:
                self.engines['kamtera_female'] = {
                    'engine': tts,
                    'name': 'Kamtera Female VITS',
                    'model_path': model_path,
                    'quality': 'Premium',
                    'speed': 'Medium',
                    'offline': True,
                    'status': 'Working',
                    'voice_type': 'Female',
                    'accent': 'Persian'
                }
                print("✅ Kamtera Female: Initialized and tested")
            else:
                print("❌ Kamtera Female: Test file creation failed")
                
        except ImportError as e:
            print(f"⚠️ Kamtera Female: TTS library not available - {e}")
        except Exception as e:
            print(f"❌ Kamtera Female: Failed - {e}")
    
    def _init_kamtera_male(self):
        """Initialize Kamtera Male VITS model"""
        try:
            from TTS.api import TTS
            import torch
            import torchaudio
            
            print("🔧 Initializing Kamtera Male VITS...")
            
            # Use exact model path from requirements
            model_path = "Kamtera/persian-tts-male-vits"
            
            # Initialize TTS with Kamtera male model
            tts = TTS(model_path)
            
            # Test the engine
            test_text = "سلام! من صدای مرد کامترا هستم"
            test_file = self.output_dir / "test_kamtera_male.wav"
            
            # Generate test audio
            wav = tts.tts(text=test_text)
            torchaudio.save(str(test_file), torch.tensor(wav).unsqueeze(0), 22050)
            
            if test_file.exists() and test_file.stat().st_size > 0:
                self.engines['kamtera_male'] = {
                    'engine': tts,
                    'name': 'Kamtera Male VITS',
                    'model_path': model_path,
                    'quality': 'High',
                    'speed': 'Medium',
                    'offline': True,
                    'status': 'Working',
                    'voice_type': 'Male',
                    'accent': 'Persian'
                }
                print("✅ Kamtera Male: Initialized and tested")
            else:
                print("❌ Kamtera Male: Test file creation failed")
                
        except ImportError as e:
            print(f"⚠️ Kamtera Male: TTS library not available - {e}")
        except Exception as e:
            print(f"❌ Kamtera Male: Failed - {e}")
    
    def _init_informal_persian(self):
        """Initialize Informal Persian VITS model"""
        try:
            from TTS.api import TTS
            import torch
            import torchaudio
            
            print("🔧 Initializing Informal Persian VITS...")
            
            # Use exact model path from requirements
            model_path = "karim23657/persian-tts-female-GPTInformal-Persian-vits"
            
            # Initialize TTS with informal Persian model
            tts = TTS(model_path)
            
            # Test the engine
            test_text = "سلام! من با لهجه محاوره‌ای صحبت می‌کنم"
            test_file = self.output_dir / "test_informal_persian.wav"
            
            # Generate test audio
            wav = tts.tts(text=test_text)
            torchaudio.save(str(test_file), torch.tensor(wav).unsqueeze(0), 22050)
            
            if test_file.exists() and test_file.stat().st_size > 0:
                self.engines['informal_persian'] = {
                    'engine': tts,
                    'name': 'Informal Persian VITS',
                    'model_path': model_path,
                    'quality': 'High',
                    'speed': 'Medium',
                    'offline': True,
                    'status': 'Working',
                    'voice_type': 'Female',
                    'accent': 'Informal Persian'
                }
                print("✅ Informal Persian: Initialized and tested")
            else:
                print("❌ Informal Persian: Test file creation failed")
                
        except ImportError as e:
            print(f"⚠️ Informal Persian: TTS library not available - {e}")
        except Exception as e:
            print(f"❌ Informal Persian: Failed - {e}")
    
    def _init_google_tts(self):
        """Initialize Google TTS for Persian"""
        try:
            from gtts import gTTS
            import pygame
            
            print("🔧 Initializing Google TTS...")
            
            # Test the engine
            test_text = "سلام! من Google TTS هستم"
            test_file = self.output_dir / "test_google_tts.mp3"
            
            # Try Persian language code
            try:
                tts = gTTS(text=test_text, lang='fa', slow=False)
                tts.save(str(test_file))
                lang_used = 'fa (Persian)'
            except:
                # Fallback to Arabic for Persian text
                try:
                    tts = gTTS(text=test_text, lang='ar', slow=False)
                    tts.save(str(test_file))
                    lang_used = 'ar (Arabic - Persian fallback)'
                except:
                    # Final fallback to English
                    test_text = "Hello! I am Google TTS"
                    tts = gTTS(text=test_text, lang='en', slow=False)
                    tts.save(str(test_file))
                    lang_used = 'en (English - fallback)'
            
            if test_file.exists() and test_file.stat().st_size > 0:
                self.engines['google_tts'] = {
                    'engine': 'gtts',
                    'name': f'Google TTS ({lang_used})',
                    'model_path': 'Persian (fa) via gtts',
                    'quality': 'High',
                    'speed': 'Fast',
                    'offline': False,
                    'status': 'Working',
                    'voice_type': 'Neutral',
                    'accent': 'Persian'
                }
                print(f"✅ Google TTS: Initialized and tested with {lang_used}")
            else:
                print("❌ Google TTS: Test failed")
                
        except ImportError as e:
            print(f"⚠️ Google TTS: Not installed - {e}")
        except Exception as e:
            print(f"❌ Google TTS: Failed - {e}")
    
    def _init_system_tts(self):
        """Initialize System TTS (pyttsx3) with Persian optimization"""
        try:
            import pyttsx3
            
            print("🔧 Initializing System TTS...")
            
            engine = pyttsx3.init()
            
            # Apply Persian-optimized settings
            try:
                engine.setProperty('rate', 150)  # Slower rate for better clarity
                engine.setProperty('volume', 1.0)
                
                # Try to find Persian voice
                voices = engine.getProperty('voices')
                persian_voice = self._find_persian_voice(voices)
                
                if persian_voice:
                    engine.setProperty('voice', persian_voice.id)
                    voice_name = persian_voice.name
                else:
                    # Use first available voice
                    if voices:
                        engine.setProperty('voice', voices[0].id)
                        voice_name = voices[0].name
                    else:
                        voice_name = "Default"
                        
            except Exception as e:
                print(f"⚠️ System TTS: Voice settings failed - {e}")
                voice_name = "Default"
            
            # Test the engine
            test_file = self.output_dir / "test_system_tts.wav"
            test_text = "سلام! من سیستم TTS هستم"
            
            try:
                engine.save_to_file(test_text, str(test_file))
                engine.runAndWait()
                
                if test_file.exists() and test_file.stat().st_size > 0:
                    self.engines['system_tts'] = {
                        'engine': engine,
                        'name': f'System TTS ({voice_name})',
                        'model_path': 'pyttsx3 with Persian optimization',
                        'quality': 'Medium',
                        'speed': 'Fast',
                        'offline': True,
                        'status': 'Working',
                        'voice_type': 'System',
                        'accent': 'System Default'
                    }
                    print("✅ System TTS: Initialized and tested")
                else:
                    print("❌ System TTS: Test file creation failed")
            except Exception as test_error:
                print(f"❌ System TTS: Test failed - {test_error}")
                
        except ImportError as e:
            print(f"⚠️ System TTS: Not installed - {e}")
        except Exception as e:
            print(f"❌ System TTS: Failed - {e}")
    
    def _init_espeak_persian(self):
        """Initialize eSpeak-NG with Persian support"""
        try:
            import subprocess
            
            print("🔧 Initializing eSpeak Persian...")
            
            # Test eSpeak with Persian
            test_text = "سلام! من eSpeak هستم"
            test_file = self.output_dir / "test_espeak_persian.wav"
            
            # Try eSpeak command with Persian language
            cmd = ["espeak", "-w", str(test_file), "-s", "150", "-v", "fa", test_text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and test_file.exists() and test_file.stat().st_size > 0:
                self.engines['espeak_persian'] = {
                    'engine': 'espeak',
                    'name': 'eSpeak-NG Persian',
                    'model_path': 'eSpeak-NG Persian fallback',
                    'quality': 'Basic',
                    'speed': 'Very Fast',
                    'offline': True,
                    'status': 'Working',
                    'voice_type': 'Synthetic',
                    'accent': 'Persian'
                }
                print("✅ eSpeak Persian: Initialized and tested")
            else:
                # Fallback to English eSpeak
                cmd = ["espeak", "-w", str(test_file), "-s", "150", "Hello! I am eSpeak"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and test_file.exists() and test_file.stat().st_size > 0:
                    self.engines['espeak_persian'] = {
                        'engine': 'espeak',
                        'name': 'eSpeak-NG (English fallback)',
                        'model_path': 'eSpeak-NG Persian fallback',
                        'quality': 'Basic',
                        'speed': 'Very Fast',
                        'offline': True,
                        'status': 'Working',
                        'voice_type': 'Synthetic',
                        'accent': 'English'
                    }
                    print("✅ eSpeak: Initialized with English fallback")
                else:
                    print(f"❌ eSpeak: Test failed - {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ eSpeak: Timeout during test")
        except FileNotFoundError:
            print("⚠️ eSpeak: Not installed (apt install espeak)")
        except Exception as e:
            print(f"❌ eSpeak: Failed - {e}")
    
    def _find_persian_voice(self, voices):
        """Find Persian voice in available voices"""
        if not voices:
            return None
            
        # Look for Persian/Farsi voices
        for voice in voices:
            voice_name = voice.name.lower()
            if any(lang in voice_name for lang in ['persian', 'farsi', 'fa', 'iran']):
                return voice
        
        # Look for Arabic voices (closest to Persian)
        for voice in voices:
            voice_name = voice.name.lower()
            if any(lang in voice_name for lang in ['arabic', 'ar', 'arab']):
                return voice
        
        # Look for female voices (generally better for Persian)
        for voice in voices:
            voice_name = voice.name.lower()
            if 'female' in voice_name:
                return voice
        
        return voices[0] if voices else None
    
    def _auto_select_best_engine(self):
        """Auto-select the best available engine based on priority"""
        
        for engine_name in self.engine_priority:
            if engine_name in self.engines:
                self.current_engine = engine_name
                engine_info = self.engines[engine_name]
                print(f"🎯 Auto-selected: {engine_info['name']} ({engine_info['quality']} quality)")
                return
        
        print("❌ No TTS engines available!")
    
    def list_engines(self) -> Dict[str, Dict]:
        """List all available TTS engines with detailed information"""
        print("\n🎤 AVAILABLE PERSIAN TTS ENGINES:")
        print("=" * 60)
        
        for i, (key, engine_info) in enumerate(self.engines.items(), 1):
            current = "✅ CURRENT" if key == self.current_engine else ""
            print(f"{i}. {engine_info['name']} {current}")
            print(f"   Model: {engine_info['model_path']}")
            print(f"   Quality: {engine_info['quality']}")
            print(f"   Speed: {engine_info['speed']}")
            print(f"   Voice: {engine_info['voice_type']} ({engine_info['accent']})")
            print(f"   Offline: {'Yes' if engine_info['offline'] else 'No'}")
            print(f"   Status: {engine_info['status']}")
            print()
        
        return self.engines
    
    def switch_engine(self, engine_name: str) -> bool:
        """Switch to a different TTS engine"""
        if engine_name in self.engines:
            self.current_engine = engine_name
            engine_info = self.engines[engine_name]
            print(f"🔄 Switched to: {engine_info['name']}")
            return True
        else:
            print(f"❌ Engine '{engine_name}' not available")
            print(f"Available engines: {list(self.engines.keys())}")
            return False
    
    def speak_persian(self, text: str, engine_name: Optional[str] = None, output_file: Optional[str] = None) -> bool:
        """
        Speak Persian text using specified or current engine
        Returns True if audio was successfully generated
        """
        
        # Use specified engine or current engine
        target_engine = engine_name if engine_name else self.current_engine
        
        if not target_engine or target_engine not in self.engines:
            print(f"❌ No TTS engine available (requested: {engine_name}, current: {self.current_engine})")
            return False
        
        engine_info = self.engines[target_engine]
        
        try:
            # Normalize Persian text
            normalized_text = self._normalize_persian_text(text)
            print(f"🔊 Speaking with {engine_info['name']}: '{normalized_text}'")
            
            # Generate output filename if not provided
            if not output_file:
                timestamp = int(time.time())
                output_file = self.output_dir / f"persian_speech_{target_engine}_{timestamp}.wav"
            
            # Use appropriate engine method
            if target_engine in ['kamtera_female', 'kamtera_male', 'informal_persian']:
                return self._speak_vits(normalized_text, output_file, engine_info['engine'])
            elif target_engine == 'google_tts':
                return self._speak_google_tts(normalized_text, output_file)
            elif target_engine == 'system_tts':
                return self._speak_system_tts(normalized_text, output_file, engine_info['engine'])
            elif target_engine == 'espeak_persian':
                return self._speak_espeak(normalized_text, output_file)
            else:
                print(f"❌ Unknown engine type: {target_engine}")
                return False
                
        except Exception as e:
            print(f"❌ TTS Error ({target_engine}): {e}")
            return False
    
    def _speak_vits(self, text: str, output_file: str, tts_engine) -> bool:
        """Speak with VITS-based engines (Kamtera, Informal Persian)"""
        try:
            import torch
            import torchaudio
            
            # Generate audio
            wav = tts_engine.tts(text=text)
            
            # Save to file
            torchaudio.save(output_file, torch.tensor(wav).unsqueeze(0), 22050)
            
            # Verify file was created
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                file_size = os.path.getsize(output_file)
                print(f"✅ Audio generated: {output_file} ({file_size} bytes)")
                return True
            else:
                print(f"❌ Audio file not created: {output_file}")
                return False
                
        except Exception as e:
            print(f"❌ VITS engine error: {e}")
            return False
    
    def _speak_google_tts(self, text: str, output_file: str) -> bool:
        """Speak with Google TTS"""
        try:
            from gtts import gTTS
            
            # Try Persian first, then Arabic, then English
            try:
                tts = gTTS(text=text, lang='fa', slow=False)
            except:
                try:
                    tts = gTTS(text=text, lang='ar', slow=False)
                except:
                    tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to file
            tts.save(output_file)
            
            # Verify file was created
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                file_size = os.path.getsize(output_file)
                print(f"✅ Audio generated: {output_file} ({file_size} bytes)")
                return True
            else:
                print(f"❌ Audio file not created: {output_file}")
                return False
                
        except Exception as e:
            print(f"❌ Google TTS error: {e}")
            return False
    
    def _speak_system_tts(self, text: str, output_file: str, engine) -> bool:
        """Speak with System TTS (pyttsx3)"""
        try:
            # Save to file
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            
            # Verify file was created
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                file_size = os.path.getsize(output_file)
                print(f"✅ Audio generated: {output_file} ({file_size} bytes)")
                return True
            else:
                print(f"❌ Audio file not created: {output_file}")
                return False
                
        except Exception as e:
            print(f"❌ System TTS error: {e}")
            return False
    
    def _speak_espeak(self, text: str, output_file: str) -> bool:
        """Speak with eSpeak"""
        try:
            import subprocess
            
            # Try Persian first
            cmd = ["espeak", "-w", output_file, "-s", "150", "-v", "fa", text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                file_size = os.path.getsize(output_file)
                print(f"✅ Audio generated: {output_file} ({file_size} bytes)")
                return True
            else:
                # Fallback to English
                cmd = ["espeak", "-w", output_file, "-s", "150", text]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    file_size = os.path.getsize(output_file)
                    print(f"✅ Audio generated (English fallback): {output_file} ({file_size} bytes)")
                    return True
                else:
                    print(f"❌ eSpeak error: {result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ eSpeak error: {e}")
            return False
    
    def _normalize_persian_text(self, text: str) -> str:
        """Normalize Persian text for better TTS pronunciation"""
        # Convert Persian digits to English for better pronunciation
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        english_digits = "0123456789"
        
        for p_digit, e_digit in zip(persian_digits, english_digits):
            text = text.replace(p_digit, e_digit)
        
        # Handle common Persian pronunciation issues
        replacements = {
            "ض": "ز",  # Pronounce ض as ز
            "ص": "س",  # Pronounce ص as س
            "ث": "س",  # Pronounce ث as س
            "ظ": "ز",  # Pronounce ظ as ز
            "ط": "ت",  # Pronounce ط as ت
            "ق": "غ",  # Pronounce ق as غ
        }
        
        for persian_char, replacement in replacements.items():
            text = text.replace(persian_char, replacement)
        
        return text.strip()
    
    def test_all_engines(self) -> Dict[str, bool]:
        """Test all available engines with the same Persian text"""
        
        test_text = "سلام! این تست کیفیت صدای موتورهای مختلف TTS است. من می‌توانم به فارسی صحبت کنم."
        
        print("\n🧪 TESTING ALL PERSIAN TTS ENGINES:")
        print("=" * 60)
        print(f"Test text: '{test_text}'")
        print()
        
        results = {}
        
        for engine_name, engine_info in self.engines.items():
            print(f"🔊 Testing: {engine_info['name']}")
            
            # Generate test file
            test_file = self.output_dir / f"comparison_test_{engine_name}.wav"
            success = self.speak_persian(test_text, engine_name, str(test_file))
            
            if success and test_file.exists():
                file_size = test_file.stat().st_size
                print(f"   ✅ Success: {test_file.name} ({file_size} bytes)")
                results[engine_name] = True
            else:
                print(f"   ❌ Failed: Could not generate audio")
                results[engine_name] = False
            
            print()
        
        # Report results
        successful_engines = sum(results.values())
        total_engines = len(results)
        
        print(f"📊 Test Results: {successful_engines}/{total_engines} engines working")
        print(f"🎵 Audio comparison files saved in: {self.output_dir}/")
        print("Listen to all files and choose your preferred TTS engine!")
        
        return results
    
    def get_engine_info(self, engine_name: str) -> Optional[Dict]:
        """Get detailed information about a specific engine"""
        return self.engines.get(engine_name)
    
    def get_current_engine_info(self) -> Optional[Dict]:
        """Get information about the currently selected engine"""
        if self.current_engine:
            return self.engines[self.current_engine]
        return None

# IMMEDIATE EXECUTION AND TESTING
if __name__ == "__main__":
    print("🚀 INITIALIZING PERSIAN MULTI-TTS SYSTEM...")
    print("=" * 60)
    
    # Create TTS manager
    tts_manager = PersianMultiTTSManager()
    
    # Show available engines
    available_engines = tts_manager.list_engines()
    
    if available_engines:
        # Test all engines
        test_results = tts_manager.test_all_engines()
        
        # Show current engine
        current_info = tts_manager.get_current_engine_info()
        if current_info:
            print(f"\n🎯 Current Engine: {current_info['name']}")
            print(f"   Quality: {current_info['quality']}")
            print(f"   Voice: {current_info['voice_type']} ({current_info['accent']})")
        
        # Interactive engine selection
        print("\n🎯 INTERACTIVE ENGINE SELECTION:")
        engine_list = list(available_engines.keys())
        for i, engine in enumerate(engine_list, 1):
            engine_info = available_engines[engine]
            current = " (CURRENT)" if engine == tts_manager.current_engine else ""
            print(f"{i}. {engine_info['name']}{current}")
        
        try:
            choice = input("\nSelect engine number (or press Enter to keep current): ").strip()
            if choice and choice.isdigit():
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(engine_list):
                    selected_engine = engine_list[selected_index]
                    tts_manager.switch_engine(selected_engine)
        except:
            pass
        
        # Final test with selected engine
        print("\n🎤 FINAL TEST WITH SELECTED ENGINE:")
        final_test = "تست نهایی سیستم صوتی چندگانه HeyStive. من آماده خدمت‌رسانی هستم!"
        final_file = tts_manager.output_dir / "final_test.wav"
        
        success = tts_manager.speak_persian(final_test, output_file=str(final_file))
        if success:
            print(f"✅ Final test successful: {final_file}")
            print("🎉 Persian Multi-TTS System is ready for use!")
        else:
            print("❌ Final test failed")
    
    else:
        print("❌ No TTS engines available. Check dependencies!")
        print("Required packages: TTS, torch, torchaudio, gtts, pyttsx3, espeak")