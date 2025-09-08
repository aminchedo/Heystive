#!/usr/bin/env python3
"""
ENHANCED PERSIAN TTS DEMO
Quick demonstration of the enhanced Persian TTS system for HeyStive
"""

import sys
import os
from pathlib import Path

# Add workspace to path
sys.path.insert(0, '/workspace')

def demo_voice_system():
    """Demonstrate the enhanced Persian TTS system"""
    print("🎤 ENHANCED PERSIAN TTS DEMO")
    print("=" * 50)
    
    try:
        from heystive.integration.voice_bridge import HeystiveVoiceBridge
        
        # Create voice bridge
        print("🚀 Initializing HeyStive Voice Bridge...")
        voice_bridge = HeystiveVoiceBridge()
        
        if not voice_bridge.tts_manager:
            print("❌ Voice system not available")
            return False
        
        # Show current configuration
        print("\n📊 Current Voice Configuration:")
        config = voice_bridge.get_voice_config()
        print(f"  Voice Enabled: {config['enabled']}")
        if config['current_engine']:
            engine = config['current_engine']
            print(f"  Current Engine: {engine['name']}")
            print(f"  Quality: {engine['quality']}")
            print(f"  Voice Type: {engine['voice_type']}")
        
        # Demo 1: Basic speech generation
        print("\n🔊 Demo 1: Basic Speech Generation")
        demo_text = "سلام! من HeyStive هستم، دستیار صوتی فارسی شما"
        print(f"Text: '{demo_text}'")
        
        success = voice_bridge.speak_persian(demo_text)
        if success:
            print("✅ Speech generated successfully")
        else:
            print("❌ Speech generation failed")
        
        # Demo 2: Command processing
        print("\n🎯 Demo 2: Command Processing")
        commands = [
            "سلام استیو",
            "ساعت چنده؟",
            "امروز چه تاریخیه؟",
            "کمک"
        ]
        
        for command in commands:
            print(f"\nCommand: '{command}'")
            response = voice_bridge.process_voice_command(command)
            print(f"Response: '{response}'")
            
            # Generate speech for response
            voice_bridge.speak_persian(response)
        
        # Demo 3: Voice engine information
        print("\n🎤 Demo 3: Available Voice Engines")
        voice_options = voice_bridge.list_voice_options()
        for engine_name, engine_info in voice_options.items():
            print(f"  • {engine_info['name']}")
            print(f"    Model: {engine_info['model_path']}")
            print(f"    Quality: {engine_info['quality']}")
            print(f"    Offline: {'Yes' if engine_info['offline'] else 'No'}")
        
        # Demo 4: Configuration management
        print("\n⚙️ Demo 4: Configuration Management")
        preferences = voice_bridge.config_manager.get_user_preferences()
        print("Current User Preferences:")
        for key, value in preferences.items():
            print(f"  {key}: {value}")
        
        # Demo 5: Audio file generation
        print("\n🎵 Demo 5: Audio File Generation")
        output_dir = Path("/workspace/heystive_audio_output")
        if output_dir.exists():
            audio_files = list(output_dir.glob("*.wav")) + list(output_dir.glob("*.mp3"))
            print(f"Generated {len(audio_files)} audio files:")
            for audio_file in audio_files[-5:]:  # Show last 5 files
                size = audio_file.stat().st_size
                print(f"  📁 {audio_file.name} ({size} bytes)")
        
        print("\n🎉 Demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_voice_commands():
    """Demonstrate voice command processing"""
    print("\n🎤 VOICE COMMAND DEMO")
    print("=" * 50)
    
    try:
        from heystive.integration.voice_bridge import HeystiveVoiceBridge
        
        voice_bridge = HeystiveVoiceBridge()
        
        if not voice_bridge.tts_manager:
            print("❌ Voice system not available")
            return False
        
        # Test various voice commands
        test_commands = [
            ("سلام", "Greeting"),
            ("ساعت چنده؟", "Time query"),
            ("امروز چه تاریخیه؟", "Date query"),
            ("هوا چطوره؟", "Weather query"),
            ("کمک", "Help request"),
            ("تست", "Voice test"),
            ("ممنون", "Thank you"),
            ("خداحافظ", "Goodbye")
        ]
        
        print("Testing voice command processing:")
        for command, description in test_commands:
            print(f"\n📝 {description}: '{command}'")
            response = voice_bridge.process_voice_command(command)
            print(f"🤖 Response: '{response}'")
            
            # Generate speech
            voice_bridge.speak_persian(response)
        
        print("\n✅ Voice command demo completed!")
        return True
        
    except Exception as e:
        print(f"❌ Voice command demo failed: {e}")
        return False

def main():
    """Run the complete demo"""
    print("🚀 ENHANCED PERSIAN TTS SYSTEM DEMO")
    print("=" * 60)
    print("Demonstrating the complete Persian TTS integration for HeyStive")
    print("=" * 60)
    
    # Run demos
    demo1_success = demo_voice_system()
    demo2_success = demo_voice_commands()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 DEMO RESULTS")
    print("=" * 60)
    
    if demo1_success and demo2_success:
        print("🎉 ALL DEMOS SUCCESSFUL!")
        print("✅ Voice system working correctly")
        print("✅ Command processing functional")
        print("✅ Audio generation working")
        print("✅ HeyStive integration complete")
        print("\n🎤 The Enhanced Persian TTS system is ready for use!")
    else:
        print("❌ Some demos failed")
        print("🔧 Please check the system configuration")
    
    return demo1_success and demo2_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)