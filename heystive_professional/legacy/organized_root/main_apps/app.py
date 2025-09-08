#!/usr/bin/env python3
"""
Persian Voice Assistant "استیو" - Main Flask Backend
Production-ready TTS implementation with real audio generation
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import logging
import json
import base64
import tempfile
import os
import threading
import time
from pathlib import Path
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Steve components
try:
    from steve.core.tts_engine import PersianTTSEngine
    from steve.core.voice_pipeline import SteveVoiceAssistant
    from steve.utils.system_monitor import SystemPerformanceMonitor
    from steve.smart_home.device_controller import SmartHomeController
except ImportError as e:
    logger.error(f"Failed to import Steve components: {e}")
    # Create minimal fallback implementations
    class PersianTTSEngine:
        def __init__(self, config=None):
            self.initialized = False
        async def initialize(self):
            return False
        async def speak_text(self, text):
            return None
    
    class SteveVoiceAssistant:
        def __init__(self, config=None):
            pass
    
    class SystemPerformanceMonitor:
        async def assess_system_capabilities(self):
            return {"hardware_tier": "medium", "ram_gb": 8, "cpu_cores": 4}
    
    class SmartHomeController:
        def __init__(self):
            pass

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Global components
tts_engine = None
voice_assistant = None
system_monitor = None
smart_home_controller = None

# Application state
app_state = {
    'tts_ready': False,
    'system_initialized': False,
    'last_error': None,
    'initialization_time': None
}

async def initialize_steve_components():
    """Initialize all Steve Voice Assistant components"""
    global tts_engine, voice_assistant, system_monitor, smart_home_controller, app_state
    
    try:
        logger.info("🚀 Initializing Steve Voice Assistant components...")
        
        # Initialize system monitor
        system_monitor = SystemPerformanceMonitor()
        system_config = await system_monitor.assess_system_capabilities()
        logger.info(f"System assessment: {system_config['hardware_tier']} tier")
        
        # Initialize TTS engine
        logger.info("🎤 Initializing Persian TTS engine...")
        tts_engine = PersianTTSEngine(system_config)
        tts_success = await tts_engine.initialize()
        
        if tts_success:
            app_state['tts_ready'] = True
            logger.info("✅ TTS engine initialized successfully")
        else:
            logger.warning("⚠️ TTS engine initialization failed, using fallback")
            app_state['tts_ready'] = False
        
        # Initialize voice assistant
        logger.info("🎯 Initializing voice assistant...")
        voice_assistant = SteveVoiceAssistant(system_config)
        
        # Initialize smart home controller
        logger.info("🏠 Initializing smart home controller...")
        smart_home_controller = SmartHomeController()
        
        app_state['system_initialized'] = True
        app_state['initialization_time'] = time.time()
        logger.info("🎉 Steve Voice Assistant initialization complete!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        app_state['last_error'] = str(e)
        app_state['system_initialized'] = False
        return False

def run_async(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Async execution failed: {e}")
        return None

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """System health and TTS availability check"""
    try:
        health_status = {
            'status': 'healthy' if app_state['system_initialized'] else 'initializing',
            'tts_ready': app_state['tts_ready'],
            'system_initialized': app_state['system_initialized'],
            'timestamp': time.time(),
            'initialization_time': app_state['initialization_time'],
            'last_error': app_state['last_error'],
            'components': {
                'tts_engine': tts_engine is not None,
                'voice_assistant': voice_assistant is not None,
                'system_monitor': system_monitor is not None,
                'smart_home': smart_home_controller is not None
            }
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Convert Persian text to speech and return audio"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({
                'success': False,
                'error': 'Empty text provided'
            }), 400
        
        logger.info(f"TTS request for text: '{text}'")
        
        # Check if TTS is available
        if not app_state['tts_ready'] or not tts_engine:
            logger.error("TTS engine not available")
            return jsonify({
                'success': False,
                'error': 'TTS engine not available',
                'fallback_text': text
            }), 503
        
        # Generate speech audio
        audio_result = run_async(tts_engine.speak_text(text))
        
        if audio_result and audio_result.get('success'):
            logger.info(f"TTS generation successful, audio size: {len(audio_result.get('audio_data', ''))} bytes")
            return jsonify({
                'success': True,
                'text': text,
                'audio': audio_result['audio_data'],  # Base64 encoded
                'format': audio_result.get('format', 'wav'),
                'duration': audio_result.get('duration', 0),
                'timestamp': time.time()
            })
        else:
            error_msg = audio_result.get('error', 'TTS generation failed') if audio_result else 'TTS engine returned no result'
            logger.error(f"TTS generation failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg,
                'fallback_text': text
            }), 500
        
    except Exception as e:
        logger.error(f"TTS API error: {e}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'fallback_text': data.get('text', '') if 'data' in locals() else ''
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_conversation():
    """Handle text-based conversation"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        user_message = data['message'].strip()
        logger.info(f"Chat request: '{user_message}'")
        
        # Generate response (simplified for now)
        response = generate_persian_response(user_message)
        
        return jsonify({
            'success': True,
            'user_message': user_message,
            'response': response,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/voice', methods=['POST'])
def voice_interaction():
    """Complete voice interaction (TTS + conversation)"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        user_text = data['text'].strip()
        logger.info(f"Voice interaction request: '{user_text}'")
        
        # Generate conversational response
        response_text = generate_persian_response(user_text)
        
        # Convert response to speech
        if app_state['tts_ready'] and tts_engine:
            audio_result = run_async(tts_engine.speak_text(response_text))
            
            if audio_result and audio_result.get('success'):
                return jsonify({
                    'success': True,
                    'user_text': user_text,
                    'response_text': response_text,
                    'audio': audio_result['audio_data'],
                    'format': audio_result.get('format', 'wav'),
                    'timestamp': time.time()
                })
        
        # Fallback: text-only response
        return jsonify({
            'success': True,
            'user_text': user_text,
            'response_text': response_text,
            'audio': None,
            'error': 'TTS not available',
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Voice interaction error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices')
def get_devices():
    """Get smart home devices"""
    try:
        if smart_home_controller:
            devices = smart_home_controller.get_all_devices()
            return jsonify({
                'success': True,
                'devices': devices,
                'count': len(devices)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Smart home controller not available',
                'devices': {},
                'count': 0
            })
            
    except Exception as e:
        logger.error(f"Devices API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'devices': {},
            'count': 0
        }), 500

@app.route('/api/control', methods=['POST'])
def control_device():
    """Control smart home device"""
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({
                'success': False,
                'error': 'No command provided'
            }), 400
        
        persian_command = data['command'].strip()
        logger.info(f"Device control command: '{persian_command}'")
        
        if smart_home_controller:
            result = run_async(smart_home_controller.execute_persian_command(persian_command))
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': 'Smart home controller not available'
            })
            
    except Exception as e:
        logger.error(f"Device control error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_persian_response(user_input: str) -> str:
    """Generate Persian response to user input"""
    user_lower = user_input.lower()
    
    # Simple response patterns
    if any(word in user_lower for word in ["سلام", "درود", "صبح بخیر", "عصر بخیر"]):
        return "سلام! من استیو هستم. چطور می‌تونم کمکتون کنم؟"
    elif any(word in user_lower for word in ["چطوری", "حالت چطوره", "خوبی"]):
        return "من خوبم، ممنون! شما چطورید؟"
    elif any(word in user_lower for word in ["کمک", "راهنما"]):
        return "می‌تونم چراغ‌ها رو کنترل کنم، به سوالاتتون جواب بدم، و کمکتون کنم."
    elif any(word in user_lower for word in ["ساعت", "زمان"]):
        import datetime
        now = datetime.datetime.now()
        return f"الان ساعت {now.strftime('%H:%M')} است."
    elif any(word in user_lower for word in ["چراغ", "لامپ"]):
        if "روشن" in user_lower:
            return "چراغ را روشن می‌کنم."
        elif "خاموش" in user_lower:
            return "چراغ را خاموش می‌کنم."
        else:
            return "می‌خواهید چراغ را روشن کنم یا خاموش؟"
    elif "استیو" in user_lower:
        return "بله، من استیو هستم. چه کاری برات انجام بدم؟"
    else:
        return f"متوجه شدم که گفتید '{user_input}'. چطور می‌تونم کمکتون کنم؟"

def initialize_app():
    """Initialize the Flask application"""
    try:
        logger.info("🚀 Starting Persian Voice Assistant Backend...")
        
        # Run async initialization in background thread
        def init_async():
            run_async(initialize_steve_components())
        
        init_thread = threading.Thread(target=init_async, daemon=True)
        init_thread.start()
        
        logger.info("✅ Flask backend initialized")
        return True
        
    except Exception as e:
        logger.error(f"❌ App initialization failed: {e}")
        app_state['last_error'] = str(e)
        return False

if __name__ == '__main__':
    # Initialize components
    initialize_app()
    
    # Start Flask server
    logger.info("🌐 Starting Flask server on http://localhost:5000")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )