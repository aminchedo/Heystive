# Silta Persian TTS Download Guide
# راهنمای دانلود Silta Persian TTS

## Model Information
- **Name**: Silta Persian TTS
- **Quality**: متوسط
- **Size**: 0.2GB
- **Hugging Face**: persian-tts/silta-persian

## Features
- Lightweight
- CPU Optimized
- Fast Inference

## Requirements
2GB+ RAM, CPU only

## Manual Download Instructions

### Option 1: Using Hugging Face Hub
```bash
pip install huggingface_hub
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='persian-tts/silta-persian',
    local_dir='heystive/models/persian_tts/silta_persian',
    local_dir_use_symlinks=False
)
"
```

### Option 2: Git LFS
```bash
git lfs install
git clone https://huggingface.co/persian-tts/silta-persian heystive/models/persian_tts/silta_persian
```

### Option 3: Direct Download
Visit: https://huggingface.co/persian-tts/silta-persian
Download files manually to: heystive/models/persian_tts/silta_persian

## Usage Example
```python
from heystive.models import IntelligentModelManager
manager = IntelligentModelManager()
manager.switch_model('silta_persian')
audio = manager.generate_tts_audio("بله سرورم")
```

## Description
Lightweight Persian TTS suitable for resource-constrained systems
