# Heystive Persian Voice Assistant - UI Routing Map

## Quick Navigation
- [Interface Overview](#interface-overview)
- [Legacy Interfaces](#legacy-interfaces)
- [Modern Interfaces](#modern-interfaces)
- [Launch Commands](#launch-commands)
- [Dependencies](#dependencies)
- [Port Assignments](#port-assignments)
- [Troubleshooting](#troubleshooting)

## Interface Overview

The Heystive Persian Voice Assistant project contains multiple UI implementations:

### Status Legend
- 🟢 **Active**: Fully functional and recommended
- 🟡 **Legacy**: Working but superseded by modern versions
- 🔵 **Modern**: New implementations with enhanced features

## Legacy Interfaces

### Desktop Applications
**Location**: `/workspace/heystive_professional/heystive/ui/desktop/`
**Status**: 🟡 Legacy but functional

#### Primary Desktop App
- **File**: `heystive_main_app.py`
- **Description**: Enhanced Persian voice assistant with comprehensive integration
- **Launch Command**: 
  ```bash
  cd /workspace/heystive_professional
  python3 -m heystive.ui.desktop.heystive_main_app
  ```
- **Features**: Persian TTS, STT, AI conversation capabilities

#### Modern Desktop App (Legacy)
- **File**: `modern_desktop_app.py`
- **Description**: Material Design desktop interface
- **Launch Command**:
  ```bash
  cd /workspace/heystive_professional
  python3 -m heystive.ui.desktop.modern_desktop_app
  ```
- **Features**: Enhanced UI with modern design patterns

### Web Interfaces
**Location**: `/workspace/heystive_professional/heystive/ui/web/`
**Status**: 🟡 Legacy but functional

#### Functional Web Interface
- **File**: `functional_web_interface.py`
- **Description**: Basic web interface with core functionality
- **Launch Command**:
  ```bash
  cd /workspace/heystive_professional
  python3 -m heystive.ui.web.functional_web_interface
  ```
- **Port**: 5000 (default)

#### Professional Web Interface
- **File**: `professional_web_interface.py`
- **Description**: Enhanced web interface with Persian UI/UX support
- **Launch Command**:
  ```bash
  cd /workspace/heystive_professional
  python3 -m heystive.ui.web.professional_web_interface
  ```
- **Port**: 5000 (default)
- **Features**: Real-time voice visualization, Multi-TTS engines, Persian RTL design

## Modern Interfaces

### Modern Web UI
**Location**: `/workspace/ui_modern_web/`
**Status**: 🔵 Modern - FastAPI Implementation

- **Entry Point**: `app.py`
- **Framework**: FastAPI with Jinja2 templates
- **Launch Command**:
  ```bash
  cd /workspace/ui_modern_web
  python3 app.py
  ```
- **Alternative Launch**:
  ```bash
  cd /workspace/ui_modern_web
  uvicorn app:app --host 0.0.0.0 --port 5001 --reload
  ```
- **Port**: 5001 (default)
- **Dependencies**: `requirements-web.txt`
- **Features**: Modern hybrid interface, WebSocket support, Persian language support

### Modern Desktop UI
**Location**: `/workspace/ui_modern_desktop/`
**Status**: 🔵 Modern - PySide6 Implementation

- **Entry Point**: `main_desktop.py`
- **Framework**: PySide6 with Material Design
- **Launch Command**:
  ```bash
  cd /workspace/ui_modern_desktop
  python3 main_desktop.py
  ```
- **Dependencies**: `requirements-desktop.txt`
- **Features**: Modern Material Design interface, System tray integration, Voice visualization

## Launch Commands

### Prerequisites
1. **Backend Service** (Required for all interfaces):
   ```bash
   cd /workspace/heystive_professional
   python3 main.py --mode web --port 8000
   ```

### Unified Launcher (Recommended)
The professional system includes a unified launcher:

```bash
cd /workspace/heystive_professional
python3 main.py --mode [desktop|web|cli] --port [PORT]
```

**Examples**:
```bash
# Desktop mode
python3 main.py --mode desktop

# Web mode on port 5000
python3 main.py --mode web --port 5000

# CLI mode
python3 main.py --mode cli
```

### Direct Interface Launch

#### Legacy Desktop Interfaces
```bash
# Primary desktop app
cd /workspace/heystive_professional
python3 -m heystive.ui.desktop.heystive_main_app

# Modern desktop app (legacy)
cd /workspace/heystive_professional
python3 -m heystive.ui.desktop.modern_desktop_app
```

#### Legacy Web Interfaces
```bash
# Functional web interface
cd /workspace/heystive_professional
python3 -m heystive.ui.web.functional_web_interface

# Professional web interface
cd /workspace/heystive_professional
python3 -m heystive.ui.web.professional_web_interface
```

#### Modern Interfaces
```bash
# Modern web interface
cd /workspace/ui_modern_web
python3 app.py

# Modern desktop interface
cd /workspace/ui_modern_desktop
python3 main_desktop.py
```

### Convenience Launchers
The project includes convenience launcher scripts:

```bash
# Launch modern web interface
cd /workspace
python3 start_web.py

# Launch modern desktop interface
cd /workspace
python3 start_desktop.py
```

## Dependencies

### Backend Dependencies
**File**: `/workspace/heystive_professional/requirements.txt`
**Install**:
```bash
cd /workspace/heystive_professional
pip3 install -r requirements.txt
```

**Key Dependencies**:
- Audio: pyaudio, librosa, soundfile, pygame, pydub
- Persian: gtts, hazm, persian-tools, arabic-reshaper
- AI: openai-whisper, transformers, langgraph
- Web: Flask, Flask-CORS, Flask-SocketIO

### Modern Web Dependencies
**File**: `/workspace/ui_modern_web/requirements-web.txt`
**Install**:
```bash
cd /workspace/ui_modern_web
pip3 install -r requirements-web.txt
```

**Key Dependencies**:
- FastAPI, uvicorn, jinja2
- websockets, httpx, requests
- Persian language support

### Modern Desktop Dependencies
**File**: `/workspace/ui_modern_desktop/requirements-desktop.txt`
**Install**:
```bash
cd /workspace/ui_modern_desktop
pip3 install -r requirements-desktop.txt
```

**Key Dependencies**:
- PySide6 (Qt6 framework)
- Audio processing: pyaudio, sounddevice
- System integration: psutil, pynput, plyer

## Port Assignments

| Interface | Default Port | Configurable |
|-----------|--------------|--------------|
| Backend Service | 8000 | Yes (--port) |
| Legacy Web Interfaces | 5000 | Yes |
| Modern Web Interface | 5001 | Yes |
| Desktop Interfaces | N/A | N/A |

### Port Conflict Prevention
- Backend: 8000 (API services)
- Legacy Web: 5000 
- Modern Web: 5001
- Alternative ports: 5002, 5003, etc.

## Working Directory Requirements

### Critical Path Information
- **Python Executable**: Use `python3` (located at `/usr/bin/python3`)
- **Python Version**: 3.13.3
- **Module Imports**: All legacy interfaces use Python module syntax (`-m`)

### Legacy Interfaces Working Directory
**MUST be in**: `/workspace/heystive_professional/`
```bash
cd /workspace/heystive_professional
# Then run module commands
python3 -m heystive.ui.desktop.heystive_main_app
```

### Modern Interfaces Working Directory
**Web**: `/workspace/ui_modern_web/`
**Desktop**: `/workspace/ui_modern_desktop/`

## Agent Instructions

### For Desktop Interfaces
1. **Legacy Desktop**:
   ```bash
   cd /workspace/heystive_professional
   python3 -m heystive.ui.desktop.heystive_main_app
   ```

2. **Modern Desktop**:
   ```bash
   cd /workspace/ui_modern_desktop
   python3 main_desktop.py
   ```

### For Web Interfaces
1. **Start Backend First**:
   ```bash
   cd /workspace/heystive_professional
   python3 main.py --mode web --port 8000
   ```

2. **Legacy Web**:
   ```bash
   cd /workspace/heystive_professional
   python3 -m heystive.ui.web.professional_web_interface
   ```

3. **Modern Web**:
   ```bash
   cd /workspace/ui_modern_web
   python3 app.py
   ```

## Troubleshooting

### Common Issues

#### Python Not Found
- **Issue**: `bash: python: command not found`
- **Solution**: Use `python3` instead of `python`

#### Module Import Errors
- **Issue**: `ModuleNotFoundError`
- **Solution**: Ensure you're in the correct working directory
  - Legacy interfaces: `/workspace/heystive_professional/`
  - Modern interfaces: respective directories

#### Permission Errors
- **Issue**: Permission denied when running scripts
- **Solution**: 
  ```bash
  chmod +x script_name.py
  ```

#### Port Already in Use
- **Issue**: Port conflicts
- **Solution**: Use different ports:
  ```bash
  python3 main.py --port 5002
  ```

#### Missing Dependencies
- **Issue**: Import errors for packages
- **Solution**: Install requirements in correct directory:
  ```bash
  cd [appropriate_directory]
  pip3 install -r requirements*.txt
  ```

### Dependency Installation Order
1. **Backend first**: `/workspace/heystive_professional/requirements.txt`
2. **Modern Web**: `/workspace/ui_modern_web/requirements-web.txt`
3. **Modern Desktop**: `/workspace/ui_modern_desktop/requirements-desktop.txt`

### Validation Commands
Test if interfaces are accessible:

```bash
# Test legacy desktop
cd /workspace/heystive_professional && python3 -c "from heystive.ui.desktop import heystive_main_app; print('✅ Legacy desktop accessible')"

# Test modern web
cd /workspace/ui_modern_web && python3 -c "import app; print('✅ Modern web accessible')"

# Test modern desktop  
cd /workspace/ui_modern_desktop && python3 -c "import main_desktop; print('✅ Modern desktop accessible')"
```

## Success Criteria Checklist

- ✅ All file paths verified and accessible
- ✅ Launch commands tested with correct Python executable
- ✅ Working directories clearly specified
- ✅ Dependencies mapped to specific requirement files
- ✅ Port assignments documented to prevent conflicts
- ✅ Agent-friendly instructions with exact syntax
- ✅ Fallback options and error handling included
- ✅ Single source of truth for UI navigation

---

**Last Updated**: Created by Cursor Agent
**Python Version**: 3.13.3
**Platform**: Linux 6.12.8+

This routing file serves as the definitive guide for any AI agent to locate, configure, and launch Heystive Persian Voice Assistant interfaces without ambiguity.