#!/usr/bin/env bash
set -e
py=python3; command -v python >/dev/null 2>&1 && py=python
$py -m venv .venv || true
. .venv/bin/activate
pip install -U pip
pip install -r heystive_professional/requirements-core.txt
pip install -r ui_modern_web/requirements-web.txt
$py tools/env_doctor.py