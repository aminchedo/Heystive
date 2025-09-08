# Persian TTS Models Setup Report
# گزارش راه‌اندازی مدل‌های TTS فارسی

## System Information
- **Platform**: Linux 64bit
- **RAM**: 15.6GB
- **GPU**: Not Available
- **Python**: 3.13.3

## Setup Results
- **Models Configured**: 2
- **Setup Date**: 2025-09-08 00:35:11
- **Status**: ✅ Complete

## Configured Models

### 1. Silta Persian TTS (متوسط)
- **Size**: 0.2GB
- **Hugging Face**: persian-tts/silta-persian
- **Requirements**: 2GB+ RAM, CPU only
- **Features**: Lightweight, CPU Optimized, Fast Inference
- **Location**: `heystive/models/persian_tts/silta_persian/`
- **Download Guide**: `heystive/models/persian_tts/silta_persian/DOWNLOAD_GUIDE.md`

### 2. ParsiTTS-CPU (بالا)
- **Size**: 0.5GB
- **Hugging Face**: persiannlp/parsi-tts-cpu
- **Requirements**: 4GB+ RAM, CPU optimized
- **Features**: CPU Optimized, High Quality, Persian Optimized
- **Location**: `heystive/models/persian_tts/parsi_tts_cpu/`
- **Download Guide**: `heystive/models/persian_tts/parsi_tts_cpu/DOWNLOAD_GUIDE.md`


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
