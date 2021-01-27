from PySide2 import QtGui
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QListView,
    QSplitter,
    QHBoxLayout,
    QWidget,
    QAbstractItemView,
    QMenu,
    QAction,
)


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.file_menu = QMenu("File")
        self.save_action = QAction("Save")
        self.reload_action = QAction("Reload")
        self.close_action = QAction("Close")
        self.quit_action = QAction("Quit")
        self.file_menu.addAction(self.save_action)
        self.file_menu.addSeparator()
        self.file_menu.addActions([self.reload_action, self.close_action])
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.quit_action)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QMenu("Help")
        self.about_action = QAction("About")
        self.help_menu.addAction(self.about_action)
        self.menuBar().addMenu(self.help_menu)

        self.nodes_list = QListView()
        self.multis_list = QListView()
        self.nodes_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.multis_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        nodes_view = QTabWidget()
        nodes_view.addTab(self.nodes_list, "Nodes")
        nodes_view.addTab(self.multis_list, "Multis")

        layout = QHBoxLayout()
        layout.addWidget(nodes_view)

        widget = QWidget()
        widget.setLayout(layout)

        self.splitter = QSplitter()
        self.splitter.setOrientation(QtGui.Qt.Horizontal)
        self.splitter.addWidget(widget)

        self.setWindowTitle("Paragon")
        self.setWindowIcon(QIcon("paragon.ico"))
        self.setCentralWidget(self.splitter)
        self.resize(600, 400)
