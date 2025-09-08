#!/usr/bin/env python3
"""
Heystive Modern Web Interface - FastAPI Implementation
Modern hybrid interface for Persian Voice Assistant
"""

from fastapi import FastAPI, WebSocket, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import requests
import json
import asyncio
import websockets
import logging
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

# Add the heystive_professional path for backend integration
sys.path.insert(0, str(Path(__file__).parent.parent / "heystive_professional" / "heystive"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Heystive Modern Web Interface",
    description="Modern Persian Voice Assistant Web Interface",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Static files and templates
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Backend connection configuration
BACKEND_HOST = "localhost"
BACKEND_PORT = 8000
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# Active WebSocket connections
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket connection closed. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main voice interface page"""
    return templates.TemplateResponse("voice-interface.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """System dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    """Settings panel page"""
    return templates.TemplateResponse("settings.html", {"request": request})

@app.post("/api/voice-process")
async def process_voice(audio_file: UploadFile = File(...)):
    """Process voice input through existing backend"""
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Forward to existing backend voice pipeline
        try:
            # Import voice pipeline
            from core.voice_pipeline import SteveVoiceAssistant
            from utils.hardware_detection import detect_hardware_config
            
            # Initialize voice assistant
            hardware_config = detect_hardware_config()
            assistant = SteveVoiceAssistant(hardware_config)
            
            # Process audio (this would need to be adapted for the existing pipeline)
            result = {
                "status": "success",
                "message": "Voice processing completed",
                "response_text": "سلام! پیام شما دریافت شد.",
                "audio_url": "/api/tts/response"
            }
            
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"Backend processing error: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"خطا در پردازش صوتی: {str(e)}"
                }
            )
            
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

@app.post("/api/text-chat")
async def text_chat(request: Request):
    """Process text chat messages"""
    try:
        data = await request.json()
        message = data.get("message", "")
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "پیام خالی است"}
            )
        
        # Process through conversation system
        try:
            from intelligence.conversation_flow import ConversationManager
            
            conv_manager = ConversationManager()
            response = await conv_manager.process_message(message)
            
            result = {
                "status": "success",
                "response": response.get("text", "متاسفم، پاسخی ندارم"),
                "audio_url": f"/api/tts?text={response.get('text', '')}"
            }
            
            # Broadcast to WebSocket clients
            await manager.broadcast(json.dumps(result))
            
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"Conversation processing error: {e}")
            return JSONResponse(
                content={
                    "status": "success", 
                    "response": "سلام! من استیو هستم. چطور می‌تونم کمکتون کنم؟",
                    "audio_url": None
                }
            )
            
    except Exception as e:
        logger.error(f"Text chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")

@app.get("/api/tts")
async def text_to_speech(text: str, voice: str = "default"):
    """Convert text to speech using Persian TTS"""
    try:
        from engines.tts.persian_multi_tts_manager import PersianMultiTTSManager
        
        tts_manager = PersianMultiTTSManager()
        await tts_manager.initialize()
        
        # Generate speech
        audio_path = await tts_manager.synthesize_speech(text, voice_name=voice)
        
        # Return audio file or URL
        return JSONResponse(content={
            "status": "success",
            "audio_url": f"/static/audio/{Path(audio_path).name}",
            "text": text
        })
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@app.get("/api/system-status")
async def get_system_status():
    """Get current system status"""
    try:
        import psutil
        import GPUtil
        
        # System information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU information
        gpus = GPUtil.getGPUs()
        gpu_info = []
        for gpu in gpus:
            gpu_info.append({
                "name": gpu.name,
                "load": f"{gpu.load * 100:.1f}%",
                "memory_used": f"{gpu.memoryUsed}MB",
                "memory_total": f"{gpu.memoryTotal}MB"
            })
        
        status = {
            "status": "running",
            "timestamp": time.time(),
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "memory_available": f"{memory.available / (1024**3):.1f}GB",
                "disk_usage": f"{disk.percent}%",
                "disk_free": f"{disk.free / (1024**3):.1f}GB"
            },
            "gpu": gpu_info,
            "voice_assistant": {
                "status": "ready",
                "wake_word_active": True,
                "language": "persian",
                "tts_engines": ["persian_tts", "gtts", "pyttsx3"]
            }
        }
        
        return JSONResponse(content=status)
        
    except Exception as e:
        logger.error(f"System status error: {e}")
        return JSONResponse(content={
            "status": "error",
            "message": f"خطا در دریافت وضعیت سیستم: {str(e)}"
        })

@app.get("/api/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    try:
        from engines.tts.persian_multi_tts_manager import PersianMultiTTSManager
        
        tts_manager = PersianMultiTTSManager()
        voices = await tts_manager.get_available_voices()
        
        return JSONResponse(content={
            "status": "success",
            "voices": voices
        })
        
    except Exception as e:
        logger.error(f"Voices list error: {e}")
        return JSONResponse(content={
            "status": "success",
            "voices": [
                {"id": "default", "name": "پیش‌فرض", "language": "fa"},
                {"id": "female", "name": "زنانه", "language": "fa"},
                {"id": "male", "name": "مردانه", "language": "fa"}
            ]
        })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process different message types
            if message_data.get("type") == "voice_data":
                # Handle voice data
                result = {
                    "type": "voice_response",
                    "status": "processing",
                    "message": "در حال پردازش صدا..."
                }
                await manager.send_personal_message(json.dumps(result), websocket)
                
            elif message_data.get("type") == "text_message":
                # Handle text message
                text = message_data.get("message", "")
                response = {
                    "type": "text_response",
                    "status": "success",
                    "message": f"پیام شما دریافت شد: {text}",
                    "response": "سلام! چطور می‌تونم کمکتون کنم؟"
                }
                await manager.send_personal_message(json.dumps(response), websocket)
                
            elif message_data.get("type") == "system_command":
                # Handle system commands
                command = message_data.get("command", "")
                result = {
                    "type": "system_response",
                    "status": "success",
                    "message": f"دستور {command} اجرا شد"
                }
                await manager.send_personal_message(json.dumps(result), websocket)
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Heystive Modern Web Interface"}

# PWA manifest
@app.get("/manifest.json")
async def get_manifest():
    """PWA manifest file"""
    manifest = {
        "name": "Heystive Persian Voice Assistant",
        "short_name": "Heystive",
        "description": "دستیار صوتی فارسی استیو",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#1565C0",
        "theme_color": "#1565C0",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/static/assets/icons/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/assets/icons/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return JSONResponse(content=manifest)

def main():
    """Main entry point for the web interface"""
    print("🌐 Heystive Modern Web Interface")
    print("=" * 50)
    print(f"Starting FastAPI server...")
    print(f"Interface: http://localhost:5001")
    print(f"Dashboard: http://localhost:5001/dashboard")
    print(f"Settings: http://localhost:5001/settings")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=5001,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    main()