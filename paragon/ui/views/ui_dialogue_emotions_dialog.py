from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QToolBar, QTableWidget, QVBoxLayout


class Ui_DialogueEmotionsDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.table = QTableWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.setWindowTitle("Dialogue Emotions")
        self.setWindowIcon(QIcon("paragon.ico"))
        self.resize(500, 500)
