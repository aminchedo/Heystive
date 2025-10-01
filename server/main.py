from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from server.middleware import RequestLoggerMiddleware
from server.errors import unhandled_exception_handler
from server.metrics import metrics_handler
from server.rag_lite import router as rag_router
from server.os_skills import router as os_router
from server.settings_api import router as settings_router
from server.brain_api import router as brain_router
ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.append(str(ROOT / "heystive_professional"))
from backend_min import app as api_app
UI_TEMPLATES = ROOT / "ui_modern_web" / "templates"
UI_STATIC = ROOT / "ui_modern_web" / "static"
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8765","http://localhost:8765"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(RequestLoggerMiddleware)
app.add_exception_handler(Exception, unhandled_exception_handler)
templates = Jinja2Templates(directory=str(UI_TEMPLATES))
app.mount("/static", StaticFiles(directory=str(UI_STATIC)), name="static")
app.mount("/api", api_app)
app.include_router(rag_router, prefix="/api/memory", tags=["memory"])
app.include_router(os_router, prefix="/api/os", tags=["os"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
app.include_router(brain_router, prefix="/api/brain", tags=["brain"])
@app.get("/healthz", response_class=JSONResponse)
def healthz():
    return {"ok": True}
@app.get("/readyz", response_class=JSONResponse)
def readyz():
    return {"ready": True}
@app.get("/metrics")
def metrics():
    return metrics_handler()
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    page = "index.html" if (UI_TEMPLATES / "index.html").exists() else "voice-interface.html"
    return templates.TemplateResponse(page, {"request": request})
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    page = "dashboard.html" if (UI_TEMPLATES / "dashboard.html").exists() else "index.html"
    return templates.TemplateResponse(page, {"request": request})
@app.get("/settings", response_class=HTMLResponse)
def settings(request: Request):
    page = "settings.html" if (UI_TEMPLATES / "settings.html").exists() else "index.html"
    return templates.TemplateResponse(page, {"request": request})
def run():
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
if __name__ == "__main__":
    run()