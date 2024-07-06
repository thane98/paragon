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


class Ui_ChapterEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.new_action = QAction("New")
        self.toggle_chapter_list_action = QAction("Toggle Chapter List")
        self.tool_bar = QToolBar()
        self.tool_bar.addAction(self.new_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.toggle_chapter_list_action)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.list = QListView()

        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.addWidget(self.search)
        self.left_layout.addWidget(self.list)
        self.left_widget.setLayout(self.left_layout)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.left_widget)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 0, 5, 5)
        self.main_layout.addWidget(self.tool_bar)
        self.main_layout.addWidget(self.splitter)

        self.setLayout(self.main_layout)

        self.setWindowTitle("Paragon - Chapter Editor")
        self.setWindowIcon(QIcon("paragon.ico"))
