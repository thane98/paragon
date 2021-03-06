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
    QLineEdit,
    QVBoxLayout,
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

        self.view_menu = QMenu("View")
        self.show_animations_action = QAction("Show Animations")
        self.show_animations_action.setCheckable(True)
        self.view_menu.addAction(self.show_animations_action)
        self.menuBar().addMenu(self.view_menu)

        self.help_menu = QMenu("Help")
        self.about_action = QAction("About")
        self.help_menu.addAction(self.about_action)
        self.menuBar().addMenu(self.help_menu)

        self.nodes_list = QListView()
        self.nodes_search = QLineEdit()
        self.nodes_search.setPlaceholderText("Search...")
        self.multis_list = QListView()
        self.multis_search = QLineEdit()
        self.multis_search.setPlaceholderText("Search...")
        self.nodes_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.multis_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.nodes_layout = QVBoxLayout()
        self.nodes_layout.setSpacing(5)
        self.nodes_layout.setContentsMargins(0, 0, 0, 0)
        self.nodes_layout.addWidget(self.nodes_search)
        self.nodes_layout.addWidget(self.nodes_list)
        self.nodes_widget = QWidget()
        self.nodes_widget.setContentsMargins(0, 0, 0, 0)
        self.nodes_widget.setLayout(self.nodes_layout)

        self.multis_layout = QVBoxLayout()
        self.multis_layout.setSpacing(5)
        self.multis_layout.setContentsMargins(0, 0, 0, 0)
        self.multis_layout.addWidget(self.multis_search)
        self.multis_layout.addWidget(self.multis_list)
        self.multis_widget = QWidget()
        self.multis_widget.setContentsMargins(0, 0, 0, 0)
        self.multis_widget.setLayout(self.multis_layout)

        nodes_view = QTabWidget()
        nodes_view.addTab(self.nodes_widget, "Nodes")
        nodes_view.addTab(self.multis_widget, "Multis")

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
        self.resize(700, 450)
