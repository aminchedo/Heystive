#!/bin/bash
# Persian Voice Assistant Installation Script for Linux/macOS

echo "🚀 Installing Persian Voice Assistant 'استیو'"
echo "================================================"

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Detected Linux system"
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev libasound2-dev espeak espeak-data
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS system"
    if command -v brew &> /dev/null; then
        brew install portaudio espeak
    else
        echo "⚠️ Homebrew not found. Please install PortAudio manually."
    fi
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv steve_env

# Activate virtual environment
source steve_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import pyttsx3
import flask
import numpy
print('✅ Core dependencies installed successfully')
"

# Test TTS engines
echo "🎤 Testing TTS engines..."
python3 -c "
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

echo ""
echo "🎉 Installation completed!"
echo "================================================"
echo "To start Steve Voice Assistant:"
echo "1. source steve_env/bin/activate"
echo "2. python3 app.py"
echo "3. Open http://localhost:5000 in your browser"
echo ""
echo "For testing: python3 test_tts_real.py"