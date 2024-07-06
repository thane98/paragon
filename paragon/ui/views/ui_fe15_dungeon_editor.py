from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QWidget,
    QToolBar,
    QLineEdit,
    QListView,
    QVBoxLayout,
    QSplitter,
    QTabWidget,
)


class Ui_FE15DungeonEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.toggle_dungeon_list_action = QAction("Toggle Dungeon List")
        self.tool_bar = QToolBar()
        self.tool_bar.addAction(self.toggle_dungeon_list_action)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.list = QListView()

        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.addWidget(self.search)
        self.left_layout.addWidget(self.list)
        self.left_widget.setLayout(self.left_layout)

        self.tabs = QTabWidget()

        self.splitter = QSplitter()
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.tabs)
        self.splitter.setStretchFactor(1, 1)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tool_bar)
        self.main_layout.addWidget(self.splitter)

        self.setLayout(self.main_layout)

        self.setWindowTitle("Paragon - Dungeon Editor")
        self.setWindowIcon(QIcon("paragon.ico"))
