import re, sys, time, pathlib
p = pathlib.Path("docs/PHASES_TRACK.md")
s = p.read_text(encoding="utf-8") if p.exists() else ""
if not s:
    print("tracker missing")
    sys.exit(1)
lines = s.splitlines()
if len(sys.argv) == 1 or sys.argv[1] == "next":
    for idx, ln in enumerate(lines):
        m = re.match(r"- \[ \] Phase (\d+&\d+|\d+) ", ln)
        if m:
            print(m.group(1))
            sys.exit(0)
    print("done")
    sys.exit(0)
if sys.argv[1] == "check":
    ids = sys.argv[2:]
    if not ids:
        sys.exit("usage: phase_check.py check <ID> [<ID2> ...]")
    out = []
    checked = set()
    for ln in lines:
        for ident in ids:
            if ident not in checked and re.match(rf"- \[ \] Phase {re.escape(ident)} ", ln):
                ln = ln.replace("[ ]", "[x]", 1)
                checked.add(ident)
        out.append(ln)
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    out = out + ["", f"<!-- Phases {', '.join(ids)} completed at {ts} -->"]
    p.write_text("\n".join(out), encoding="utf-8")
    print("checked " + " ".join(ids))
    sys.exit(0)
sys.exit("unknown command")