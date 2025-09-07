#!/usr/bin/env python3
"""
Persian Voice Assistant "استیو" (Steve)
Complete Production Implementation

Usage: python main.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from steve.core.voice_pipeline import SteveVoiceAssistant
from steve.utils.system_monitor import SystemPerformanceMonitor

async def main():
    """Main entry point for Steve Voice Assistant"""
    print("🚀 راه‌اندازی دستیار صوتی استیو...")
    print("🚀 Initializing Steve Voice Assistant...")
    
    # Initialize system monitor
    monitor = SystemPerformanceMonitor()
    system_status = await monitor.assess_system_capabilities()
    
    print(f"💻 System Profile: {system_status['hardware_tier']}")
    print(f"💾 RAM: {system_status['ram_gb']}GB")
    print(f"🖥️  CPU Cores: {system_status['cpu_cores']}")
    print(f"🎮 GPU Available: {system_status['gpu_available']}")
    
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