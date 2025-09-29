set -e
py=python3
[ -x "$(command -v python)" ] && py=python
$py -m venv .venv
. .venv/bin/activate
pip install -r heystive_professional/requirements-core.txt
pip install -r ui_modern_web/requirements-web.txt
($py heystive_professional/backend_min.py) &
sleep 2
$py ui_modern_web/app.py