@echo off
REM Persian Voice Assistant Installation Script for Windows

echo 🚀 Installing Persian Voice Assistant 'استیو'
echo ================================================

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo 🐍 Creating virtual environment...
python -m venv steve_env

REM Activate virtual environment
call steve_env\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install Python dependencies
echo 📚 Installing Python dependencies...
pip install -r requirements.txt

REM Test installation
echo 🧪 Testing installation...
python -c "import pyttsx3; import flask; import numpy; print('✅ Core dependencies installed successfully')"

REM Test TTS engines
echo 🎤 Testing TTS engines...
python -c "
try:
    import pyttsx3
    engine = pyttsx3.init()
    print('✅ pyttsx3 TTS engine available')
except Exception as e:
    print(f'⚠️ pyttsx3 issue: {e}')

try:
    from gtts import gTTS
    print('✅ Google TTS engine available')
except Exception as e:
    print(f'⚠️ gTTS issue: {e}')
"

echo.
echo 🎉 Installation completed!
echo ================================================
echo To start Steve Voice Assistant:
echo 1. steve_env\Scripts\activate.bat
echo 2. python app.py
echo 3. Open http://localhost:5000 in your browser
echo.
echo For testing: python test_tts_real.py
pause