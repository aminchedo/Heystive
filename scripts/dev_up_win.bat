@echo off
REM Heystive MVP Development Startup Script
REM Windows version

echo 🚀 Heystive MVP Development Environment
echo ======================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [INFO] Python found
python --version

REM Check if we're in the right directory
if not exist "heystive_professional\backend_min.py" (
    echo [ERROR] Please run this script from the Heystive project root directory
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment activated

REM Install backend dependencies
echo [INFO] Installing backend dependencies...
pip install -r heystive_professional\requirements-core.txt
echo [SUCCESS] Backend dependencies installed

REM Install web UI dependencies
echo [INFO] Installing web UI dependencies...
pip install -r ui_modern_web\requirements-web.txt
echo [SUCCESS] Web UI dependencies installed

REM Install desktop UI dependencies
echo [INFO] Installing desktop UI dependencies...
pip install -r ui_modern_desktop\requirements-desktop.txt
echo [SUCCESS] Desktop UI dependencies installed

echo [SUCCESS] All dependencies installed successfully!

echo.
echo 🎯 Starting Heystive MVP Services
echo =================================

REM Start backend
echo [INFO] Starting backend server...
cd heystive_professional
start "Heystive Backend" python backend_min.py
cd ..
timeout /t 2 /nobreak >nul
echo [SUCCESS] Backend started

REM Start web UI
echo [INFO] Starting web UI...
cd ui_modern_web
start "Heystive Web UI" python app.py
cd ..
echo [SUCCESS] Web UI started

echo.
echo ✅ Heystive MVP is now running!
echo ===============================
echo Backend API: http://127.0.0.1:8000
echo Web Interface: http://127.0.0.1:5174
echo Health Check: http://127.0.0.1:8000/ping
echo.
echo Press any key to exit...

pause >nul
