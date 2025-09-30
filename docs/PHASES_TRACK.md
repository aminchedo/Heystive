# Heystive – Phase Tracker (Single Source of Truth)

## Phase Checklist
- [x] Phase 1 – MVP boot
- [x] Phase 2 – Offline STT/TTS + Config
- [x] Phase 3 – Intent Router + Skills + Logs
- [x] Phase 4 – Streaming Mic + VAD + Wake
- [x] Phase 5 – Orchestrator (Auto-Intent/Speak) + Logs API + Notes
- [x] Phase 6 – Conversational Brain (+ Tool Use Gateway)
- [ ] Phase 7 – Plugin Sandbox (Permissions/Isolation)
- [ ] Phase 8 – Memory & Retrieval (RAG-lite)
- [ ] Phase 9 – STT/TTS Production-grade (models & downloader)
- [ ] Phase 10 – Packaging/Service/Settings
- [ ] Phase 11 – Security/Permissions/Privacy Policies
- [ ] Phase 12 – QA/CI/CD (tests, builds, artifacts)

---

## Phase 5 – Orchestrator (Auto-Intent/Speak) + Logs API + Notes
### Tasks (must implement all)
- [ ] Add Note skill and persist notes to SQLite.
- [ ] Expose GET /api/logs with pagination params.
- [ ] Web UI: Auto-Intent toggle; Speak toggle; Results panel; STT/stream → intent → optional TTS playback.
### Quality Gates (must all pass)
- [ ] `curl -fsS -X POST http://127.0.0.1:8000/api/intent -H "Content-Type: application/json" -d '{"text":"note buy milk"}'` returns `{"skill":"note","result":{"saved":true,"id":<int>}}`
- [ ] `curl -fsS "http://127.0.0.1:8000/api/logs?limit=5"` returns JSON with `items` array length ≥ 1
- [ ] Home UI contains `id="auto_intent"`, `id="auto_speak"`, and `id="results"`
### Completion
- unchecked

---

## Phase 6 – Conversational Brain (+ Tool Use Gateway)
### Tasks
- [ ] Add POST /api/brain that accepts text and returns `{engine:"<name|demo>", plan:[{skill, args}], message:"..."}`.
- [ ] If LLM unavailable, fall back to rule-based planner; response must clearly indicate `engine:"demo"`.
- [ ] Wire /api/intent to optionally accept a `plan` to execute multiple skills.
### Quality Gates
- [ ] `curl -fsS -X POST http://127.0.0.1:8000/api/brain -H "Content-Type: application/json" -d '{"text":"what time is it"}'` returns `plan` with at least one step or `engine:"demo"`
- [ ] Planner output schema strictly matches: top-level keys `engine, plan, message`
### Completion
- unchecked

---

## Phase 7 – Plugin Sandbox (Permissions/Isolation)
### Tasks
- [ ] Stable skill contract; skills registered via manifest file.
- [ ] Skill execution in subprocess with time/memory limits.
- [ ] Permission prompts for sensitive actions (open URL, file I/O, system ops).
### Quality Gates
- [ ] `GET /api/skills` lists installed skills with permission requirements.
- [ ] A skill requiring file write is blocked until explicit allow; JSON states `granted:false` before approval.
### Completion
- unchecked

---

## Phase 8 – Memory & Retrieval (RAG-lite)
### Tasks
- [ ] Add POST /api/memory/search (keyword first; vector optional if available).
- [ ] Auto-log conversational turns; search integrates with /api/brain when enabled.
### Quality Gates
- [ ] `curl -fsS -X POST http://127.0.0.1:8000/api/memory/search -H "Content-Type: application/json" -d '{"q":"milk"}'` returns `results` array (possibly empty, but valid schema).
### Completion
- unchecked

---

## Phase 9 – STT/TTS Production-grade (models & downloader)
### Tasks
- [ ] Safe downloader with checksum and caching for models.
- [ ] Faster-Whisper (CTranslate2) integration or honest demo fallback.
- [ ] Coqui/VITS TTS or honest demo fallback.
### Quality Gates
- [ ] Downloader writes to `models/` and verifies checksum; JSON reports `verified:true`.
- [ ] If models missing, endpoints clearly return demo with `engine:"demo"` and `note`.
### Completion
- unchecked

---

## Phase 10 – Packaging/Service/Settings
### Tasks
- [ ] Local service runner script (start/stop/restart, log rotation).
- [ ] Settings UI page (web) reading/writing a JSON settings file.
### Quality Gates
- [ ] `scripts/service.sh start` spawns backend; `scripts/service.sh stop` stops it; log file exists and grows.
- [ ] `GET /settings` serves a non-empty page; `POST /api/settings` writes JSON.
### Completion
- unchecked

---

## Phase 11 – Security/Permissions/Privacy Policies
### Tasks
- [ ] Central policy enforcement for skills; allow/deny audit log.
- [ ] Redact sensitive fields in logs and API responses.
### Quality Gates
- [ ] Attempt a blocked action returns `{allowed:false, reason:"policy"}`.
- [ ] Logs API redacts configured fields.
### Completion
- unchecked

---

## Phase 12 – QA/CI/CD
### Tasks
- [ ] PyTest suite for core endpoints and skills.
- [ ] GitHub Actions building artifacts and running tests.
### Quality Gates
- [ ] `pytest -q` exits 0.
- [ ] CI workflow artifact present in `dist/` or the CI run summary.
### Completion
- unchecked

<!-- Phase 5 completed at 2025-09-29 15:47:43 UTC -->

<!-- Phase 6 completed at 2025-09-30 01:06:10 UTC -->