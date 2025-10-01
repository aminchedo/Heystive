import os, sys, requests, logging
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from desktop.hotkeys import GlobalHotkeys

logging.basicConfig(filename="heystive_desktop.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8765")

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heystive Desktop MVP")
        self.out = QLabel()
        btn = QPushButton("Ping Backend")
        btn.clicked.connect(self.ping)
        lay = QVBoxLayout(self)
        lay.addWidget(btn)
        lay.addWidget(self.out)
        self.hotkeys = GlobalHotkeys(on_toggle_listen=self.toggle_listen, on_focus=self.focus_window)
        self.hotkeys.start()

    def ping(self):
        try:
            r = requests.get(BACKEND_URL + "/ping", timeout=3)
            self.out.setText(r.text)
            logging.info("Ping OK: %s", r.text)
        except Exception as e:
            self.out.setText("error")
            logging.exception("Ping error: %s", e)
    
    def toggle_listen(self):
        logging.info("Global hotkey triggered: toggle listen")
        self.out.setText("Hotkey: Toggle Listen")
    
    def focus_window(self):
        logging.info("Global hotkey triggered: focus window")
        self.raise_()
        self.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Main()
    w.resize(360, 180)
    w.show()
    sys.exit(app.exec())