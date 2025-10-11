from fastapi import APIRouter
from fastapi.responses import JSONResponse
from heystive_professional.heystive.brain.executor import run
router = APIRouter()
@router.post("/chat")
def chat(payload: dict):
    text = payload.get("text","")
    if not text:
        return JSONResponse(status_code=400, content={"ok": False, "error": "empty"})
    res = run(text)
    return {"ok": True, "result": res}