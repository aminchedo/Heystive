#!/usr/bin/env python3
"""
HEYSTIVE PERSIAN TTS MODULE - STEP 1 IMPLEMENTATION
Real Persian text-to-speech that generates actual audio files
OBJECTIVE: Create working Persian TTS with immediate testing and proof generation
"""

import os
from pathlib import Path
import time
import sys
from gtts import gTTS
import pygame
import io

class PersianVoiceEngine:
    """
    REAL Persian TTS implementation - NO PLACEHOLDERS
    Must produce actual .wav files as proof of functionality
    """
    
    def __init__(self):
        self.output_dir = Path("/workspace/heystive_audio_output")
        self.output_dir.mkdir(exist_ok=True)
        self.test_results = {}
        
        print("🚀 Initializing Persian Voice Engine...")
        
        # Initialize pygame mixer for audio playback
        self._initialize_pygame()
        
        # IMMEDIATE TESTING
        self._run_persian_voice_test()
    
    def _initialize_pygame(self):
        """Initialize pygame mixer for audio playback."""
        try:
            pygame.mixer.init()
            print("✅ Pygame audio mixer initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️ Pygame initialization failed: {e}")
            return False
    
    def _run_persian_voice_test(self):
        """
        MANDATORY: Test Persian voice immediately with real audio generation
        """
        print("\n🎤 PERSIAN VOICE TEST - GENERATING ACTUAL AUDIO:")
        print("=" * 60)
        
        persian_test_phrases = [
            "سلام، من استیو هستم",
            "دستیار صوتی فارسی شما آماده است", 
            "آیا صدای من را می‌شنوید؟",
            "من می‌توانم به فارسی صحبت کنم",
            "تست سیستم صوتی با موفقیت انجام شد"
        ]
        
        for i, phrase in enumerate(persian_test_phrases, 1):
            try:
                # Generate unique filename
                audio_file = self.output_dir / f"persian_test_{i:02d}.mp3"
                
                print(f"\n🎵 Test {i}/5: '{phrase}'")
                print(f"   📁 Generating → {audio_file}")
                
                # ACTUALLY CREATE AUDIO FILE
                success = self.speak_and_save(phrase, str(audio_file))
                
                if success and audio_file.exists():
                    file_size = audio_file.stat().st_size
                    print(f"   ✅ SUCCESS: Audio file created ({file_size} bytes)")
                    self.test_results[f"test_{i}"] = {
                        "status": "SUCCESS",
                        "file": str(audio_file),
                        "size_bytes": file_size,
                        "text": phrase
                    }
                else:
                    print(f"   ❌ FAILED: No audio file generated")
                    self.test_results[f"test_{i}"] = {
                        "status": "FAILED", 
                        "text": phrase
                    }
                
                time.sleep(0.5)  # Brief pause between tests
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                self.test_results[f"test_{i}"] = {
                    "status": "ERROR",
                    "error": str(e),
                    "text": phrase
                }
        
        # REPORT RESULTS
        self._report_test_results()
    
    def speak_and_save(self, text: str, output_file: str) -> bool:
        """
        Generate Persian speech and save to file - REAL IMPLEMENTATION using gTTS
        Returns True only if file actually created
        """
        try:
            # Normalize Persian text for better pronunciation
            normalized_text = self._normalize_persian_text(text)
            print(f"   🔄 Processing: '{normalized_text}'")
            
            # Create gTTS object for Persian (using Arabic as closest supported language)
            tts = gTTS(text=normalized_text, lang='ar', slow=False)
            
            # Save to file
            tts.save(output_file)
            
            # Verify file was actually created
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return True
            else:
                print(f"   ⚠️ File not created or empty: {output_file}")
                return False
            
        except Exception as e:
            print(f"   ❌ Speech generation error: {e}")
            return False
    
    def speak_immediately(self, text: str) -> bool:
        """Speak text immediately by generating audio file (fallback for environments without audio)."""
        try:
            normalized_text = self._normalize_persian_text(text)
            print(f"🔊 Speaking: '{text}'")
            
            # In environments without audio output, generate file instead
            temp_file = self.output_dir / f"temp_speech_{int(time.time())}.mp3"
            
            # Create gTTS object for Persian (using Arabic as closest supported language)
            tts = gTTS(text=normalized_text, lang='ar', slow=False)
            tts.save(str(temp_file))
            
            # Verify file was created
            if temp_file.exists() and temp_file.stat().st_size > 0:
                print(f"   ✅ Audio generated: {temp_file.name} ({temp_file.stat().st_size} bytes)")
                
                # Try to play with pygame if available
                try:
                    if pygame.mixer.get_init():
                        pygame.mixer.music.load(str(temp_file))
                        pygame.mixer.music.play()
                        
                        # Wait for playback to finish
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                        print("   🔊 Audio played successfully")
                    else:
                        print("   ⚠️ Audio mixer not available, file generated instead")
                except Exception as play_error:
                    print(f"   ⚠️ Playback failed, but file generated: {play_error}")
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Immediate speech error: {e}")
            return False
    
    def _normalize_persian_text(self, text: str) -> str:
        """Optimize Persian text for better TTS pronunciation."""
        # Convert Persian digits to English for better pronunciation
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        english_digits = "0123456789"
        
        for p_digit, e_digit in zip(persian_digits, english_digits):
            text = text.replace(p_digit, e_digit)
        
        # Handle common Persian pronunciation issues for better TTS
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
    
    def _report_test_results(self):
        """Generate honest test report with actual results."""
        print("\n📊 PERSIAN TTS TEST RESULTS:")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() 
                             if result.get("status") == "SUCCESS")
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"📊 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result["status"] == "SUCCESS" else "❌"
            print(f"{status_emoji} {test_name}: {result['status']}")
            
            if result["status"] == "SUCCESS":
                print(f"   📁 File: {result['file']}")
                print(f"   📏 Size: {result['size_bytes']} bytes")
            elif result["status"] == "ERROR":
                print(f"   ⚠️ Error: {result['error']}")
        
        # List all generated files
        audio_files = list(self.output_dir.glob("*.mp3"))
        if audio_files:
            print(f"\n🎵 Generated Audio Files ({len(audio_files)} total):")
            for audio_file in sorted(audio_files):
                size = audio_file.stat().st_size
                print(f"   📁 {audio_file.name} ({size} bytes)")
        else:
            print("\n❌ No audio files were generated!")
        
        # Final verdict
        if successful_tests >= 3:
            print(f"\n🎉 STEP 1 STATUS: SUCCESS! Generated {successful_tests} working audio files")
            print("✅ Ready to proceed to Step 2 (Persian STT)")
        else:
            print(f"\n❌ STEP 1 STATUS: FAILED! Only {successful_tests} successful tests")
            print("🛑 Must fix TTS before proceeding to Step 2")

# IMMEDIATE EXECUTION AND TESTING
if __name__ == "__main__":
    print("🚀 STARTING PERSIAN TTS IMPLEMENTATION - STEP 1")
    print("=" * 60)
    tts_engine = PersianVoiceEngine()
    
    # Additional manual test
    print("\n🎯 MANUAL VERIFICATION TEST:")
    test_phrase = "این یک تست دستی از سیستم صوتی استیو است"
    manual_file = tts_engine.output_dir / "manual_verification.mp3"
    
    print(f"🔄 Testing phrase: '{test_phrase}'")
    success = tts_engine.speak_and_save(test_phrase, str(manual_file))
    
    if success:
        size = manual_file.stat().st_size if manual_file.exists() else 0
        print(f"✅ Manual verification successful: {manual_file} ({size} bytes)")
    else:
        print("❌ Manual verification failed")
    
    print("\n🏁 STEP 1 IMPLEMENTATION COMPLETE!")
    print("Check the /workspace/heystive_audio_output/ directory for generated audio files.")