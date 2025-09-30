import os, sys, subprocess
rules={}
for ln in open(".archive-guard.rules","r",encoding="utf-8"):
  ln=ln.strip()
  if not ln or ln.startswith("#"): continue
  if "=" in ln:
    k,v=ln.split("=",1); rules[k.strip()]=[x.strip() for x in v.split(",") if x.strip()]
try:
  added=subprocess.check_output(["git","diff","--cached","--name-only","--diff-filter=A"]).decode().splitlines()
except Exception:
  added=[]
viol=[]
for p in added:
  low=p.lower()
  for ext in rules.get("BLOCK_EXT",[]):
    if low.endswith(ext): viol.append(p); break
  for d in rules.get("BLOCK_DIR",[]):
    if low.startswith(d.lower()+"/") or low==d.lower(): viol.append(p); break
if viol:
  print("ArchiveGuard: blocked paths:\n" + "\n".join(viol))
  sys.exit(2)
print("ArchiveGuard: OK")