# Heystive MVP

A minimal, runnable MVP with FastAPI backend, web UI, and desktop UI stubs.

## Quick Start

### Linux/macOS
```bash
bash scripts/dev_up.sh
```

### Windows
```cmd
scripts\dev_up_win.bat
```

## Manual Setup

1. Create virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

2. Install requirements:
```bash
pip install -r heystive_professional/requirements-core.txt
pip install -r ui_modern_web/requirements-web.txt
```

3. Start backend:
```bash
python heystive_professional/backend_min.py
```

4. Start web UI (in another terminal):
```bash
python ui_modern_web/app.py
```

## Testing

- Backend: http://127.0.0.1:8000/ping
- Web UI: http://127.0.0.1:5174/
- Desktop UI: `python ui_modern_desktop/main_desktop.py`

## API Endpoints

- `GET /ping` - Health check
- `POST /api/stt` - Speech-to-text (demo)
- `POST /api/tts` - Text-to-speech (demo)
- `WS /ws` - WebSocket echo

## Next Steps

- Add offline STT (Vosk) and TTS (pyttsx3/Coqui)
- Centralize config via `.env` and `settings.yaml`
- Migrate existing UI pieces to unified backend
- Add PyTest smoke tests