from PySide6 import QtGui
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


class Ui_FE9MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.maps_button = QPushButton("Maps")
        self.chapters_button = QPushButton("Chapters")
        self.characters_button = QPushButton("Characters")
        self.classes_button = QPushButton("Classes")
        self.items_button = QPushButton("Items")
        self.skills_button = QPushButton("Skills")
        self.armies_button = QPushButton("Armies")
        self.tiles_button = QPushButton("Tiles")
        self.supports_button = QPushButton("Supports")
        self.portraits_button = QPushButton("Portraits")
        self.raw_dialogue_button = QPushButton("Raw Dialogue")
        self.scripts_button = QPushButton("Scripts")
        self.store_manager_button = QPushButton("Store Manager")

        core_layout = QVBoxLayout()
        core_layout.setAlignment(QtGui.Qt.AlignmentFlag.AlignTop)
        core_layout.addWidget(self.maps_button)
        core_layout.addWidget(self.chapters_button)
        core_layout.addWidget(self.characters_button)
        core_layout.addWidget(self.classes_button)
        core_layout.addWidget(self.items_button)
        core_layout.addWidget(self.skills_button)
        core_layout.addWidget(self.armies_button)
        core_layout.addWidget(self.tiles_button)
        core_layout.addWidget(self.supports_button)
        core_layout.addWidget(self.portraits_button)
        core_layout.addWidget(self.raw_dialogue_button)
        core_layout.addWidget(self.scripts_button)
        core_layout.addWidget(self.store_manager_button)

        self.setLayout(core_layout)
