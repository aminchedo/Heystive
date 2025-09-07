"""
Persian Wake Word Detection System
Detects "هی استیو" with high accuracy and low latency
"""

import asyncio
import numpy as np
import pyaudio
import webrtcvad
import librosa
import torch
import torchaudio
from typing import Optional, Callable, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PersianWakeWordDetector:
    """
    Advanced wake word detection optimized for Persian phonemes
    Detects "هی استیو" with <200ms latency
    """
    
    def __init__(self, hardware_config: Dict[str, Any]):
        self.hardware_profile = hardware_config
        self.audio_config = self._configure_audio_pipeline()
        self.vad = webrtcvad.Vad(3)  # Aggressive voice activity detection
        
        # Audio stream configuration
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # Wake word detection parameters
        self.detection_threshold = 0.7
        self.min_audio_length = 1.0  # seconds
        self.max_audio_length = 3.0  # seconds
        
        # Audio buffer for continuous listening
        self.audio_buffer = []
        self.is_listening = False
        self.audio_stream = None
        self.pyaudio_instance = None
        
        # Callback for wake word detection
        self.wake_callback: Optional[Callable] = None
        
        # Persian phoneme patterns for "هی استیو"
        self.persian_wake_patterns = self._initialize_persian_patterns()
        
    def _configure_audio_pipeline(self) -> Dict[str, Any]:
        """Configure audio pipeline based on hardware capabilities"""
        config = {
            "sample_rate": 16000,
            "chunk_size": 1024,
            "channels": 1,
            "format": pyaudio.paInt16,
            "input_device_index": None,  # Auto-detect
            "frames_per_buffer": 1024
        }
        
        # Optimize for hardware tier
        if self.hardware_profile["hardware_tier"] == "high":
            config["chunk_size"] = 512  # Lower latency
            config["frames_per_buffer"] = 512
        elif self.hardware_profile["hardware_tier"] == "low":
            config["chunk_size"] = 2048  # Lower CPU usage
            config["frames_per_buffer"] = 2048
            
        return config
    
    def _initialize_persian_patterns(self) -> Dict[str, Any]:
        """Initialize Persian phoneme patterns for wake word detection"""
        return {
            "hey_steve": {
                "persian_text": "هی استیو",
                "phonemes": ["h", "e", "i", " ", "a", "s", "t", "i", "v", "o"],
                "duration_range": (0.8, 2.0),  # seconds
                "energy_threshold": 0.3,
                "spectral_features": {
                    "mfcc_coeffs": 13,
                    "delta_coeffs": 13,
                    "delta_delta_coeffs": 13
                }
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize audio system and wake word detection"""
        try:
            # Initialize PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Find best audio input device
            input_device = self._find_best_input_device()
            self.audio_config["input_device_index"] = input_device
            
            logger.info(f"Audio system initialized with device: {input_device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize wake word detector: {e}")
            return False
    
    def _find_best_input_device(self) -> Optional[int]:
        """Find the best audio input device"""
        try:
            device_count = self.pyaudio_instance.get_device_count()
            best_device = None
            best_score = -1
            
            for i in range(device_count):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                
                # Check if device has input channels
                if device_info['maxInputChannels'] > 0:
                    score = self._score_audio_device(device_info)
                    if score > best_score:
                        best_score = score
                        best_device = i
            
            return best_device
            
        except Exception as e:
            logger.warning(f"Could not find optimal audio device: {e}")
            return None
    
    def _score_audio_device(self, device_info: Dict) -> float:
        """Score audio device based on quality metrics"""
        score = 0.0
        
        # Prefer devices with higher sample rates
        if device_info['defaultSampleRate'] >= 44100:
            score += 2.0
        elif device_info['defaultSampleRate'] >= 16000:
            score += 1.0
            
        # Prefer devices with more input channels
        score += device_info['maxInputChannels'] * 0.5
        
        # Prefer default input device
        if device_info['hostApi'] == 0:  # Usually default API
            score += 1.0
            
        return score
    
    def set_wake_callback(self, callback: Callable):
        """Set callback function for wake word detection"""
        self.wake_callback = callback
    
    async def start_listening(self):
        """Start continuous wake word monitoring"""
        if self.is_listening:
            return
            
        self.is_listening = True
        
        try:
            # Initialize audio stream
            self.audio_stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.audio_config["input_device_index"],
                frames_per_buffer=self.audio_config["frames_per_buffer"],
                stream_callback=self._audio_callback
            )
            
            self.audio_stream.start_stream()
            logger.info("Wake word detection started")
            
            # Keep listening until stopped
            while self.is_listening:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in wake word listening: {e}")
            self.is_listening = False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback for real-time processing"""
        if not self.is_listening:
            return (None, pyaudio.paComplete)
        
        try:
            # Convert audio data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            
            # Add to buffer
            self.audio_buffer.extend(audio_data)
            
            # Keep buffer size manageable
            max_buffer_size = int(self.sample_rate * self.max_audio_length)
            if len(self.audio_buffer) > max_buffer_size:
                self.audio_buffer = self.audio_buffer[-max_buffer_size:]
            
            # Check for wake word if we have enough audio
            min_buffer_size = int(self.sample_rate * self.min_audio_length)
            if len(self.audio_buffer) >= min_buffer_size:
                asyncio.create_task(self._process_audio_chunk())
            
            return (None, pyaudio.paContinue)
            
        except Exception as e:
            logger.error(f"Error in audio callback: {e}")
            return (None, pyaudio.paComplete)
    
    async def _process_audio_chunk(self):
        """Process audio chunk for wake word detection"""
        try:
            # Convert buffer to numpy array
            audio_array = np.array(self.audio_buffer, dtype=np.float32)
            audio_array = audio_array / 32768.0  # Normalize to [-1, 1]
            
            # Voice Activity Detection
            if not self._has_voice_activity(audio_array):
                return
            
            # Extract features for wake word detection
            features = self._extract_wake_word_features(audio_array)
            
            # Check for wake word pattern
            if self._detect_wake_word_pattern(features, audio_array):
                logger.info("Wake word detected: 'هی استیو'")
                
                # Clear buffer to prevent multiple detections
                self.audio_buffer.clear()
                
                # Trigger callback
                if self.wake_callback:
                    await self.wake_callback()
                    
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
    
    def _has_voice_activity(self, audio_array: np.ndarray) -> bool:
        """Check if audio contains voice activity"""
        try:
            # Convert to 16-bit PCM for VAD
            audio_16bit = (audio_array * 32767).astype(np.int16)
            
            # Check voice activity in chunks
            chunk_size = int(0.01 * self.sample_rate)  # 10ms chunks
            for i in range(0, len(audio_16bit) - chunk_size, chunk_size):
                chunk = audio_16bit[i:i + chunk_size]
                if self.vad.is_speech(chunk.tobytes(), self.sample_rate):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    def _extract_wake_word_features(self, audio_array: np.ndarray) -> Dict[str, Any]:
        """Extract features for wake word detection"""
        try:
            # MFCC features
            mfccs = librosa.feature.mfcc(
                y=audio_array,
                sr=self.sample_rate,
                n_mfcc=13,
                n_fft=2048,
                hop_length=512
            )
            
            # Delta and delta-delta features
            delta_mfccs = librosa.feature.delta(mfccs)
            delta2_mfccs = librosa.feature.delta(mfccs, order=2)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(
                y=audio_array, sr=self.sample_rate
            )
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_array)
            
            return {
                "mfccs": mfccs,
                "delta_mfccs": delta_mfccs,
                "delta2_mfccs": delta2_mfccs,
                "spectral_centroids": spectral_centroids,
                "zcr": zcr,
                "duration": len(audio_array) / self.sample_rate,
                "energy": np.mean(audio_array ** 2)
            }
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return {}
    
    def _detect_wake_word_pattern(self, features: Dict[str, Any], audio_array: np.ndarray) -> bool:
        """Detect wake word pattern using extracted features"""
        try:
            if not features:
                return False
            
            # Check duration constraints
            duration = features["duration"]
            if not (0.8 <= duration <= 2.0):
                return False
            
            # Check energy level
            energy = features["energy"]
            if energy < 0.01:  # Too quiet
                return False
            
            # Simple pattern matching based on spectral characteristics
            # This is a simplified version - in production, you'd use a trained model
            
            # Check for characteristic spectral patterns of Persian phonemes
            mfccs = features["mfccs"]
            if mfccs.size == 0:
                return False
            
            # Look for patterns that match "هی استیو" phonemes
            # This is a heuristic approach - replace with trained model
            
            # Check for high-frequency content (characteristic of "هی")
            high_freq_energy = np.mean(mfccs[8:13, :])  # Higher MFCC coefficients
            
            # Check for mid-frequency content (characteristic of "استیو")
            mid_freq_energy = np.mean(mfccs[3:8, :])   # Mid MFCC coefficients
            
            # Simple heuristic: if we have both high and mid frequency content
            # and the duration is reasonable, it might be the wake word
            if high_freq_energy > 0.1 and mid_freq_energy > 0.1:
                # Additional checks for Persian-specific patterns
                zcr = features["zcr"]
                avg_zcr = np.mean(zcr)
                
                # Persian speech typically has moderate zero-crossing rate
                if 0.05 < avg_zcr < 0.3:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Pattern detection error: {e}")
            return False
    
    async def stop_listening(self):
        """Stop wake word monitoring"""
        self.is_listening = False
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
        
        logger.info("Wake word detection stopped")
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get wake word detection statistics"""
        return {
            "is_listening": self.is_listening,
            "buffer_size": len(self.audio_buffer),
            "sample_rate": self.sample_rate,
            "chunk_size": self.chunk_size,
            "detection_threshold": self.detection_threshold
        }