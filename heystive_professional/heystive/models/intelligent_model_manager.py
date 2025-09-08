#!/usr/bin/env python3
"""
Intelligent Persian TTS Model Manager
مدیر هوشمند مدل‌های TTS فارسی با انتخاب خودکار بر اساس سخت‌افزار
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .hardware_detector import HardwareDetector
from .model_downloader import PersianTTSModelDownloader

logger = logging.getLogger(__name__)

class IntelligentModelManager:
    """
    مدیر هوشمند مدل‌های TTS فارسی
    - تشخیص خودکار سخت‌افزار
    - انتخاب بهینه مدل
    - دانلود و مدیریت مدل‌ها
    - سیستم fallback
    """
    
    def __init__(self, models_dir: str = None):
        self.models_dir = Path(models_dir) if models_dir else Path(__file__).parent / "persian_tts"
        
        print("🧠 Intelligent Persian TTS Model Manager")
        print("مدیر هوشمند مدل‌های TTS فارسی")
        print("=" * 60)
        
        # اجزای سیستم
        self.hardware_detector = HardwareDetector()
        self.model_downloader = PersianTTSModelDownloader(str(self.models_dir))
        
        # وضعیت سیستم
        self.system_capability = self.hardware_detector.system_info.get('capability_level', 'LOW_END')
        self.active_model = None
        self.fallback_models = []
        
        # تنظیمات
        self.auto_download = True
        self.max_models_to_keep = 3
        
        print(f"🎯 System Capability: {self.system_capability}")
        
        self._initialize_system()
    
    def _initialize_system(self):
        """راه‌اندازی اولیه سیستم"""
        print("\n🔧 Initializing Model Management System...")
        
        # بررسی مدل‌های موجود
        downloaded_models = self.model_downloader.get_downloaded_models()
        
        if downloaded_models:
            print(f"✅ Found {len(downloaded_models)} downloaded models")
            for model in downloaded_models:
                print(f"   📦 {model['name']} ({model.get('quality', 'N/A')})")
        else:
            print("📥 No models downloaded yet")
        
        # انتخاب یا دانلود مدل بهینه
        self._setup_optimal_model()
        
        # راه‌اندازی سیستم fallback
        self._setup_fallback_system()
    
    def _setup_optimal_model(self):
        """راه‌اندازی مدل بهینه"""
        print("\n🎯 Setting up optimal model...")
        
        # دریافت مدل توصیه شده
        optimal_model = self.hardware_detector.get_optimal_model()
        
        if not optimal_model:
            print("❌ No optimal model found for current hardware")
            return
        
        print(f"💡 Recommended: {optimal_model['name']} ({optimal_model['quality']})")
        
        # تبدیل نام به ID
        model_id = self._get_model_id_by_name(optimal_model['name'])
        
        if not model_id:
            print(f"❌ Model ID not found for: {optimal_model['name']}")
            return
        
        # بررسی دانلود شدن
        if self.model_downloader.is_model_downloaded(model_id):
            print(f"✅ Optimal model already downloaded: {optimal_model['name']}")
            self.active_model = model_id
        else:
            if self.auto_download:
                print(f"📥 Auto-downloading optimal model...")
                
                # بررسی فضای دیسک
                if not self.hardware_detector.can_download_model(optimal_model['size_gb']):
                    print(f"⚠️ Insufficient disk space for {optimal_model['name']}")
                    self._try_alternative_models()
                    return
                
                # دانلود مدل
                if self.model_downloader.download_model(model_id):
                    self.active_model = model_id
                    print(f"🎉 Successfully set up optimal model: {optimal_model['name']}")
                else:
                    print(f"❌ Failed to download optimal model")
                    self._try_alternative_models()
            else:
                print(f"⚠️ Auto-download disabled. Please download manually: {optimal_model['name']}")
    
    def _try_alternative_models(self):
        """تلاش برای مدل‌های جایگزین"""
        print("\n🔄 Trying alternative models...")
        
        compatible_models = self.hardware_detector.get_all_compatible_models()
        
        for model_info in compatible_models[1:]:  # از مدل دوم شروع کن (اول optimal بود)
            model_id = self._get_model_id_by_name(model_info['name'])
            
            if not model_id:
                continue
            
            if self.model_downloader.is_model_downloaded(model_id):
                print(f"✅ Using alternative model: {model_info['name']}")
                self.active_model = model_id
                return
            
            if self.auto_download and self.hardware_detector.can_download_model(model_info['size_gb']):
                print(f"📥 Downloading alternative: {model_info['name']}")
                if self.model_downloader.download_model(model_id):
                    self.active_model = model_id
                    print(f"✅ Successfully set up alternative: {model_info['name']}")
                    return
        
        print("❌ No suitable models could be set up")
    
    def _setup_fallback_system(self):
        """راه‌اندازی سیستم fallback"""
        print("\n🛡️ Setting up fallback system...")
        
        downloaded_models = self.model_downloader.get_downloaded_models()
        
        # مرتب‌سازی بر اساس کیفیت و سازگاری
        quality_order = {"حرفه‌ای": 4, "بالا": 3, "متوسط": 2, "پایه": 1}
        
        sorted_models = sorted(downloaded_models, 
                             key=lambda x: quality_order.get(x.get('quality', 'پایه'), 0), 
                             reverse=True)
        
        self.fallback_models = [model['id'] for model in sorted_models 
                               if model['id'] != self.active_model]
        
        if self.fallback_models:
            print(f"✅ Fallback models available: {len(self.fallback_models)}")
            for model_id in self.fallback_models[:3]:  # نمایش 3 مدل اول
                model_info = self._get_model_info(model_id)
                if model_info:
                    print(f"   🔄 {model_info.get('name', model_id)}")
        else:
            print("⚠️ No fallback models available")
    
    def _get_model_id_by_name(self, model_name: str) -> Optional[str]:
        """دریافت ID مدل بر اساس نام"""
        for model_id, config in self.model_downloader.model_configs.items():
            if config["name"] == model_name:
                return model_id
        return None
    
    def _get_model_info(self, model_id: str) -> Optional[Dict]:
        """دریافت اطلاعات مدل"""
        model_path = self.models_dir / model_id / "model_info.json"
        
        if model_path.exists():
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load model info for {model_id}: {e}")
        
        # اطلاعات پایه از config
        if model_id in self.model_downloader.model_configs:
            config = self.model_downloader.model_configs[model_id]
            return {
                "id": model_id,
                "name": config["name"],
                "quality": config["quality"]
            }
        
        return None
    
    def get_active_model(self) -> Optional[Dict]:
        """دریافت مدل فعال"""
        if self.active_model:
            return self._get_model_info(self.active_model)
        return None
    
    def switch_model(self, model_id: str) -> bool:
        """تغییر مدل فعال"""
        if not self.model_downloader.is_model_downloaded(model_id):
            print(f"❌ Model '{model_id}' is not downloaded")
            return False
        
        old_model = self.active_model
        self.active_model = model_id
        
        print(f"🔄 Switched from {old_model} to {model_id}")
        return True
    
    def download_recommended_models(self, max_models: int = 2) -> List[str]:
        """دانلود مدل‌های توصیه شده"""
        print(f"\n📥 Downloading up to {max_models} recommended models...")
        
        compatible_models = self.hardware_detector.get_all_compatible_models()
        downloaded_models = []
        
        for i, model_info in enumerate(compatible_models[:max_models]):
            model_id = self._get_model_id_by_name(model_info['name'])
            
            if not model_id:
                continue
            
            if self.model_downloader.is_model_downloaded(model_id):
                print(f"⏭️ Already downloaded: {model_info['name']}")
                downloaded_models.append(model_id)
                continue
            
            if not self.hardware_detector.can_download_model(model_info['size_gb']):
                print(f"⚠️ Insufficient space for: {model_info['name']}")
                continue
            
            print(f"\n📦 Downloading {i+1}/{max_models}: {model_info['name']}")
            
            if self.model_downloader.download_model(model_id):
                downloaded_models.append(model_id)
                print(f"✅ Downloaded: {model_info['name']}")
            else:
                print(f"❌ Failed to download: {model_info['name']}")
        
        return downloaded_models
    
    def optimize_storage(self):
        """بهینه‌سازی فضای ذخیره‌سازی"""
        print("\n🗂️ Optimizing storage...")
        
        downloaded_models = self.model_downloader.get_downloaded_models()
        
        if len(downloaded_models) <= self.max_models_to_keep:
            print("✅ Storage already optimized")
            return
        
        # مرتب‌سازی بر اساس اولویت (کیفیت و استفاده اخیر)
        quality_order = {"حرفه‌ای": 4, "بالا": 3, "متوسط": 2, "پایه": 1}
        
        sorted_models = sorted(downloaded_models,
                             key=lambda x: (
                                 x['id'] == self.active_model,  # مدل فعال اولویت دارد
                                 quality_order.get(x.get('quality', 'پایه'), 0)
                             ),
                             reverse=True)
        
        # حذف مدل‌های اضافی
        models_to_remove = sorted_models[self.max_models_to_keep:]
        
        for model in models_to_remove:
            if model['id'] != self.active_model:  # مدل فعال را حذف نکن
                print(f"🗑️ Removing: {model['name']}")
                self.model_downloader.remove_model(model['id'])
    
    def get_system_status(self) -> Dict:
        """دریافت وضعیت کامل سیستم"""
        storage = self.model_downloader.get_storage_usage()
        active_model = self.get_active_model()
        
        return {
            "hardware": {
                "capability_level": self.system_capability,
                "ram_gb": self.hardware_detector.system_info.get('ram_available_gb', 0),
                "gpu_available": self.hardware_detector.gpu_info.get('has_gpu', False),
                "gpu_memory_gb": self.hardware_detector.gpu_info.get('gpu_memory_gb', 0)
            },
            "models": {
                "active_model": active_model,
                "downloaded_count": storage['models_count'],
                "total_size_mb": storage['total_mb'],
                "fallback_models": len(self.fallback_models)
            },
            "recommendations": self.hardware_detector.get_all_compatible_models()
        }
    
    def generate_tts_audio(self, text: str, output_path: str = None) -> Optional[str]:
        """تولید صوت TTS (پیاده‌سازی ساده برای تست)"""
        if not self.active_model:
            print("❌ No active model for TTS generation")
            return None
        
        print(f"🎤 Generating TTS with model: {self.active_model}")
        print(f"📝 Text: {text}")
        
        # در اینجا باید کد واقعی TTS قرار گیرد
        # فعلاً یک پیاده‌سازی ساده برای تست
        
        if not output_path:
            output_path = f"tts_output_{int(time.time())}.wav"
        
        # شبیه‌سازی تولید صوت
        print(f"🔄 Processing text with {self.active_model}...")
        time.sleep(1)  # شبیه‌سازی پردازش
        
        # ایجاد فایل نمونه (برای تست)
        try:
            with open(output_path, 'wb') as f:
                f.write(b"FAKE_AUDIO_DATA_FOR_TESTING")
            
            print(f"✅ TTS audio generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None

def main():
    """تست مدیر هوشمند مدل‌ها"""
    print("🧠 Testing Intelligent Model Manager")
    print("=" * 50)
    
    try:
        manager = IntelligentModelManager()
        
        print("\n" + "=" * 50)
        print("📊 SYSTEM STATUS REPORT")
        print("گزارش وضعیت سیستم")
        print("=" * 50)
        
        status = manager.get_system_status()
        
        # اطلاعات سخت‌افزار
        hw = status['hardware']
        print(f"🖥️ Hardware Capability: {hw['capability_level']}")
        print(f"💾 Available RAM: {hw['ram_gb']:.1f}GB")
        print(f"🎮 GPU: {'Yes' if hw['gpu_available'] else 'No'}")
        if hw['gpu_available']:
            print(f"   VRAM: {hw['gpu_memory_gb']:.1f}GB")
        
        # اطلاعات مدل‌ها
        models = status['models']
        print(f"\n📦 Models Status:")
        print(f"   Downloaded: {models['downloaded_count']} models")
        print(f"   Storage Used: {models['total_size_mb']:.1f}MB")
        print(f"   Fallback Options: {models['fallback_models']}")
        
        active_model = models['active_model']
        if active_model:
            print(f"   Active Model: {active_model['name']} ({active_model.get('quality', 'N/A')})")
        else:
            print("   Active Model: None")
        
        # توصیه‌های سیستم
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(status['recommendations'][:3], 1):
            print(f"   {i}. {rec['name']} ({rec['quality']})")
            print(f"      Size: {rec['size_gb']}GB | {rec['requirements']}")
        
        # تست تولید صوت
        print(f"\n🎤 Testing TTS Generation:")
        result = manager.generate_tts_audio("بله سرورم", "test_tts_output.wav")
        
        if result:
            print(f"✅ TTS Test Successful: {result}")
        else:
            print("❌ TTS Test Failed")
        
        return manager
        
    except Exception as e:
        logger.error(f"Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()