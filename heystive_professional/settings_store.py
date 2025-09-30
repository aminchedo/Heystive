import json, os, threading
SETTINGS_PATH = os.environ.get("HEYSTIVE_SETTINGS_PATH", "settings.json")
_lock = threading.Lock()
def read_settings():
  if not os.path.isfile(SETTINGS_PATH):
    return {}
  with _lock:
    try:
      return json.loads(open(SETTINGS_PATH,"r",encoding="utf-8").read())
    except Exception:
      return {}
def write_settings(data: dict):
  with _lock:
    open(SETTINGS_PATH,"w",encoding="utf-8").write(json.dumps(data, ensure_ascii=False))
  return True