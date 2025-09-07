"""
Pytest Configuration and Shared Fixtures
Provides common test fixtures and utilities for testing existing functionality
"""

import pytest
import asyncio
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def mock_hardware_config():
    """Standard mock hardware configuration"""
    return {
        "hardware_tier": "medium",
        "ram_gb": 8,
        "cpu_cores": 4,
        "gpu_available": False,
        "os_type": "Linux",
        "architecture": "x86_64"
    }

@pytest.fixture
def mock_audio_data():
    """Generate mock audio data for testing"""
    # Generate 2 seconds of mock audio at 16kHz
    sample_rate = 16000
    duration = 2.0
    samples = int(sample_rate * duration)
    
    # Generate sine wave as mock audio
    t = np.linspace(0, duration, samples)
    frequency = 440  # A4 note
    audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    return audio_data.astype(np.float32)

@pytest.fixture
def mock_persian_text():
    """Persian text samples for testing"""
    return [
        "سلام، من استیو هستم",
        "امروز هوا چطور است؟",
        "لطفاً چراغ‌های خانه را روشن کنید",
        "موسیقی آرام‌بخش پخش کنید"
    ]

@pytest.fixture
def mock_system_status():
    """Mock system status for testing"""
    return {
        "cpu_percent": 45.2,
        "memory_percent": 67.8,
        "disk_percent": 23.1,
        "network_connected": True,
        "audio_devices": 3,
        "gpu_available": False
    }

@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "mock output"
        mock_run.return_value.stderr = ""
        yield mock_run

@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing"""
    with patch('builtins.open', create=True) as mock_open, \
         patch('os.unlink') as mock_unlink, \
         patch('os.path.exists') as mock_exists:
        
        mock_exists.return_value = True
        yield {
            'open': mock_open,
            'unlink': mock_unlink,
            'exists': mock_exists
        }

@pytest.fixture
def mock_network_operations():
    """Mock network operations for testing"""
    with patch('requests.get') as mock_get, \
         patch('socket.socket') as mock_socket:
        
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_response.text = "mock response"
        mock_get.return_value = mock_response
        
        yield {
            'get': mock_get,
            'socket': mock_socket,
            'response': mock_response
        }

@pytest.fixture
def mock_audio_devices():
    """Mock audio device information"""
    return {
        "input_devices": [
            {"index": 0, "name": "Default Input", "channels": 1},
            {"index": 1, "name": "USB Microphone", "channels": 2}
        ],
        "output_devices": [
            {"index": 2, "name": "Default Output", "channels": 2},
            {"index": 3, "name": "USB Speakers", "channels": 2}
        ],
        "default_input": 0,
        "default_output": 2
    }

@pytest.fixture
def mock_model_registry():
    """Mock model registry for testing"""
    return {
        "whisper_tiny": {
            "name": "Whisper Tiny",
            "url": "https://example.com/whisper-tiny.pt",
            "size_mb": 39,
            "type": "whisper"
        },
        "test_tts_model": {
            "name": "Test TTS Model",
            "url": "https://example.com/test-tts.pth",
            "size_mb": 120,
            "type": "tts_vits"
        }
    }

@pytest.fixture
def mock_smart_home_devices():
    """Mock smart home devices for testing"""
    return [
        {
            "name": "Living Room Light",
            "ip": "192.168.1.101",
            "type": "light",
            "protocol": "hue",
            "status": "on"
        },
        {
            "name": "Bedroom AC",
            "ip": "192.168.1.102", 
            "type": "climate",
            "protocol": "mqtt",
            "status": "off"
        }
    ]

class MockTTSEngine:
    """Mock TTS engine for testing"""
    
    def __init__(self, hardware_config):
        self.hardware_config = hardware_config
        self.initialized = True
        self.active_model = "mock_model"
    
    async def synthesize_speech(self, text, voice="default"):
        """Mock speech synthesis"""
        return {
            "success": True,
            "audio_data": np.random.random(16000),  # 1 second of mock audio
            "text": text,
            "voice": voice
        }
    
    def cleanup(self):
        """Mock cleanup"""
        self.initialized = False

class MockSTTEngine:
    """Mock STT engine for testing"""
    
    def __init__(self, hardware_config):
        self.hardware_config = hardware_config
        self.initialized = True
        self.model_loaded = True
    
    async def transcribe_audio(self, audio_data):
        """Mock audio transcription"""
        # Return mock Persian transcription
        mock_transcriptions = [
            "سلام استیو",
            "چراغ را روشن کن",
            "موسیقی پخش کن"
        ]
        return {
            "success": True,
            "text": np.random.choice(mock_transcriptions),
            "confidence": 0.95
        }
    
    def cleanup(self):
        """Mock cleanup"""
        self.initialized = False

@pytest.fixture
def mock_tts_engine(mock_hardware_config):
    """Provide mock TTS engine"""
    return MockTTSEngine(mock_hardware_config)

@pytest.fixture
def mock_stt_engine(mock_hardware_config):
    """Provide mock STT engine"""
    return MockSTTEngine(mock_hardware_config)

# Test markers for different categories
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression prevention tests"
    )
    config.addinivalue_line(
        "markers", "existing_behavior: marks tests that verify existing behavior"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )

# Custom test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file names
        if "test_existing" in item.nodeid:
            item.add_marker(pytest.mark.existing_behavior)
        
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        if "test_regression" in item.nodeid:
            item.add_marker(pytest.mark.regression)

# Utility functions for tests
def create_test_config(temp_dir, config_data):
    """Create a test configuration file"""
    import json
    config_file = temp_dir / "test_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    return config_file

def create_test_audio_file(temp_dir, audio_data, filename="test_audio.wav"):
    """Create a test audio file"""
    import soundfile as sf
    audio_file = temp_dir / filename
    try:
        sf.write(str(audio_file), audio_data, 16000)
        return audio_file
    except ImportError:
        # If soundfile not available, create a dummy file
        with open(audio_file, 'wb') as f:
            f.write(b'RIFF' + b'\x00' * 40)  # Minimal WAV header
        return audio_file

def assert_persian_text_valid(text):
    """Assert that text contains valid Persian characters"""
    persian_chars = set('آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی')
    text_chars = set(text)
    assert len(text_chars.intersection(persian_chars)) > 0, f"No Persian characters found in: {text}"

def assert_audio_data_valid(audio_data):
    """Assert that audio data is valid"""
    assert isinstance(audio_data, np.ndarray), "Audio data must be numpy array"
    assert len(audio_data.shape) == 1, "Audio data must be 1D array"
    assert len(audio_data) > 0, "Audio data cannot be empty"
    assert np.all(np.abs(audio_data) <= 1.0), "Audio data must be normalized to [-1, 1]"