import re, sys, time, pathlib
p = pathlib.Path("docs/PHASES_TRACK.md")
s = p.read_text(encoding="utf-8")
lines = s.splitlines()
if len(sys.argv) == 1 or sys.argv[1] == "next":
  for idx, ln in enumerate(lines):
    m = re.match(r"- \[ \] Phase (\d+) ", ln)
    if m:
      print(m.group(1))
      sys.exit(0)
  print("done")
  sys.exit(0)
if sys.argv[1] == "check":
  if len(sys.argv) < 3: sys.exit("usage: phase_check.py check <N>")
  n = sys.argv[2]
  out = []
  checked = False
  for ln in lines:
    if not checked and re.match(rf"- \[ \] Phase {re.escape(n)} ", ln):
      ln = ln.replace("[ ]", "[x]", 1)
      checked = True
    out.append(ln)
  ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
  out = out + ["", f"<!-- Phase {n} completed at {ts} -->"]
  p.write_text("\n".join(out), encoding="utf-8")
  print(f"checked {n}")
  sys.exit(0)
sys.exit("unknown command")