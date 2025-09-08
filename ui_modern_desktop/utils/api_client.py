"""
API Client for Heystive Desktop Application
Handles communication with the backend voice processing system
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import tempfile
import time

logger = logging.getLogger(__name__)

class HeystiveAPIClient:
    """
    API client for communicating with Heystive backend services
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = 30  # seconds
        
        # Configure session
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Heystive-Desktop/1.0.0'
        })
        
        logger.info(f"🔗 API Client initialized: {self.base_url}")
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to API endpoint
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                return {'status': 'success', 'data': response.text}
                
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Connection failed: {url}")
            raise Exception("اتصال به سرور برقرار نشد")
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ Request timeout: {url}")
            raise Exception("درخواست منقضی شد")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP error {e.response.status_code}: {url}")
            
            try:
                error_data = e.response.json()
                error_msg = error_data.get('message', f'خطای HTTP {e.response.status_code}')
            except:
                error_msg = f'خطای HTTP {e.response.status_code}'
                
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            raise Exception(f"خطا در درخواست: {str(e)}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status
        """
        try:
            response = self._make_request('GET', '/api/system-status')
            logger.debug("✅ System status retrieved")
            return response
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get system status: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'system': {
                    'cpu_usage': 'N/A',
                    'memory_usage': 'N/A',
                    'disk_usage': 'N/A'
                },
                'voice_assistant': {
                    'status': 'unknown',
                    'tts_engines': []
                }
            }
    
    def process_voice_data(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process voice audio data
        """
        try:
            # Create multipart form data
            files = {
                'audio': ('recording.wav', audio_data, 'audio/wav')
            }
            
            # Remove JSON content-type for multipart request
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{self.base_url}/api/voice-process",
                files=files,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info("✅ Voice processing completed")
            return result
            
        except requests.exceptions.ConnectionError:
            logger.error("❌ Voice processing connection failed")
            return {
                'status': 'error',
                'message': 'اتصال به سرور پردازش صوت برقرار نشد'
            }
            
        except requests.exceptions.Timeout:
            logger.error("❌ Voice processing timeout")
            return {
                'status': 'error',
                'message': 'پردازش صوت منقضی شد'
            }
            
        except Exception as e:
            logger.error(f"❌ Voice processing failed: {e}")
            return {
                'status': 'error',
                'message': f'خطا در پردازش صوت: {str(e)}'
            }
    
    def send_text_message(self, message: str) -> Dict[str, Any]:
        """
        Send text message for processing
        """
        try:
            data = {
                'message': message,
                'timestamp': time.time(),
                'language': 'persian'
            }
            
            response = self._make_request('POST', '/api/text-chat', json=data)
            logger.info(f"✅ Text message sent: {message[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to send text message: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'response': 'متاسفم، پیام شما پردازش نشد'
            }
    
    def get_available_voices(self) -> Dict[str, Any]:
        """
        Get list of available TTS voices
        """
        try:
            response = self._make_request('GET', '/api/voices')
            logger.debug("✅ Available voices retrieved")
            return response
            
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
    
    def text_to_speech(self, text: str, voice: str = 'default') -> Dict[str, Any]:
        """
        Convert text to speech
        """
        try:
            params = {
                'text': text,
                'voice': voice
            }
            
            response = self._make_request('GET', '/api/tts', params=params)
            logger.info(f"✅ TTS generated for: {text[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ TTS failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def set_voice_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update voice settings
        """
        try:
            response = self._make_request('POST', '/api/settings/voice', json=settings)
            logger.info("✅ Voice settings updated")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to update voice settings: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_conversation_history(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get conversation history
        """
        try:
            params = {'limit': limit}
            response = self._make_request('GET', '/api/conversation/history', params=params)
            logger.debug(f"✅ Conversation history retrieved ({limit} items)")
            return response
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get conversation history: {e}")
            return {
                'status': 'success',
                'conversations': []
            }
    
    def clear_conversation_history(self) -> Dict[str, Any]:
        """
        Clear conversation history
        """
        try:
            response = self._make_request('DELETE', '/api/conversation/history')
            logger.info("✅ Conversation history cleared")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to clear conversation history: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_wake_word_status(self) -> Dict[str, Any]:
        """
        Get wake word detection status
        """
        try:
            response = self._make_request('GET', '/api/wake-word/status')
            logger.debug("✅ Wake word status retrieved")
            return response
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get wake word status: {e}")
            return {
                'status': 'unknown',
                'active': False,
                'sensitivity': 0.5
            }
    
    def set_wake_word_sensitivity(self, sensitivity: float) -> Dict[str, Any]:
        """
        Set wake word detection sensitivity
        """
        try:
            data = {'sensitivity': sensitivity}
            response = self._make_request('POST', '/api/wake-word/sensitivity', json=data)
            logger.info(f"✅ Wake word sensitivity set to {sensitivity}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to set wake word sensitivity: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def health_check(self) -> bool:
        """
        Check if the API is healthy
        """
        try:
            response = self._make_request('GET', '/health')
            return response.get('status') == 'healthy'
            
        except Exception:
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information
        """
        try:
            response = self._make_request('GET', '/api/info')
            return response
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'version': 'unknown',
                'features': []
            }
    
    def upload_audio_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload audio file for processing
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"فایل یافت نشد: {file_path}")
            
            with open(file_path, 'rb') as audio_file:
                files = {
                    'audio': (file_path.name, audio_file, 'audio/wav')
                }
                
                headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
                
                response = requests.post(
                    f"{self.base_url}/api/voice-process",
                    files=files,
                    headers=headers,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"✅ Audio file processed: {file_path.name}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Audio file upload failed: {e}")
            return {
                'status': 'error',
                'message': f'خطا در آپلود فایل: {str(e)}'
            }
    
    def get_system_logs(self, level: str = 'INFO', limit: int = 100) -> Dict[str, Any]:
        """
        Get system logs
        """
        try:
            params = {
                'level': level,
                'limit': limit
            }
            
            response = self._make_request('GET', '/api/system/logs', params=params)
            logger.debug(f"✅ System logs retrieved ({limit} entries)")
            return response
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get system logs: {e}")
            return {
                'status': 'success',
                'logs': []
            }
    
    # Context manager support
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def close(self):
        """Close the API client session"""
        if self.session:
            self.session.close()
            logger.info("🔌 API Client session closed")


class APIClientPool:
    """
    Pool of API clients for load balancing
    """
    
    def __init__(self, base_urls: List[str]):
        self.clients = [HeystiveAPIClient(url) for url in base_urls]
        self.current_index = 0
        
    def get_client(self) -> HeystiveAPIClient:
        """Get next available client (round-robin)"""
        client = self.clients[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client
        
    def get_healthy_client(self) -> Optional[HeystiveAPIClient]:
        """Get first healthy client"""
        for client in self.clients:
            if client.health_check():
                return client
        return None
        
    def close_all(self):
        """Close all clients"""
        for client in self.clients:
            client.close()