# Heystive MVP - Minimal Viable Product

## Overview

This is a minimal viable product (MVP) for the Heystive Persian Voice Assistant project. It provides a working foundation with basic functionality for development and testing.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Linux/macOS:**
```bash
bash scripts/dev_up.sh
```

**Windows:**
```cmd
scripts\dev_up_win.bat
```

### Option 2: Manual Setup

1. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

2. **Install dependencies:**
```bash
pip install -r heystive_professional/requirements-core.txt
pip install -r ui_modern_web/requirements-web.txt
pip install -r ui_modern_desktop/requirements-desktop.txt
```

3. **Start services:**
```bash
# Terminal 1 - Backend
python heystive_professional/backend_min.py

# Terminal 2 - Web UI
python ui_modern_web/app.py
```

## 📁 Project Structure

```
heystive_professional/
├── backend_min.py              # Minimal FastAPI backend
├── requirements-core.txt       # Backend dependencies
└── heystive/                   # Full backend (existing)

ui_modern_web/
├── app.py                      # Web UI server
├── requirements-web.txt        # Web UI dependencies
├── static/                     # Static assets
└── templates/                  # HTML templates

ui_modern_desktop/
├── main_desktop.py             # Desktop application
├── requirements-desktop.txt    # Desktop dependencies
└── components/                 # UI components
    ├── persian_text_widget.py  # Persian text widget
    └── system_tray_icon.py     # System tray icon

scripts/
├── dev_up.sh                   # Linux/macOS startup script
└── dev_up_win.bat             # Windows startup script
```

## 🔧 Components

### Backend (FastAPI)
- **Port:** 8000
- **Health Check:** http://127.0.0.1:8000/ping
- **Endpoints:**
  - `GET /ping` - Health check
  - `POST /api/stt` - Speech-to-text (demo)
  - `POST /api/tts` - Text-to-speech (demo)
  - `GET /api/status` - System status
  - `WebSocket /ws` - Real-time communication

### Web UI (FastAPI + HTML)
- **Port:** 5174
- **URL:** http://127.0.0.1:5174/
- **Features:**
  - Interactive buttons for testing
  - WebSocket connection
  - Persian language support
  - Modern responsive design

### Desktop UI (PySide6)
- **Features:**
  - Modern Material Design interface
  - Persian RTL support
  - System tray integration
  - Voice recording capabilities

## 🧪 Testing the MVP

### 1. Test Backend
```bash
curl http://127.0.0.1:8000/ping
```
Expected response:
```json
{
  "status": "healthy",
  "message": "Heystive MVP Backend is running",
  "timestamp": 1234567890.123,
  "service": "heystive-backend"
}
```

### 2. Test Web UI
1. Open http://127.0.0.1:5174/
2. Click "Ping" button - should show JSON response
3. Click "Open WS" then "Send" - should echo message
4. Test voice recording (if microphone available)

### 3. Test Desktop UI
```bash
python ui_modern_desktop/main_desktop.py
```

## 🔌 API Endpoints

### Health Check
```http
GET /ping
```

### Speech-to-Text (Demo)
```http
POST /api/stt
Content-Type: application/json

{
  "text": "سلام! این یک پیام تست است."
}
```

### Text-to-Speech (Demo)
```http
POST /api/tts
Content-Type: application/json

{
  "text": "سلام! من استیو هستم.",
  "voice": "default"
}
```

### WebSocket Connection
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws');
ws.send(JSON.stringify({message: "hello"}));
```

## 🛠️ Development

### Adding New Features
1. Backend: Modify `heystive_professional/backend_min.py`
2. Web UI: Modify `ui_modern_web/app.py` and templates
3. Desktop UI: Modify `ui_modern_desktop/main_desktop.py`

### Dependencies
- **Backend:** FastAPI, Uvicorn, CORS
- **Web UI:** FastAPI, Jinja2, WebSockets
- **Desktop UI:** PySide6, Audio libraries

### Configuration
- Backend runs on port 8000
- Web UI runs on port 5174
- All services use localhost/127.0.0.1

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   - Kill existing processes: `lsof -ti:8000 | xargs kill`
   - Change ports in the respective files

2. **Dependencies not found:**
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements-*.txt`

3. **WebSocket connection failed:**
   - Check if backend is running on port 8000
   - Verify firewall settings

4. **Desktop UI won't start:**
   - Install PySide6: `pip install PySide6`
   - Check display environment (for headless systems)

### Logs
- Backend logs: Console output
- Web UI logs: Console output
- Desktop UI logs: `heystive_desktop.log`

## 📋 Next Steps

1. **Integrate Real STT/TTS:**
   - Replace demo endpoints with actual voice processing
   - Add audio file handling

2. **Configuration Management:**
   - Add config files for settings
   - Environment variable support

3. **Database Integration:**
   - Add conversation history
   - User preferences storage

4. **Advanced Features:**
   - Wake word detection
   - Multi-language support
   - Plugin system

## 📄 License

This MVP is part of the Heystive project. See main project for license information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the MVP
5. Submit a pull request

---

**Note:** This is an MVP for development and testing purposes. For production use, additional security, error handling, and performance optimizations are required.