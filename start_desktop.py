#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# Start desktop interface
desktop_path = Path(__file__).parent / "ui_modern_desktop" / "main_desktop.py"
subprocess.run([sys.executable, str(desktop_path)])
