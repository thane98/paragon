from PySide2 import QtGui
from PySide2.QtCore import QRectF
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QComboBox, QStatusBar, QLabel,
)

from paragon.ui.controllers.scene_graphics_view import DialogueGraphicsView


class Ui_EndingEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.keys_box = QComboBox()
        self.keys_box.setStyleSheet("combobox-popup: 0;")
        self.keys_box.setEditable(True)
        self.keys_box.setInsertPolicy(QComboBox.NoInsert)
        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")

        self.generic_layout = QHBoxLayout()
        self.generic_layout.addWidget(self.keys_box)
        self.generic_layout.addWidget(self.new_button)
        self.generic_layout.addWidget(self.delete_button)
        self.generic_layout.setStretch(0, 1)

        self.view = QGraphicsView()
        self.view.scale(2.0, 2.0)
        self.view.setFixedSize(400 * 2, 242 * 2)
        self.view.setHorizontalScrollBarPolicy(QtGui.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(QtGui.Qt.ScrollBarAlwaysOff)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 400, 242)
        self.view.setScene(self.scene)

        self.status_bar = QStatusBar()
        self.ending_info_widget = QLabel()
        self.status_bar.addPermanentWidget(self.ending_info_widget)

        layout = QVBoxLayout()
        layout.addLayout(self.generic_layout)
        layout.addWidget(self.view)
        layout.addWidget(self.status_bar)
        layout.setAlignment(self.view, QtGui.Qt.AlignHCenter)
        self.setLayout(layout)

        self.setWindowTitle("Paragon - Ending Editor")
        self.setWindowIcon(QIcon("paragon.ico"))
