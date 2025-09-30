#!/usr/bin/env bash
set -e
bash scripts/dev_up.sh || sh scripts/dev_up.sh
curl -fsS http://127.0.0.1:8000/ping | python3 - <<'PY'
import sys,json
j=json.load(sys.stdin)
assert j.get("status")=="healthy"
print("PASS: backend healthy")
PY
curl -fsS http://127.0.0.1:5174/ >/dev/null
echo "PASS: web UI reachable"