from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
WS_URL = BACKEND_URL.replace("http", "ws")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Heystive MVP</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{font-family:system-ui,Arial;margin:40px;}}button{{padding:10px 16px;margin-right:8px}}#log{{white-space:pre-wrap;border:1px solid #ddd;padding:12px;margin-top:16px}}</style>
</head><body>
<h1>Heystive MVP</h1>
<p>Backend: <code>{BACKEND_URL}</code></p>
<button id="ping">Ping</button>
<button id="ws">Open WS</button>
<button id="send" disabled>Send "hello"</button>
<div id="log"></div>
<script>
const backend = "{BACKEND_URL}";
const wsUrl = "{WS_URL}/ws";
const log = (t)=>{{ const el=document.getElementById('log'); el.textContent += t+"\\n"; }};
document.getElementById('ping').onclick = async ()=>{{
  try{{
    const r = await fetch(backend + "/ping");
    const j = await r.json();
    log("ping: " + JSON.stringify(j));
  }}catch(e){{ log("ping error"); }}
}};
let sock=null;
document.getElementById('ws').onclick = ()=>{{
  sock = new WebSocket(wsUrl);
  sock.onopen = ()=>{{ log("ws open"); document.getElementById('send').disabled=false; }};
  sock.onmessage = (ev)=> log("ws msg: " + ev.data);
  sock.onclose = ()=>{{ log("ws closed"); document.getElementById('send').disabled=true; }};
  sock.onerror = ()=> log("ws error");
}};
document.getElementById('send').onclick = ()=>{{
  if(sock && sock.readyState===1){{ sock.send("hello"); }}
}};
</script>
</body></html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5174)