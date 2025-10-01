from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .settings_store import load, save, Settings
router = APIRouter()
@router.get("")
def get_settings():
    s = load()
    return s.model_dump()
@router.put("")
def update_settings(payload: dict):
    try:
        s = Settings(**payload)
    except:
        return JSONResponse(status_code=400, content={"ok": False, "error": "invalid"})
    save(s)
    return {"ok": True}