import os, sys, shutil, subprocess, json, socket
R = {"python":None,"venv":None,"deps":{},"ports":{},"result":"fail","notes":[]}
def ok(x): return {"ok":True,"note":x}
def ng(x): return {"ok":False,"note":x}
def pyver():
  v = sys.version_info; return f"{v.major}.{v.minor}.{v.micro}"
def port_free(p):
  s=socket.socket(); s.settimeout(0.2)
  try: s.bind(("127.0.0.1", p)); s.close(); return True
  except Exception: return False
R["python"]=pyver()
R["venv"]=bool(os.environ.get("VIRTUAL_ENV"))
need=[("fastapi","fastapi"),("uvicorn","uvicorn"),("jinja2","jinja2")]
for mod,pipname in need:
  try: __import__(mod); R["deps"][pipname]=ok("present")
  except Exception: R["deps"][pipname]=ng("missing")
for p in (8000,5174):
  R["ports"][str(p)] = ok("free") if port_free(p) else ng("busy")
missing=[k for k,v in R["deps"].items() if not v["ok"]]
busy=[p for p,v in R["ports"].items() if not v["ok"]]
if missing: R["notes"].append("missing_deps:" + ",".join(missing))
if busy: R["notes"].append("busy_ports:" + ",".join(busy))
R["result"] = "pass" if not missing and not busy else "fail"
print(json.dumps(R, ensure_ascii=False))
sys.exit(0 if R["result"]=="pass" else 2)