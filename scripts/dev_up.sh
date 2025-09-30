set -e
py=python3
[ -x "$(command -v python)" ] && py=python
$py -m venv .venv
. .venv/bin/activate
pip install -r heystive_professional/requirements-core.txt
pip install -r ui_modern_web/requirements-web.txt
if [ -f heystive_professional/requirements-extra.txt ]; then pip install -r heystive_professional/requirements-extra.txt || true; fi
if [ -f heystive_professional/requirements-audio.txt ]; then pip install -r heystive_professional/requirements-audio.txt || true; fi
if [ -f heystive_professional/requirements-models.txt ]; then pip install -r heystive_professional/requirements-models.txt || true; fi
($py heystive_professional/backend_min.py) &
sleep 2
BACKEND_URL=${BACKEND_URL:-http://127.0.0.1:8000} $py ui_modern_web/app.py