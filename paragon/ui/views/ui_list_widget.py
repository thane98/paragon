from PySide2 import QtGui
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import (
    QWidget,
    QToolBar,
    QAction,
    QLineEdit,
    QListView,
    QVBoxLayout,
    QSplitter,
    QSizePolicy,
    QShortcut,
    QAbstractItemView,
)


class Ui_ListWidget(QWidget):
    def __init__(self, static_items, orientation):
        super().__init__()

        self.add_action = QAction("Add")
        self.delete_action = QAction("Delete")
        self.copy_to_action = QAction("Copy To")
        self.advanced_copy_action = QAction("Advanced Copy")

        self.deselect_shortcut = QShortcut(QKeySequence(QKeySequence.Cancel), self)
        self.copy_shortcut = QShortcut(QKeySequence("CTRL+C"), self)
        self.paste_shortcut = QShortcut(QKeySequence("CTRL+V"), self)

        self.tool_bar = QToolBar()
        self.tool_bar.addActions([self.add_action, self.delete_action])
        self.tool_bar.addSeparator()
        self.tool_bar.addActions([self.copy_to_action, self.advanced_copy_action])
        if static_items:
            self.tool_bar.setVisible(False)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")

        self.list = QListView()
        if not static_items:
            self.list.setDragDropMode(QAbstractItemView.InternalMove)
            self.list.setDragEnabled(True)
            self.list.setDropIndicatorShown(True)
            self.list.setAcceptDrops(True)

        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.addWidget(self.search)
        self.left_layout.addWidget(self.list)
        self.left_widget.setLayout(self.left_layout)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.left_widget)
        if orientation == "vertical":
            self.splitter.setOrientation(QtGui.Qt.Vertical)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tool_bar)
        self.main_layout.addWidget(self.splitter)

        self.setLayout(self.main_layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
