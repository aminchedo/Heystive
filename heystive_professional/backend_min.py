from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
import time
from typing import Optional
from heystive_professional.intent_router import route_intent
from heystive_professional.store import log_message

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class State:
    awake_until = 0.0

state = State()

class STTIn(BaseModel):
    audio_base64: Optional[str] = None
    text: Optional[str] = None

class TTSIn(BaseModel):
    text: str
    voice: Optional[str] = None

class IntentIn(BaseModel):
    text: str

def _status_payload():
    now_epoch = time.time()
    return {"status": "healthy", "message": "Heystive MVP Backend is running", "timestamp": now_epoch, "service": "heystive-backend", "ok": True, "ts": datetime.now(timezone.utc).isoformat()}

@app.get("/ping")
def ping():
    return _status_payload()

@app.get("/api/status")
def status():
    return _status_payload()

@app.get("/api/wake")
def wake():
    state.awake_until = time.time() + 10.0
    return {"awake": True, "until": state.awake_until}

@app.post("/api/stt")
def stt(payload: STTIn):
    if payload.text:
        log_message("user", payload.text, "stt_demo", {"text": payload.text})
        return {"text": payload.text, "engine": "demo"}
    if payload.audio_base64:
        try:
            from heystive_professional.services.stt_vosk import stt_wav_base64
            from heystive_professional.config import settings
            text = stt_wav_base64(payload.audio_base64, settings.vosk_model_dir)
            log_message("user", "<audio>", "stt_vosk", {"text": text})
            return {"text": text, "engine": "vosk"}
        except Exception as e:
            log_message("user", "<audio>", "stt_demo", {"note": str(e)})
            return {"text": "demo", "engine": "demo", "note": str(e)}
    return {"text": "", "engine": "demo", "note": "no input provided"}

@app.post("/api/tts")
def tts(payload: TTSIn):
    try:
        from heystive_professional.services.tts_pyttsx3 import tts_to_base64
        from heystive_professional.config import settings
        audio_b64 = tts_to_base64(payload.text, settings.tts_tmp_dir)
        log_message("assistant", payload.text, "tts_pyttsx3", {"bytes": len(audio_b64)})
        return {"audio_base64": audio_b64, "engine": "pyttsx3", "voice": payload.voice}
    except Exception as e:
        log_message("assistant", payload.text, "tts_demo", {"note": str(e)})
        return {"ok": True, "text": payload.text, "engine": "demo", "note": str(e), "voice": payload.voice}

@app.post("/api/intent")
def intent(payload: IntentIn):
    name, result = route_intent(payload.text, {})
    log_message("user", payload.text, name, result)
    return {"skill": name, "result": result}

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