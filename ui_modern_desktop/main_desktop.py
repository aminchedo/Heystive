import os, sys, requests, logging
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

logging.basicConfig(filename="heystive_desktop.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

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

    def ping(self):
        try:
            r = requests.get(BACKEND_URL + "/ping", timeout=3)
            self.out.setText(r.text)
            logging.info("Ping OK: %s", r.text)
        except Exception as e:
            self.out.setText("error")
            logging.exception("Ping error: %s", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Main()
    w.resize(360, 180)
    w.show()
    sys.exit(app.exec())