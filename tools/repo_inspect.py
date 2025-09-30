import os, json, subprocess, re, sys, time, hashlib
root = os.getcwd()
def exists(p): return os.path.exists(os.path.join(root,p))
def read(p):
  try: return open(os.path.join(root,p),"r",encoding="utf-8").read()
  except Exception: return ""
def curl_json(url, data=None):
  try:
    import urllib.request, json as _j
    req = urllib.request.Request(url, data=_j.dumps(data).encode() if data else None, headers={"Content-Type":"application/json"} if data else {})
    res = urllib.request.urlopen(req, timeout=2).read().decode()
    return _j.loads(res)
  except Exception as e:
    return {"_error": str(e)}
# scripts
scripts = [p for p in (
  "scripts/dev_up.sh","scripts/dev_up_win.bat","scripts/service.sh","scripts/service_win.bat",
  "scripts/smoke_after_archive.sh","scripts/dev_env.sh","scripts/voice_hard_test.sh"
) if exists(p)]
# tools
tools = [p for p in (
  "tools/archive_plan.py","tools/archive_apply.sh","tools/archive_apply.ps1","tools/archive_guard.py","tools/archive_restore.py","tools/env_doctor.py"
) if exists(p)]
# web templates
tpl = [p for p in ("ui_modern_web/templates/index.html",) if exists(p)]
# endpoints quick probe (best-effort)
ping = curl_json("http://127.0.0.1:8000/ping")
models = curl_json("http://127.0.0.1:8000/api/models/list")
settings_html = ""
try:
  import urllib.request
  settings_html = urllib.request.urlopen("http://127.0.0.1:8000/settings", timeout=2).read().decode()[:200]
except Exception as e:
  settings_html = f"_error:{e}"
# phase tracker
phase_path = "docs/PHASES_TRACK.md"
phases = read(phase_path)
# requirements
reqs = [p for p in (
  "heystive_professional/requirements-core.txt",
  "ui_modern_web/requirements-web.txt",
  "ui_modern_desktop/requirements-desktop.txt",
  "heystive_professional/requirements-models.txt"
) if exists(p)]
# minimal hash to show snapshot integrity
def tree_hash():
  h=hashlib.sha256()
  for dirpath,_,files in os.walk(root):
    if ".git" in dirpath: continue
    for f in files:
      p=os.path.join(dirpath,f)
      try:
        st=os.stat(p); h.update(f"{os.path.relpath(p,root)}:{st.st_size}:{int(st.st_mtime)}".encode())
      except Exception: pass
  return h.hexdigest()
out = {
  "timestamp": int(time.time()),
  "scripts": scripts,
  "tools": tools,
  "templates": tpl,
  "requirements": reqs,
  "phase_tracker_exists": exists(phase_path),
  "phase_tracker_head": phases.splitlines()[:30],
  "endpoints_sample": {"ping": ping, "models_list": models, "settings_head": settings_html},
  "tree_hash": tree_hash()
}
print(json.dumps(out, ensure_ascii=False, indent=2))