#!/usr/bin/env python3
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
            print(f"\n📦 {model['name']} ({model['quality']})")
            print(f"   Size: {model['size_gb']}GB")
            print(f"   HuggingFace: {model['huggingface_id']}")
            print(f"   Guide: heystive/models/persian_tts/{model_id}/DOWNLOAD_GUIDE.md")
    
    print(f"\n💡 To download models:")
    print(f"1. Install: pip install huggingface_hub")
    print(f"2. Follow guides in each model's DOWNLOAD_GUIDE.md")
    print(f"3. Test with: python test_persian_tts_models.py")

if __name__ == "__main__":
    show_download_instructions()
