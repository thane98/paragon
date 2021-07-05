from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QToolBar, QTableWidget, QVBoxLayout, QAction


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
