"""
Sample Test Data
Provides sample data for testing existing functionality
"""

import numpy as np
from typing import Dict, List, Any

# Persian text samples for testing
PERSIAN_TEXT_SAMPLES = [
    "سلام، من استیو هستم",
    "امروز هوا چطور است؟", 
    "لطفاً چراغ‌های خانه را روشن کنید",
    "موسیقی آرام‌بخش پخش کنید",
    "فردا جلسه مهمی دارم",
    "درجه حرارت را کم کنید",
    "خبرهای امروز را بخوانید",
    "یادآوری برای ساعت هشت تنظیم کنید"
]

# English text samples for testing multilingual support
ENGLISH_TEXT_SAMPLES = [
    "Hello, I am Steve",
    "What's the weather like today?",
    "Please turn on the house lights",
    "Play relaxing music",
    "Set a reminder for tomorrow"
]

# Wake word samples
WAKE_WORD_SAMPLES = [
    "هی استیو",
    "استیو",
    "hey steve",
    "steve"
]

# Mock hardware configurations
HARDWARE_CONFIGS = {
    "high_end": {
        "hardware_tier": "high",
        "ram_gb": 32,
        "cpu_cores": 16,
        "gpu_available": True,
        "gpu_memory_gb": 8,
        "os_type": "Linux",
        "architecture": "x86_64"
    },
    "medium": {
        "hardware_tier": "medium",
        "ram_gb": 8,
        "cpu_cores": 4,
        "gpu_available": False,
        "os_type": "Linux",
        "architecture": "x86_64"
    },
    "low_end": {
        "hardware_tier": "low",
        "ram_gb": 4,
        "cpu_cores": 2,
        "gpu_available": False,
        "os_type": "Linux",
        "architecture": "x86_64"
    }
}

# Mock system status data
SYSTEM_STATUS_SAMPLES = {
    "healthy": {
        "cpu_percent": 25.5,
        "memory_percent": 45.2,
        "disk_percent": 30.1,
        "network_connected": True,
        "audio_devices": 4,
        "gpu_available": True,
        "temperature_celsius": 45
    },
    "degraded": {
        "cpu_percent": 75.8,
        "memory_percent": 85.3,
        "disk_percent": 90.2,
        "network_connected": True,
        "audio_devices": 2,
        "gpu_available": False,
        "temperature_celsius": 75
    },
    "critical": {
        "cpu_percent": 95.1,
        "memory_percent": 98.7,
        "disk_percent": 95.8,
        "network_connected": False,
        "audio_devices": 0,
        "gpu_available": False,
        "temperature_celsius": 85
    }
}

# Mock smart home devices
SMART_HOME_DEVICES = [
    {
        "name": "Living Room Light",
        "persian_name": "چراغ اتاق نشیمن",
        "ip_address": "192.168.1.101",
        "mac_address": "aa:bb:cc:dd:ee:01",
        "device_type": "light",
        "protocol": "hue",
        "manufacturer": "Philips",
        "model": "Hue Color",
        "capabilities": ["on_off", "dimming", "color"],
        "status": "on",
        "brightness": 80,
        "color": {"r": 255, "g": 255, "b": 255}
    },
    {
        "name": "Bedroom AC",
        "persian_name": "کولر اتاق خواب",
        "ip_address": "192.168.1.102",
        "mac_address": "aa:bb:cc:dd:ee:02",
        "device_type": "climate",
        "protocol": "mqtt",
        "manufacturer": "Samsung",
        "model": "WindFree",
        "capabilities": ["temperature", "fan_speed", "mode"],
        "status": "off",
        "temperature": 24,
        "target_temperature": 22,
        "mode": "cool"
    },
    {
        "name": "Kitchen TV",
        "persian_name": "تلویزیون آشپزخانه",
        "ip_address": "192.168.1.103",
        "mac_address": "aa:bb:cc:dd:ee:03",
        "device_type": "media",
        "protocol": "upnp",
        "manufacturer": "LG",
        "model": "OLED55CX",
        "capabilities": ["on_off", "volume", "channel", "input"],
        "status": "on",
        "volume": 15,
        "channel": 5,
        "input": "HDMI1"
    }
]

# Mock model registry data
MODEL_REGISTRY = {
    "whisper_tiny": {
        "name": "Whisper Tiny",
        "description": "Smallest Whisper model for Persian speech recognition",
        "url": "https://example.com/whisper/tiny.pt",
        "size_mb": 39,
        "checksum": "abc123",
        "type": "whisper",
        "language": "multilingual",
        "quality": "basic",
        "hardware_requirements": "minimal"
    },
    "whisper_small": {
        "name": "Whisper Small", 
        "description": "Small Whisper model for Persian speech recognition",
        "url": "https://example.com/whisper/small.pt",
        "size_mb": 244,
        "checksum": "def456",
        "type": "whisper",
        "language": "multilingual",
        "quality": "good",
        "hardware_requirements": "low"
    },
    "test_tts_model": {
        "name": "Test Persian TTS",
        "description": "Test Persian TTS model",
        "url": "https://example.com/tts/test.pth",
        "size_mb": 120,
        "checksum": "ghi789",
        "type": "tts_vits",
        "language": "persian",
        "voice": "female",
        "quality": "good",
        "hardware_requirements": "medium"
    }
}

