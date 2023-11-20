from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QToolBar, QTableWidget, QVBoxLayout


class Ui_DialogueAssetsDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.tool_bar = QToolBar()
        self.refresh_action = QAction("Refresh")
        self.tool_bar.addActions([self.refresh_action])

        self.table = QTableWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.tool_bar)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.setWindowTitle("Dialogue Assets")
        self.setWindowIcon(QIcon("paragon.ico"))
        self.resize(500, 500)
