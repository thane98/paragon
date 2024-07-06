from PySide6 import QtGui
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


class Ui_FE13MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.chapters_button = QPushButton("Chapters")
        self.characters_button = QPushButton("Characters")
        self.items_button = QPushButton("Items")
        self.classes_button = QPushButton("Classes")
        self.skills_button = QPushButton("Skills")
        self.armies_button = QPushButton("Armies")
        self.tiles_button = QPushButton("Tiles")
        self.sprite_data_button = QPushButton("BMap / Sprite Data")
        self.gmap_button = QPushButton("Chapter Placements / GMap")
        self.endings_button = QPushButton("Endings")

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
        core_layout_2.addWidget(self.sprite_data_button)
        core_layout_2.addWidget(self.gmap_button)
        core_layout_2.addWidget(self.endings_button)
        core_layout_main = QHBoxLayout()
        core_layout_main.addLayout(core_layout)
        core_layout_main.addLayout(core_layout_2)
        core_box.setLayout(core_layout_main)

        self.asset_definitions_button = QPushButton("Asset Definitions")
        self.presets_button = QPushButton("Presets")
        self.portraits_button = QPushButton("Portraits")

        assets_box = QGroupBox("Assets")
        assets_layout = QVBoxLayout()
        assets_layout.setAlignment(QtGui.Qt.AlignTop)
        assets_layout.addWidget(self.asset_definitions_button)
        assets_layout.addWidget(self.presets_button)
        assets_layout.addWidget(self.portraits_button)
        assets_box.setLayout(assets_layout)

        self.edit_dialogue_button = QPushButton("Edit Dialogue")
        self.quick_dialogue_button = QPushButton("Quick Dialogue Generator")
        self.configure_avatar_button = QPushButton("Configure Avatar")
        self.store_manager_button = QPushButton("Store Manager")

        misc_box = QGroupBox("Misc.")
        misc_layout = QVBoxLayout()
        misc_layout.setAlignment(QtGui.Qt.AlignTop)
        misc_layout.addWidget(self.edit_dialogue_button)
        misc_layout.addWidget(self.quick_dialogue_button)
        misc_layout.addWidget(self.configure_avatar_button)
        misc_layout.addWidget(self.store_manager_button)
        misc_box.setLayout(misc_layout)

        layout = QGridLayout()
        layout.addWidget(core_box, 0, 0, 1, 2)
        layout.addWidget(assets_box, 1, 0)
        layout.addWidget(misc_box, 1, 1)

        self.setLayout(layout)
