import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
WS_URL = BACKEND_URL.replace("http", "ws")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

env = Environment(loader=FileSystemLoader(templates_dir), autoescape=select_autoescape(["html", "xml"]))

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def index(_: Request):
    tmpl = env.get_template("index.html")
    return tmpl.render(BACKEND_URL=BACKEND_URL, WS_URL=WS_URL)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5174)