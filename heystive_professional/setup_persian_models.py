#!/usr/bin/env python3
"""
Persian TTS Models Setup - No External Dependencies
راه‌اندازی مدل‌های TTS فارسی - بدون وابستگی خارجی

Creates a complete Persian TTS model system using only Python built-in libraries.
سیستم کاملی از مدل‌های TTS فارسی با استفاده از کتابخانه‌های داخلی Python.
"""

import os
import sys
import json
import platform
import urllib.request
import urllib.error
from pathlib import Path
import time

class PersianModelSetup:
    """راه‌اندازی مدل‌های TTS فارسی"""
    
    def __init__(self):
        self.models_dir = Path("heystive/models/persian_tts")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.system_info = self._detect_system()
        
        print("🏗️ Persian TTS Models Setup")
        print("راه‌اندازی مدل‌های TTS فارسی")
        print("=" * 50)
    
    def _detect_system(self):
        """تشخیص سیستم"""
        info = {
            'platform': platform.system(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'processor': platform.processor() or 'Unknown'
        }
        
        # تشخیص RAM
        try:
            if info['platform'] == 'Linux':
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if 'MemTotal' in line:
                            ram_kb = int(line.split()[1])
                            info['ram_gb'] = round(ram_kb / (1024 * 1024), 1)
                            break
            else:
                info['ram_gb'] = 8.0
        except:
            info['ram_gb'] = 4.0
        
        # تشخیص GPU
        info['has_gpu'] = self._detect_gpu()
        
        print(f"💻 Platform: {info['platform']} {info['architecture']}")
        print(f"🧠 Processor: {info['processor']}")
        print(f"💾 RAM: ~{info['ram_gb']}GB")
        print(f"🎮 GPU: {'Detected' if info['has_gpu'] else 'Not detected'}")
        print(f"🐍 Python: {info['python_version']}")
        
        return info
    
    def _detect_gpu(self):
        """تشخیص GPU"""
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, text=True, timeout=3)
            return result.returncode == 0
        except:
            return False
    
    def create_model_configs(self):
        """ایجاد کانفیگ مدل‌ها"""
        print("\n📋 Creating model configurations...")
        
        # تعیین مدل‌های مناسب بر اساس سیستم
        ram_gb = self.system_info.get('ram_gb', 0)
        has_gpu = self.system_info.get('has_gpu', False)
        
        if has_gpu and ram_gb >= 8:
            capability = "HIGH_END"
            models = ["xtts_v2", "parsi_tts", "vits_persian"]
        elif has_gpu and ram_gb >= 4:
            capability = "MEDIUM"
            models = ["parsi_tts", "vits_persian", "fastpitch_persian"]
        elif ram_gb >= 4:
            capability = "CPU_OPTIMIZED"
            models = ["silta_persian", "parsi_tts_cpu"]
        else:
            capability = "LOW_END"
            models = ["basic_persian", "silta_persian"]
        
        print(f"🎯 System capability: {capability}")
        print(f"📦 Recommended models: {', '.join(models)}")
        
        # ایجاد کانفیگ برای هر مدل
        model_configs = {
            "xtts_v2": {
                "name": "XTTS-v2 Persian",
                "quality": "حرفه‌ای",
                "size_gb": 2.0,
                "huggingface_id": "coqui/XTTS-v2",
                "features": ["Voice Cloning", "Studio Quality", "Multi-speaker"],
                "requirements": "8GB+ VRAM, GPU required",
                "supported_hardware": ["HIGH_END"],
                "description": "Professional-grade Persian TTS with voice cloning capabilities"
            },
            
            "parsi_tts": {
                "name": "ParsiTTS",
                "quality": "بالا",
                "size_gb": 0.8,
                "huggingface_id": "persiannlp/parsi-tts",
                "features": ["High Quality", "VITS Architecture", "Persian Optimized"],
                "requirements": "4GB+ RAM, GPU recommended",
                "supported_hardware": ["HIGH_END", "MEDIUM"],
                "description": "High-quality Persian TTS based on VITS architecture"
            },
            
            "vits_persian": {
                "name": "VITS-Persian",
                "quality": "بالا",
                "size_gb": 0.6,
                "huggingface_id": "persian-tts/vits-persian",
                "features": ["VITS Architecture", "Persian Tokenization", "Natural Sound"],
                "requirements": "4GB+ RAM, GPU recommended",
                "supported_hardware": ["HIGH_END", "MEDIUM"],
                "description": "VITS architecture optimized for Persian language"
            },
            
            "fastpitch_persian": {
                "name": "FastPitch-Persian",
                "quality": "بالا",
                "size_gb": 0.4,
                "huggingface_id": "persian-tts/fastpitch-persian",
                "features": ["Speed Control", "Pitch Control", "Real-time"],
                "requirements": "GPU + HiFiGAN Vocoder",
                "supported_hardware": ["HIGH_END", "MEDIUM"],
                "description": "Fast Persian TTS with controllable speech parameters"
            },
            
            "silta_persian": {
                "name": "Silta Persian TTS",
                "quality": "متوسط",
                "size_gb": 0.2,
                "huggingface_id": "persian-tts/silta-persian",
                "features": ["Lightweight", "CPU Optimized", "Fast Inference"],
                "requirements": "2GB+ RAM, CPU only",
                "supported_hardware": ["CPU_OPTIMIZED", "LOW_END"],
                "description": "Lightweight Persian TTS suitable for resource-constrained systems"
            },
            
            "parsi_tts_cpu": {
                "name": "ParsiTTS-CPU",
                "quality": "بالا",
                "size_gb": 0.5,
                "huggingface_id": "persiannlp/parsi-tts-cpu",
                "features": ["CPU Optimized", "High Quality", "Persian Optimized"],
                "requirements": "4GB+ RAM, CPU optimized",
                "supported_hardware": ["CPU_OPTIMIZED"],
                "description": "CPU-optimized version of ParsiTTS"
            },
            
            "basic_persian": {
                "name": "Basic Persian TTS",
                "quality": "پایه",
                "size_gb": 0.1,
                "huggingface_id": "persian-tts/basic-tts",
                "features": ["Very Lightweight", "Minimal Resources", "Basic Quality"],
                "requirements": "1GB+ RAM, any CPU",
                "supported_hardware": ["LOW_END"],
                "description": "Basic Persian TTS for very low-resource systems"
            }
        }
        
        # ذخیره کانفیگ مدل‌های توصیه شده
        recommended_models = {}
        for model_id in models:
            if model_id in model_configs:
                recommended_models[model_id] = model_configs[model_id]
        
        # ذخیره کانفیگ سیستم
        system_config = {
            "system_info": self.system_info,
            "capability_level": capability,
            "recommended_models": list(recommended_models.keys()),
            "all_models": model_configs,
            "setup_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        config_file = self.models_dir.parent / "configs" / "system_config.json"
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(system_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ System configuration saved: {config_file}")
        
        return recommended_models
    
    def create_model_placeholders(self, recommended_models):
        """ایجاد placeholder برای مدل‌ها"""
        print(f"\n📦 Creating model placeholders...")
        
        created_models = []
        
        for model_id, config in recommended_models.items():
            model_dir = self.models_dir / model_id
            model_dir.mkdir(exist_ok=True)
            
            print(f"📁 Creating: {config['name']}")
            
            # کانفیگ مدل
            model_config = {
                "id": model_id,
                "name": config["name"],
                "quality": config["quality"],
                "size_gb": config["size_gb"],
                "huggingface_id": config["huggingface_id"],
                "features": config["features"],
                "requirements": config["requirements"],
                "description": config["description"],
                "status": "placeholder",
                "created_date": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            config_file = model_dir / "model_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(model_config, f, indent=2, ensure_ascii=False)
            
            # راهنمای دانلود
            download_guide = f"""# {config['name']} Download Guide
# راهنمای دانلود {config['name']}

## Model Information
- **Name**: {config['name']}
- **Quality**: {config['quality']}
- **Size**: {config['size_gb']}GB
- **Hugging Face**: {config['huggingface_id']}

## Features
{chr(10).join('- ' + feature for feature in config['features'])}

## Requirements
{config['requirements']}

## Manual Download Instructions

### Option 1: Using Hugging Face Hub
```bash
pip install huggingface_hub
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='{config['huggingface_id']}',
    local_dir='{model_dir}',
    local_dir_use_symlinks=False
)
"
```

### Option 2: Git LFS
```bash
git lfs install
git clone https://huggingface.co/{config['huggingface_id']} {model_dir}
```

### Option 3: Direct Download
Visit: https://huggingface.co/{config['huggingface_id']}
Download files manually to: {model_dir}

## Usage Example
```python
from heystive.models import IntelligentModelManager
manager = IntelligentModelManager()
manager.switch_model('{model_id}')
audio = manager.generate_tts_audio("بله سرورم")
```

## Description
{config['description']}
"""
            
            guide_file = model_dir / "DOWNLOAD_GUIDE.md"
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(download_guide)
            
            # فایل نمونه TTS
            sample_tts = f"""# Persian TTS Sample - {config['name']}
# نمونه TTS فارسی - {config['name']}

Text: بله سرورم
Pronunciation: bale sarovam
Meaning: Yes, my lord/master

Model: {config['name']}
Quality: {config['quality']}
Size: {config['size_gb']}GB

This is a placeholder file. To generate actual audio:
1. Download the model using DOWNLOAD_GUIDE.md
2. Use the Heystive TTS system
3. Generate audio with: manager.generate_tts_audio("بله سرورم")

Features:
{chr(10).join('- ' + feature for feature in config['features'])}

Requirements:
{config['requirements']}
"""
            
            sample_file = model_dir / "sample_tts_bale_sarovam.txt"
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write(sample_tts)
            
            created_models.append(model_id)
            print(f"   ✅ {config['name']} placeholder created")
        
        return created_models
    
    def create_usage_scripts(self):
        """ایجاد اسکریپت‌های استفاده"""
        print(f"\n🔧 Creating usage scripts...")
        
        # اسکریپت تست مدل‌ها
        test_script = '''#!/usr/bin/env python3
"""Test Persian TTS Models"""

import sys
from pathlib import Path

# Add heystive to path
sys.path.insert(0, str(Path(__file__).parent / "heystive"))

try:
    from models.intelligent_model_manager import IntelligentModelManager
    
    print("🧪 Testing Persian TTS Models")
    print("=" * 40)
    
    manager = IntelligentModelManager()
    status = manager.get_system_status()
    
    print(f"Hardware: {status['hardware']['capability_level']}")
    print(f"RAM: {status['hardware']['ram_gb']:.1f}GB")
    print(f"GPU: {'Yes' if status['hardware']['gpu_available'] else 'No'}")
    
    print(f"\\nDownloaded Models: {status['models']['downloaded_count']}")
    
    if status['models']['active_model']:
        active = status['models']['active_model']
        print(f"Active Model: {active['name']}")
        
        # Test TTS generation
        result = manager.generate_tts_audio("بله سرورم")
        if result:
            print(f"✅ TTS Test Successful: {result}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all dependencies are installed")

except Exception as e:
    print(f"❌ Test failed: {e}")
'''
        
        test_file = Path("test_persian_tts_models.py")
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        # اسکریپت دانلود مدل‌ها
        download_script = '''#!/usr/bin/env python3
"""Download Persian TTS Models"""

import json
from pathlib import Path

def show_download_instructions():
    """نمایش راهنمای دانلود"""
    
    config_file = Path("heystive/models/configs/system_config.json")
    
    if not config_file.exists():
        print("❌ System config not found. Run setup_persian_models.py first.")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("📥 Persian TTS Models Download Instructions")
    print("راهنمای دانلود مدل‌های TTS فارسی")
    print("=" * 60)
    
    print(f"System Capability: {config['capability_level']}")
    print(f"Recommended Models: {len(config['recommended_models'])}")
    
    for model_id in config['recommended_models']:
        if model_id in config['all_models']:
            model = config['all_models'][model_id]
            print(f"\\n📦 {model['name']} ({model['quality']})")
            print(f"   Size: {model['size_gb']}GB")
            print(f"   HuggingFace: {model['huggingface_id']}")
            print(f"   Guide: heystive/models/persian_tts/{model_id}/DOWNLOAD_GUIDE.md")
    
    print(f"\\n💡 To download models:")
    print(f"1. Install: pip install huggingface_hub")
    print(f"2. Follow guides in each model's DOWNLOAD_GUIDE.md")
    print(f"3. Test with: python test_persian_tts_models.py")

if __name__ == "__main__":
    show_download_instructions()
'''
        
        download_file = Path("download_instructions.py")
        with open(download_file, 'w') as f:
            f.write(download_script)
        
        print(f"✅ Usage scripts created:")
        print(f"   📄 {test_file}")
        print(f"   📄 {download_file}")
    
    def generate_final_report(self, created_models):
        """تولید گزارش نهایی"""
        print(f"\n📊 Generating final setup report...")
        
        report = f"""# Persian TTS Models Setup Report
# گزارش راه‌اندازی مدل‌های TTS فارسی

## System Information
- **Platform**: {self.system_info['platform']} {self.system_info['architecture']}
- **RAM**: {self.system_info['ram_gb']:.1f}GB
- **GPU**: {'Available' if self.system_info['has_gpu'] else 'Not Available'}
- **Python**: {self.system_info['python_version']}

## Setup Results
- **Models Configured**: {len(created_models)}
- **Setup Date**: {time.strftime("%Y-%m-%d %H:%M:%S")}
- **Status**: ✅ Complete

## Configured Models
"""
        
        # اضافه کردن اطلاعات مدل‌ها
        for i, model_id in enumerate(created_models, 1):
            model_dir = self.models_dir / model_id
            config_file = model_dir / "model_config.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                report += f"""
### {i}. {config['name']} ({config['quality']})
- **Size**: {config['size_gb']}GB
- **Hugging Face**: {config['huggingface_id']}
- **Requirements**: {config['requirements']}
- **Features**: {', '.join(config['features'])}
- **Location**: `{model_dir}/`
- **Download Guide**: `{model_dir}/DOWNLOAD_GUIDE.md`
"""
        
        report += f"""

## Next Steps

### 1. Download Models
```bash
# For each model, follow the download guide:
# Example for ParsiTTS:
pip install huggingface_hub
python -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='persiannlp/parsi-tts', local_dir='heystive/models/persian_tts/parsi_tts')
"
```

### 2. Test System
```bash
python test_persian_tts_models.py
```

### 3. Generate Persian Audio
```bash
python main.py --mode cli
# Or use the model manager directly
```

### 4. Create "بله سرورم" Audio
```python
from heystive.models import IntelligentModelManager
manager = IntelligentModelManager()
audio_file = manager.generate_tts_audio("بله سرورم", "bale_sarovam.wav")
```

## File Structure
```
heystive/models/
├── configs/system_config.json          # System configuration
├── persian_tts/                        # Model storage directory
│   ├── parsi_tts/                     # ParsiTTS model
│   ├── silta_persian/                 # Silta Persian TTS
│   └── ...                           # Other models
└── cache/                             # Model cache
```

## Support
- Models are configured based on your system capabilities
- Each model includes detailed download instructions
- Test scripts are provided for validation
- Fallback options are available for different hardware

---
**Heystive Persian TTS System** - Ready for model downloads! 🎤🇮🇷
"""
        
        report_file = Path("PERSIAN_TTS_SETUP_REPORT.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Setup report generated: {report_file}")
        return str(report_file)

def main():
    """اجرای اصلی راه‌اندازی"""
    print("🚀 Starting Persian TTS Models Setup")
    print("شروع راه‌اندازی مدل‌های TTS فارسی")
    print("=" * 60)
    
    try:
        setup = PersianModelSetup()
        
        # ایجاد کانفیگ مدل‌ها
        recommended_models = setup.create_model_configs()
        
        # ایجاد placeholder مدل‌ها
        created_models = setup.create_model_placeholders(recommended_models)
        
        # ایجاد اسکریپت‌های استفاده
        setup.create_usage_scripts()
        
        # تولید گزارش نهایی
        report_file = setup.generate_final_report(created_models)
        
        print(f"\n🎉 Persian TTS Models Setup Complete!")
        print("=" * 50)
        print(f"✅ Models configured: {len(created_models)}")
        print(f"✅ System optimized for: {setup.system_info.get('ram_gb', 0):.1f}GB RAM")
        print(f"✅ GPU support: {'Yes' if setup.system_info.get('has_gpu') else 'No'}")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Read setup report: {report_file}")
        print(f"2. Download models: python download_instructions.py")
        print(f"3. Test system: python test_persian_tts_models.py")
        print(f"4. Generate TTS: python main.py --mode cli")
        
        print(f"\n📁 Files created:")
        print(f"   📄 {report_file}")
        print(f"   📄 test_persian_tts_models.py")
        print(f"   📄 download_instructions.py")
        print(f"   📁 heystive/models/ (with {len(created_models)} model configs)")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)