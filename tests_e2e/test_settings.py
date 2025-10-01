import requests
BASE="http://127.0.0.1:8765"
def test_get_settings():
    r=requests.get(f"{BASE}/api/settings",timeout=5)
    assert r.status_code==200
def test_put_settings():
    r=requests.put(f"{BASE}/api/settings",json={"theme":"dark","stt_engine":"vosk","tts_engine":"pyttsx3","llm_engine":"llama_cpp","llm_model_path":"models/llm/gguf/model.gguf","hotkey_toggle":"ctrl+alt+space","allow_origins":["http://127.0.0.1:8765"],"log_level":"info","os_whitelist_paths":["knowledge"],"os_whitelist_apps":[]},timeout=10)
    assert r.status_code==200