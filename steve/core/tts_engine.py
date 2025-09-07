"""
Persian TTS Engine - Production Implementation
Real text-to-speech with multiple engine support and audio generation
"""

import asyncio
import logging
import tempfile
import os
import base64
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class PersianTTSEngine:
    """
    Production Persian Text-to-Speech Engine
    Supports multiple TTS engines with fallback mechanisms
    """
    
    def __init__(self, system_config: Dict[str, Any] = None):
        self.system_config = system_config or {}
        self.hardware_tier = self.system_config.get('hardware_tier', 'medium')
        
        # TTS engines
        self.engines = {}
        self.active_engine = None
        self.initialized = False
        
        # Audio configuration
        self.audio_config = {
            'sample_rate': 22050,
            'format': 'wav',
            'quality': 'high' if self.hardware_tier == 'high' else 'medium'
        }
        
        # Performance tracking
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'average_generation_time': 0.0,
            'engine_usage': {}
        }
    
    async def initialize(self) -> bool:
        """Initialize TTS engines in order of preference"""
        try:
            logger.info("🎤 Initializing Persian TTS engines...")
            
            # Try to initialize engines in order of preference
            initialization_order = [
                ('pyttsx3', self._init_pyttsx3_engine),
                ('gtts', self._init_gtts_engine),
                ('espeak', self._init_espeak_engine),
                ('fallback', self._init_fallback_engine)
            ]
            
            for engine_name, init_func in initialization_order:
                try:
                    logger.info(f"Trying to initialize {engine_name}...")
                    engine = await init_func()
                    
                    if engine:
                        self.engines[engine_name] = engine
                        if not self.active_engine:
                            self.active_engine = engine_name
                        logger.info(f"✅ {engine_name} engine initialized successfully")
                    else:
                        logger.warning(f"⚠️ {engine_name} engine initialization failed")
                        
                except Exception as e:
                    logger.warning(f"❌ {engine_name} engine error: {e}")
                    continue
            
            if self.engines:
                self.initialized = True
                logger.info(f"🎉 TTS initialization complete. Active engine: {self.active_engine}")
                
                # Test the active engine
                await self._test_active_engine()
                return True
            else:
                logger.error("❌ No TTS engines could be initialized")
                return False
                
        except Exception as e:
            logger.error(f"TTS initialization failed: {e}")
            return False
    
    async def _init_pyttsx3_engine(self) -> Optional[Dict[str, Any]]:
        """Initialize pyttsx3 TTS engine"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Configure for Persian if possible
            voices = engine.getProperty('voices')
            persian_voice = None
            
            # Look for Persian or Farsi voice
            for voice in voices:
                if any(lang in voice.id.lower() for lang in ['persian', 'farsi', 'fa', 'iran']):
                    persian_voice = voice
                    break
            
            if persian_voice:
                engine.setProperty('voice', persian_voice.id)
                logger.info(f"Found Persian voice: {persian_voice.name}")
            else:
                logger.warning("No Persian voice found, using default")
            
            # Configure speech properties
            engine.setProperty('rate', 150)  # Slower for Persian
            engine.setProperty('volume', 0.9)
            
            return {
                'engine': engine,
                'type': 'pyttsx3',
                'supports_persian': persian_voice is not None,
                'quality': 'high' if persian_voice else 'medium'
            }
            
        except ImportError:
            logger.warning("pyttsx3 not available. Install with: pip install pyttsx3")
            return None
        except Exception as e:
            logger.error(f"pyttsx3 initialization error: {e}")
            return None
    
    async def _init_gtts_engine(self) -> Optional[Dict[str, Any]]:
        """Initialize Google Text-to-Speech engine"""
        try:
            from gtts import gTTS
            import requests
            
            # Test internet connectivity
            try:
                requests.get('https://www.google.com', timeout=5)
                internet_available = True
            except:
                internet_available = False
                logger.warning("No internet connection for gTTS")
                return None
            
            if internet_available:
                # Test gTTS with Persian
                test_tts = gTTS(text="تست", lang='fa', slow=False)
                
                return {
                    'engine': gTTS,
                    'type': 'gtts',
                    'supports_persian': True,
                    'quality': 'high',
                    'requires_internet': True
                }
            else:
                return None
                
        except ImportError:
            logger.warning("gTTS not available. Install with: pip install gtts")
            return None
        except Exception as e:
            logger.error(f"gTTS initialization error: {e}")
            return None
    
    async def _init_espeak_engine(self) -> Optional[Dict[str, Any]]:
        """Initialize eSpeak TTS engine"""
        try:
            import subprocess
            
            # Check if espeak is available
            # TODO: Consider migrating to SecureSubprocess.safe_run() for enhanced security
            result = subprocess.run(['espeak', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return {
                    'engine': 'espeak',
                    'type': 'espeak',
                    'supports_persian': True,
                    'quality': 'medium'
                }
            else:
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("eSpeak not available. Install with: sudo apt-get install espeak")
            return None
        except Exception as e:
            logger.error(f"eSpeak initialization error: {e}")
            return None
    
    async def _init_fallback_engine(self) -> Optional[Dict[str, Any]]:
        """Initialize fallback TTS engine"""
        try:
            # Simple fallback that generates tone-based audio
            return {
                'engine': 'fallback',
                'type': 'fallback',
                'supports_persian': False,
                'quality': 'low'
            }
            
        except Exception as e:
            logger.error(f"Fallback engine error: {e}")
            return None
    
    async def _test_active_engine(self):
        """Test the active TTS engine"""
        try:
            test_text = "تست"
            logger.info(f"Testing active engine {self.active_engine} with text: '{test_text}'")
            
            result = await self.speak_text(test_text)
            
            if result and result.get('success'):
                logger.info("✅ TTS engine test successful")
            else:
                logger.warning("⚠️ TTS engine test failed")
                
        except Exception as e:
            logger.error(f"TTS engine test error: {e}")
    
    async def speak_text(self, text: str) -> Dict[str, Any]:
        """
        Convert text to speech and return audio data
        
        Args:
            text: Persian text to convert to speech
            
        Returns:
            Dictionary with success status and audio data
        """
        start_time = time.time()
        
        try:
            if not self.initialized or not self.active_engine:
                return {
                    'success': False,
                    'error': 'TTS engine not initialized'
                }
            
            self.stats['total_requests'] += 1
            logger.info(f"Generating speech for: '{text}' using {self.active_engine}")
            
            # Generate audio using active engine
            audio_result = await self._generate_audio(text)
            
            if audio_result['success']:
                # Update statistics
                generation_time = time.time() - start_time
                self._update_stats(generation_time, True)
                
                logger.info(f"✅ TTS generation successful in {generation_time:.2f}s")
                return audio_result
            else:
                # Try fallback engines
                logger.warning(f"Primary engine {self.active_engine} failed, trying fallbacks...")
                return await self._try_fallback_engines(text)
                
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            self._update_stats(0, False)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_audio(self, text: str) -> Dict[str, Any]:
        """Generate audio using the active engine"""
        try:
            engine_info = self.engines[self.active_engine]
            engine_type = engine_info['type']
            
            if engine_type == 'pyttsx3':
                return await self._generate_pyttsx3_audio(text, engine_info)
            elif engine_type == 'gtts':
                return await self._generate_gtts_audio(text, engine_info)
            elif engine_type == 'espeak':
                return await self._generate_espeak_audio(text, engine_info)
            elif engine_type == 'fallback':
                return await self._generate_fallback_audio(text, engine_info)
            else:
                return {
                    'success': False,
                    'error': f'Unknown engine type: {engine_type}'
                }
                
        except Exception as e:
            logger.error(f"Audio generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_pyttsx3_audio(self, text: str, engine_info: Dict) -> Dict[str, Any]:
        """Generate audio using pyttsx3"""
        try:
            import pyttsx3
            
            engine = engine_info['engine']
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Generate speech to file
            def generate_speech():
                try:
                    engine.save_to_file(text, temp_path)
                    engine.runAndWait()
                except Exception as e:
                    logger.error(f"pyttsx3 generation error: {e}")
                    raise
            
            # Run in thread to avoid blocking
            await asyncio.to_thread(generate_speech)
            
            # Check if file was created
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                return {
                    'success': False,
                    'error': 'pyttsx3 failed to generate audio file'
                }
            
            # Read and encode audio file
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                # NEW: Add logging to silent failure but keep same behavior
                logger.debug(f"Temp file cleanup failed (non-critical): {e}")
                pass
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                'success': True,
                'audio_data': audio_base64,
                'format': 'wav',
                'engine': 'pyttsx3',
                'duration': len(audio_data) / (self.audio_config['sample_rate'] * 2),  # Rough estimate
                'size_bytes': len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"pyttsx3 audio generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_gtts_audio(self, text: str, engine_info: Dict) -> Dict[str, Any]:
        """Generate audio using Google TTS"""
        try:
            from gtts import gTTS
            
            # Create gTTS object for Persian
            tts = gTTS(text=text, lang='fa', slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Generate audio file
            await asyncio.to_thread(tts.save, temp_path)
            
            # Check if file was created
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                return {
                    'success': False,
                    'error': 'gTTS failed to generate audio file'
                }
            
            # Read and encode audio file
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                # NEW: Add logging to silent failure but keep same behavior
                logger.debug(f"Temp file cleanup failed (non-critical): {e}")
                pass
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                'success': True,
                'audio_data': audio_base64,
                'format': 'mp3',
                'engine': 'gtts',
                'duration': len(text) * 0.1,  # Rough estimate
                'size_bytes': len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"gTTS audio generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_espeak_audio(self, text: str, engine_info: Dict) -> Dict[str, Any]:
        """Generate audio using eSpeak"""
        try:
            import subprocess
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Generate speech using eSpeak command
            cmd = [
                'espeak',
                '-v', 'fa',  # Persian voice
                '-s', '150',  # Speed
                '-w', temp_path,  # Output file
                text
            ]
            
            # TODO: Consider migrating to SecureSubprocess.safe_run_async() for enhanced security
            result = await asyncio.to_thread(
                subprocess.run, cmd, capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'eSpeak failed: {result.stderr}'
                }
            
            # Check if file was created
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                return {
                    'success': False,
                    'error': 'eSpeak failed to generate audio file'
                }
            
            # Read and encode audio file
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                # NEW: Add logging to silent failure but keep same behavior
                logger.debug(f"Temp file cleanup failed (non-critical): {e}")
                pass
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                'success': True,
                'audio_data': audio_base64,
                'format': 'wav',
                'engine': 'espeak',
                'duration': len(text) * 0.08,  # Rough estimate
                'size_bytes': len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"eSpeak audio generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_fallback_audio(self, text: str, engine_info: Dict) -> Dict[str, Any]:
        """Generate fallback audio (simple tone pattern)"""
        try:
            import numpy as np
            import wave
            
            # Generate simple tone pattern based on text
            duration = max(1.0, len(text) * 0.1)  # Minimum 1 second
            sample_rate = 22050
            samples = int(duration * sample_rate)
            
            # Generate tone pattern
            t = np.linspace(0, duration, samples)
            
            # Create multiple tones for more natural sound
            frequency_base = 200 + (hash(text) % 100)  # Vary frequency based on text
            
            audio_signal = (
                0.3 * np.sin(2 * np.pi * frequency_base * t) +
                0.2 * np.sin(2 * np.pi * frequency_base * 1.5 * t) +
                0.1 * np.sin(2 * np.pi * frequency_base * 2 * t)
            )
            
            # Add envelope for natural sound
            envelope = np.ones(samples)
            fade_samples = int(0.1 * sample_rate)
            envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
            envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
            
            audio_signal *= envelope
            
            # Convert to 16-bit PCM
            audio_16bit = (audio_signal * 32767).astype(np.int16)
            
            # Create WAV file in memory
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Write WAV file
            with wave.open(temp_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_16bit.tobytes())
            
            # Read and encode audio file
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                # NEW: Add logging to silent failure but keep same behavior
                logger.debug(f"Temp file cleanup failed (non-critical): {e}")
                pass
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                'success': True,
                'audio_data': audio_base64,
                'format': 'wav',
                'engine': 'fallback',
                'duration': duration,
                'size_bytes': len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"Fallback audio generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _try_fallback_engines(self, text: str) -> Dict[str, Any]:
        """Try fallback engines when primary fails"""
        try:
            # Try other available engines
            for engine_name, engine_info in self.engines.items():
                if engine_name != self.active_engine:
                    logger.info(f"Trying fallback engine: {engine_name}")
                    
                    # Temporarily switch to this engine
                    original_engine = self.active_engine
                    self.active_engine = engine_name
                    
                    result = await self._generate_audio(text)
                    
                    if result['success']:
                        logger.info(f"✅ Fallback engine {engine_name} succeeded")
                        return result
                    else:
                        # Restore original engine
                        self.active_engine = original_engine
            
            # All engines failed
            return {
                'success': False,
                'error': 'All TTS engines failed'
            }
            
        except Exception as e:
            logger.error(f"Fallback engine attempt failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_stats(self, generation_time: float, success: bool):
        """Update TTS performance statistics"""
        if success:
            self.stats['successful_requests'] += 1
            
            # Update average generation time
            total_successful = self.stats['successful_requests']
            current_avg = self.stats['average_generation_time']
            self.stats['average_generation_time'] = (
                (current_avg * (total_successful - 1) + generation_time) / total_successful
            )
        
        # Update engine usage stats
        if self.active_engine:
            if self.active_engine in self.stats['engine_usage']:
                self.stats['engine_usage'][self.active_engine] += 1
            else:
                self.stats['engine_usage'][self.active_engine] = 1
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get current engine status and statistics"""
        return {
            'initialized': self.initialized,
            'active_engine': self.active_engine,
            'available_engines': list(self.engines.keys()),
            'hardware_tier': self.hardware_tier,
            'audio_config': self.audio_config,
            'stats': self.stats,
            'engine_details': {
                name: {
                    'type': info['type'],
                    'supports_persian': info['supports_persian'],
                    'quality': info['quality']
                }
                for name, info in self.engines.items()
            }
        }
    
    async def switch_engine(self, engine_name: str) -> bool:
        """Switch to a different TTS engine"""
        try:
            if engine_name in self.engines:
                self.active_engine = engine_name
                logger.info(f"Switched to TTS engine: {engine_name}")
                return True
            else:
                logger.error(f"Engine {engine_name} not available")
                return False
                
        except Exception as e:
            logger.error(f"Engine switch failed: {e}")
            return False
    
    async def cleanup(self):
        """Clean up TTS engine resources"""
        try:
            # Clean up pyttsx3 engines
            for engine_name, engine_info in self.engines.items():
                if engine_info['type'] == 'pyttsx3':
                    try:
                        engine_info['engine'].stop()
                    except Exception as e:
                        # NEW: Add logging to silent failure but keep same behavior
                        logger.debug(f"Engine stop failed (non-critical): {e}")
                        pass
            
            self.engines.clear()
            self.active_engine = None
            self.initialized = False
            
            logger.info("TTS engine cleanup completed")
            
        except Exception as e:
            logger.error(f"TTS cleanup error: {e}")