from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox, QVBoxLayout


class Ui_ErrorDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.buttons)

        self.setLayout(layout)
        self.setModal(True)
        self.resize(400, 300)

        self.setWindowTitle("Error!")
        self.setWindowIcon(QIcon("paragon.ico"))
