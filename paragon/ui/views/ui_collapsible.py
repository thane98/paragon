from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton


class Ui_Collapsible(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.toggle = QPushButton("Toggle")
        layout.addWidget(self.toggle)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setContentsMargins(0, 0, 0, 0)
