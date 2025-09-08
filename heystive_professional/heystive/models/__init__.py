#!/usr/bin/env python3
"""
Heystive Persian TTS Models Package
پکیج مدل‌های TTS فارسی هیستیو

This package provides intelligent Persian TTS model management including:
- Hardware detection and optimization
- Automatic model selection based on system capabilities  
- Model downloading and caching from Hugging Face
- Fallback system for different hardware configurations
- Storage optimization and management

این پکیج مدیریت هوشمند مدل‌های TTS فارسی را ارائه می‌دهد شامل:
- تشخیص و بهینه‌سازی سخت‌افزار
- انتخاب خودکار مدل بر اساس قابلیت‌های سیستم
- دانلود و کش مدل‌ها از Hugging Face
- سیستم fallback برای تنظیمات مختلف سخت‌افزار
- بهینه‌سازی و مدیریت فضای ذخیره‌سازی
"""

from .hardware_detector import HardwareDetector
from .model_downloader import PersianTTSModelDownloader
from .intelligent_model_manager import IntelligentModelManager

__version__ = "1.0.0"
__author__ = "Heystive Team"

# Main exports
__all__ = [
    'HardwareDetector',
    'PersianTTSModelDownloader', 
    'IntelligentModelManager',
    'get_optimal_model_for_system',
    'download_recommended_models',
    'get_system_recommendations'
]

def get_optimal_model_for_system():
    """
    Get optimal Persian TTS model for current system
    دریافت بهترین مدل TTS فارسی برای سیستم فعلی
    
    Returns:
        Dict: Model information or None if no suitable model found
    """
    try:
        detector = HardwareDetector()
        return detector.get_optimal_model()
    except Exception as e:
        print(f"❌ Failed to detect optimal model: {e}")
        return None

def download_recommended_models(max_models: int = 2) -> List[str]:
    """
    Download recommended models for current system
    دانلود مدل‌های توصیه شده برای سیستم فعلی
    
    Args:
        max_models: Maximum number of models to download
        
    Returns:
        List[str]: List of successfully downloaded model IDs
    """
    try:
        manager = IntelligentModelManager()
        return manager.download_recommended_models(max_models)
    except Exception as e:
        print(f"❌ Failed to download recommended models: {e}")
        return []

def get_system_recommendations() -> Dict:
    """
    Get complete system recommendations and status
    دریافت توصیه‌های کامل سیستم و وضعیت
    
    Returns:
        Dict: Complete system status and recommendations
    """
    try:
        manager = IntelligentModelManager()
        return manager.get_system_status()
    except Exception as e:
        print(f"❌ Failed to get system recommendations: {e}")
        return {}

# Quick access functions
def quick_setup():
    """
    Quick setup for Persian TTS models
    راه‌اندازی سریع مدل‌های TTS فارسی
    
    This function:
    1. Detects system hardware
    2. Downloads optimal model
    3. Sets up fallback system
    
    Returns:
        IntelligentModelManager: Configured model manager
    """
    print("🚀 Quick Setup for Persian TTS Models")
    print("راه‌اندازی سریع مدل‌های TTS فارسی")
    print("=" * 50)
    
    try:
        manager = IntelligentModelManager()
        
        # Download recommended models if none are available
        active_model = manager.get_active_model()
        if not active_model:
            print("📥 No active model found. Downloading recommended models...")
            downloaded = manager.download_recommended_models(1)
            
            if downloaded:
                print(f"✅ Quick setup completed with model: {downloaded[0]}")
            else:
                print("⚠️ Quick setup completed but no models could be downloaded")
        else:
            print(f"✅ Quick setup completed with existing model: {active_model['name']}")
        
        return manager
        
    except Exception as e:
        print(f"❌ Quick setup failed: {e}")
        return None

# Model information constants
SUPPORTED_MODELS = {
    "ParsiTTS": {
        "quality": "بالا",
        "size_mb": 800,
        "gpu_recommended": True,
        "description": "High-quality Persian TTS based on VITS architecture"
    },
    "VITS-Persian": {
        "quality": "بالا", 
        "size_mb": 600,
        "gpu_recommended": True,
        "description": "VITS architecture optimized for Persian with tokenization support"
    },
    "Silta Persian TTS": {
        "quality": "متوسط",
        "size_mb": 200,
        "gpu_recommended": False,
        "description": "Lightweight Persian TTS suitable for CPU-only systems"
    },
    "XTTS-v2": {
        "quality": "حرفه‌ای",
        "size_mb": 2000,
        "gpu_required": True,
        "description": "Professional-grade TTS with voice cloning capabilities"
    },
    "FastPitch-Persian": {
        "quality": "بالا",
        "size_mb": 400,
        "gpu_recommended": True,
        "description": "Fast TTS with pitch and speed control"
    }
}

HARDWARE_REQUIREMENTS = {
    "HIGH_END": {
        "ram_gb": 8,
        "gpu_vram_gb": 8,
        "recommended_models": ["XTTS-v2", "ParsiTTS", "VITS-Persian"]
    },
    "MEDIUM": {
        "ram_gb": 4,
        "gpu_vram_gb": 4,
        "recommended_models": ["ParsiTTS", "VITS-Persian", "FastPitch-Persian"]
    },
    "CPU_OPTIMIZED": {
        "ram_gb": 4,
        "gpu_vram_gb": 0,
        "recommended_models": ["Silta Persian TTS", "ParsiTTS-CPU"]
    },
    "LOW_END": {
        "ram_gb": 2,
        "gpu_vram_gb": 0,
        "recommended_models": ["Silta Persian TTS", "Basic Persian TTS"]
    }
}

def print_model_info():
    """Print information about supported models"""
    print("\n📋 Supported Persian TTS Models:")
    print("=" * 50)
    
    for name, info in SUPPORTED_MODELS.items():
        gpu_req = "🎮 GPU Required" if info.get("gpu_required") else "🎮 GPU Recommended" if info.get("gpu_recommended") else "💻 CPU Compatible"
        
        print(f"\n{name} ({info['quality']})")
        print(f"  📦 Size: {info['size_mb']}MB")
        print(f"  ⚙️ Hardware: {gpu_req}")
        print(f"  📝 Description: {info['description']}")

if __name__ == "__main__":
    print_model_info()
    print("\n" + "="*50)
    quick_setup()