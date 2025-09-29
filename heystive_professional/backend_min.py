from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
import time
from typing import Optional

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class STTIn(BaseModel):
    audio_base64: Optional[str] = None
    text: Optional[str] = None

class TTSIn(BaseModel):
    text: str
    voice: Optional[str] = None

def _status_payload():
    now_epoch = time.time()
    return {
        "status": "healthy",
        "message": "Heystive MVP Backend is running",
        "timestamp": now_epoch,
        "service": "heystive-backend",
        "ok": True,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/ping")
def ping():
    return _status_payload()

@app.get("/api/status")
def status():
    return _status_payload()

@app.post("/api/stt")
def stt(payload: STTIn):
    if payload.text:
        return {"text": payload.text, "engine": "demo"}
    if payload.audio_base64:
        try:
            from heystive_professional.services.stt_vosk import stt_wav_base64
            from heystive_professional.config import settings
            text = stt_wav_base64(payload.audio_base64, settings.vosk_model_dir)
            return {"text": text, "engine": "vosk"}
        except Exception as e:
            return {"text": "demo", "engine": "demo", "note": str(e)}
    return {"text": "", "engine": "demo", "note": "no input provided"}

@app.post("/api/tts")
def tts(payload: TTSIn):
    try:
        from heystive_professional.services.tts_pyttsx3 import tts_to_base64
        from heystive_professional.config import settings
        audio_b64 = tts_to_base64(payload.text, settings.tts_tmp_dir)
        return {"audio_base64": audio_b64, "engine": "pyttsx3", "voice": payload.voice}
    except Exception as e:
        return {"ok": True, "text": payload.text, "engine": "demo", "note": str(e), "voice": payload.voice}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            await ws.send_text(msg)
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)