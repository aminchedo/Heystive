#!/usr/bin/env python3
"""Test Persian TTS Models"""

import sys
from pathlib import Path

# Add heystive to path
sys.path.insert(0, str(Path(__file__).parent / "heystive"))

try:
    from models.intelligent_model_manager import IntelligentModelManager
    
    print("🧪 Testing Persian TTS Models")
    print("=" * 40)
    
    manager = IntelligentModelManager()
    status = manager.get_system_status()
    
    print(f"Hardware: {status['hardware']['capability_level']}")
    print(f"RAM: {status['hardware']['ram_gb']:.1f}GB")
    print(f"GPU: {'Yes' if status['hardware']['gpu_available'] else 'No'}")
    
    print(f"\nDownloaded Models: {status['models']['downloaded_count']}")
    
    if status['models']['active_model']:
        active = status['models']['active_model']
        print(f"Active Model: {active['name']}")
        
        # Test TTS generation
        result = manager.generate_tts_audio("بله سرورم")
        if result:
            print(f"✅ TTS Test Successful: {result}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all dependencies are installed")

except Exception as e:
    print(f"❌ Test failed: {e}")
