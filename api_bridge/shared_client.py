"""
Shared API Client for Heystive Modern Interfaces
Common functionality for both web and desktop interfaces
"""

import requests
import json
import asyncio
import websockets
import logging
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import time
import threading
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class HeystiveSharedClient:
    """
    Shared API client for Heystive backend integration
    Used by both web and desktop interfaces
    """
    
    def __init__(self, backend_host: str = "localhost", backend_port: int = 8000):
        self.backend_host = backend_host
        self.backend_port = backend_port
        self.base_url = f"http://{backend_host}:{backend_port}"
        self.ws_url = f"ws://{backend_host}:{backend_port}/ws"
        
        # HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Heystive-Modern-Interface/1.0.0',
            'Accept': 'application/json'
        })
        
        # WebSocket connection
        self.websocket = None
        self.ws_connected = False
        self.ws_callbacks = {}
        
        # Connection state
        self.last_health_check = 0
        self.health_check_interval = 30  # seconds
        
        logger.info(f"🔗 Shared API client initialized: {self.base_url}")
        
    async def health_check(self) -> bool:
        """Check if backend is healthy"""
        try:
            current_time = time.time()
            if current_time - self.last_health_check < self.health_check_interval:
                return True  # Skip frequent checks
                
            response = requests.get(f"{self.base_url}/health", timeout=5)
            healthy = response.status_code == 200 and response.json().get('status') == 'healthy'
            
            self.last_health_check = current_time
            return healthy
            
        except Exception as e:
            logger.warning(f"⚠️ Health check failed: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            response = self.session.get(f"{self.base_url}/api/system-status", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.debug("✅ System status retrieved")
            return data
            
        except requests.exceptions.ConnectionError:
            logger.error("❌ Cannot connect to backend")
            return self._get_offline_status()
            
        except requests.exceptions.Timeout:
            logger.error("❌ Backend request timeout")
            return self._get_timeout_status()
            
        except Exception as e:
            logger.error(f"❌ System status failed: {e}")
            return self._get_error_status(str(e))
    
    def process_voice_data(self, audio_data: bytes, audio_format: str = "wav") -> Dict[str, Any]:
        """Process voice audio data"""
        try:
            files = {
                'audio': (f'recording.{audio_format}', audio_data, f'audio/{audio_format}')
            }
            
            response = self.session.post(
                f"{self.base_url}/api/voice-process",
                files=files,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info("✅ Voice processing completed")
            return result
            
        except requests.exceptions.ConnectionError:
            return {
                'status': 'error',
                'message': 'اتصال به سرور پردازش صوت برقرار نشد'
            }
            
        except requests.exceptions.Timeout:
            return {
                'status': 'error',
                'message': 'پردازش صوت منقضی شد - لطفاً دوباره تلاش کنید'
            }
            
        except Exception as e:
            logger.error(f"❌ Voice processing failed: {e}")
            return {
                'status': 'error',
                'message': f'خطا در پردازش صوت: {str(e)}'
            }
    
    def send_text_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Send text message for conversation"""
        try:
            payload = {
                'message': message,
                'timestamp': time.time(),
                'language': 'persian'
            }
            
            if context:
                payload['context'] = context
                
            response = self.session.post(
                f"{self.base_url}/api/text-chat",
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Text message processed: {message[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"❌ Text message failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'response': 'متاسفم، پیام شما پردازش نشد. لطفاً دوباره تلاش کنید.'
            }
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available TTS voices"""
        try:
            response = self.session.get(f"{self.base_url}/api/voices", timeout=10)
            response.raise_for_status()
            
            result = response.json()
            logger.debug("✅ Available voices retrieved")
            return result
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get voices: {e}")
            return {
                'status': 'success',
                'voices': [
                    {'id': 'default', 'name': 'پیش‌فرض', 'language': 'fa'},
                    {'id': 'female', 'name': 'زنانه', 'language': 'fa'},
                    {'id': 'male', 'name': 'مردانه', 'language': 'fa'}
                ]
            }
    
    def text_to_speech(self, text: str, voice_id: str = 'default') -> Dict[str, Any]:
        """Convert text to speech"""
        try:
            params = {
                'text': text,
                'voice': voice_id
            }
            
            response = self.session.get(
                f"{self.base_url}/api/tts",
                params=params,
                timeout=20
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ TTS generated: {text[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"❌ TTS failed: {e}")
            return {
                'status': 'error',
                'message': f'خطا در تولید صوت: {str(e)}'
            }
    
    # WebSocket Methods
    async def connect_websocket(self, on_message: Callable = None, on_error: Callable = None):
        """Connect to WebSocket for real-time communication"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.ws_connected = True
            
            logger.info("🔗 WebSocket connected")
            
            # Start listening for messages
            if on_message:
                asyncio.create_task(self._listen_websocket(on_message, on_error))
                
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            self.ws_connected = False
            if on_error:
                on_error(str(e))
    
    async def _listen_websocket(self, on_message: Callable, on_error: Callable = None):
        """Listen for WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    if on_message:
                        on_message(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Invalid WebSocket message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 WebSocket connection closed")
            self.ws_connected = False
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            self.ws_connected = False
            if on_error:
                on_error(str(e))
    
    async def send_websocket_message(self, message: Dict[str, Any]) -> bool:
        """Send message via WebSocket"""
        if not self.ws_connected or not self.websocket:
            logger.warning("⚠️ WebSocket not connected")
            return False
            
        try:
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"❌ WebSocket send failed: {e}")
            return False
    
    async def close_websocket(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.ws_connected = False
            logger.info("🔌 WebSocket closed")
    
    # Voice Commands
    def send_voice_command(self, command: str) -> Dict[str, Any]:
        """Send predefined voice command"""
        try:
            payload = {
                'command': command,
                'type': 'voice_command',
                'timestamp': time.time()
            }
            
            response = self.session.post(
                f"{self.base_url}/api/voice-command",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Voice command failed: {e}")
            return {
                'status': 'error',
                'message': f'خطا در اجرای دستور: {str(e)}'
            }
    
    # Settings Management
    def get_settings(self) -> Dict[str, Any]:
        """Get current system settings"""
        try:
            response = self.session.get(f"{self.base_url}/api/settings", timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get settings: {e}")
            return {
                'status': 'success',
                'settings': {
                    'voice': {'default_voice': 'default', 'volume': 80, 'speed': 1.0},
                    'recognition': {'language': 'fa', 'sensitivity': 0.5},
                    'interface': {'theme': 'dark', 'language': 'fa'}
                }
            }
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update system settings"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/settings",
                json=settings,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("✅ Settings updated")
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Settings update failed: {e}")
            return {
                'status': 'error',
                'message': f'خطا در بروزرسانی تنظیمات: {str(e)}'
            }
    
    # Conversation History
    def get_conversation_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get conversation history"""
        try:
            params = {'limit': limit}
            response = self.session.get(
                f"{self.base_url}/api/conversation/history",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get conversation history: {e}")
            return {
                'status': 'success',
                'conversations': []
            }
    
    def clear_conversation_history(self) -> Dict[str, Any]:
        """Clear conversation history"""
        try:
            response = self.session.delete(
                f"{self.base_url}/api/conversation/history",
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("✅ Conversation history cleared")
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Failed to clear history: {e}")
            return {
                'status': 'error',
                'message': f'خطا در پاک کردن تاریخچه: {str(e)}'
            }
    
    # System Control
    def restart_voice_assistant(self) -> Dict[str, Any]:
        """Restart voice assistant components"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/system/restart",
                timeout=30
            )
            response.raise_for_status()
            
            logger.info("✅ Voice assistant restart requested")
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Restart failed: {e}")
            return {
                'status': 'error',
                'message': f'خطا در راه‌اندازی مجدد: {str(e)}'
            }
    
    def get_system_logs(self, level: str = 'INFO', limit: int = 100) -> Dict[str, Any]:
        """Get system logs"""
        try:
            params = {
                'level': level,
                'limit': limit
            }
            
            response = self.session.get(
                f"{self.base_url}/api/system/logs",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get logs: {e}")
            return {
                'status': 'success',
                'logs': []
            }
    
    # Utility Methods
    def _get_offline_status(self) -> Dict[str, Any]:
        """Return status when backend is offline"""
        return {
            'status': 'offline',
            'message': 'سرور در دسترس نیست',
            'system': {
                'cpu_usage': 'N/A',
                'memory_usage': 'N/A',
                'disk_usage': 'N/A'
            },
            'voice_assistant': {
                'status': 'offline',
                'tts_engines': []
            }
        }
    
    def _get_timeout_status(self) -> Dict[str, Any]:
        """Return status when backend times out"""
        return {
            'status': 'timeout',
            'message': 'درخواست منقضی شد',
            'system': {
                'cpu_usage': 'Timeout',
                'memory_usage': 'Timeout',
                'disk_usage': 'Timeout'
            },
            'voice_assistant': {
                'status': 'timeout',
                'tts_engines': []
            }
        }
    
    def _get_error_status(self, error_msg: str) -> Dict[str, Any]:
        """Return status when there's an error"""
        return {
            'status': 'error',
            'message': error_msg,
            'system': {
                'cpu_usage': 'Error',
                'memory_usage': 'Error',
                'disk_usage': 'Error'
            },
            'voice_assistant': {
                'status': 'error',
                'tts_engines': []
            }
        }
    
    def close(self):
        """Close all connections"""
        if self.session:
            self.session.close()
        
        if self.websocket:
            asyncio.create_task(self.close_websocket())
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class PersianTextProcessor:
    """
    Persian text processing utilities for voice assistant
    """
    
    def __init__(self):
        # Persian digits mapping
        self.persian_digits = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
        self.english_digits = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
        
        # Arabic to Persian character mapping
        self.arabic_to_persian = {
            'ي': 'ی',  # Arabic yeh to Persian yeh
            'ك': 'ک',  # Arabic kaf to Persian kaf
            'ء': 'ٔ',  # Arabic hamza to Persian hamza
            'ة': 'ه',  # Arabic teh marbuta to Persian heh
        }
    
    def to_persian_digits(self, text: str) -> str:
        """Convert English digits to Persian"""
        return text.translate(self.persian_digits)
    
    def to_english_digits(self, text: str) -> str:
        """Convert Persian digits to English"""
        return text.translate(self.english_digits)
    
    def normalize_persian_text(self, text: str) -> str:
        """Normalize Persian text by replacing Arabic characters"""
        normalized = text
        for arabic, persian in self.arabic_to_persian.items():
            normalized = normalized.replace(arabic, persian)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def is_persian_text(self, text: str) -> bool:
        """Check if text contains Persian characters"""
        persian_range = range(0x0600, 0x06FF + 1)  # Persian/Arabic Unicode range
        return any(ord(char) in persian_range for char in text)
    
    def clean_for_voice(self, text: str) -> str:
        """Clean text for voice synthesis"""
        # Normalize text
        cleaned = self.normalize_persian_text(text)
        
        # Remove HTML tags
        import re
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Remove special characters except Persian punctuation
        cleaned = re.sub(r'[^\u0600-\u06FF\s\.\!\?\،\؛\؟]', '', cleaned)
        
        # Normalize whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def format_time_persian(self, timestamp: float = None) -> str:
        """Format time in Persian"""
        import datetime
        
        if timestamp is None:
            timestamp = time.time()
            
        dt = datetime.datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%H:%M:%S")
        
        return self.to_persian_digits(time_str)
    
    def format_date_persian(self, timestamp: float = None) -> str:
        """Format date in Persian (simplified)"""
        import datetime
        
        if timestamp is None:
            timestamp = time.time()
            
        dt = datetime.datetime.fromtimestamp(timestamp)
        date_str = dt.strftime("%Y/%m/%d")
        
        return self.to_persian_digits(date_str)