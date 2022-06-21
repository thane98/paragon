from PySide2 import QtGui
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QWidget,
    QToolBar,
    QAction,
    QTableView,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
)


class Ui_ProjectSelect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.new_action = QAction("New")
        self.edit_action = QAction("Edit")
        self.open_action = QAction("Open")
        self.delete_action = QAction("Delete")
        self.move_up_action = QAction("Move Up")
        self.move_down_action = QAction("Move Down")

        tool_bar = QToolBar()
        tool_bar.setOrientation(QtGui.Qt.Vertical)
        tool_bar.addAction(self.new_action)
        tool_bar.addSeparator()
        tool_bar.addActions([self.edit_action, self.open_action, self.delete_action])
        tool_bar.addSeparator()
        tool_bar.addActions([self.move_up_action, self.move_down_action])

        self.table = QTableView()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.verticalHeader().hide()
        self.remember_check = QCheckBox("Remember selection.")

        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table)
        table_layout.addWidget(self.remember_check)
        table_widget = QWidget()
        table_widget.setContentsMargins(0, 0, 0, 0)
        table_widget.setLayout(table_layout)

        layout = QHBoxLayout()
        layout.addWidget(tool_bar)
        layout.addWidget(table_widget)
        self.setLayout(layout)
        self.resize(650, 400)
        self.setWindowTitle("Paragon")
        self.setWindowIcon(QIcon("paragon.ico"))
