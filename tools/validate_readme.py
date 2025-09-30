import re, sys, json, os
rd = open("README.md","r",encoding="utf-8").read()
must = [
  r"# Heystive",
  r"## Quick Start",
  r"## Architecture Overview",
  r"## Runbook",
  r"## API Reference",
  r"## Phase Tracker",
  r"## Archiving System",
  r"## Testing & Smoke",
  r"## Troubleshooting",
  r"## Conventions"
]
for rx in must:
  if not re.search(rx, rd, re.I|re.M):
    print("MISSING_SECTION:", rx); sys.exit(2)
if len(rd) < 2000:
  print("README_TOO_SHORT"); sys.exit(2)
print("PASS: README structure and length OK")