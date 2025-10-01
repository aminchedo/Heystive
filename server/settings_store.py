from pathlib import Path
from pydantic import BaseModel, Field
import json, threading
LOCK = threading.Lock()
CONF_DIR = Path(".config"); CONF_DIR.mkdir(exist_ok=True, parents=True)
CONF_FILE = CONF_DIR/"settings.json"
class Settings(BaseModel):
    theme: str = Field("light")
    stt_engine: str = Field("vosk")
    tts_engine: str = Field("pyttsx3")
    llm_engine: str = Field("llama_cpp")
    llm_model_path: str = Field("models/llm/gguf/model.gguf")
    hotkey_toggle: str = Field("ctrl+alt+space")
    allow_origins: list[str] = Field(["http://127.0.0.1:8765","http://localhost:8765"])
    log_level: str = Field("info")
    os_whitelist_paths: list[str] = Field(["knowledge","models"])
    os_whitelist_apps: list[str] = Field([])
def _default():
    return Settings().model_dump()
def load():
    with LOCK:
        if not CONF_FILE.exists():
            save(_default())
        try:
            data = json.loads(CONF_FILE.read_text(encoding="utf-8"))
        except:
            data = _default()
        return Settings(**data)
def save(d: dict | Settings):
    with LOCK:
        payload = d.model_dump() if isinstance(d, Settings) else d
        CONF_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return Settings(**payload)