from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit


class Ui_MessageWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.key = QLineEdit()
        self.value = QLineEdit()
        layout.addWidget(self.key)
        layout.addWidget(self.value)
        self.setLayout(layout)
