import os, sys, glob, shutil, subprocess
if len(sys.argv)<2:
  print("usage: archive_restore.py <relative/path>")
  sys.exit(1)
rel=sys.argv[1]
candidates=sorted(glob.glob(os.path.join("archive","*","**",rel), recursive=True))
if not candidates:
  print("not_found")
  sys.exit(2)
src=candidates[-1]; dst=rel
os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
try: subprocess.check_call(["git","mv",src,dst])
except Exception: shutil.move(src,dst)
print("restored", dst)