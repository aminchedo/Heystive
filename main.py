#!/usr/bin/env python3
"""
Persian Voice Assistant "استیو" (Steve)
Complete Production Implementation with Web Interface

Usage: python main.py
"""

import asyncio
import sys
import os
import signal
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from steve.core.voice_pipeline import SteveVoiceAssistant
from steve.utils.system_monitor import SystemPerformanceMonitor
from steve.ui.web_interface import SteveWebInterface
from steve.smart_home.device_controller import SmartHomeController

class CompleteVoiceAssistant:
    """
    Complete Persian Voice Assistant with all components integrated
    Includes voice processing, web interface, and smart home control
    """
    
    def __init__(self):
        """Initialize complete voice assistant with all components"""
        print("🚀 Initializing Complete Persian Voice Assistant...")
        
        # System assessment
        self.system_monitor = SystemPerformanceMonitor()
        self.system_config = None
        self.web_interface = None
        self.voice_assistant = None
        self.smart_home_controller = None
        
        # Component status tracking
        self.components_status = {
            'system_monitor': False,
            'tts_engine': False, 
            'stt_engine': False,
            'wake_word_detector': False,
            'smart_home_controller': False,
            'voice_pipeline': False,
            'web_interface': False
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        asyncio.create_task(self.shutdown())

    async def initialize_all_components(self):
        """Initialize all system components with error handling"""
        try:
            # 1. System assessment
            print("📊 Assessing system capabilities...")
            self.system_config = await self.system_monitor.assess_system_capabilities()
            self.components_status['system_monitor'] = True
            print(f"✅ System: {self.system_config['hardware_tier']} tier, {self.system_config['ram_gb']}GB RAM")
            
            # 2. Initialize smart home controller
            print("🏠 Initializing smart home controller...")
            self.smart_home_controller = SmartHomeController()
            # Give it time to discover devices
            await asyncio.sleep(2)
            self.components_status['smart_home_controller'] = True
            print("✅ Smart home controller initialized")
            
            # 3. Initialize voice assistant with system config
            print("🎤 Initializing voice assistant...")
            self.voice_assistant = SteveVoiceAssistant(self.system_config)
            await self.voice_assistant.initialize()
            self.components_status['voice_pipeline'] = True
            print("✅ Voice assistant initialized")
            
            # 4. Test all voice components
            print("🧪 Testing voice components...")
            await self._test_voice_components()
            
            # 5. Initialize web interface
            print("🌐 Starting web interface...")
            self.web_interface = SteveWebInterface(self.voice_assistant)
            web_url = self.web_interface.start_server()
            self.components_status['web_interface'] = True
            print(f"✅ Web interface available at: {web_url}")
            
            # 6. Start voice assistant
            print("🎙️ Starting voice assistant...")
            await self.voice_assistant.start_listening()
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _test_voice_components(self):
        """Test all voice components systematically"""
        print("🧪 Voice Component Testing:")
        
        # Test TTS
        try:
            await self.voice_assistant.test_tts_output("تست سیستم تولید گفتار")
            self.components_status['tts_engine'] = True
            print("✅ TTS: Working")
        except Exception as e:
            print(f"❌ TTS Failed: {e}")
            
        # Test Wake Word
        try:
            await self.voice_assistant.test_wake_word_response()
            self.components_status['wake_word_detector'] = True
            print("✅ Wake Word: Working")
        except Exception as e:
            print(f"❌ Wake Word Failed: {e}")
            
        # Test STT  
        try:
            stt_ready = await self.voice_assistant.test_stt_ready()
            self.components_status['stt_engine'] = stt_ready
            print(f"✅ STT: {'Working' if stt_ready else 'Limited'}")
        except Exception as e:
            print(f"❌ STT Failed: {e}")
    
    def get_complete_status(self):
        """Get complete system status for web interface"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_config': self.system_config,
            'components_status': self.components_status,
            'tts_ready': self.components_status['tts_engine'],
            'stt_ready': self.components_status['stt_engine'], 
            'wake_word_ready': self.components_status['wake_word_detector'],
            'devices': self.voice_assistant.get_discovered_devices() if self.voice_assistant else {},
            'listening': self.voice_assistant.is_listening if self.voice_assistant else False
        }
    
    async def run_forever(self):
        """Keep assistant running until interrupted"""
        print("\n🎉 Steve Voice Assistant is running!")
        print("🌐 Web interface: http://localhost:5000")
        print("🎤 Say 'هی استیو' to interact")
        print("⚠️ Press Ctrl+C to stop")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Steve Voice Assistant...")
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown of all components"""
        print("🔌 Shutting down all components...")
        
        try:
            if self.voice_assistant:
                await self.voice_assistant.stop_listening()
                await self.voice_assistant.shutdown()
                print("✅ Voice assistant stopped")
            
            if self.web_interface:
                self.web_interface.stop_server()
                print("✅ Web interface stopped")
            
            if self.smart_home_controller:
                await self.smart_home_controller.cleanup()
                print("✅ Smart home controller stopped")
            
            print("👋 Steve Voice Assistant stopped successfully")
            
        except Exception as e:
            print(f"❌ Shutdown error: {e}")

async def main():
    """Main application entry point"""
    print("🎤 Persian Voice Assistant 'استیو' - Starting...")
    print("=" * 60)
    
    # Create and initialize complete assistant
    assistant = CompleteVoiceAssistant()
    
    # Initialize all components
    success = await assistant.initialize_all_components()
    
    if success:
        # Run until interrupted
        await assistant.run_forever()
    else:
        print("❌ Failed to initialize. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)