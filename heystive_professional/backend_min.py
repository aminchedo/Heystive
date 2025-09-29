#!/usr/bin/env python3
"""
Heystive MVP Backend - Minimal FastAPI Implementation
Simple backend for testing and development
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
import asyncio
import logging
from typing import Dict, Any, List
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Heystive MVP Backend",
    description="Minimal backend for Heystive Persian Voice Assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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

@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Heystive MVP Backend is running",
        "timestamp": time.time(),
        "service": "heystive-backend"
    }

@app.post("/api/stt")
async def speech_to_text(request: Dict[str, Any]):
    """Demo Speech-to-Text endpoint"""
    try:
        # Demo implementation - in real version this would process audio
        text = request.get("text", "سلام! این یک پیام تست است.")
        
        result = {
            "status": "success",
            "text": text,
            "confidence": 0.95,
            "language": "fa",
            "timestamp": time.time()
        }
        
        logger.info(f"STT processed: {text}")
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=f"STT processing failed: {str(e)}")

@app.post("/api/tts")
async def text_to_speech(request: Dict[str, Any]):
    """Demo Text-to-Speech endpoint"""
    try:
        text = request.get("text", "سلام! من استیو هستم.")
        voice = request.get("voice", "default")
        
        # Demo implementation - in real version this would generate audio
        result = {
            "status": "success",
            "text": text,
            "voice": voice,
            "audio_url": f"/api/audio/demo_{int(time.time())}.mp3",
            "duration": 2.5,
            "timestamp": time.time()
        }
        
        logger.info(f"TTS processed: {text} with voice {voice}")
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS processing failed: {str(e)}")

@app.get("/api/status")
async def get_status():
    """Get backend status"""
    return {
        "status": "running",
        "version": "1.0.0",
        "uptime": time.time(),
        "connections": len(active_connections),
        "endpoints": [
            "/ping",
            "/api/stt",
            "/api/tts",
            "/api/status",
            "/ws"
        ]
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Echo the message back with a response
            response = {
                "type": "echo",
                "original_message": message_data,
                "response": "پیام شما دریافت شد!",
                "timestamp": time.time()
            }
            
            await manager.send_personal_message(json.dumps(response), websocket)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Heystive MVP Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "/ping",
            "stt": "/api/stt",
            "tts": "/api/tts",
            "status": "/api/status",
            "websocket": "/ws"
        }
    }

def main():
    """Main entry point"""
    print("🚀 Heystive MVP Backend")
    print("=" * 40)
    print("Starting FastAPI server...")
    print("Backend: http://127.0.0.1:8000")
    print("Health: http://127.0.0.1:8000/ping")
    print("WebSocket: ws://127.0.0.1:8000/ws")
    print("=" * 40)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    main()
