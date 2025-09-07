#!/usr/bin/env python3
"""
HEYSTIVE MAIN VOICE INTEGRATION
Enhanced Persian TTS integration for the main HeyStive application
"""

import sys
import os
from pathlib import Path
import asyncio
from typing import Optional

# Add workspace to path
sys.path.insert(0, '/workspace')

from heystive.integration.voice_bridge import HeystiveVoiceBridge

class HeyStiveVoiceApp:
    """
    Main HeyStive application with enhanced Persian TTS capabilities
    """
    
    def __init__(self):
        print("🚀 Initializing HeyStive with Enhanced Persian TTS...")
        
        # Initialize voice bridge
        self.voice_bridge = HeystiveVoiceBridge()
        
        # Check if voice is available
        if not self.voice_bridge.tts_manager:
            print("⚠️ Voice system not available - running in text-only mode")
            self.voice_enabled = False
        else:
            self.voice_enabled = True
            print("✅ Voice system initialized successfully")
        
        # Get current voice configuration
        self.voice_config = self.voice_bridge.get_voice_config()
        
        print(f"🎯 Voice enabled: {self.voice_config['enabled']}")
        if self.voice_enabled:
            current_engine = self.voice_config['current_engine']
            if current_engine:
                print(f"🎤 Current voice: {current_engine['name']} ({current_engine['quality']} quality)")
    
    async def start(self):
        """Start the HeyStive application"""
        print("\n🎤 HeyStive is ready!")
        print("=" * 50)
        
        if self.voice_enabled:
            print("🔊 Voice capabilities enabled")
            print("📋 Available voice commands:")
            print("   - 'تست صدا' - Test voice system")
            print("   - 'تغییر صدا' - Change voice engine")
            print("   - 'لیست صداها' - List available voices")
            print("   - 'خاموش کردن صدا' - Disable voice")
            print("   - 'روشن کردن صدا' - Enable voice")
        else:
            print("🔇 Voice capabilities disabled")
        
        print("\n📋 General commands:")
        print("   - 'سلام' - Greeting")
        print("   - 'ساعت چنده؟' - What time is it?")
        print("   - 'امروز چه تاریخیه؟' - What's today's date?")
        print("   - 'کمک' - Help")
        print("   - 'خداحافظ' - Goodbye")
        print("=" * 50)
        
        # Start interactive session
        await self.interactive_session()
    
    async def interactive_session(self):
        """Start interactive session with voice capabilities"""
        interaction_count = 0
        
        while True:
            try:
                interaction_count += 1
                print(f"\n🎧 Interaction {interaction_count}: Waiting for your input...")
                
                # Get user input (in a real app, this would be from microphone)
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if any(exit_word in user_input.lower() for exit_word in ['exit', 'خداحافظ', 'خدافظ', 'goodbye']):
                    await self.handle_goodbye()
                    break
                
                # Handle voice-specific commands
                if self.voice_enabled and self.handle_voice_commands(user_input):
                    continue
                
                # Process regular command
                await self.process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                if self.voice_enabled:
                    self.voice_bridge.speak_persian("متاسفم، خطایی رخ داد")
    
    def handle_voice_commands(self, user_input: str) -> bool:
        """Handle voice-specific commands"""
        user_input_lower = user_input.lower()
        
        if 'تست صدا' in user_input_lower or 'test voice' in user_input_lower:
            self.test_voice_system()
            return True
        
        elif 'تغییر صدا' in user_input_lower or 'change voice' in user_input_lower:
            self.change_voice_engine()
            return True
        
        elif 'لیست صداها' in user_input_lower or 'list voices' in user_input_lower:
            self.list_voice_engines()
            return True
        
        elif 'خاموش کردن صدا' in user_input_lower or 'disable voice' in user_input_lower:
            self.disable_voice()
            return True
        
        elif 'روشن کردن صدا' in user_input_lower or 'enable voice' in user_input_lower:
            self.enable_voice()
            return True
        
        return False
    
    def test_voice_system(self):
        """Test the voice system"""
        print("🧪 Testing voice system...")
        
        test_text = "سلام! این تست سیستم صوتی HeyStive است. آیا صدای من را می‌شنوید؟"
        print(f"🔊 Speaking: '{test_text}'")
        
        success = self.voice_bridge.speak_persian(test_text)
        if success:
            print("✅ Voice test successful")
        else:
            print("❌ Voice test failed")
    
    def change_voice_engine(self):
        """Change the voice engine"""
        print("🔄 Available voice engines:")
        
        voice_options = self.voice_bridge.list_voice_options()
        if not voice_options:
            print("❌ No voice engines available")
            return
        
        # List available engines
        engine_list = list(voice_options.keys())
        for i, engine_name in enumerate(engine_list, 1):
            engine_info = voice_options[engine_name]
            current = " (CURRENT)" if engine_name == self.voice_bridge.tts_manager.current_engine else ""
            print(f"{i}. {engine_info['name']}{current}")
            print(f"   Quality: {engine_info['quality']}, Voice: {engine_info['voice_type']}")
        
        try:
            choice = input("\nSelect engine number: ").strip()
            if choice and choice.isdigit():
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(engine_list):
                    selected_engine = engine_list[selected_index]
                    success = self.voice_bridge.change_voice_engine(selected_engine)
                    if success:
                        print(f"✅ Switched to {selected_engine}")
                        # Test the new voice
                        test_text = f"سلام! من حالا با موتور {selected_engine} صحبت می‌کنم"
                        self.voice_bridge.speak_persian(test_text)
                    else:
                        print(f"❌ Failed to switch to {selected_engine}")
        except Exception as e:
            print(f"❌ Error changing voice engine: {e}")
    
    def list_voice_engines(self):
        """List all available voice engines"""
        print("🎤 Available voice engines:")
        
        voice_options = self.voice_bridge.list_voice_options()
        if not voice_options:
            print("❌ No voice engines available")
            return
        
        for engine_name, engine_info in voice_options.items():
            current = " (CURRENT)" if engine_name == self.voice_bridge.tts_manager.current_engine else ""
            print(f"• {engine_info['name']}{current}")
            print(f"  Model: {engine_info['model_path']}")
            print(f"  Quality: {engine_info['quality']}")
            print(f"  Voice: {engine_info['voice_type']} ({engine_info['accent']})")
            print(f"  Offline: {'Yes' if engine_info['offline'] else 'No'}")
            print()
    
    def disable_voice(self):
        """Disable voice functionality"""
        print("🔇 Disabling voice...")
        success = self.voice_bridge.update_voice_settings({'enabled': False})
        if success:
            self.voice_enabled = False
            print("✅ Voice disabled")
        else:
            print("❌ Failed to disable voice")
    
    def enable_voice(self):
        """Enable voice functionality"""
        print("🔊 Enabling voice...")
        success = self.voice_bridge.update_voice_settings({'enabled': True})
        if success:
            self.voice_enabled = True
            print("✅ Voice enabled")
        else:
            print("❌ Failed to enable voice")
    
    async def process_command(self, user_input: str):
        """Process a regular command"""
        print(f"🤖 Processing: '{user_input}'")
        
        # Process the command
        response = self.voice_bridge.process_voice_command(user_input)
        print(f"Response: {response}")
        
        # Speak the response if voice is enabled
        if self.voice_enabled:
            self.voice_bridge.speak_persian(response)
    
    async def handle_goodbye(self):
        """Handle goodbye command"""
        goodbye_text = "خداحافظ! امیدوارم تجربه خوبی با HeyStive داشته باشید."
        print(f"🤖 {goodbye_text}")
        
        if self.voice_enabled:
            self.voice_bridge.speak_persian(goodbye_text)

async def main():
    """Main entry point"""
    print("🚀 Starting HeyStive with Enhanced Persian TTS...")
    
    # Create and start the app
    app = HeyStiveVoiceApp()
    await app.start()

if __name__ == "__main__":
    asyncio.run(main())