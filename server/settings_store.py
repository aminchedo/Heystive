"""
Settings Store for Heystive Server
Manages application settings with thread safety
"""

import json
import os
import threading
from typing import Dict, Any, List
from pydantic import BaseModel

SETTINGS_PATH = os.environ.get("HEYSTIVE_SETTINGS_PATH", "settings.json")
_lock = threading.Lock()

class Settings(BaseModel):
    """Application settings model"""
    theme: str = "light"
    os_whitelist_paths: List[str] = ["/tmp", "/home", "/workspace"]
    os_whitelist_apps: List[str] = ["notepad", "gedit", "code", "firefox", "chrome"]
    auto_listen: bool = False
    notifications: bool = True
    rtl_support: bool = True
    language: str = "fa"  # Persian
    voice_enabled: bool = True
    tts_enabled: bool = True
    stt_enabled: bool = True

def read_settings() -> Dict[str, Any]:
    """Read settings from file"""
    if not os.path.isfile(SETTINGS_PATH):
        return {}
    
    with _lock:
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except Exception:
            return {}

def write_settings(data: Dict[str, Any]) -> bool:
    """Write settings to file"""
    with _lock:
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=2))
            return True
        except Exception:
            return False

def load() -> Settings:
    """Load settings as Settings object"""
    data = read_settings()
    return Settings(**data)

def save(settings: Settings) -> bool:
    """Save Settings object to file"""
    return write_settings(settings.model_dump())

def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting value"""
    settings = read_settings()
    return settings.get(key, default)

def set_setting(key: str, value: Any) -> bool:
    """Set a specific setting value"""
    settings = read_settings()
    settings[key] = value
    return write_settings(settings)

def reset_settings() -> bool:
    """Reset settings to defaults"""
    default_settings = Settings()
    return save(default_settings)