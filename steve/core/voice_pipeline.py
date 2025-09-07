"""
Steve Voice Assistant - Main Voice Pipeline
Integrates wake word detection, STT, TTS, and conversation management
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable
import numpy as np

from .wake_word_detector import PersianWakeWordDetector
from .persian_stt import AdaptivePersianSTT
from .persian_tts import ElitePersianTTS

logger = logging.getLogger(__name__)

class SteveVoiceAssistant:
    """
    Complete Persian Voice Assistant "استیو" (Steve)
    Integrates all voice processing components
    """
    
    def __init__(self, hardware_config: Dict[str, Any]):
        self.hardware_config = hardware_config
        
        # Core components
        self.wake_detector = None
        self.stt_engine = None
        self.tts_engine = None
        
        # System state
        self.is_initialized = False
        self.is_listening = False
        self.conversation_active = False
        
        # Performance tracking
        self.performance_stats = {
            "wake_word_detections": 0,
            "successful_conversations": 0,
            "total_latency": 0.0,
            "average_response_time": 0.0
        }
        
        # Configuration
        self.config = {
            "wake_word_response": "بله سرورم",
            "greeting": "سلام! من استیو هستم و آماده کمک به شما می‌باشم.",
            "error_message": "متاسفم، متوجه نشدم. لطفاً دوباره بگویید.",
            "max_conversation_duration": 30.0,  # seconds
            "silence_timeout": 5.0  # seconds
        }
        
    async def initialize(self) -> bool:
        """Initialize all voice assistant components"""
        try:
            logger.info("🚀 Initializing Steve Voice Assistant...")
            
            # Initialize wake word detector
            logger.info("Initializing wake word detector...")
            self.wake_detector = PersianWakeWordDetector(self.hardware_config)
            wake_success = await self.wake_detector.initialize()
            if not wake_success:
                raise Exception("Wake word detector initialization failed")
            
            # Set wake word callback
            self.wake_detector.set_wake_callback(self._on_wake_word_detected)
            
            # Initialize STT engine
            logger.info("Initializing Persian STT engine...")
            self.stt_engine = AdaptivePersianSTT(self.hardware_config)
            stt_success = await self.stt_engine.initialize()
            if not stt_success:
                raise Exception("STT engine initialization failed")
            
            # Initialize TTS engine
            logger.info("Initializing Persian TTS engine...")
            self.tts_engine = ElitePersianTTS(self.hardware_config)
            tts_success = await self.tts_engine.initialize()
            if not tts_success:
                raise Exception("TTS engine initialization failed")
            
            # Test all components
            await self._test_components()
            
            self.is_initialized = True
            logger.info("✅ Steve Voice Assistant initialized successfully!")
            
            # Play greeting
            await self.tts_engine.speak_immediately(self.config["greeting"])
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Steve initialization failed: {e}")
            await self.cleanup()
            return False
    
    async def _test_components(self):
        """Test all components to ensure they're working"""
        try:
            logger.info("Testing voice components...")
            
            # Test TTS with a simple phrase
            test_phrase = "تست سیستم"
            logger.info(f"Testing TTS with: {test_phrase}")
            await self.tts_engine.speak_immediately(test_phrase)
            
            # Test wake word detector
            logger.info("Testing wake word detector...")
            stats = self.wake_detector.get_detection_stats()
            logger.info(f"Wake word detector stats: {stats}")
            
            # Test STT engine
            logger.info("Testing STT engine...")
            stt_stats = self.stt_engine.get_performance_stats()
            logger.info(f"STT engine stats: {stt_stats}")
            
            logger.info("✅ All components tested successfully!")
            
        except Exception as e:
            logger.error(f"Component testing failed: {e}")
            raise
    
    async def start_listening(self):
        """Start the main voice assistant loop"""
        if not self.is_initialized:
            raise Exception("Steve not initialized. Call initialize() first.")
        
        try:
            logger.info("🎤 Starting Steve voice assistant...")
            self.is_listening = True
            
            # Start wake word detection
            await self.wake_detector.start_listening()
            
        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            self.is_listening = False
            raise
    
    async def _on_wake_word_detected(self):
        """Handle wake word detection"""
        try:
            logger.info("🔔 Wake word detected: 'هی استیو'")
            self.performance_stats["wake_word_detections"] += 1
            
            # Respond immediately
            await self.tts_engine.speak_immediately(self.config["wake_word_response"])
            
            # Start conversation
            await self._handle_conversation()
            
        except Exception as e:
            logger.error(f"Wake word handling failed: {e}")
            await self.tts_engine.speak_immediately(self.config["error_message"])
    
    async def _handle_conversation(self):
        """Handle a complete conversation turn"""
        try:
            logger.info("💬 Starting conversation...")
            self.conversation_active = True
            conversation_start = time.time()
            
            # Capture user speech
            logger.info("🎤 Listening for user speech...")
            audio_data = await self.stt_engine.capture_speech(duration=5.0)
            
            # Transcribe speech
            logger.info("📝 Transcribing speech...")
            transcription_result = await self.stt_engine.transcribe_persian_audio(audio_data)
            
            if transcription_result["confidence"] < 0.5:
                logger.warning(f"Low confidence transcription: {transcription_result['confidence']}")
                await self.tts_engine.speak_immediately("متاسفم، صدای شما را واضح نشنیدم.")
                return
            
            user_text = transcription_result["text"]
            logger.info(f"User said: '{user_text}'")
            
            # Generate response (simplified for Phase 1)
            response = await self._generate_response(user_text)
            
            # Speak response
            logger.info(f"Steve responding: '{response}'")
            await self.tts_engine.synthesize_premium_persian(response)
            
            # Update performance stats
            conversation_duration = time.time() - conversation_start
            self._update_performance_stats(conversation_duration, True)
            
            logger.info("✅ Conversation completed successfully")
            
        except Exception as e:
            logger.error(f"Conversation handling failed: {e}")
            await self.tts_engine.speak_immediately(self.config["error_message"])
            self._update_performance_stats(0, False)
        
        finally:
            self.conversation_active = False
    
    async def _generate_response(self, user_input: str) -> str:
        """Generate response to user input (simplified for Phase 1)"""
        try:
            # Simple response generation for Phase 1
            # This will be enhanced in Phase 2 with LLM integration
            
            user_input_lower = user_input.lower()
            
            # Greeting responses
            if any(word in user_input_lower for word in ["سلام", "درود", "صبح بخیر", "عصر بخیر"]):
                return "سلام! چطور می‌تونم کمکتون کنم؟"
            
            # Help responses
            elif any(word in user_input_lower for word in ["کمک", "راهنما", "چطور"]):
                return "من استیو هستم، دستیار صوتی شما. می‌تونم به شما کمک کنم."
            
            # Status responses
            elif any(word in user_input_lower for word in ["حال", "چطور", "خوب"]):
                return "من خوبم، ممنون! شما چطورید؟"
            
            # Time responses
            elif any(word in user_input_lower for word in ["ساعت", "زمان", "وقت"]):
                import datetime
                now = datetime.datetime.now()
                time_str = now.strftime("%H:%M")
                return f"الان ساعت {time_str} است."
            
            # Default response
            else:
                return f"متوجه شدم که گفتید '{user_input}'. در حال حاضر در حال یادگیری هستم."
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return self.config["error_message"]
    
    def _update_performance_stats(self, conversation_duration: float, success: bool):
        """Update performance statistics"""
        try:
            if success:
                self.performance_stats["successful_conversations"] += 1
            
            # Update average response time
            total_conversations = self.performance_stats["successful_conversations"]
            if total_conversations > 0:
                current_avg = self.performance_stats["average_response_time"]
                self.performance_stats["average_response_time"] = (
                    (current_avg * (total_conversations - 1) + conversation_duration) / total_conversations
                )
            
        except Exception as e:
            logger.error(f"Performance stats update failed: {e}")
    
    async def stop_listening(self):
        """Stop the voice assistant"""
        try:
            logger.info("🛑 Stopping Steve voice assistant...")
            self.is_listening = False
            
            if self.wake_detector:
                await self.wake_detector.stop_listening()
            
            logger.info("✅ Steve stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop Steve: {e}")
    
    async def shutdown(self):
        """Complete shutdown of Steve voice assistant"""
        try:
            logger.info("🔌 Shutting down Steve voice assistant...")
            
            # Stop listening
            await self.stop_listening()
            
            # Cleanup components
            await self.cleanup()
            
            logger.info("✅ Steve shutdown completed")
            
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
    
    async def cleanup(self):
        """Clean up all resources"""
        try:
            logger.info("🧹 Cleaning up resources...")
            
            if self.wake_detector:
                await self.wake_detector.stop_listening()
                self.wake_detector = None
            
            if self.stt_engine:
                await self.stt_engine.cleanup()
                self.stt_engine = None
            
            if self.tts_engine:
                await self.tts_engine.cleanup()
                self.tts_engine = None
            
            self.is_initialized = False
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of Steve voice assistant"""
        return {
            "is_initialized": self.is_initialized,
            "is_listening": self.is_listening,
            "conversation_active": self.conversation_active,
            "hardware_config": self.hardware_config,
            "performance_stats": self.performance_stats,
            "config": self.config
        }
    
    def get_performance_report(self) -> str:
        """Get human-readable performance report"""
        try:
            stats = self.performance_stats
            
            report = f"""
Steve Voice Assistant Performance Report:
========================================
- Wake Word Detections: {stats['wake_word_detections']}
- Successful Conversations: {stats['successful_conversations']}
- Average Response Time: {stats['average_response_time']:.2f} seconds
- Success Rate: {(stats['successful_conversations'] / max(1, stats['wake_word_detections'])) * 100:.1f}%

Hardware Configuration:
- Tier: {self.hardware_config.get('hardware_tier', 'unknown')}
- RAM: {self.hardware_config.get('ram_gb', 0)} GB
- CPU Cores: {self.hardware_config.get('cpu_cores', 0)}
- GPU Available: {self.hardware_config.get('gpu_available', False)}
"""
            return report.strip()
            
        except Exception as e:
            logger.error(f"Performance report generation failed: {e}")
            return "Performance report unavailable"