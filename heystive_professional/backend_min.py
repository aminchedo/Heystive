import base64, time, json, os, sqlite3
from typing import Optional, List, Dict
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
try:
    import webrtcvad
except Exception:
    webrtcvad = None
from intent_router import route_intent, execute_plan
from store import log_message, DB_PATH
from brain import plan_text
from models_registry import list_models, register_model, download_model
from settings_store import read_settings, write_settings
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
class ModelRegisterIn(BaseModel):
    name: str
    type: str
    url: str
    sha256: str
def _status_payload():
    now_epoch = time.time()
    return {"status": "healthy", "message": "Heystive MVP Backend is running", "timestamp": now_epoch, "service": "heystive-backend", "ok": True, "ts": datetime.now(timezone.utc).isoformat(), "awake_until": AWAKE_UNTIL}
@app.get("/ping")
def ping():
    return _status_payload()
@app.get("/api/status")
def status():
    return _status_payload()
@app.get("/settings", response_class=HTMLResponse)
def settings_page():
    s = read_settings()
    html = "<!doctype html><html><body><h1>Heystive Settings</h1><pre>"+json.dumps(s, ensure_ascii=False, indent=2)+"</pre></body></html>"
    return HTMLResponse(html)
@app.post("/api/settings")
def settings_upsert(body: Dict):
    ok = write_settings(body or {})
    return {"ok": bool(ok)}
@app.get("/api/models/list")
def models_list():
    return {"items": list_models()}
@app.post("/api/models/register")
def models_register(body: ModelRegisterIn):
    return register_model(body.name, body.type, body.url, body.sha256)
@app.post("/api/models/download")
def models_download(name: str):
    return download_model(name)
@app.post("/api/brain")
def brain(payload: BrainIn):
    engine, plan, message = plan_text(payload.text)
    return {"engine": engine, "plan": plan, "message": message}
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
@app.post("/api/stt")
def stt(payload: STTIn):
    if payload.text:
        log_message("user", payload.text, "stt_demo", {"text": payload.text})
        return {"text": payload.text, "engine": "demo"}
    return {"text": "", "engine": "demo", "note": "no input provided"}
@app.post("/api/tts")
def tts(payload: TTSIn):
    try:
        from services.tts_pyttsx3 import tts_to_base64
        from config import settings
        audio_b64 = tts_to_base64(payload.text, getattr(settings, "tts_tmp_dir", "./.tmp_tts"))
        log_message("assistant", payload.text, "tts_pyttsx3", {"bytes": len(audio_b64)})
        return {"audio_base64": audio_b64, "engine": "pyttsx3", "voice": payload.voice}
    except Exception as e:
        log_message("assistant", payload.text, "tts_demo", {"note": str(e)})
        return {"ok": True, "text": payload.text, "engine": "demo", "note": str(e), "voice": payload.voice}
@app.post("/api/intent")
def intent(payload: Dict):
    text = payload.get("text")
    plan = payload.get("plan")
    if plan:
        from intent_router import execute_plan
        results = execute_plan(plan, {})
        for step in results:
            if "result" in step:
                log_message("user", str(step["result"]), step["skill"], step["result"])
        return {"skill": "plan", "results": results}
    if text:
        from intent_router import route_intent
        name, result = route_intent(text, {})
        log_message("user", text, name, result)
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
    await ws.accept()
    await ws.close()
if __name__ == "__main__":
    import uvicorn
    s = read_settings()
    host = s.get("server", {}).get("host", "127.0.0.1")
    port = int(s.get("server", {}).get("port", 8000))
    uvicorn.run(app, host=host, port=port)