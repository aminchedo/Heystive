#!/usr/bin/env python3
"""
Persian TTS Model Downloader with Intelligent Management
دانلود هوشمند مدل‌های TTS فارسی از Hugging Face
"""

import os
import sys
import json
import time
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional, Callable
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class PersianTTSModelDownloader:
    """
    دانلودکننده هوشمند مدل‌های TTS فارسی
    """
    
    def __init__(self, models_dir: str = None):
        self.models_dir = Path(models_dir) if models_dir else Path(__file__).parent / "persian_tts"
        self.cache_dir = self.models_dir.parent / "cache"
        self.configs_dir = self.models_dir.parent / "configs"
        
        # ایجاد پوشه‌ها
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Heystive-Persian-TTS/1.0'
        })
        
        print("📥 Persian TTS Model Downloader")
        print("دانلودکننده مدل‌های TTS فارسی")
        print("=" * 50)
        
        # لود کانفیگ مدل‌ها
        self._load_model_configs()
    
    def _load_model_configs(self):
        """بارگذاری کانفیگ مدل‌ها"""
        self.model_configs = {
            "parsi-tts": {
                "name": "ParsiTTS",
                "huggingface_id": "persiannlp/parsi-tts",
                "files": [
                    "config.json",
                    "pytorch_model.bin",
                    "tokenizer.json",
                    "vocab.txt"
                ],
                "size_mb": 800,
                "quality": "بالا",
                "requirements": ["torch", "transformers", "librosa"],
                "gpu_recommended": True
            },
            
            "vits-persian": {
                "name": "VITS-Persian", 
                "huggingface_id": "persian-tts/vits-persian",
                "files": [
                    "config.json",
                    "G_latest.pth",
                    "symbols.txt"
                ],
                "size_mb": 600,
                "quality": "بالا",
                "requirements": ["torch", "librosa", "phonemizer"],
                "gpu_recommended": True
            },
            
            "silta-persian": {
                "name": "Silta Persian TTS",
                "huggingface_id": "persian-tts/silta-persian", 
                "files": [
                    "config.json",
                    "model.onnx",
                    "tokenizer.json"
                ],
                "size_mb": 200,
                "quality": "متوسط",
                "requirements": ["onnxruntime", "librosa"],
                "gpu_recommended": False
            },
            
            "xtts-v2": {
                "name": "XTTS-v2",
                "huggingface_id": "coqui/XTTS-v2",
                "files": [
                    "config.json",
                    "model.pth",
                    "vocab.json",
                    "speakers_xtts.pth"
                ],
                "size_mb": 2000,
                "quality": "حرفه‌ای",
                "requirements": ["torch", "torchaudio", "transformers"],
                "gpu_recommended": True,
                "gpu_required": True
            },
            
            "fastpitch-persian": {
                "name": "FastPitch-Persian",
                "huggingface_id": "persian-tts/fastpitch-persian",
                "files": [
                    "config.json", 
                    "fastpitch.pth",
                    "hifigan.pth"
                ],
                "size_mb": 400,
                "quality": "بالا",
                "requirements": ["torch", "librosa"],
                "gpu_recommended": True
            }
        }
    
    def list_available_models(self) -> List[Dict]:
        """لیست مدل‌های در دسترس"""
        models = []
        for model_id, config in self.model_configs.items():
            model_info = {
                "id": model_id,
                "name": config["name"],
                "size_mb": config["size_mb"],
                "quality": config["quality"],
                "gpu_recommended": config.get("gpu_recommended", False),
                "gpu_required": config.get("gpu_required", False),
                "downloaded": self.is_model_downloaded(model_id)
            }
            models.append(model_info)
        
        return models
    
    def is_model_downloaded(self, model_id: str) -> bool:
        """بررسی دانلود شدن مدل"""
        if model_id not in self.model_configs:
            return False
        
        model_path = self.models_dir / model_id
        if not model_path.exists():
            return False
        
        config = self.model_configs[model_id]
        required_files = config.get("files", [])
        
        for file_name in required_files:
            file_path = model_path / file_name
            if not file_path.exists():
                return False
        
        return True
    
    def get_download_url(self, huggingface_id: str, filename: str) -> str:
        """ایجاد URL دانلود از Hugging Face"""
        return f"https://huggingface.co/{huggingface_id}/resolve/main/{filename}"
    
    def download_file(self, url: str, destination: Path, 
                     progress_callback: Optional[Callable] = None) -> bool:
        """دانلود فایل با progress bar"""
        try:
            print(f"📥 Downloading: {destination.name}")
            
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            progress_callback(progress, downloaded_size, total_size)
            
            print(f"✅ Downloaded: {destination.name}")
            return True
            
        except Exception as e:
            logger.error(f"Download failed for {url}: {e}")
            if destination.exists():
                destination.unlink()  # حذف فایل ناقص
            return False
    
    def progress_callback(self, progress: float, downloaded: int, total: int):
        """نمایش پیشرفت دانلود"""
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        
        bar_length = 30
        filled_length = int(bar_length * progress / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\r[{bar}] {progress:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='')
        
        if progress >= 100:
            print()  # خط جدید در پایان
    
    def download_model(self, model_id: str, force_redownload: bool = False) -> bool:
        """دانلود مدل کامل"""
        if model_id not in self.model_configs:
            print(f"❌ Model '{model_id}' not found in configs")
            return False
        
        if self.is_model_downloaded(model_id) and not force_redownload:
            print(f"✅ Model '{model_id}' already downloaded")
            return True
        
        config = self.model_configs[model_id]
        model_path = self.models_dir / model_id
        model_path.mkdir(exist_ok=True)
        
        print(f"🚀 Downloading model: {config['name']}")
        print(f"📦 Size: ~{config['size_mb']} MB")
        print(f"🏷️ Quality: {config['quality']}")
        
        # دانلود فایل‌ها
        huggingface_id = config["huggingface_id"]
        files_to_download = config.get("files", [])
        
        downloaded_files = 0
        total_files = len(files_to_download)
        
        for file_name in files_to_download:
            file_path = model_path / file_name
            
            if file_path.exists() and not force_redownload:
                print(f"⏭️ Skipping existing: {file_name}")
                downloaded_files += 1
                continue
            
            download_url = self.get_download_url(huggingface_id, file_name)
            
            if self.download_file(download_url, file_path, self.progress_callback):
                downloaded_files += 1
            else:
                print(f"❌ Failed to download: {file_name}")
        
        # ذخیره اطلاعات مدل
        model_info_file = model_path / "model_info.json"
        model_info = {
            "id": model_id,
            "name": config["name"],
            "huggingface_id": huggingface_id,
            "download_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": files_to_download,
            "size_mb": config["size_mb"],
            "quality": config["quality"],
            "requirements": config.get("requirements", [])
        }
        
        with open(model_info_file, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, indent=2, ensure_ascii=False)
        
        success = downloaded_files == total_files
        
        if success:
            print(f"🎉 Model '{config['name']}' downloaded successfully!")
            print(f"📁 Location: {model_path}")
        else:
            print(f"⚠️ Partial download: {downloaded_files}/{total_files} files")
        
        return success
    
    def download_optimal_model(self, hardware_info: Dict) -> Optional[str]:
        """دانلود بهترین مدل بر اساس سخت‌افزار"""
        from .hardware_detector import HardwareDetector
        
        detector = HardwareDetector()
        optimal_model = detector.get_optimal_model()
        
        if not optimal_model:
            print("❌ No optimal model found for this hardware")
            return None
        
        # تبدیل نام مدل به ID
        model_id = None
        for mid, config in self.model_configs.items():
            if config["name"] == optimal_model["name"]:
                model_id = mid
                break
        
        if not model_id:
            print(f"❌ Model ID not found for: {optimal_model['name']}")
            return None
        
        print(f"🎯 Downloading optimal model: {optimal_model['name']}")
        
        if self.download_model(model_id):
            return model_id
        else:
            print("❌ Failed to download optimal model")
            return None
    
    def get_downloaded_models(self) -> List[Dict]:
        """لیست مدل‌های دانلود شده"""
        downloaded_models = []
        
        for model_id in self.model_configs.keys():
            if self.is_model_downloaded(model_id):
                model_path = self.models_dir / model_id
                info_file = model_path / "model_info.json"
                
                if info_file.exists():
                    with open(info_file, 'r', encoding='utf-8') as f:
                        model_info = json.load(f)
                    downloaded_models.append(model_info)
                else:
                    # اطلاعات پایه اگر فایل info موجود نباشد
                    config = self.model_configs[model_id]
                    downloaded_models.append({
                        "id": model_id,
                        "name": config["name"],
                        "quality": config["quality"]
                    })
        
        return downloaded_models
    
    def remove_model(self, model_id: str) -> bool:
        """حذف مدل"""
        if not self.is_model_downloaded(model_id):
            print(f"⚠️ Model '{model_id}' is not downloaded")
            return False
        
        model_path = self.models_dir / model_id
        
        try:
            import shutil
            shutil.rmtree(model_path)
            print(f"🗑️ Model '{model_id}' removed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to remove model {model_id}: {e}")
            return False
    
    def get_storage_usage(self) -> Dict:
        """محاسبه استفاده از فضای ذخیره‌سازی"""
        total_size = 0
        model_sizes = {}
        
        for model_id in self.model_configs.keys():
            if self.is_model_downloaded(model_id):
                model_path = self.models_dir / model_id
                size = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file())
                model_sizes[model_id] = size
                total_size += size
        
        return {
            "total_mb": total_size / (1024 * 1024),
            "model_sizes_mb": {k: v / (1024 * 1024) for k, v in model_sizes.items()},
            "models_count": len(model_sizes)
        }

def main():
    """تست سیستم دانلود مدل‌ها"""
    downloader = PersianTTSModelDownloader()
    
    print("\n📋 Available Persian TTS Models:")
    print("-" * 40)
    
    models = downloader.list_available_models()
    for model in models:
        status = "✅ Downloaded" if model["downloaded"] else "⬇️ Available"
        gpu_req = "🎮 GPU" if model["gpu_required"] else "💻 CPU" if not model["gpu_recommended"] else "🎮 GPU Rec."
        
        print(f"{model['name']} ({model['quality']})")
        print(f"  {status} | {model['size_mb']}MB | {gpu_req}")
        print()
    
    # نمایش مدل‌های دانلود شده
    downloaded = downloader.get_downloaded_models()
    if downloaded:
        print("📥 Downloaded Models:")
        for model in downloaded:
            print(f"  ✅ {model['name']} ({model.get('quality', 'N/A')})")
    
    # نمایش استفاده از فضا
    storage = downloader.get_storage_usage()
    print(f"\n💾 Storage Usage: {storage['total_mb']:.1f}MB ({storage['models_count']} models)")
    
    return downloader

if __name__ == "__main__":
    main()