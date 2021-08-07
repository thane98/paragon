from PySide2 import QtGui
from PySide2.QtWidgets import (
    QWidget,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


class Ui_FE10MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.chapters_button = QPushButton("Chapters")
        self.characters_button = QPushButton("Characters")
        self.items_button = QPushButton("Items")
        self.classes_button = QPushButton("Classes")
        self.skills_button = QPushButton("Skills")
        self.armies_button = QPushButton("Armies")
        self.tiles_button = QPushButton("Tiles")
        self.supports_button = QPushButton("Supports")
        self.no_battle_button = QPushButton("No Battle")

        core_box = QGroupBox("Core Data")
        core_layout = QVBoxLayout()
        core_layout.setAlignment(QtGui.Qt.AlignTop)
        core_layout.addWidget(self.chapters_button)
        core_layout.addWidget(self.characters_button)
        core_layout.addWidget(self.items_button)
        core_layout.addWidget(self.classes_button)
        core_layout.addWidget(self.skills_button)
        core_layout_2 = QVBoxLayout()
        core_layout_2.setAlignment(QtGui.Qt.AlignTop)
        core_layout_2.addWidget(self.armies_button)
        core_layout_2.addWidget(self.tiles_button)
        core_layout_2.addWidget(self.supports_button)
        core_layout_2.addWidget(self.no_battle_button)
        core_layout_main = QHBoxLayout()
        core_layout_main.addLayout(core_layout)
        core_layout_main.addLayout(core_layout_2)
        core_box.setLayout(core_layout_main)

        self.portraits_button = QPushButton("Portraits")

        assets_box = QGroupBox("Assets")
        assets_layout = QVBoxLayout()
        assets_layout.setAlignment(QtGui.Qt.AlignTop)
        assets_layout.addWidget(self.portraits_button)
        assets_box.setLayout(assets_layout)

        layout = QGridLayout()
        layout.addWidget(core_box, 0, 0, 1, 2)
        layout.addWidget(assets_box, 1, 0)

        self.setLayout(layout)
