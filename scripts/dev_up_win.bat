@echo off
set PY=python
%PY% -m venv .venv
call .venv\Scripts\activate
%PY% -m pip install -r heystive_professional\requirements-core.txt
%PY% -m pip install -r ui_modern_web\requirements-web.txt
start cmd /c "%PY% heystive_professional\backend_min.py"
timeout /t 2 >nul
%PY% ui_modern_web\app.py