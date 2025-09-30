import os, sqlite3, hashlib, shutil, urllib.parse, json, time
from typing import Dict, List
from .store import DB_PATH
MODELS_DIR = os.environ.get("HEYSTIVE_MODELS_DIR", "models")
os.makedirs(MODELS_DIR, exist_ok=True)
def _conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("CREATE TABLE IF NOT EXISTS models (name TEXT PRIMARY KEY, type TEXT, url TEXT, sha256 TEXT, path TEXT, status TEXT, updated REAL)")
    return c
def list_models() -> List[Dict]:
    c=_conn(); cur=c.execute("SELECT name,type,url,sha256,path,status,updated FROM models ORDER BY name")
    out=[{"name":r[0],"type":r[1],"url":r[2],"sha256":r[3],"path":r[4],"status":r[5],"updated":r[6]} for r in cur.fetchall()]
    c.close(); return out
def register_model(name: str, type_: str, url: str, sha256: str):
    c=_conn()
    c.execute("INSERT OR REPLACE INTO models (name,type,url,sha256,path,status,updated) VALUES (?,?,?,?,?,?,?)",
              (name, type_, url, sha256, "", "registered", time.time()))
    c.commit(); c.close()
    return {"ok": True, "name": name}
def _sha256(path: str) -> str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()
def download_model(name: str) -> Dict:
    c=_conn()
    cur=c.execute("SELECT type,url,sha256 FROM models WHERE name=?", (name,))
    row=cur.fetchone()
    if not row:
        c.close(); return {"ok": False, "error": "unknown_model"}
    type_, url, want=row
    parsed=urllib.parse.urlparse(url)
    out_dir=os.path.join(MODELS_DIR, name); os.makedirs(out_dir, exist_ok=True)
    out_path=os.path.join(out_dir,"model.bin")
    if parsed.scheme=="file":
        src=parsed.path
        if not os.path.isfile(src):
            c.close(); return {"ok": False, "error": "source_missing"}
        shutil.copyfile(src, out_path)
    else:
        c.close(); return {"ok": False, "error": "unsupported_scheme"}
    got=_sha256(out_path)
    verified = (want.lower()==got.lower())
    status="ready" if verified else "corrupt"
    c.execute("UPDATE models SET path=?, status=?, updated=? WHERE name=?", (out_path, status, time.time(), name))
    c.commit(); c.close()
    return {"ok": True, "name": name, "path": out_path, "verified": verified, "status": status}