# Mock conversation contexts
CONVERSATION_CONTEXTS = [
    {
        "user_intent": "smart_home_control",
        "entities": {
            "device": "چراغ",
            "action": "روشن کردن",
            "location": "اتاق نشیمن"
        },
        "confidence": 0.95,
        "language": "persian"
    },
    {
        "user_intent": "weather_query",
        "entities": {
            "location": "تهران",
            "time": "امروز"
        },
        "confidence": 0.88,
        "language": "persian"
    },
    {
        "user_intent": "media_control",
        "entities": {
            "action": "پخش",
            "media_type": "موسیقی",
            "genre": "آرام"
        },
        "confidence": 0.92,
        "language": "persian"
    }
]

def generate_mock_audio(duration_seconds: float = 2.0, 
                       sample_rate: int = 16000,
                       frequency: float = 440.0) -> np.ndarray:
    """Generate mock audio data for testing"""
    samples = int(sample_rate * duration_seconds)
    t = np.linspace(0, duration_seconds, samples)
    
    # Generate sine wave
    audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    # Add some noise for realism
    noise = np.random.normal(0, 0.01, samples)
    audio_data += noise
    
    return audio_data.astype(np.float32)

def generate_mock_persian_audio_segments() -> List[np.ndarray]:
    """Generate mock audio segments for Persian wake words"""
    segments = []
    
    # Different frequencies for different wake word variations
    frequencies = [440.0, 523.25, 659.25, 783.99]  # A4, C5, E5, G5
    
    for freq in frequencies:
        audio = generate_mock_audio(duration_seconds=1.5, frequency=freq)
        segments.append(audio)
    
    return segments

def get_mock_performance_metrics() -> Dict[str, Any]:
    """Generate mock performance metrics"""
    return {
        "tts_synthesis": {
            "call_count": 150,
            "average_time": 0.45,
            "success_rate": 0.96,
            "throughput": 2.2
        },
        "stt_transcription": {
            "call_count": 89,
            "average_time": 0.32,
            "success_rate": 0.94,
            "throughput": 3.1
        },
        "wake_word_detection": {
            "call_count": 1250,
            "average_time": 0.05,
            "success_rate": 0.98,
            "throughput": 20.0
        }
    }

def get_mock_error_events() -> List[Dict[str, Any]]:
    """Generate mock error events for testing"""
    return [
        {
            "timestamp": "2024-12-30T10:30:15",
            "component": "TTS",
            "function": "synthesize_speech",
            "error_type": "ConnectionError",
            "error_message": "Model server unavailable",
            "severity": "WARNING"
        },
        {
            "timestamp": "2024-12-30T11:15:22",
            "component": "STT",
            "function": "transcribe_audio",
            "error_type": "TimeoutError", 
            "error_message": "Audio processing timeout",
            "severity": "ERROR"
        },
        {
            "timestamp": "2024-12-30T12:05:33",
            "component": "SmartHome",
            "function": "control_device",
            "error_type": "NetworkError",
            "error_message": "Device not responding",
            "severity": "WARNING"
        }
    ]

# Configuration templates for testing
CONFIG_TEMPLATES = {
    "minimal": {
        "wake_word": "هی استیو",
        "response": "بله سرورم",
        "language": "fa",
        "audio": {
            "sample_rate": 16000,
            "chunk_size": 1024
        }
    },
    "full": {
        "wake_word": "هی استیو",
        "response": "بله سرورم",
        "language": "fa",
        "audio": {
            "sample_rate": 16000,
            "chunk_size": 1024,
            "input_device": 0,
            "output_device": 2
        },
        "models": {
            "stt": "whisper-medium",
            "tts": "kamtera-female",
            "wake_word": "custom"
        },
        "smart_home": {
            "hue_bridge_ip": "192.168.1.100",
            "mqtt_broker": "localhost",
            "mqtt_port": 1883
        },
        "performance": {
            "enable_monitoring": True,
            "log_level": "INFO",
            "metrics_interval": 60
        }
    }
}

# Expected API response formats for testing web interface
API_RESPONSE_FORMATS = {
    "health_check": {
        "status": "ok",
        "timestamp": "2024-12-30T12:00:00Z",
        "system_health": {
            "overall_status": "healthy",
            "components": {
                "tts": "healthy",
                "stt": "healthy", 
                "voice_pipeline": "healthy"
            }
        }
    },
    "synthesis_request": {
        "success": True,
        "text": "سلام، من استیو هستم",
        "audio_url": "/api/audio/12345.wav",
        "duration_seconds": 2.5,
        "voice": "female_persian"
    },
    "transcription_request": {
        "success": True,
        "text": "هی استیو، چراغ را روشن کن",
        "confidence": 0.95,
        "language": "fa",
        "processing_time": 0.32
    }
}