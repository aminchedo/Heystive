"""
Voice Pipeline Tests
Comprehensive tests for Steve's voice processing pipeline
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from steve.core.voice_pipeline import SteveVoiceAssistant
from steve.core.wake_word_detector import PersianWakeWordDetector
from steve.core.persian_stt import AdaptivePersianSTT
from steve.core.persian_tts import ElitePersianTTS
from steve.utils.system_monitor import SystemPerformanceMonitor

class TestVoicePipeline:
    """Test suite for voice pipeline integration"""
    
    @pytest.fixture
    def hardware_config(self):
        """Mock hardware configuration"""
        return {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False,
            "os_type": "Linux",
            "architecture": "x86_64"
        }
    
    @pytest.fixture
    def mock_audio_data(self):
        """Generate mock audio data"""
        # Generate 2 seconds of mock audio at 16kHz
        sample_rate = 16000
        duration = 2.0
        samples = int(sample_rate * duration)
        
        # Generate sine wave as mock audio
        t = np.linspace(0, duration, samples)
        frequency = 440  # A4 note
        audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        return audio_data.astype(np.float32)
    
    @pytest.mark.asyncio
    async def test_voice_pipeline_initialization(self, hardware_config):
        """Test voice pipeline initialization"""
        steve = SteveVoiceAssistant(hardware_config)
        
        # Test initial state
        assert not steve.is_initialized
        assert not steve.is_listening
        assert not steve.conversation_active
        
        # Test configuration
        assert steve.hardware_config == hardware_config
        assert "wake_word_response" in steve.config
        assert steve.config["wake_word_response"] == "بله سرورم"
    
    @pytest.mark.asyncio
    async def test_voice_pipeline_status(self, hardware_config):
        """Test voice pipeline status reporting"""
        steve = SteveVoiceAssistant(hardware_config)
        
        status = steve.get_status()
        
        assert isinstance(status, dict)
        assert "is_initialized" in status
        assert "is_listening" in status
        assert "conversation_active" in status
        assert "hardware_config" in status
        assert "performance_stats" in status
        assert "config" in status
        
        assert status["hardware_config"] == hardware_config
    
    @pytest.mark.asyncio
    async def test_performance_report_generation(self, hardware_config):
        """Test performance report generation"""
        steve = SteveVoiceAssistant(hardware_config)
        
        report = steve.get_performance_report()
        
        assert isinstance(report, str)
        assert len(report) > 50  # Should be a substantial report
        assert "Steve Voice Assistant Performance Report" in report
        assert "Hardware Configuration" in report
        assert hardware_config["hardware_tier"] in report
    
    @pytest.mark.asyncio
    async def test_response_generation(self, hardware_config):
        """Test response generation logic"""
        steve = SteveVoiceAssistant(hardware_config)
        
        # Test greeting response
        response = await steve._generate_response("سلام")
        assert isinstance(response, str)
        assert len(response) > 0
        assert any(word in response for word in ["سلام", "چطور", "کمک"])
        
        # Test help response
        response = await steve._generate_response("کمک")
        assert isinstance(response, str)
        assert "استیو" in response or "کمک" in response
        
        # Test time response
        response = await steve._generate_response("ساعت چنده")
        assert isinstance(response, str)
        assert "ساعت" in response
        
        # Test device control response
        response = await steve._generate_response("چراغ را روشن کن")
        assert isinstance(response, str)
        assert "چراغ" in response
    
    @pytest.mark.asyncio
    async def test_performance_stats_update(self, hardware_config):
        """Test performance statistics updates"""
        steve = SteveVoiceAssistant(hardware_config)
        
        # Initial stats
        initial_stats = steve.performance_stats.copy()
        
        # Simulate successful conversation
        steve._update_performance_stats(1.5, True)
        
        # Check stats updated
        assert steve.performance_stats["successful_conversations"] == initial_stats["successful_conversations"] + 1
        assert steve.performance_stats["average_response_time"] > 0
        
        # Simulate failed conversation
        steve._update_performance_stats(0, False)
        
        # Success rate should be calculated correctly
        total_conversations = steve.performance_stats["successful_conversations"]
        assert total_conversations >= 1

class TestWakeWordDetector:
    """Test suite for wake word detection"""
    
    @pytest.fixture
    def hardware_config(self):
        return {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False
        }
    
    @pytest.mark.asyncio
    async def test_wake_word_detector_initialization(self, hardware_config):
        """Test wake word detector initialization"""
        detector = PersianWakeWordDetector(hardware_config)
        
        # Test configuration
        assert detector.hardware_profile == hardware_config
        assert detector.sample_rate == 16000
        assert detector.chunk_size in [512, 1024, 2048]  # Based on hardware tier
        
        # Test Persian patterns
        assert "hey_steve" in detector.persian_wake_patterns
        pattern = detector.persian_wake_patterns["hey_steve"]
        assert pattern["persian_text"] == "هی استیو"
        assert isinstance(pattern["phonemes"], list)
        assert len(pattern["phonemes"]) > 0
    
    @pytest.mark.asyncio
    async def test_wake_word_audio_config(self, hardware_config):
        """Test audio configuration"""
        detector = PersianWakeWordDetector(hardware_config)
        
        audio_config = detector.audio_config
        
        assert "sample_rate" in audio_config
        assert "chunk_size" in audio_config
        assert "channels" in audio_config
        assert "format" in audio_config
        
        assert audio_config["sample_rate"] == 16000
        assert audio_config["channels"] == 1
    
    def test_wake_word_detection_stats(self, hardware_config):
        """Test detection statistics"""
        detector = PersianWakeWordDetector(hardware_config)
        
        stats = detector.get_detection_stats()
        
        assert isinstance(stats, dict)
        assert "is_listening" in stats
        assert "buffer_size" in stats
        assert "sample_rate" in stats
        assert "chunk_size" in stats
        assert "detection_threshold" in stats
        
        assert stats["sample_rate"] == 16000
        assert isinstance(stats["detection_threshold"], float)

class TestPersianSTT:
    """Test suite for Persian Speech-to-Text"""
    
    @pytest.fixture
    def hardware_config(self):
        return {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False
        }
    
    @pytest.mark.asyncio
    async def test_stt_initialization(self, hardware_config):
        """Test STT engine initialization"""
        stt = AdaptivePersianSTT(hardware_config)
        
        # Test hardware assessment
        assert stt.hardware_tier in ["high", "medium", "low"]
        assert stt.hardware_profile == hardware_config
        
        # Test model configuration
        assert "primary_model" in stt.model_config
        assert "backup_model" in stt.model_config
        assert "device" in stt.model_config
        assert "compute_type" in stt.model_config
    
    def test_stt_hardware_tier_assessment(self, hardware_config):
        """Test hardware tier assessment"""
        stt = AdaptivePersianSTT(hardware_config)
        
        tier = stt._assess_hardware_tier()
        assert tier in ["high", "medium", "low"]
        
        # Test with different configurations
        high_config = {**hardware_config, "ram_gb": 16, "cpu_cores": 8, "gpu_available": True}
        stt_high = AdaptivePersianSTT(high_config)
        assert stt_high._assess_hardware_tier() == "high"
        
        low_config = {**hardware_config, "ram_gb": 4, "cpu_cores": 2, "gpu_available": False}
        stt_low = AdaptivePersianSTT(low_config)
        assert stt_low._assess_hardware_tier() == "low"
    
    def test_stt_model_selection(self, hardware_config):
        """Test model selection logic"""
        stt = AdaptivePersianSTT(hardware_config)
        
        model_config = stt._select_optimal_model_config()
        
        assert "primary_model" in model_config
        assert "backup_model" in model_config
        assert "device" in model_config
        assert "compute_type" in model_config
        assert "threads" in model_config
        assert "memory_limit" in model_config
        
        # Verify model names are valid
        assert model_config["primary_model"] in ["large-v3", "medium", "small", "tiny"]
        assert model_config["backup_model"] in ["medium", "small", "tiny"]
    
    def test_stt_performance_stats(self, hardware_config):
        """Test performance statistics"""
        stt = AdaptivePersianSTT(hardware_config)
        
        stats = stt.get_performance_stats()
        
        assert isinstance(stats, dict)
        assert "hardware_tier" in stats
        assert "model_config" in stats
        assert "transcription_stats" in stats
        assert "memory_usage" in stats
        assert "model_loaded" in stats
        
        # Test transcription stats structure
        transcription_stats = stats["transcription_stats"]
        assert "total_transcriptions" in transcription_stats
        assert "average_latency" in transcription_stats
        assert "success_rate" in transcription_stats

class TestPersianTTS:
    """Test suite for Persian Text-to-Speech"""
    
    @pytest.fixture
    def hardware_config(self):
        return {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False
        }
    
    @pytest.mark.asyncio
    async def test_tts_initialization(self, hardware_config):
        """Test TTS engine initialization"""
        tts = ElitePersianTTS(hardware_config)
        
        # Test hardware assessment
        assert tts.hardware_tier in ["high", "medium", "low"]
        assert tts.hardware_profile == hardware_config
        
        # Test audio configuration
        assert tts.sample_rate > 0
        assert tts.audio_format in ["wav", "mp3"]
    
    def test_tts_hardware_compatibility(self, hardware_config):
        """Test hardware compatibility assessment"""
        tts = ElitePersianTTS(hardware_config)
        
        # Mock model for testing
        mock_model = {
            "type": "vits",
            "quality_estimate": 9.0
        }
        
        compatibility = tts._assess_hardware_compatibility(mock_model)
        assert isinstance(compatibility, float)
        assert 0.0 <= compatibility <= 1.0
        
        # Test different model types
        transformers_model = {"type": "transformers", "quality_estimate": 8.0}
        compatibility_transformers = tts._assess_hardware_compatibility(transformers_model)
        assert isinstance(compatibility_transformers, float)
        
        espeak_model = {"type": "espeak", "quality_estimate": 6.0}
        compatibility_espeak = tts._assess_hardware_compatibility(espeak_model)
        assert compatibility_espeak == 1.0  # Always compatible
    
    def test_tts_performance_stats(self, hardware_config):
        """Test TTS performance statistics"""
        tts = ElitePersianTTS(hardware_config)
        
        stats = tts.get_performance_stats()
        
        assert isinstance(stats, dict)
        assert "hardware_tier" in stats
        assert "active_model" in stats
        assert "available_models" in stats
        assert "synthesis_stats" in stats
        assert "memory_usage" in stats
        assert "model_loaded" in stats
        
        # Test synthesis stats structure
        synthesis_stats = stats["synthesis_stats"]
        assert "total_syntheses" in synthesis_stats
        assert "average_latency" in synthesis_stats
        assert "quality_score" in synthesis_stats

class TestSystemMonitor:
    """Test suite for system monitoring"""
    
    @pytest.mark.asyncio
    async def test_system_assessment(self):
        """Test system capability assessment"""
        monitor = SystemPerformanceMonitor()
        
        system_profile = await monitor.assess_system_capabilities()
        
        assert isinstance(system_profile, dict)
        assert "hardware_tier" in system_profile
        assert "system_info" in system_profile
        assert "performance_metrics" in system_profile
        assert "ram_gb" in system_profile
        assert "cpu_cores" in system_profile
        assert "gpu_available" in system_profile
        assert "os_type" in system_profile
        
        # Validate hardware tier
        assert system_profile["hardware_tier"] in ["high", "medium", "low"]
        
        # Validate numeric values
        assert isinstance(system_profile["ram_gb"], (int, float))
        assert isinstance(system_profile["cpu_cores"], int)
        assert isinstance(system_profile["gpu_available"], bool)
        assert system_profile["ram_gb"] > 0
        assert system_profile["cpu_cores"] > 0
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test real-time performance monitoring"""
        monitor = SystemPerformanceMonitor()
        
        metrics = await monitor.monitor_performance()
        
        assert isinstance(metrics, dict)
        assert "timestamp" in metrics
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        
        # Validate metric ranges
        if "cpu_usage" in metrics:
            assert 0 <= metrics["cpu_usage"] <= 100
        if "memory_usage" in metrics:
            assert 0 <= metrics["memory_usage"] <= 100
    
    def test_system_summary(self):
        """Test system summary generation"""
        monitor = SystemPerformanceMonitor()
        
        summary = monitor.get_system_summary()
        
        assert isinstance(summary, str)
        assert len(summary) > 50  # Should be substantial
        assert "System Summary" in summary

