#!/usr/bin/env python3
"""
Real TTS Testing Script
Tests the actual TTS functionality with audio generation and playback
"""

import asyncio
import sys
import os
import tempfile
import base64
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_tts_engines():
    """Test all available TTS engines"""
    print("🎤 Testing Persian TTS Engines")
    print("=" * 40)
    
    try:
        from steve.core.tts_engine import PersianTTSEngine
        
        # Create TTS engine
        tts_engine = PersianTTSEngine()
        
        # Initialize
        print("🔧 Initializing TTS engine...")
        success = await tts_engine.initialize()
        
        if not success:
            print("❌ TTS engine initialization failed")
            return False
        
        print(f"✅ TTS engine initialized. Active: {tts_engine.active_engine}")
        
        # Test phrases
        test_phrases = [
            "سلام! من استیو هستم",
            "بله سرورم",
            "چراغ روشن شد",
            "تست سیستم تولید گفتار فارسی"
        ]
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n🧪 Test {i}: '{phrase}'")
            
            # Generate audio
            result = await tts_engine.speak_text(phrase)
            
            if result['success']:
                print(f"✅ Audio generated successfully")
                print(f"   Engine: {result.get('engine', 'unknown')}")
                print(f"   Format: {result.get('format', 'unknown')}")
                print(f"   Size: {result.get('size_bytes', 0)} bytes")
                print(f"   Duration: {result.get('duration', 0):.2f} seconds")
                
                # Save audio file for manual testing
                audio_data = base64.b64decode(result['audio_data'])
                test_file = f"test_audio_{i}.{result.get('format', 'wav')}"
                
                with open(test_file, 'wb') as f:
                    f.write(audio_data)
                
                print(f"   Saved to: {test_file}")
                
                # Try to play audio if possible
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(test_file)
                    pygame.mixer.music.play()
                    
                    print("   🔊 Playing audio...")
                    
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)
                    
                    print("   ✅ Audio playback completed")
                    
                except ImportError:
                    print("   ⚠️ pygame not available for playback test")
                except Exception as e:
                    print(f"   ⚠️ Playback error: {e}")
                
            else:
                print(f"❌ Audio generation failed: {result.get('error', 'unknown error')}")
        
        # Print engine statistics
        print("\n📊 Engine Statistics:")
        stats = tts_engine.get_engine_status()
        print(f"   Available engines: {stats['available_engines']}")
        print(f"   Active engine: {stats['active_engine']}")
        print(f"   Total requests: {stats['stats']['total_requests']}")
        print(f"   Successful requests: {stats['stats']['successful_requests']}")
        print(f"   Average generation time: {stats['stats']['average_generation_time']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ TTS testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_flask_api():
    """Test Flask API endpoints"""
    print("\n🌐 Testing Flask API")
    print("=" * 30)
    
    try:
        import requests
        import time
        
        base_url = "http://localhost:5000"
        
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        try:
            response = requests.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Health check: {health.get('status', 'unknown')}")
                print(f"   TTS ready: {health.get('tts_ready', False)}")
                print(f"   System initialized: {health.get('system_initialized', False)}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Flask server. Make sure it's running.")
            return False
        
        # Test TTS endpoint
        print("\n🎤 Testing TTS endpoint...")
        try:
            tts_data = {
                "text": "تست API سیستم تولید گفتار"
            }
            
            response = requests.post(
                f"{base_url}/api/speak",
                json=tts_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ TTS API working")
                    print(f"   Audio format: {result.get('format', 'unknown')}")
                    print(f"   Audio size: {len(result.get('audio', ''))} characters (base64)")
                    
                    # Save test audio
                    if result.get('audio'):
                        audio_data = base64.b64decode(result['audio'])
                        with open(f"api_test.{result.get('format', 'wav')}", 'wb') as f:
                            f.write(audio_data)
                        print("   Saved API test audio file")
                else:
                    print(f"❌ TTS API failed: {result.get('error', 'unknown')}")
            else:
                print(f"❌ TTS API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ TTS API test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ API testing failed: {e}")
        return False

async def main():
    """Main testing function"""
    print("🧪 Persian Voice Assistant - Real TTS Testing")
    print("=" * 50)
    
    # Test TTS engines
    tts_success = await test_tts_engines()
    
    # Test Flask API (if server is running)
    api_success = await test_flask_api()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    if tts_success:
        print("✅ TTS Engines: Working")
    else:
        print("❌ TTS Engines: Failed")
    
    if api_success:
        print("✅ Flask API: Working")
    else:
        print("❌ Flask API: Not available or failed")
    
    if tts_success:
        print("\n🎉 TTS SYSTEM IS WORKING!")
        print("🚀 Start the server with: python3 app.py")
        print("🌐 Then open: http://localhost:5000")
        return True
    else:
        print("\n❌ TTS SYSTEM NEEDS FIXES")
        print("🔧 Check the errors above and install missing dependencies")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)