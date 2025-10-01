import json, os, subprocess
from pathlib import Path
from typing import List
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
router = APIRouter()
ALLOW = {"paths": [], "apps": []}
def load_allow():
    p = Path("skills/whitelist.json")
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except:
            data = json.loads(p.read_text(errors="ignore"))
        ALLOW["paths"] = data.get("paths", [])
        ALLOW["apps"] = data.get("apps", [])
load_allow()
def safe_path(p):
    rp = Path(p).resolve()
    for root in ALLOW["paths"]:
        if str(rp).startswith(str(Path(root).resolve())):
            return True
    return False
@router.get("/fs/list")
def fs_list(p: str = Query(...)):
    if not safe_path(p):
        return JSONResponse(status_code=403, content={"ok": False, "error": "forbidden"})
    try:
        items = []
        for entry in Path(p).iterdir():
            items.append({"name": entry.name, "is_dir": entry.is_dir()})
        return {"ok": True, "items": items}
    except Exception as e:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(e)})
@router.get("/fs/read")
def fs_read(p: str = Query(...), n: int = 65536):
    if not safe_path(p):
        return JSONResponse(status_code=403, content={"ok": False, "error": "forbidden"})
    try:
        text = Path(p).read_text(encoding="utf-8")[:n]
        return {"ok": True, "text": text}
    except Exception as e:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(e)})
@router.post("/app/open")
def app_open(name: str):
    if name not in ALLOW["apps"]:
        return JSONResponse(status_code=403, content={"ok": False, "error": "forbidden"})
    try:
        subprocess.Popen([name])
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(e)})