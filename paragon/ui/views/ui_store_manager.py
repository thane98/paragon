from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QTableView,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
    QPushButton, QStatusBar,
)


class Ui_StoreManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableView()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.verticalHeader().hide()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFixedWidth(100)
        self.auto_refresh_check = QCheckBox("Auto refresh?")

        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(self.refresh_button)
        refresh_layout.addWidget(self.auto_refresh_check)

        self.status_bar = QStatusBar()

        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table)
        table_layout.addLayout(refresh_layout)
        table_layout.addWidget(self.status_bar)

        self.setLayout(table_layout)
        self.resize(800, 600)
        self.setWindowTitle("Paragon - Store Manager")
        self.setWindowIcon(QIcon("paragon.ico"))
