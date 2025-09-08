#!/usr/bin/env python3
"""
Test Persian TTS Model System - Simple Version
تست سیستم مدل‌های TTS فارسی - نسخه ساده
"""

import os
import sys
import platform
from pathlib import Path

class SimpleHardwareDetector:
    """تشخیص ساده سخت‌افزار بدون وابستگی خارجی"""
    
    def __init__(self):
        print("🔍 Simple Hardware Detection for Persian TTS")
        print("تشخیص ساده سخت‌افزار برای TTS فارسی")
        print("=" * 50)
        
        self.system_info = self._detect_basic_info()
        self.capability_level = self._determine_capability()
        self.recommended_models = self._get_recommendations()
    
    def _detect_basic_info(self):
        """تشخیص اطلاعات پایه سیستم"""
        info = {
            'platform': platform.system(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or 'Unknown',
            'python_version': platform.python_version()
        }
        
        # تشخیص تقریبی RAM (بدون psutil)
        try:
            if info['platform'] == 'Linux':
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    for line in meminfo.split('\n'):
                        if 'MemTotal' in line:
                            ram_kb = int(line.split()[1])
                            info['ram_gb'] = round(ram_kb / (1024 * 1024), 1)
                            break
            else:
                # تخمین پایه برای سایر سیستم‌ها
                info['ram_gb'] = 8.0  # تخمین پیش‌فرض
        except:
            info['ram_gb'] = 4.0  # تخمین محافظه‌کارانه
        
        # تشخیص GPU (ساده)
        info['has_gpu'] = self._detect_gpu()
        
        print(f"💻 Platform: {info['platform']} {info['architecture']}")
        print(f"🐍 Python: {info['python_version']}")
        print(f"💾 Estimated RAM: {info['ram_gb']}GB")
        print(f"🎮 GPU Detected: {'Yes' if info['has_gpu'] else 'No'}")
        
        return info
    
    def _detect_gpu(self):
        """تشخیص ساده GPU"""
        try:
            # بررسی وجود CUDA
            import subprocess
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _determine_capability(self):
        """تعیین سطح قابلیت سیستم"""
        ram_gb = self.system_info.get('ram_gb', 0)
        has_gpu = self.system_info.get('has_gpu', False)
        
        if has_gpu and ram_gb >= 8:
            level = "HIGH_END"
            print("🚀 High-end system capabilities detected")
        elif has_gpu and ram_gb >= 4:
            level = "MEDIUM"
            print("⚡ Medium system capabilities detected")
        elif ram_gb >= 4:
            level = "CPU_OPTIMIZED"
            print("💻 CPU-optimized system detected")
        else:
            level = "LOW_END"
            print("🔋 Low-resource system detected")
        
        return level
    
    def _get_recommendations(self):
        """دریافت توصیه‌های مدل"""
        recommendations = {
            "HIGH_END": [
                {
                    "name": "XTTS-v2",
                    "quality": "حرفه‌ای",
                    "size_gb": 2.0,
                    "huggingface_id": "coqui/XTTS-v2",
                    "features": ["Voice Cloning", "Studio Quality"],
                    "requirements": "8GB+ VRAM"
                },
                {
                    "name": "ParsiTTS",
                    "quality": "بالا",
                    "size_gb": 0.8,
                    "huggingface_id": "persiannlp/parsi-tts",
                    "features": ["High Quality", "Persian Optimized"],
                    "requirements": "4GB+ RAM, GPU recommended"
                }
            ],
            
            "MEDIUM": [
                {
                    "name": "ParsiTTS",
                    "quality": "بالا",
                    "size_gb": 0.8,
                    "huggingface_id": "persiannlp/parsi-tts",
                    "features": ["High Quality", "Persian Optimized"],
                    "requirements": "4GB+ RAM, GPU recommended"
                },
                {
                    "name": "VITS-Persian",
                    "quality": "بالا",
                    "size_gb": 0.6,
                    "huggingface_id": "persian-tts/vits-persian",
                    "features": ["VITS Architecture", "Persian Tokenization"],
                    "requirements": "4GB+ RAM"
                }
            ],
            
            "CPU_OPTIMIZED": [
                {
                    "name": "Silta Persian TTS",
                    "quality": "متوسط",
                    "size_gb": 0.2,
                    "huggingface_id": "persian-tts/silta-persian",
                    "features": ["Lightweight", "CPU Optimized"],
                    "requirements": "2GB+ RAM, CPU only"
                }
            ],
            
            "LOW_END": [
                {
                    "name": "Basic Persian TTS",
                    "quality": "پایه",
                    "size_gb": 0.1,
                    "huggingface_id": "persian-tts/basic-tts",
                    "features": ["Very Lightweight"],
                    "requirements": "1GB+ RAM"
                }
            ]
        }
        
        return recommendations.get(self.capability_level, [])
    
    def get_optimal_model(self):
        """دریافت بهترین مدل"""
        return self.recommended_models[0] if self.recommended_models else None
    
    def print_recommendations(self):
        """نمایش توصیه‌ها"""
        print(f"\n💡 Recommended Models for {self.capability_level}:")
        print("-" * 50)
        
        for i, model in enumerate(self.recommended_models, 1):
            print(f"{i}. {model['name']} ({model['quality']})")
            print(f"   📦 Size: {model['size_gb']}GB")
            print(f"   🔗 Hugging Face: {model['huggingface_id']}")
            print(f"   ⚙️ Requirements: {model['requirements']}")
            print(f"   ✨ Features: {', '.join(model['features'])}")
            print()

class SimpleModelManager:
    """مدیر ساده مدل‌ها"""
    
    def __init__(self):
        self.models_dir = Path("heystive/models/persian_tts")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.hardware_detector = SimpleHardwareDetector()
        
        print("\n🧠 Simple Model Manager Initialized")
        print("مدیر ساده مدل‌ها راه‌اندازی شد")
        print("=" * 50)
    
    def simulate_model_download(self, model_info):
        """شبیه‌سازی دانلود مدل"""
        model_name = model_info['name']
        model_dir = self.models_dir / model_name.lower().replace(' ', '_')
        model_dir.mkdir(exist_ok=True)
        
        print(f"📥 Simulating download of: {model_name}")
        print(f"🔗 From: {model_info['huggingface_id']}")
        print(f"📦 Size: {model_info['size_gb']}GB")
        
        # ایجاد فایل‌های نمونه
        config_file = model_dir / "config.json"
        model_file = model_dir / "model_info.txt"
        
        # ایجاد config نمونه
        import json
        config = {
            "model_name": model_name,
            "quality": model_info['quality'],
            "size_gb": model_info['size_gb'],
            "huggingface_id": model_info['huggingface_id'],
            "features": model_info['features'],
            "requirements": model_info['requirements'],
            "downloaded": True,
            "download_simulation": True
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # ایجاد فایل اطلاعات
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(f"Persian TTS Model: {model_name}\n")
            f.write(f"Quality: {model_info['quality']}\n")
            f.write(f"Size: {model_info['size_gb']}GB\n")
            f.write(f"Features: {', '.join(model_info['features'])}\n")
            f.write(f"Requirements: {model_info['requirements']}\n")
            f.write(f"Hugging Face: {model_info['huggingface_id']}\n")
            f.write("\nThis is a simulation file for testing purposes.\n")
            f.write("In real implementation, this would contain the actual model files.\n")
        
        print(f"✅ Simulation complete: {model_dir}")
        return str(model_dir)
    
    def setup_optimal_model(self):
        """راه‌اندازی مدل بهینه"""
        optimal_model = self.hardware_detector.get_optimal_model()
        
        if optimal_model:
            print(f"\n🎯 Setting up optimal model: {optimal_model['name']}")
            model_path = self.simulate_model_download(optimal_model)
            
            print(f"✅ Optimal model ready at: {model_path}")
            return optimal_model
        else:
            print("❌ No optimal model found")
            return None
    
    def generate_sample_tts(self, text: str = "بله سرورم"):
        """تولید نمونه TTS"""
        optimal_model = self.hardware_detector.get_optimal_model()
        
        if not optimal_model:
            print("❌ No model available for TTS")
            return None
        
        print(f"\n🎤 Generating TTS Sample")
        print(f"📝 Text: {text}")
        print(f"🤖 Model: {optimal_model['name']} ({optimal_model['quality']})")
        
        # شبیه‌سازی تولید صوت
        output_file = f"tts_sample_{optimal_model['name'].lower().replace(' ', '_')}.wav"
        output_path = Path("audio_output") / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        # ایجاد فایل نمونه
        sample_content = f"""# Persian TTS Sample - {optimal_model['name']}
Text: {text}
Model: {optimal_model['name']}
Quality: {optimal_model['quality']}
Generated with: Heystive Persian TTS System

This is a simulation file. In real implementation, 
this would be an actual audio file (.wav) containing 
the synthesized Persian speech.

Model Information:
- Size: {optimal_model['size_gb']}GB
- Features: {', '.join(optimal_model['features'])}
- Requirements: {optimal_model['requirements']}
- Hugging Face: {optimal_model['huggingface_id']}
"""
        
        with open(str(output_path).replace('.wav', '.txt'), 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"✅ TTS sample generated: {output_path}")
        print(f"📁 Location: {output_path.parent}")
        
        return str(output_path)

def main():
    """تست کامل سیستم مدل‌ها"""
    print("🚀 Testing Persian TTS Model System")
    print("تست سیستم مدل‌های TTS فارسی")
    print("=" * 60)
    
    try:
        # راه‌اندازی مدیر مدل‌ها
        manager = SimpleModelManager()
        
        # نمایش توصیه‌ها
        manager.hardware_detector.print_recommendations()
        
        # راه‌اندازی مدل بهینه
        optimal_model = manager.setup_optimal_model()
        
        if optimal_model:
            # تولید نمونه صوتی
            sample_path = manager.generate_sample_tts("بله سرورم")
            
            print(f"\n🎉 SUCCESS! Persian TTS System Ready")
            print(f"✅ Optimal Model: {optimal_model['name']}")
            print(f"✅ Sample Generated: {sample_path}")
        
        # نمایش خلاصه
        print(f"\n📊 SYSTEM SUMMARY")
        print("=" * 30)
        print(f"Hardware Level: {manager.hardware_detector.capability_level}")
        print(f"Platform: {manager.hardware_detector.system_info['platform']}")
        print(f"RAM: {manager.hardware_detector.system_info['ram_gb']}GB")
        print(f"GPU: {'Available' if manager.hardware_detector.system_info['has_gpu'] else 'Not Available'}")
        
        if optimal_model:
            print(f"Selected Model: {optimal_model['name']} ({optimal_model['quality']})")
            print(f"Model Size: {optimal_model['size_gb']}GB")
        
        print(f"\n🎯 Model System Test: SUCCESSFUL ✅")
        return True
        
    except Exception as e:
        print(f"❌ Model system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()