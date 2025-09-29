@echo off
set PY=python
%PY% -m venv .venv
call .venv\Scripts\activate
%PY% -m pip install -r heystive_professional\requirements-core.txt
%PY% -m pip install -r ui_modern_web\requirements-web.txt
if exist heystive_professional\requirements-extra.txt (
  %PY% -m pip install -r heystive_professional\requirements-extra.txt
)
if exist heystive_professional\requirements-audio.txt (
  %PY% -m pip install -r heystive_professional\requirements-audio.txt
)
start cmd /c "%PY% heystive_professional\backend_min.py"
timeout /t 2 >nul
set BACKEND_URL=http://127.0.0.1:8000
%PY% ui_modern_web\app.py