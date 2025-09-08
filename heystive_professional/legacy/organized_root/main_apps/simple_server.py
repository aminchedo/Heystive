#!/usr/bin/env python3
"""
Simple Flask server to demonstrate CORS fix for the Persian Voice Assistant
This is a minimal server that handles the API endpoints needed by the frontend
"""

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not available. Creating a simple HTTP server instead...")

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

if FLASK_AVAILABLE:
    # Flask-based server
    app = Flask(__name__)
    CORS(app)  # This enables CORS for all routes

    @app.route('/api/health')
    def health_check():
        """System health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'tts_ready': True,
            'system_initialized': True,
            'timestamp': time.time(),
            'components': {
                'tts_engine': True,
                'voice_assistant': True,
                'system_monitor': True,
                'smart_home': True
            }
        })

    @app.route('/api/speak', methods=['POST'])
    def speak_text():
        """Text-to-speech endpoint"""
        try:
            data = request.get_json()
            text = data.get('text', '')
            return jsonify({
                'success': True,
                'text': text,
                'message': 'TTS simulation successful',
                'timestamp': time.time()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/voice', methods=['POST'])
    def voice_interaction():
        """Voice interaction endpoint"""
        try:
            data = request.get_json()
            user_text = data.get('text', '')
            response_text = f"شما گفتید: {user_text}. این یک پاسخ شبیه‌سازی شده است."
            
            return jsonify({
                'success': True,
                'user_text': user_text,
                'response_text': response_text,
                'timestamp': time.time()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/chat', methods=['POST'])
    def chat_conversation():
        """Chat conversation endpoint"""
        try:
            data = request.get_json()
            message = data.get('message', '')
            response = f"پاسخ به: {message}"
            
            return jsonify({
                'success': True,
                'user_message': message,
                'response': response,
                'timestamp': time.time()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def run_flask_server():
        print("🌐 Starting Flask server with CORS enabled...")
        print("✅ CORS is configured to allow all origins")
        print("🔗 Server will be available at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)

else:
    # Simple HTTP server fallback
    class CORSHTTPRequestHandler(BaseHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()

        def do_OPTIONS(self):
            # Handle preflight requests
            self.send_response(200)
            self.end_headers()

        def do_GET(self):
            if self.path == '/api/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'status': 'healthy',
                    'tts_ready': True,
                    'system_initialized': True,
                    'timestamp': time.time(),
                    'components': {
                        'tts_engine': True,
                        'voice_assistant': True,
                        'system_monitor': True,
                        'smart_home': True
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except:
                data = {}
            
            if self.path == '/api/speak':
                text = data.get('text', '')
                response = {
                    'success': True,
                    'text': text,
                    'message': 'TTS simulation successful',
                    'timestamp': time.time()
                }
            elif self.path == '/api/voice':
                user_text = data.get('text', '')
                response_text = f"شما گفتید: {user_text}. این یک پاسخ شبیه‌سازی شده است."
                response = {
                    'success': True,
                    'user_text': user_text,
                    'response_text': response_text,
                    'timestamp': time.time()
                }
            elif self.path == '/api/chat':
                message = data.get('message', '')
                response = {
                    'success': True,
                    'user_message': message,
                    'response': f"پاسخ به: {message}",
                    'timestamp': time.time()
                }
            else:
                self.send_response(404)
                self.end_headers()
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

    def run_simple_server():
        print("🌐 Starting simple HTTP server with CORS headers...")
        print("✅ CORS headers are manually added to all responses")
        print("🔗 Server will be available at: http://localhost:5000")
        
        server = HTTPServer(('0.0.0.0', 5000), CORSHTTPRequestHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
            server.shutdown()

if __name__ == '__main__':
    print("🚀 Persian Voice Assistant - CORS Test Server")
    print("=" * 50)
    
    if FLASK_AVAILABLE:
        run_flask_server()
    else:
        run_simple_server()