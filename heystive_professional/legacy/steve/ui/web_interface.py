"""
Steve Voice Assistant - Web Interface
Professional web interface for Persian Voice Assistant with real-time status and control
"""

from flask import Flask, render_template, jsonify, request, session
import asyncio
import threading
import json
from datetime import datetime
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SteveWebInterface:
    """
    Professional web interface for Steve Voice Assistant
    Provides real-time status, device control, and voice testing
    """
    
    def __init__(self, voice_assistant):
        """Initialize web interface with voice assistant reference"""
        self.voice_assistant = voice_assistant
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        self.app.secret_key = 'steve_voice_assistant_2024_secure_key'
        
        # Web interface state
        self.is_running = False
        self.server_thread = None
        
        # Setup routes
        self.setup_routes()
        
        logger.info("Steve Web Interface initialized")
        
        # NEW: Add monitoring endpoints (safe addition)
        self._add_monitoring_endpoints()
        
    def setup_routes(self):
        """Setup all web interface routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main professional dashboard page"""
            return render_template('professional-dashboard.html')
        
        @self.app.route('/legacy')
        def legacy_dashboard():
            """Legacy dashboard for compatibility"""
            return render_template('dashboard.html')
        
        @self.app.route('/enhanced')
        def enhanced_dashboard():
            """NEW: Enhanced dashboard with monitoring features"""
            return render_template('enhanced-dashboard.html')
            
        @self.app.route('/api/status')
        def get_system_status():
            """Get complete system status"""
            try:
                status = self.voice_assistant.get_complete_status()
                return jsonify(status)
            except Exception as e:
                logger.error(f"Status API error: {e}")
                return jsonify({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/voice/test-tts', methods=['POST'])
        def test_tts():
            """Test TTS output"""
            try:
                data = request.get_json()
                text = data.get('text', 'سلام! تست سیستم استیو')
                
                # Test TTS in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(
                    self.voice_assistant.test_tts_output(text)
                )
                loop.close()
                
                return jsonify({
                    'success': success,
                    'text': text,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"TTS test error: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/voice/start-listening', methods=['POST'])
        def start_voice_listening():
            """Start voice detection"""
            try:
                # Start wake word detection in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.voice_assistant.start_wake_word_detection()
                )
                loop.close()
                
                return jsonify({
                    'listening': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Voice listening start error: {e}")
                return jsonify({
                    'listening': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/voice/stop-listening', methods=['POST'])
        def stop_voice_listening():
            """Stop voice detection"""
            try:
                # Stop wake word detection in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    self.voice_assistant.stop_listening()
                )
                loop.close()
                
                return jsonify({
                    'listening': False,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Voice listening stop error: {e}")
                return jsonify({
                    'listening': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/devices')
        def get_smart_devices():
            """Get discovered smart home devices"""
            try:
                devices = self.voice_assistant.get_discovered_devices()
                return jsonify({
                    'devices': devices,
                    'count': len(devices),
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Devices API error: {e}")
                return jsonify({
                    'devices': {},
                    'count': 0,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/devices/control', methods=['POST'])
        def control_device():
            """Execute smart home device command"""
            try:
                data = request.get_json()
                command = data.get('persian_command', '')
                
                if not command:
                    return jsonify({
                        'success': False,
                        'error': 'No command provided',
                        'timestamp': datetime.now().isoformat()
                    }), 400
                
                # Execute command in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.voice_assistant.execute_device_command(command)
                )
                loop.close()
                
                return jsonify({
                    'success': result.get('success', False),
                    'response': result.get('response', ''),
                    'command': command,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Device control error: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/performance')
        def get_performance_stats():
            """Get performance statistics"""
            try:
                stats = self.voice_assistant.get_performance_report()
                return jsonify({
                    'performance_report': stats,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Performance API error: {e}")
                return jsonify({
                    'performance_report': 'Performance data unavailable',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'Steve Voice Assistant Web Interface',
                'timestamp': datetime.now().isoformat()
            })
    
    def start_server(self, host='0.0.0.0', port=5000):
        """Start web server in background thread"""
        if self.is_running:
            return f"http://{host}:{port}"
            
        def run_server():
            try:
                self.app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)
            except Exception as e:
                logger.error(f"Web server error: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True
        
        logger.info(f"Web interface started at http://{host}:{port}")
        return f"http://{host}:{port}"
    
    def stop_server(self):
        """Stop web server"""
        if self.is_running:
            self.is_running = False
            logger.info("Web interface stopped")
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get web server status"""
        return {
            'is_running': self.is_running,
            'server_thread_alive': self.server_thread.is_alive() if self.server_thread else False,
            'voice_assistant_connected': self.voice_assistant is not None
        }
    
    def _add_monitoring_endpoints(self):
        """
        NEW: Add monitoring endpoints without breaking existing APIs
        Safe addition that enhances functionality
        """
        try:
            from steve.utils.monitoring_endpoints import register_monitoring_routes
            register_monitoring_routes(self.app)
            logger.info("Enhanced monitoring endpoints added successfully")
        except ImportError as e:
            logger.warning(f"Monitoring endpoints not available: {e}")
        except Exception as e:
            logger.error(f"Failed to add monitoring endpoints: {e}")