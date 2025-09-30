from typing import List, Dict

_models = []

def list_models() -> List[Dict]:
    return _models

def register_model(name: str, type: str, url: str, sha256: str) -> Dict:
    model = {"name": name, "type": type, "url": url, "sha256": sha256}
    _models.append(model)
    return {"ok": True, "model": model}

def download_model(name: str) -> Dict:
    for model in _models:
        if model["name"] == name:
            return {"ok": True, "message": f"Downloaded {name}"}
    return {"ok": False, "error": "Model not found"}