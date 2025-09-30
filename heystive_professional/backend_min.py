import base64, time, json, os, sqlite3
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
try:
    import webrtcvad
except Exception:
    webrtcvad = None
from heystive_professional.intent_router import route_intent, execute_plan
from heystive_professional.store import log_message, DB_PATH
from heystive_professional.brain import plan_text

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

AWAKE_UNTIL = 0.0
WAKE_PHRASES = ["hey heystive", "hey steve", "heystive", "steve"]

class STTIn(BaseModel):
    audio_base64: Optional[str] = None
    text: Optional[str] = None

class TTSIn(BaseModel):
    text: str
    voice: Optional[str] = None

class IntentIn(BaseModel):
    text: Optional[str] = None
    plan: Optional[List[dict]] = None

class BrainIn(BaseModel):
    text: str

def _status_payload():
    now_epoch = time.time()
    return {"status": "healthy", "message": "Heystive MVP Backend is running", "timestamp": now_epoch, "service": "heystive-backend", "ok": True, "ts": datetime.now(timezone.utc).isoformat(), "awake_until": AWAKE_UNTIL}

@app.get("/ping")
def ping():
    return _status_payload()

@app.get("/api/status")
def status():
    return _status_payload()

@app.get("/api/wake")
def wake():
    global AWAKE_UNTIL
    AWAKE_UNTIL = time.time() + 10.0
    return {"awake": True, "until": AWAKE_UNTIL}

@app.get("/api/logs")
def logs(limit: int = Query(20, ge=1, le=200)):
    con = sqlite3.connect(DB_PATH)
    cur = con.execute("SELECT id, ts, role, text, skill, result FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    con.close()
    out = []
    for r in rows:
        try:
            res = json.loads(r[5]) if r[5] else {}
        except Exception:
            res = {}
        out.append({"id": r[0], "ts": r[1], "role": r[2], "text": r[3], "skill": r[4], "result": res})
    return {"items": out}

@app.post("/api/brain")
def brain(payload: BrainIn):
    engine, plan, message = plan_text(payload.text)
    return {"engine": engine, "plan": plan, "message": message}

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
    global AWAKE_UNTIL
    if payload.plan:
        results = execute_plan(payload.plan, {})
        for step in results:
            if "result" in step:
                log_message("user", str(step["result"]), step["skill"], step["result"])
        return {"skill": "plan", "results": results}
    if payload.text:
        name, result = route_intent(payload.text, {})
        log_message("user", payload.text, name, result)
        low = payload.text.lower()
        if any(p in low for p in WAKE_PHRASES):
            AWAKE_UNTIL = time.time() + 10.0
        return {"skill": name, "result": result}
    return {"skill": "none", "result": {"message": "no input"}}

@app.websocket("/ws")
async def ws_echo(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            await ws.send_text(msg)
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/stream")
async def ws_stream(ws: WebSocket):
    global AWAKE_UNTIL
    await ws.accept()
    engine = None
    sr = 16000
    vad = None
    speech_only = True
    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except Exception:
                await ws.send_text(json.dumps({"type": "error", "note": "invalid json"}))
                continue
            t = data.get("type")
            if t == "start":
                sr = int(data.get("sr", 16000))
                try:
                    from heystive_professional.config import settings
                    from heystive_professional.services.streaming_vosk import StreamingSTTEngine
                    engine = StreamingSTTEngine(getattr(settings, "vosk_model_dir", "models/vosk-fa"), sr)
                except Exception:
                    engine = None
                if webrtcvad:
                    try:
                        vad = webrtcvad.Vad(2)
                    except Exception:
                        vad = None
                await ws.send_text(json.dumps({"type": "ack", "engine": "vosk" if engine and engine.enabled else "demo", "vad": bool(vad)}))
            elif t == "chunk":
                b64 = data.get("pcm_b64")
                if not b64:
                    continue
                pcm = base64.b64decode(b64)
                use = True
                if vad:
                    frame_ms = 20
                    frame_len = int(sr * 2 * frame_ms / 1000)
                    use = False
                    i = 0
                    while i + frame_len <= len(pcm):
                        fr = pcm[i:i+frame_len]
                        try:
                            if vad.is_speech(fr, sr):
                                use = True
                                break
                        except Exception:
                            use = True
                            break
                        i += frame_len
                if not use and speech_only:
                    continue
                if engine:
                    part, final = engine.accept(pcm)
                    if part:
                        await ws.send_text(json.dumps({"type": "partial", "text": part}))
                        low = part.lower()
                        if any(p in low for p in WAKE_PHRASES):
                            AWAKE_UNTIL = time.time() + 10.0
                            await ws.send_text(json.dumps({"type": "wake", "until": AWAKE_UNTIL}))
                    if final:
                        await ws.send_text(json.dumps({"type": "final", "text": final}))
                        low = final.lower()
                        if any(p in low for p in WAKE_PHRASES):
                            AWAKE_UNTIL = time.time() + 10.0
                            await ws.send_text(json.dumps({"type": "wake", "until": AWAKE_UNTIL}))
                else:
                    await ws.send_text(json.dumps({"type": "partial", "text": ""}))
            elif t == "stop":
                if engine:
                    txt = engine.finalize()
                    await ws.send_text(json.dumps({"type": "final", "text": txt}))
                break
            else:
                await ws.send_text(json.dumps({"type": "error", "note": "unknown type"}))
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)