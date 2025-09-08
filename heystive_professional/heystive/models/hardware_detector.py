#!/usr/bin/env python3
"""
Hardware Detection System for Optimal Persian TTS Model Selection
تشخیص سخت‌افزار برای انتخاب بهینه مدل TTS فارسی
"""

import os
import sys
import psutil
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class HardwareDetector:
    """
    تشخیص سخت‌افزار سیستم برای انتخاب بهینه مدل TTS
    """
    
    def __init__(self):
        self.system_info = {}
        self.gpu_info = {}
        self.recommended_models = []
        
        print("🔍 Hardware Detection for Persian TTS Models")
        print("تشخیص سخت‌افزار برای مدل‌های TTS فارسی")
        print("=" * 50)
        
        self._detect_system_info()
        self._detect_gpu_info()
        self._analyze_capabilities()
    
    def _detect_system_info(self):
        """تشخیص اطلاعات کلی سیستم"""
        try:
            self.system_info = {
                'platform': platform.system(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor() or 'Unknown',
                'cpu_count': psutil.cpu_count(logical=True),
                'cpu_count_physical': psutil.cpu_count(logical=False),
                'ram_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'ram_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'disk_free_gb': round(psutil.disk_usage('/').free / (1024**3), 2)
            }
            
            print(f"💻 System: {self.system_info['platform']} {self.system_info['architecture']}")
            print(f"🧠 CPU: {self.system_info['cpu_count']} cores ({self.system_info['cpu_count_physical']} physical)")
            print(f"💾 RAM: {self.system_info['ram_available_gb']:.1f}GB available / {self.system_info['ram_total_gb']:.1f}GB total")
            print(f"💽 Disk: {self.system_info['disk_free_gb']:.1f}GB free")
            
        except Exception as e:
            logger.error(f"System info detection failed: {e}")
    
    def _detect_gpu_info(self):
        """تشخیص GPU و CUDA"""
        self.gpu_info = {
            'has_gpu': False,
            'gpu_count': 0,
            'gpu_memory_gb': 0,
            'cuda_available': False,
            'gpu_names': []
        }
        
        # Check for NVIDIA GPU
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            if gpus:
                self.gpu_info['has_gpu'] = True
                self.gpu_info['gpu_count'] = len(gpus)
                self.gpu_info['gpu_memory_gb'] = max(gpu.memoryTotal / 1024 for gpu in gpus)
                self.gpu_info['gpu_names'] = [gpu.name for gpu in gpus]
                
                print(f"🎮 GPU: {self.gpu_info['gpu_count']} GPU(s) detected")
                for gpu in gpus:
                    print(f"   📊 {gpu.name}: {gpu.memoryTotal/1024:.1f}GB VRAM")
            else:
                print("🚫 No NVIDIA GPU detected")
                
        except ImportError:
            print("⚠️ GPUtil not available - GPU detection limited")
        except Exception as e:
            logger.warning(f"GPU detection error: {e}")
        
        # Check CUDA availability
        try:
            import torch
            if torch.cuda.is_available():
                self.gpu_info['cuda_available'] = True
                cuda_version = torch.version.cuda
                print(f"✅ CUDA available: {cuda_version}")
            else:
                print("❌ CUDA not available")
        except ImportError:
            print("⚠️ PyTorch not installed - CUDA check skipped")
        except Exception as e:
            logger.warning(f"CUDA check error: {e}")
    
    def _analyze_capabilities(self):
        """تحلیل قابلیت‌های سیستم"""
        ram_gb = self.system_info.get('ram_available_gb', 0)
        gpu_memory_gb = self.gpu_info.get('gpu_memory_gb', 0)
        has_gpu = self.gpu_info.get('has_gpu', False)
        cuda_available = self.gpu_info.get('cuda_available', False)
        
        print(f"\n🎯 System Capability Analysis:")
        print("-" * 30)
        
        # تعیین سطح سخت‌افزار
        if has_gpu and cuda_available and gpu_memory_gb >= 8 and ram_gb >= 8:
            capability_level = "HIGH_END"
            print("🚀 High-end system detected")
        elif has_gpu and cuda_available and gpu_memory_gb >= 4 and ram_gb >= 4:
            capability_level = "MEDIUM"
            print("⚡ Medium-performance system detected")
        elif ram_gb >= 4:
            capability_level = "CPU_OPTIMIZED"
            print("💻 CPU-optimized system detected")
        else:
            capability_level = "LOW_END"
            print("🔋 Low-resource system detected")
        
        self.system_info['capability_level'] = capability_level
        
        # توصیه مدل‌ها بر اساس سخت‌افزار
        self._recommend_models(capability_level)
    
    def _recommend_models(self, capability_level: str):
        """توصیه مدل‌ها بر اساس سخت‌افزار"""
        
        model_recommendations = {
            "HIGH_END": [
                {
                    "name": "XTTS-v2",
                    "huggingface_id": "coqui/XTTS-v2",
                    "priority": 1,
                    "features": ["Voice Cloning", "Studio Quality", "Multi-language"],
                    "requirements": "8GB+ VRAM, GPU required",
                    "size_gb": 2.0,
                    "quality": "حرفه‌ای"
                },
                {
                    "name": "ParsiTTS",
                    "huggingface_id": "persiannlp/parsi-tts",
                    "priority": 2,
                    "features": ["High Quality", "VITS Architecture", "Persian Optimized"],
                    "requirements": "4GB+ RAM, GPU recommended",
                    "size_gb": 0.8,
                    "quality": "بالا"
                },
                {
                    "name": "VITS-Persian",
                    "huggingface_id": "persian-tts/vits-persian",
                    "priority": 3,
                    "features": ["VITS Architecture", "Persian Tokenization"],
                    "requirements": "4GB+ RAM, GPU recommended",
                    "size_gb": 0.6,
                    "quality": "بالا"
                }
            ],
            
            "MEDIUM": [
                {
                    "name": "ParsiTTS",
                    "huggingface_id": "persiannlp/parsi-tts",
                    "priority": 1,
                    "features": ["High Quality", "VITS Architecture", "Persian Optimized"],
                    "requirements": "4GB+ RAM, GPU recommended",
                    "size_gb": 0.8,
                    "quality": "بالا"
                },
                {
                    "name": "VITS-Persian",
                    "huggingface_id": "persian-tts/vits-persian",
                    "priority": 2,
                    "features": ["VITS Architecture", "Persian Tokenization"],
                    "requirements": "4GB+ RAM, GPU recommended",
                    "size_gb": 0.6,
                    "quality": "بالا"
                },
                {
                    "name": "FastPitch-Persian",
                    "huggingface_id": "persian-tts/fastpitch-persian",
                    "priority": 3,
                    "features": ["Speed Control", "Pitch Control", "Interactive"],
                    "requirements": "GPU + Vocoder",
                    "size_gb": 0.4,
                    "quality": "بالا"
                }
            ],
            
            "CPU_OPTIMIZED": [
                {
                    "name": "Silta Persian TTS",
                    "huggingface_id": "persian-tts/silta-persian",
                    "priority": 1,
                    "features": ["Lightweight", "CPU Optimized", "Embedded Systems"],
                    "requirements": "2GB+ RAM, CPU only",
                    "size_gb": 0.2,
                    "quality": "متوسط"
                },
                {
                    "name": "ParsiTTS-CPU",
                    "huggingface_id": "persiannlp/parsi-tts-cpu",
                    "priority": 2,
                    "features": ["CPU Optimized", "Persian Optimized"],
                    "requirements": "4GB+ RAM, CPU only",
                    "size_gb": 0.5,
                    "quality": "بالا"
                }
            ],
            
            "LOW_END": [
                {
                    "name": "Silta Persian TTS",
                    "huggingface_id": "persian-tts/silta-persian",
                    "priority": 1,
                    "features": ["Lightweight", "CPU Optimized", "Embedded Systems"],
                    "requirements": "2GB+ RAM, CPU only",
                    "size_gb": 0.2,
                    "quality": "متوسط"
                },
                {
                    "name": "Basic Persian TTS",
                    "huggingface_id": "persian-tts/basic-tts",
                    "priority": 2,
                    "features": ["Very Lightweight", "Basic Quality"],
                    "requirements": "1GB+ RAM, CPU only",
                    "size_gb": 0.1,
                    "quality": "پایه"
                }
            ]
        }
        
        self.recommended_models = model_recommendations.get(capability_level, [])
        
        print(f"\n💡 Recommended Models for {capability_level}:")
        print("-" * 40)
        
        for i, model in enumerate(self.recommended_models, 1):
            print(f"{i}. {model['name']} ({model['quality']})")
            print(f"   📦 Size: {model['size_gb']}GB")
            print(f"   ⚙️ Requirements: {model['requirements']}")
            print(f"   ✨ Features: {', '.join(model['features'])}")
            print()
    
    def get_optimal_model(self) -> Optional[Dict]:
        """دریافت بهترین مدل برای سیستم فعلی"""
        if self.recommended_models:
            return self.recommended_models[0]  # بالاترین اولویت
        return None
    
    def get_all_compatible_models(self) -> List[Dict]:
        """دریافت تمام مدل‌های سازگار"""
        return self.recommended_models
    
    def can_download_model(self, model_size_gb: float) -> bool:
        """بررسی امکان دانلود مدل بر اساس فضای دیسک"""
        available_space = self.system_info.get('disk_free_gb', 0)
        required_space = model_size_gb * 1.5  # 50% buffer
        
        return available_space >= required_space
    
    def get_system_summary(self) -> Dict:
        """خلاصه اطلاعات سیستم"""
        return {
            'system_info': self.system_info,
            'gpu_info': self.gpu_info,
            'recommended_models': self.recommended_models,
            'optimal_model': self.get_optimal_model()
        }

def main():
    """تست سیستم تشخیص سخت‌افزار"""
    detector = HardwareDetector()
    
    print("\n" + "=" * 50)
    print("📋 HARDWARE DETECTION SUMMARY")
    print("خلاصه تشخیص سخت‌افزار")
    print("=" * 50)
    
    optimal_model = detector.get_optimal_model()
    if optimal_model:
        print(f"🎯 Optimal Model: {optimal_model['name']}")
        print(f"📦 Size: {optimal_model['size_gb']}GB")
        print(f"🏷️ Quality: {optimal_model['quality']}")
        print(f"🔗 Hugging Face: {optimal_model['huggingface_id']}")
        
        if detector.can_download_model(optimal_model['size_gb']):
            print("✅ Sufficient disk space for download")
        else:
            print("❌ Insufficient disk space for download")
    else:
        print("❌ No compatible models found")
    
    return detector

if __name__ == "__main__":
    main()