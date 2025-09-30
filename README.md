# Heystive — Local Voice Assistant (Developer README)

Heystive is a local-first Persian/English voice assistant with a FastAPI backend, modern web UI, optional desktop shell, and a skill-based intent system. This README gives you everything you need to boot, test, and extend the project without guessing.

## Quick Start

### Linux/macOS
```bash
bash scripts/dev_up.sh || sh scripts/dev_up.sh
# Backend → http://127.0.0.1:8000  |  Web UI → http://127.0.0.1:5174
curl -fsS http://127.0.0.1:8000/ping
```

### Windows
```cmd
scripts\dev_up_win.bat
REM Backend → http://127.0.0.1:8000  |  Web UI → http://127.0.0.1:5174
curl http://127.0.0.1:8000/ping
```

## Architecture Overview
- **Backend (FastAPI):** `/ping`, `/api/status`, `/api/stt`, `/api/tts`, `/api/brain`, `/api/intent`, `/api/logs`, `/api/models/*`, `/settings`. SQLite is used for logs/memory where present.
- **Web UI (FastAPI + Jinja):** `ui_modern_web/app.py` serves the interface (port 5174) with mic controls and streaming.
- **Desktop UI (PySide6):** Optional GUI wrapper (`ui_modern_desktop/main_desktop.py`).
- **Skills & Brain:** `heystive_professional/skills/*`, `heystive_professional/intent_router.py`, `heystive_professional/brain.py`.
- **Streaming STT & VAD:** WebSocket `/ws/stream` with Vosk/Demo path and wake phrase handling.
- **Models Registry:** `/api/models/register|download|list` with checksum verification (file:// supported).
- **Settings:** `/settings` (HTML) and `/api/settings` (JSON upsert to `settings.json`).

## Runbook

### Start Services
```bash
bash scripts/dev_up.sh || sh scripts/dev_up.sh
```

### Health & Settings
```bash
curl -fsS http://127.0.0.1:8000/ping
curl -fsS http://127.0.0.1:8000/settings | head -n 5
```

### WebSocket Streaming (overview)
- `GET ws://127.0.0.1:8000/ws/stream`
  - Send `{"type":"start","sr":16000}` → receive `{"type":"ack","engine":"vosk|demo","vad":true|false}`
  - Send `{"type":"chunk","pcm_b64":"..."}` repeatedly
  - Send `{"type":"stop"}` to finalize; you'll receive `{"type":"final","text":"..."}`

## API Reference (selected)

### `GET /ping`
Returns backend status and timestamps.

### `POST /api/brain`
```http
POST /api/brain
Content-Type: application/json

{"text":"what time is it"}
```
Response shape:
```json
{"engine":"demo|llm","plan":[{"skill":"time","args":{"text":"what time is it"}}],"message":"..."}
```

### `POST /api/intent`
- Text route:
  ```json
  {"text":"note buy milk"}
  ```
  Response:
  ```json
  {"skill":"note","result":{"saved":true,"id":123}}
  ```
- Plan route:
  ```json
  {"plan":[{"skill":"note","args":{"text":"note buy tea"}},{"skill":"time","args":{"text":"what time"}}]}
  ```
  Response:
  ```json
  {"skill":"plan","results":[{"skill":"note","result":{"saved":true,"id":124}},{"skill":"time","result":{"time_iso":"..."}}]}
  ```

### `POST /api/stt`
Accept `{"audio_base64": "<PCM/WAV base64>"}` or `{"text":"..."}`; engine reports honestly as `whisper|vosk|demo`.

### `POST /api/tts`
Accept `{"text":"Hello"}`; returns `{"audio_base64":"...","engine":"pyttsx3|xtts|demo"}`. If a model is unavailable, returns an honest demo response with `engine:"demo"`.

### Models
- `GET /api/models/list`
- `POST /api/models/register` → `{name,type,url,sha256}`
- `POST /api/models/download?name=<model>` → verifies checksum and caches under `models/<name>/model.bin`

### Logs & Memory (if present)
- `GET /api/logs?limit=20`
- `POST /api/memory/upsert` → `{"text":"remember apples","tags":["grocery"]}`
- `POST /api/memory/search` → `{"q":"apples","limit":5}`

### Settings
- `GET /settings` (HTML preview of current JSON)
- `POST /api/settings` → upserts `settings.json`
  ```json
  {"web":{"theme":"light"},"audio":{"sr":16000},"server":{"host":"127.0.0.1","port":8000}}
  ```

## Phase Tracker
The file `docs/PHASES_TRACK.md` is the single source of truth. Only the **first unchecked** phase is executed by the agent, then ticked. This ensures deterministic, sequential progress.

## Archiving System
- Plan: `tools/archive_plan.py` → produces `archive_plan_<date>.csv`
- Apply: `tools/archive_apply.sh` (bash) / `tools/archive_apply.ps1` (PowerShell) — git-aware `mv`
- Guard: `tools/archive_guard.py` blocks `.log/.mp3/legacy` on commit
- Restore: `tools/archive_restore.py <path>` returns last archived version into the tree
- Ledger: `README_ARCHIVE.md`

## Testing & Smoke
- Environment doctor: `python tools/env_doctor.py`
- One-shot smoke: `bash scripts/smoke_after_archive.sh`
- Optional voice hard tests: `scripts/voice_hard_test.sh` (if present)

## Troubleshooting
- **Ports busy (8000/5174):** stop other processes or change `settings.json`.
- **Missing deps:** ensure venv active and run `scripts/dev_env.sh`.
- **Audio libs/models optional:** endpoints honestly fall back and return `engine:"demo"` with a `note`.

## Conventions
- Conventional Commits
- English-only content
- No code comments inside code files
- Additive & safe changes only

---
_This README is generated against the current repository snapshot. See `.repo_snapshot.json` for auto-detected details._