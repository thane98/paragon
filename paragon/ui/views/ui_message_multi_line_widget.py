from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPlainTextEdit


class Ui_MessageMultiLineWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.key = QLineEdit()
        self.value = QPlainTextEdit()
        layout.addWidget(self.key)
        layout.addWidget(self.value)
        self.setLayout(layout)
