from PySide6 import QtGui
from PySide6.QtCore import QRectF
from PySide6.QtWidgets import (
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QComboBox,
)

from paragon.ui.controllers.scene_graphics_view import DialogueGraphicsView


class Ui_DialoguePlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.view = DialogueGraphicsView()
        self.view.setFixedSize(400, 242)
        self.view.setHorizontalScrollBarPolicy(QtGui.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(QtGui.Qt.ScrollBarAlwaysOff)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 400, 242)
        self.view.setScene(self.scene)

        self.begin_button = QPushButton("<<")
        self.previous_button = QPushButton("<")
        self.next_button = QPushButton(">")
        self.end_button = QPushButton(">>")

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.addWidget(self.begin_button)
        self.buttons_layout.addWidget(self.previous_button)
        self.buttons_layout.addWidget(self.next_button)
        self.buttons_layout.addWidget(self.end_button)
        self.buttons_layout.setAlignment(QtGui.Qt.AlignHCenter)

        self.background_box = QComboBox()
        self.window_type_box = QComboBox()
        config_layout = QFormLayout()
        config_layout.addRow("Background", self.background_box)
        config_layout.addRow("Window Type", self.window_type_box)
        config_box = QGroupBox("Configure Preview")
        config_box.setLayout(config_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        layout.addLayout(self.buttons_layout)
        layout.addWidget(config_box)
        layout.addStretch()
        self.setLayout(layout)
