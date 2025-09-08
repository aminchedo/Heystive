#!/usr/bin/env python3
"""
Persian Voice Assistant "استیو" (Steve)
Complete Production Implementation

Usage: python main.py
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from steve.core.voice_pipeline import SteveVoiceAssistant
from steve.utils.system_monitor import SystemPerformanceMonitor

# NEW: Optional model downloader import (safe integration)
try:
    from steve.utils.model_downloader import ModelDownloader
    MODEL_DOWNLOADER_AVAILABLE = True
except ImportError:
    MODEL_DOWNLOADER_AVAILABLE = False

async def main():
    """Main entry point for Steve Voice Assistant"""
    # NEW: Parse command line arguments (safe addition)
    parser = argparse.ArgumentParser(description="Steve Persian Voice Assistant")
    parser.add_argument("--download-models", action="store_true", 
                       help="Download missing models before starting")
    parser.add_argument("--models-tier", choices=["auto", "high", "medium", "low"], 
                       default="auto", help="Hardware tier for model selection")
    args = parser.parse_args()
    
    print("🚀 راه‌اندازی دستیار صوتی استیو...")
    print("🚀 Initializing Steve Voice Assistant...")
    
    # Initialize system monitor
    monitor = SystemPerformanceMonitor()
    system_status = await monitor.assess_system_capabilities()
    
    print(f"💻 System Profile: {system_status['hardware_tier']}")
    print(f"💾 RAM: {system_status['ram_gb']}GB")
    print(f"🖥️  CPU Cores: {system_status['cpu_cores']}")
    print(f"🎮 GPU Available: {system_status['gpu_available']}")
    
    # NEW: Optional model downloading (safe addition with try/except)
    if args.download_models and MODEL_DOWNLOADER_AVAILABLE:
        try:
            print("\n📥 Checking and downloading missing models...")
            downloader = ModelDownloader()
            
            # Use system-detected tier or user-specified tier
            tier = args.models_tier if args.models_tier != "auto" else system_status['hardware_tier']
            success = await downloader.download_missing_models(tier)
            
            if success:
                print("✅ Model download completed successfully")
            else:
                print("⚠️  Model download skipped or failed (continuing anyway)")
        except Exception as e:
            print(f"⚠️  Model download error: {e} (continuing anyway)")
    
    # Initialize Steve
    steve = SteveVoiceAssistant(system_status)
    
    try:
        # Initialize all components
        await steve.initialize()
        
        # Start voice assistant
        print("\n🎤 استیو آماده است! بگویید 'هی استیو'")
        print("🎤 Steve is ready! Say 'Hey Steve'")
        
        await steve.start_listening()
        
    except KeyboardInterrupt:
        print("\n👋 خداحافظ! Steve shutting down...")
        await steve.shutdown()
    except Exception as e:
        print(f"❌ خطای سیستم: {e}")
        print(f"❌ System Error: {e}")
        await steve.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())