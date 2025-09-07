#!/bin/bash
# Safe Installation Script for Heystive Persian Voice Assistant
# Compatible with externally-managed Python environments (PEP 668)

set -e

echo "🚀 Heystive Persian Voice Assistant - Safe Installation"
echo "=" * 60

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $python_version"

if [ "$(echo "$python_version < 3.8" | bc -l)" -eq 1 ]; then
    echo "❌ Error: Python 3.8+ required, found $python_version"
    exit 1
fi

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "📦 Virtual environment detected: $VIRTUAL_ENV"
else
    echo "🌍 System Python detected - creating virtual environment..."
    
    # Create virtual environment
    python3 -m venv .venv
    echo "✅ Virtual environment created: .venv"
    echo "📋 To activate: source .venv/bin/activate"
    echo "   Then re-run this script"
    exit 0
fi

echo "🔧 Installing dependencies in virtual environment..."

# Upgrade pip and core tools
echo "📦 Upgrading pip and core tools..."
python -m pip install --upgrade pip setuptools wheel

# Install core dependencies first (order matters)
echo "📦 Installing core dependencies..."
python -m pip install numpy==2.3.2
python -m pip install scipy==1.11.4

# Install audio processing dependencies
echo "🎵 Installing audio dependencies..."
python -m pip install librosa==0.10.1
python -m pip install soundfile==0.12.1 || python -m pip install soundfile==0.13.1
python -m pip install pydub==0.25.1
python -m pip install pygame==2.6.1

# Install TTS engines
echo "🎤 Installing TTS engines..."
python -m pip install pyttsx3==2.99
python -m pip install gtts==2.5.4

# Install STT dependencies
echo "🎙️ Installing STT dependencies..."
python -m pip install SpeechRecognition==3.14.3
python -m pip install openai-whisper==20231117

# Install ML dependencies
echo "🤖 Installing ML dependencies..."
python -m pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install transformers==4.35.2
python -m pip install accelerate==0.24.1

# Install Persian language processing
echo "🇮🇷 Installing Persian language processing..."
python -m pip install hazm==0.7.0
python -m pip install persian-tools==0.0.7
python -m pip install arabic-reshaper==3.0.0
python -m pip install python-bidi==0.4.2

# Install system utilities
echo "⚙️ Installing system utilities..."
python -m pip install psutil==5.9.6
python -m pip install requests==2.31.0
python -m pip install python-dotenv==1.0.0
python -m pip install colorama==0.4.6
python -m pip install tqdm==4.66.1
python -m pip install PyYAML==6.0.1

# Install web framework dependencies
echo "🌐 Installing web dependencies..."
python -m pip install aiohttp==3.9.1
python -m pip install websockets==12.0

# Try to install PyAudio (may fail without system libraries)
echo "🔊 Installing audio I/O (may require system libraries)..."
python -m pip install pyaudio==0.2.11 || {
    echo "⚠️ PyAudio installation failed"
    echo "   On Ubuntu/Debian: sudo apt-get install portaudio19-dev"
    echo "   On macOS: brew install portaudio"
    echo "   On Windows: Use pre-compiled wheel"
}

# Install optional dependencies
echo "📱 Installing optional dependencies..."
python -m pip install duckdb==0.9.2 || echo "⚠️ DuckDB installation failed"

echo ""
echo "✅ Installation completed!"
echo "🧪 Test the installation:"
echo "   python3 test_tts_real.py"
echo ""
echo "🚀 Start the voice assistant:"
echo "   python3 main.py"
echo ""
echo "🌐 Start the web interface:"
echo "   python3 app.py"
echo ""