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
        self.weapon_interactions_button = QPushButton("Weapon Interactions")

        core_box = QGroupBox("Core Data")
        core_layout = QVBoxLayout()
        core_layout.setContentsMargins(5, 5, 5, 5)
        core_layout.setAlignment(QtGui.Qt.AlignTop)
        core_layout.addWidget(self.chapters_button)
        core_layout.addWidget(self.characters_button)
        core_layout.addWidget(self.items_button)
        core_layout.addWidget(self.classes_button)
        core_layout.addWidget(self.skills_button)
        core_layout_2 = QVBoxLayout()
        core_layout_2.setContentsMargins(5, 5, 5, 5)
        core_layout_2.setAlignment(QtGui.Qt.AlignTop)
        core_layout_2.addWidget(self.armies_button)
        core_layout_2.addWidget(self.tiles_button)
        core_layout_2.addWidget(self.supports_button)
        core_layout_2.addWidget(self.no_battle_button)
        core_layout_2.addWidget(self.weapon_interactions_button)
        core_layout_main = QHBoxLayout()
        core_layout_main.addLayout(core_layout)
        core_layout_main.addLayout(core_layout_2)
        core_box.setLayout(core_layout_main)

        self.scripts_button = QPushButton("Scripts")

        chapter_data_box = QGroupBox("Chapter Data")
        chapter_data_layout = QVBoxLayout()
        chapter_data_layout.setContentsMargins(5, 5, 5, 5)
        chapter_data_layout.addWidget(self.scripts_button)
        chapter_data_box.setLayout(chapter_data_layout)

        self.portraits_button = QPushButton("Portraits")
        self.effects_button = QPushButton("Effects")

        assets_box = QGroupBox("Assets")
        assets_layout = QVBoxLayout()
        assets_layout.setContentsMargins(5, 5, 5, 5)
        assets_layout.setAlignment(QtGui.Qt.AlignTop)
        assets_layout.addWidget(self.portraits_button)
        assets_layout.addWidget(self.effects_button)
        assets_box.setLayout(assets_layout)

        self.dialogue_button = QPushButton("Raw Dialogue Editor")
        self.conversations_button = QPushButton("Base Conversations")
        self.yell_fe8_button = QPushButton("Yell (FE8)")
        self.yell_mini_button = QPushButton("Yell (Mini)")
        self.epilogue_button = QPushButton("Epilogue")

        dialogue_box = QGroupBox("Dialogue && Text Data")
        dialogue_layout = QVBoxLayout()
        dialogue_layout.setContentsMargins(5, 5, 5, 5)
        dialogue_layout.addWidget(self.dialogue_button)
        dialogue_layout.addWidget(self.conversations_button)
        dialogue_layout.addWidget(self.yell_fe8_button)
        dialogue_layout.addWidget(self.yell_mini_button)
        dialogue_layout.addWidget(self.epilogue_button)
        dialogue_box.setLayout(dialogue_layout)

        layout = QGridLayout()
        layout.addWidget(core_box, 0, 0, 2, 2)
        layout.addWidget(chapter_data_box, 2, 0)
        layout.addWidget(assets_box, 3, 0)
        layout.addWidget(dialogue_box, 2, 1, 2, 1)

        self.setLayout(layout)
