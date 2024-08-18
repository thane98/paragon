from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QListView, QLineEdit, QVBoxLayout, QSplitter

from paragon.ui.controllers.gcn_map_editor import GcnMapEditor


class Ui_GcnTopLevelMapEditor(QWidget):
    def __init__(self, ms, gs):
        super().__init__()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.list = QListView()

        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.addWidget(self.search)
        self.left_layout.addWidget(self.list)
        self.left_widget.setLayout(self.left_layout)

        self.map_editor = GcnMapEditor(ms, gs)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.map_editor)
        self.splitter.setStretchFactor(1, 1)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.addWidget(self.splitter)

        self.setLayout(self.main_layout)

        self.setWindowTitle("Paragon - Map Editor")
        self.setWindowIcon(QIcon("paragon.ico"))
