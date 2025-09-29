from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout
class PersianTextWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QTextEdit()
        self.view.setReadOnly(False)
        lay = QVBoxLayout(self)
        lay.addWidget(self.view)