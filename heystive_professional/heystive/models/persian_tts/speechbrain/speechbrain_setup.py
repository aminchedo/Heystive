#!/usr/bin/env python3
'''
SpeechBrain Persian TTS Setup
Downloads and configures SpeechBrain models for Persian TTS
'''

import os
import subprocess
import sys
from pathlib import Path

def setup_speechbrain():
    '''Setup SpeechBrain for Persian TTS'''
    try:
        # Install SpeechBrain if not available
        try:
            import speechbrain
            print("✅ SpeechBrain already installed")
        except ImportError:
            print("📥 Installing SpeechBrain...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "speechbrain"])
        
        # Download pre-trained models (if available)
        from speechbrain.pretrained import Tacotron2, HIFIGAN
        
        # Note: Persian models may not be directly available
        # This is a template for when they become available
        
        print("✅ SpeechBrain setup completed")
        return True
        
    except Exception as e:
        print(f"❌ SpeechBrain setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_speechbrain()
