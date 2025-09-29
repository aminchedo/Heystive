import os, sys, requests
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
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
        except Exception:
            self.out.setText("error")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Main()
    w.resize(360, 180)
    w.show()
    sys.exit(app.exec())