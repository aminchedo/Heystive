#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# Start web interface
web_path = Path(__file__).parent / "ui_modern_web" / "app.py"
subprocess.run([sys.executable, str(web_path)])
