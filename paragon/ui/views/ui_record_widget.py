from PySide2 import QtGui
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout


class Ui_RecordWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")
        self.toggle_button = QPushButton("Toggle Widget")

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.addWidget(self.new_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.toggle_button)

        self.buttons_widget = QWidget()
        self.buttons_widget.setLayout(self.buttons_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.buttons_widget)
        layout.setAlignment(QtGui.Qt.AlignTop)
        self.setLayout(layout)
