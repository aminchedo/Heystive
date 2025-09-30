import base64, time, json, os, sqlite3
from typing import Optional, List, Dict
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
from heystive_professional.skills_registry import list_manifests, request_permission, grant_permission, exec_sandbox, is_granted
from heystive_professional.memory import upsert as mem_upsert, search as mem_search
from heystive_professional.models_registry import list_models, register_model, download_model

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

AWAKE_UNTIL = 0.0
WAKE_PHRASES = ["hey heystive", "hey steve", "heystive", "steve"]
STT_ENGINE = os.environ.get("HEYSTIVE_STT_ENGINE", "auto")
TTS_ENGINE = os.environ.get("HEYSTIVE_TTS_ENGINE", "auto")
STT_MODEL_DIR = os.environ.get("HEYSTIVE_STT_MODEL", "models/whisper-tiny")
TTS_MODEL_DIR = os.environ.get("HEYSTIVE_TTS_MODEL", "models/xtts")

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

class PermissionGrantIn(BaseModel):
    permission: str

class SkillExecIn(BaseModel):
    name: str
    args: Dict

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

@app.get("/api/models/list")
def models_list():
    return {"items": list_models()}

@app.post("/api/models/register")
def models_register(body: ModelRegisterIn):
    return register_model(body.name, body.type, body.url, body.sha256)

@app.post("/api/models/download")
def models_download(name: str):
    return download_model(name)

@app.get("/api/skills")
def skills():
    items = list_manifests()
    return {"items": items}

@app.post("/api/permissions/request")
def perm_request(perm: PermissionGrantIn):
    return request_permission(perm.permission)

@app.post("/api/permissions/grant")
def perm_grant(perm: PermissionGrantIn):
    return grant_permission(perm.permission)

@app.post("/api/skill/exec")
def skill_exec(payload: SkillExecIn):
    items = {m["name"]: m for m in list_manifests()}
    m = items.get(payload.name)
    if not m:
        return {"ok": False, "error": "unknown_skill"}
    required = m.get("permissions", [])
    missing = [p for p in required if not is_granted(p)]
    if missing:
        return {"allowed": False, "required": missing}
    entry = m.get("entry") or []
    if not entry:
        return {"ok": False, "error": "no_entry"}
    code, out = exec_sandbox(entry, payload.args, timeout_s=3, skill_name=payload.name)
    if code != 0:
        return {"ok": False, "error": out or "exec_error"}
    try:
        j = json.loads(out)
    except Exception:
        return {"ok": False, "error": "bad_json"}
    return j

@app.post("/api/memory/upsert")
def memory_upsert(data: Dict):
    text = str(data.get("text",""))
    tags = data.get("tags") or []
    i = mem_upsert(text, tags)
    return {"ok": True, "id": i}

@app.post("/api/memory/search")
def memory_search(data: Dict):
    q = str(data.get("q",""))
    limit = int(data.get("limit", 5))
    res = mem_search(q, limit)
    return {"results": res}

@app.get("/api/wake")
def wake():
    global AWAKE_UNTIL
    AWAKE_UNTIL = time.time() + 10.0
    return {"awake": True, "until": AWAKE_UNTIL}

@app.post("/api/stt")
def stt(payload: STTIn):
    if payload.text:
        log_message("user", payload.text, "stt_demo", {"text": payload.text})
        return {"text": payload.text, "engine": "demo"}
    if payload.audio_base64:
        if STT_ENGINE in ("auto","whisper"):
            try:
                from heystive_professional.services.stt_whisper import stt_wav_base64_whisper
                text = stt_wav_base64_whisper(payload.audio_base64, STT_MODEL_DIR)
                log_message("user", "<audio>", "stt_whisper", {"text": text})
                return {"text": text, "engine": "whisper"}
            except Exception as e:
                pass
        try:
            from heystive_professional.services.stt_vosk import stt_wav_base64
            from heystive_professional.config import settings
            text = stt_wav_base64(payload.audio_base64, getattr(settings, "vosk_model_dir", "models/vosk-fa"))
            log_message("user", "<audio>", "stt_vosk", {"text": text})
            return {"text": text, "engine": "vosk"}
        except Exception as e:
            log_message("user", "<audio>", "stt_demo", {"note": str(e)})
            return {"text": "demo", "engine": "demo", "note": str(e)}
    return {"text": "", "engine": "demo", "note": "no input provided"}

@app.post("/api/tts")
def tts(payload: TTSIn):
    if TTS_ENGINE in ("auto","xtts"):
        try:
            from heystive_professional.services.tts_xtts import tts_generate_base64_xtts
            audio_b64 = tts_generate_base64_xtts(payload.text, TTS_MODEL_DIR)
            log_message("assistant", payload.text, "tts_xtts", {"bytes": len(audio_b64)})
            return {"audio_base64": audio_b64, "engine": "xtts", "voice": payload.voice}
        except Exception as e:
            pass
    try:
        from heystive_professional.services.tts_pyttsx3 import tts_to_base64
        from heystive_professional.config import settings
        audio_b64 = tts_to_base64(payload.text, getattr(settings, "tts_tmp_dir", "./.tmp_tts"))
        log_message("assistant", payload.text, "tts_pyttsx3", {"bytes": len(audio_b64)})
        return {"audio_base64": audio_b64, "engine": "pyttsx3", "voice": payload.voice}
    except Exception as e:
        log_message("assistant", payload.text, "tts_demo", {"note": str(e)})
        return {"ok": True, "text": payload.text, "engine": "demo", "note": str(e), "voice": payload.voice}

@app.post("/api/intent")
def intent(payload: IntentIn):
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
            global AWAKE_UNTIL
            AWAKE_UNTIL = time.time() + 10.0
        return {"skill": name, "result": result}
    return {"skill": "none", "result": {"message": "no input"}}

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