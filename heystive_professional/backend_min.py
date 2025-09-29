from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class STTIn(BaseModel):
    audio_base64: str | None = None

class TTSIn(BaseModel):
    text: str

@app.get("/ping")
def ping():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}

@app.post("/api/stt")
def stt(payload: STTIn):
    return {"text": "demo"}

@app.post("/api/tts")
def tts(payload: TTSIn):
    return {"ok": True, "text": payload.text}

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