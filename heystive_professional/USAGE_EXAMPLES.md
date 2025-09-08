# Heystive Usage Examples 🎤

## Quick Start Commands

### Desktop Mode (Default)
```bash
python main.py
# or
python main.py --mode desktop
```

### Web Interface
```bash
python main.py --mode web
python main.py --mode web --port 8080
python main.py --mode web --debug
```

### CLI Interface
```bash
python main.py --mode cli
```

## Persian TTS Testing

### Test Persian Audio Generation
```bash
python test_advanced_persian_tts.py
```

### Generated Audio Files
- `audio_output/bale_sarovam_tones.wav` - Musical tone representation
- `audio_output/bale_sarovam_beeps.wav` - Beep sequence representation
- `audio_output/bale_sarovam_analysis.txt` - Detailed text analysis

## Persian Text: بله سرورم
- **Pronunciation:** bale sarovam
- **Meaning:** Yes, my lord/master
- **Context:** Respectful response to a command
- **Audio:** Available in multiple formats

## System Requirements
- Python 3.8+
- Audio system (for voice functionality)
- Network connection (for AI features)

## Installation
```bash
pip install -r requirements.txt
python scripts/comprehensive_validation.py
```

## Features Tested ✅
- Persian TTS engine architecture
- Multi-interface support (desktop/web/CLI)
- Persian text processing
- Audio file generation
- Professional project structure