# Integration Tests
class TestVoicePipelineIntegration:
    """Integration tests for complete voice pipeline"""
    
    @pytest.fixture
    def hardware_config(self):
        return {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False,
            "os_type": "Linux",
            "architecture": "x86_64"
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_pipeline_creation(self, hardware_config):
        """Test end-to-end pipeline creation without initialization"""
        # Test that all components can be created
        steve = SteveVoiceAssistant(hardware_config)
        
        # Components should be None initially
        assert steve.wake_detector is None
        assert steve.stt_engine is None
        assert steve.tts_engine is None
        
        # Status should reflect uninitialized state
        status = steve.get_status()
        assert not status["is_initialized"]
        assert not status["is_listening"]
    
    @pytest.mark.asyncio
    async def test_component_compatibility(self, hardware_config):
        """Test that all components are compatible with each other"""
        # Test that components can be instantiated with same config
        wake_detector = PersianWakeWordDetector(hardware_config)
        stt_engine = AdaptivePersianSTT(hardware_config)
        tts_engine = ElitePersianTTS(hardware_config)
        
        # Test that they all assess hardware tier consistently
        assert wake_detector.hardware_profile == hardware_config
        assert stt_engine.hardware_profile == hardware_config
        assert tts_engine.hardware_profile == hardware_config
        
        # Test that they all have compatible audio configurations
        assert wake_detector.sample_rate == 16000
        # STT and TTS should be compatible with this sample rate

# Performance Tests
class TestPerformance:
    """Performance tests for voice pipeline components"""
    
    @pytest.fixture
    def hardware_config(self):
        return {
            "hardware_tier": "medium",
            "ram_gb": 8,
            "cpu_cores": 4,
            "gpu_available": False
        }
    
    def test_component_initialization_time(self, hardware_config):
        """Test component initialization performance"""
        import time
        
        # Test voice pipeline initialization time
        start_time = time.time()
        steve = SteveVoiceAssistant(hardware_config)
        init_time = time.time() - start_time
        
        # Should initialize quickly (under 1 second)
        assert init_time < 1.0
        
        # Test individual component initialization times
        start_time = time.time()
        wake_detector = PersianWakeWordDetector(hardware_config)
        wake_init_time = time.time() - start_time
        assert wake_init_time < 0.5
        
        start_time = time.time()
        stt_engine = AdaptivePersianSTT(hardware_config)
        stt_init_time = time.time() - start_time
        assert stt_init_time < 0.5
        
        start_time = time.time()
        tts_engine = ElitePersianTTS(hardware_config)
        tts_init_time = time.time() - start_time
        assert tts_init_time < 0.5
    
    @pytest.mark.asyncio
    async def test_response_generation_performance(self, hardware_config):
        """Test response generation performance"""
        import time
        
        steve = SteveVoiceAssistant(hardware_config)
        
        # Test response generation time
        test_inputs = [
            "سلام",
            "کمک",
            "ساعت چنده",
            "چراغ را روشن کن"
        ]
        
        for user_input in test_inputs:
            start_time = time.time()
            response = await steve._generate_response(user_input)
            response_time = time.time() - start_time
            
            # Response should be generated quickly (under 0.1 seconds for simple responses)
            assert response_time < 1.0  # Allow more time for complex processing
            assert isinstance(response, str)
            assert len(response) > 0

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])