from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout


class Ui_FileSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.line_edit = QLineEdit()
        self.open_dialog_button = QPushButton(text="...")
        self.open_dialog_button.setMaximumWidth(50)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.open_dialog_button)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)
