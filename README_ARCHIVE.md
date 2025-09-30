# Heystive Archive Ledger
This repository uses a deterministic archiving plan and git-aware moves to keep the runtime lean.
- Plan file: archive_plan_<date>.csv
- Apply scripts: tools/archive_apply.sh, tools/archive_apply.ps1
- Archive root: archive/<date>/
After each archive, backend and web UI must pass the smoke tests.