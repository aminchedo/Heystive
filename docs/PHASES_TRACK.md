# Heystive – Phase Tracker (Minimal)

## Phase Checklist
- [x] Phase 1 – MVP boot
- [x] Phase 2 – Offline STT/TTS + Config
- [x] Phase 3 – Intent Router + Skills + Logs
- [x] Phase 4 – Streaming Mic + VAD + Wake
- [x] Phase 5 – Orchestrator + Logs API + Notes
- [x] Phase 6 – Conversational Brain (+ Tool Use)
- [x] Phase 7&8 – Plugin Sandbox + Memory (combined)
- [x] Phase 9 – STT/TTS Models & Downloader
- [x] Phase 10 – Packaging/Service/Settings
- [x] Phase 12 – QA/CI/CD (tests, builds, artifacts)

---

## Phase 10 – Packaging/Service/Settings
### Tasks
- [ ] Service runner: `scripts/service.sh` (Linux/macOS) و `scripts/service_win.bat` (Windows) با start/stop/restart/status و log rotation.
- [ ] Settings API: `GET /settings` (HTML non-empty) و `POST /api/settings` (JSON upsert در `settings.json`).
- [ ] Backend، روی start سرویس از `settings.json` بخونه (port/base urls).
### Quality Gates
- [ ] `scripts/service.sh start && sleep 1 && curl -fsS http://127.0.0.1:8000/ping` → `status:"healthy"`.
- [ ] `curl -fsS http://127.0.0.1:8000/settings` برمی‌گرده و non-empty است.
- [ ] `curl -fsS -X POST http://127.0.0.1:8000/api/settings -H "Content-Type: application/json" -d '{"web":{"theme":"light"},"audio":{"sr":16000}}'` → `{ok:true}` و فایل `settings.json` به‌روزشده.
- [ ] `scripts/service.sh stop` پردازش backend را متوقف می‌کند و فایل لاگ غیرخالی است.
### Completion
- unchecked

---

## Phase 12 – QA/CI/CD
### Tasks
- [ ] PyTest حداقلی برای `/ping`, `/api/settings` و سرویس start/stop (با subprocess).
- [ ] GitHub Actions: workflow ساده `python -m pip install -r ... && pytest -q` و تولید artifact لاگ سرویس نمونه.
### Quality Gates
- [ ] `pytest -q` exit code == 0.
- [ ] CI run سبز و artifact ساخته می‌شود.
### Completion
- unchecked

<!-- Phases 10 completed at 2025-09-30 01:29:10 UTC -->

<!-- Phases 12 completed at 2025-09-30 01:29:50 UTC -->