# ParsiTTS-CPU Download Guide
# راهنمای دانلود ParsiTTS-CPU

## Model Information
- **Name**: ParsiTTS-CPU
- **Quality**: بالا
- **Size**: 0.5GB
- **Hugging Face**: persiannlp/parsi-tts-cpu

## Features
- CPU Optimized
- High Quality
- Persian Optimized

## Requirements
4GB+ RAM, CPU optimized

## Manual Download Instructions

### Option 1: Using Hugging Face Hub
```bash
pip install huggingface_hub
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='persiannlp/parsi-tts-cpu',
    local_dir='heystive/models/persian_tts/parsi_tts_cpu',
    local_dir_use_symlinks=False
)
"
```

### Option 2: Git LFS
```bash
git lfs install
git clone https://huggingface.co/persiannlp/parsi-tts-cpu heystive/models/persian_tts/parsi_tts_cpu
```

### Option 3: Direct Download
Visit: https://huggingface.co/persiannlp/parsi-tts-cpu
Download files manually to: heystive/models/persian_tts/parsi_tts_cpu

## Usage Example
```python
from heystive.models import IntelligentModelManager
manager = IntelligentModelManager()
manager.switch_model('parsi_tts_cpu')
audio = manager.generate_tts_audio("بله سرورم")
```

## Description
CPU-optimized version of ParsiTTS
