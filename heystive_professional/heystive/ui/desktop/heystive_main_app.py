#!/usr/bin/env python3
"""
HEYSTIVE MAIN APPLICATION - ENHANCED PERSIAN VOICE ASSISTANT
Complete integration of Persian TTS, STT, and AI conversation capabilities
Preserves all existing functionality while adding advanced voice features
"""

import sys
import os
import asyncio
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Add workspace to path
sys.path.insert(0, '/workspace')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from heystive.integration.voice_bridge import HeystiveVoiceBridge
from heystive.voice.voice_config import VoiceConfigManager

class HeyStiveApp:
    """
    Enhanced HeyStive Application with Persian Voice Capabilities
    Integrates all existing functionality with advanced voice features
    """
    
    def __init__(self, config_path: Optional[str] = None):
        print("🚀 Initializing Enhanced HeyStive Application...")
        print("=" * 60)
        
        self.config_manager = VoiceConfigManager(config_path)
        self.voice_bridge = None
        self.running = False
        self.conversation_history = []
        
        # Initialize voice system if enabled
        if self.config_manager.get_voice_enabled():
            print("🎤 Voice system enabled - initializing voice bridge...")
            self.voice_bridge = HeystiveVoiceBridge(config_path)
        else:
            print("⚠️ Voice system disabled in configuration")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("✅ HeyStive Application initialized successfully!")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum} - shutting down gracefully...")
        self.running = False
    
    async def start_application(self):
        """Start the main HeyStive application"""
        print("\n🎯 STARTING HEYSTIVE APPLICATION")
        print("=" * 60)
        
        self.running = True
        
        # Display system status
        self._display_system_status()
        
        # Start main application loop
        await self._main_loop()
    
    def _display_system_status(self):
        """Display current system status"""
        print("\n📊 SYSTEM STATUS:")
        print("-" * 40)
        
        # Voice system status
        if self.voice_bridge:
            voice_config = self.voice_bridge.get_voice_config()
            current_engine = voice_config.get('current_engine')
            available_engines = voice_config.get('available_engines', {})
            
            print(f"🔊 Voice System: ENABLED")
            print(f"   Current Engine: {current_engine['name'] if current_engine else 'None'}")
            print(f"   Available Engines: {len(available_engines)}")
            
            if current_engine:
                print(f"   Voice Type: {current_engine['voice_type']}")
                print(f"   Quality: {current_engine['quality']}")
                print(f"   Accent: {current_engine['accent']}")
        else:
            print(f"🔇 Voice System: DISABLED")
        
        # Configuration status
        config_validation = self.config_manager.validate_config()
        print(f"⚙️ Configuration: {'VALID' if config_validation['valid'] else 'INVALID'}")
        
        if config_validation['warnings']:
            for warning in config_validation['warnings']:
                print(f"   ⚠️ Warning: {warning}")
        
        if config_validation['errors']:
            for error in config_validation['errors']:
                print(f"   ❌ Error: {error}")
        
        print()
    
    async def _main_loop(self):
        """Main application loop"""
        print("🎤 HeyStive is ready! Available commands:")
        print("   - Type 'voice' to start voice interaction")
        print("   - Type 'settings' to configure voice settings")
        print("   - Type 'engines' to list available TTS engines")
        print("   - Type 'test' to test voice system")
        print("   - Type 'help' for more commands")
        print("   - Type 'exit' to quit")
        print()
        
        while self.running:
            try:
                # Get user input
                user_input = await self._get_user_input()
                
                if not user_input:
                    continue
                
                # Process command
                await self._process_command(user_input.strip().lower())
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                print(f"❌ Error: {e}")
    
    async def _get_user_input(self) -> str:
        """Get user input (async wrapper for input())"""
        try:
            # In a real async environment, you'd use aioconsole or similar
            # For now, we'll use a simple input with timeout simulation
            return input("HeyStive> ")
        except EOFError:
            return "exit"
    
    async def _process_command(self, command: str):
        """Process user commands"""
        
        if command in ['exit', 'quit', 'bye']:
            print("👋 Goodbye!")
            self.running = False
            return
        
        elif command == 'voice':
            await self._start_voice_interaction()
        
        elif command == 'settings':
            await self._show_voice_settings()
        
        elif command == 'engines':
            await self._list_voice_engines()
        
        elif command == 'test':
            await self._test_voice_system()
        
        elif command == 'help':
            self._show_help()
        
        elif command.startswith('switch '):
            engine_name = command[7:].strip()
            await self._switch_voice_engine(engine_name)
        
        elif command.startswith('say '):
            text = command[4:].strip()
            await self._speak_text(text)
        
        else:
            # Process as a regular query
            await self._process_query(command)
    
    async def _start_voice_interaction(self):
        """Start voice interaction mode"""
        if not self.voice_bridge:
            print("❌ Voice system not available")
            return
        
        print("\n🎤 VOICE INTERACTION MODE")
        print("=" * 40)
        print("Say something or type 'back' to return to main menu")
        
        # In a full implementation, this would use actual microphone input
        # For now, we'll simulate voice interaction with text input
        
        while self.running:
            try:
                user_input = input("Voice> ").strip()
                
                if user_input.lower() in ['back', 'exit']:
                    print("Returning to main menu...")
                    break
                
                if user_input:
                    # Process voice command and speak response
                    success = self.voice_bridge.process_and_speak(user_input)
                    
                    if success:
                        print("   ✅ Voice response generated")
                    else:
                        print("   ⚠️ Voice response failed")
                    
                    # Add to conversation history
                    self.conversation_history.append({
                        'timestamp': datetime.now(),
                        'input': user_input,
                        'success': success
                    })
                
            except KeyboardInterrupt:
                print("\nExiting voice mode...")
                break
    
    async def _show_voice_settings(self):
        """Show and modify voice settings"""
        if not self.voice_bridge:
            print("❌ Voice system not available")
            return
        
        print("\n⚙️ VOICE SETTINGS")
        print("=" * 40)
        
        voice_config = self.voice_bridge.get_voice_config()
        
        print(f"Voice Enabled: {voice_config['enabled']}")
        print(f"Default Engine: {voice_config['default_engine']}")
        
        current_engine = voice_config.get('current_engine')
        if current_engine:
            print(f"Current Engine: {current_engine['name']}")
            print(f"  Voice Type: {current_engine['voice_type']}")
            print(f"  Quality: {current_engine['quality']}")
            print(f"  Accent: {current_engine['accent']}")
        
        audio_settings = voice_config.get('audio_settings', {})
        print(f"Audio Settings:")
        print(f"  Sample Rate: {audio_settings.get('sample_rate', 'N/A')}")
        print(f"  Volume: {audio_settings.get('volume', 'N/A')}")
        print(f"  Speed: {audio_settings.get('speed', 'N/A')}")
        
        user_prefs = voice_config.get('user_preferences', {})
        print(f"User Preferences:")
        print(f"  Auto Play: {user_prefs.get('auto_play', 'N/A')}")
        print(f"  Save Audio Files: {user_prefs.get('save_audio_files', 'N/A')}")
        print()
    
    async def _list_voice_engines(self):
        """List available voice engines"""
        if not self.voice_bridge:
            print("❌ Voice system not available")
            return
        
        engines = self.voice_bridge.list_voice_options()
        print(f"\n🎤 Available Voice Engines ({len(engines)}):")
        print("=" * 50)
        
        for i, (key, engine_info) in enumerate(engines.items(), 1):
            current = "✅ CURRENT" if key == self.voice_bridge.tts_manager.current_engine else ""
            print(f"{i}. {engine_info['name']} {current}")
            print(f"   Engine ID: {key}")
            print(f"   Quality: {engine_info['quality']}")
            print(f"   Voice Type: {engine_info['voice_type']} ({engine_info['accent']})")
            print(f"   Offline: {'Yes' if engine_info['offline'] else 'No'}")
            print()
        
        print("Use 'switch <engine_id>' to change engines")
        print("Example: switch kamtera_male")
        print()
    
    async def _switch_voice_engine(self, engine_name: str):
        """Switch to a different voice engine"""
        if not self.voice_bridge:
            print("❌ Voice system not available")
            return
        
        success = self.voice_bridge.change_voice_engine(engine_name)
        
        if success:
            current_info = self.voice_bridge.get_current_voice_engine()
            print(f"✅ Switched to: {current_info['name']}")
            
            # Test the new engine
            test_text = f"سلام! من الان از موتور {current_info['name']} استفاده می‌کنم"
            test_success = self.voice_bridge.speak_persian(test_text)
            
            if test_success:
                print("   ✅ Voice test successful")
            else:
                print("   ⚠️ Voice test failed")
        else:
            print(f"❌ Failed to switch to engine: {engine_name}")
    
    async def _speak_text(self, text: str):
        """Speak the provided text"""
        if not self.voice_bridge:
            print("❌ Voice system not available")
            return
        
        print(f"🔊 Speaking: '{text}'")
        success = self.voice_bridge.speak_persian(text)
        
        if success:
            print("   ✅ Speech generated successfully")
        else:
            print("   ❌ Speech generation failed")
    
    async def _test_voice_system(self):
        """Test the voice system comprehensively"""
        if not self.voice_bridge:
            print("❌ Voice system not available")
            return
        
        print("\n🧪 VOICE SYSTEM TEST")
        print("=" * 40)
        
        # Run comprehensive integration test
        test_results = self.voice_bridge.test_complete_integration()
        
        # Additional tests
        print("\n🔊 Testing individual engines...")
        engine_results = self.voice_bridge.test_voice_engines()
        
        successful_engines = sum(engine_results.values())
        total_engines = len(engine_results)
        
        print(f"\n📊 Test Summary:")
        print(f"   Integration Success Rate: {sum(test_results.values()) / len(test_results) * 100:.1f}%")
        print(f"   Working Engines: {successful_engines}/{total_engines}")
        print(f"   Conversation History: {len(self.conversation_history)} entries")
        print()
    
    async def _process_query(self, query: str):
        """Process a general query"""
        print(f"🤔 Processing query: '{query}'")
        
        if self.voice_bridge:
            # Use voice bridge to process and respond
            response = self.voice_bridge.process_voice_command(query)
            print(f"💬 Response: {response}")
            
            # Optionally speak the response
            speak_response = input("Speak response? (y/N): ").lower().startswith('y')
            if speak_response:
                success = self.voice_bridge.speak_persian(response)
                if success:
                    print("   ✅ Response spoken")
                else:
                    print("   ⚠️ Speech failed")
        else:
            # Basic text-only response
            print("💬 Voice system not available for full response processing")
            print("💬 Basic response: متوجه نشدم. سیستم صوتی فعال نیست.")
    
    def _show_help(self):
        """Show help information"""
        print("\n📖 HEYSTIVE HELP")
        print("=" * 40)
        print("Available commands:")
        print("  voice          - Start voice interaction mode")
        print("  settings       - Show voice settings")
        print("  engines        - List available TTS engines")
        print("  switch <name>  - Switch to different TTS engine")
        print("  say <text>     - Speak the provided text")
        print("  test           - Test voice system")
        print("  help           - Show this help")
        print("  exit/quit/bye  - Exit application")
        print()
        print("Persian Voice Features:")
        print("  ✅ 6 TTS engines (Kamtera, Google, System, eSpeak)")
        print("  ✅ Persian text normalization")
        print("  ✅ Voice engine switching")
        print("  ✅ Audio file generation")
        print("  ✅ Conversation processing")
        print()

async def main():
    """Main entry point"""
    try:
        # Create and start HeyStive application
        app = HeyStiveApp()
        await app.start_application()
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Application error: {e}")
    finally:
        print("🏁 HeyStive application shutdown complete")

if __name__ == "__main__":
    print("🚀 HEYSTIVE ENHANCED PERSIAN VOICE ASSISTANT")
    print("=" * 60)
    print("Complete Persian TTS/STT integration with 6 voice engines")
    print("Preserving all existing functionality while adding voice capabilities")
    print()
    
    # Run the application
    asyncio.run(main())