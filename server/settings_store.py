"""
Settings Store for Heystive Server
Manages application settings with thread safety
"""

import json
import os
import threading
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field

# Use .config directory for settings storage
CONF_DIR = Path(".config")
CONF_DIR.mkdir(exist_ok=True, parents=True)
SETTINGS_PATH = os.environ.get("HEYSTIVE_SETTINGS_PATH", str(CONF_DIR / "settings.json"))
_lock = threading.Lock()

class Settings(BaseModel):
    """Application settings model"""
    # UI Settings
    theme: str = Field("light", description="UI theme (light/dark)")
    language: str = Field("fa", description="Interface language (fa/en)")
    rtl_support: bool = Field(True, description="Right-to-left text support")
    
    # Engine Configuration
    stt_engine: str = Field("vosk", description="Speech-to-text engine")
    tts_engine: str = Field("pyttsx3", description="Text-to-speech engine")
    llm_engine: str = Field("llama_cpp", description="LLM engine")
    llm_model_path: str = Field("models/llm/gguf/model.gguf", description="Path to LLM model")
    
    # Hotkey Configuration
    hotkey_toggle: str = Field("ctrl+alt+space", description="Global hotkey for toggle")
    
    # Network Settings
    allow_origins: List[str] = Field(
        ["http://127.0.0.1:8765", "http://localhost:8765"],
        description="Allowed CORS origins"
    )
    
    # OS Integration
    os_whitelist_paths: List[str] = Field(
        ["knowledge", "models", "/tmp", "/home", "/workspace"],
        description="Whitelisted paths for OS operations"
    )
    os_whitelist_apps: List[str] = Field(
        ["notepad", "gedit", "code", "firefox", "chrome"],
        description="Whitelisted applications"
    )
    
    # Feature Flags
    auto_listen: bool = Field(False, description="Auto-start listening")
    notifications: bool = Field(True, description="Enable notifications")
    voice_enabled: bool = Field(True, description="Enable voice input")
    tts_enabled: bool = Field(True, description="Enable text-to-speech")
    stt_enabled: bool = Field(True, description="Enable speech-to-text")
    
    # Wake-word Configuration
    wakeword_enabled: bool = Field(True, description="Enable wake-word detection")
    wakeword_keyword: str = Field("hey steve", description="Wake-word keyword")
    wakeword_sensitivity: float = Field(0.5, description="Wake-word sensitivity (0.0-1.0)")
    wakeword_device_index: int = Field(None, description="Audio device index for wake-word")
    
    # Logging
    log_level: str = Field("info", description="Logging level")

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
    if not data:
        # Initialize with defaults if file doesn't exist
        default_settings = Settings()
        save(default_settings)
        return default_settings
    return Settings(**data)

def save(settings: Settings | Dict[str, Any]) -> Settings:
    """Save Settings object or dict to file, returns Settings object"""
    if isinstance(settings, dict):
        settings = Settings(**settings)
    write_settings(settings.model_dump())
    return settings

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
