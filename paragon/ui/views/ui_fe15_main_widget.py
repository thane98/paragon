from PySide2 import QtGui
from PySide2.QtWidgets import QWidget, QGridLayout, QGroupBox, QPushButton, QVBoxLayout


class Ui_FE15MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.chapters_button = QPushButton("Chapters")
        self.characters_button = QPushButton("Characters")
        self.items_button = QPushButton("Items")
        self.classes_button = QPushButton("Classes")
        self.skills_button = QPushButton("Skills")
        self.armies_button = QPushButton("Armies")
        self.spell_lists_button = QPushButton("Spell Lists")
        self.tiles_button = QPushButton("Tiles")
        self.rumors_button = QPushButton("Rumors")
        self.subquests_button = QPushButton("Subquests")
        self.food_preferences_button = QPushButton("Food Preferences")

        core_box = QGroupBox("Core Data")
        core_layout = QVBoxLayout()
        core_layout.setAlignment(QtGui.Qt.AlignTop)
        core_layout.addWidget(self.chapters_button)
        core_layout.addWidget(self.characters_button)
        core_layout.addWidget(self.items_button)
        core_layout.addWidget(self.classes_button)
        core_layout.addWidget(self.skills_button)
        core_layout.addWidget(self.armies_button)
        core_layout.addWidget(self.spell_lists_button)
        core_layout.addWidget(self.tiles_button)
        core_layout.addWidget(self.rumors_button)
        core_layout.addWidget(self.subquests_button)
        core_layout.addWidget(self.food_preferences_button)
        core_box.setLayout(core_layout)

        self.portraits_button = QPushButton("Portraits")
        self.rom0_button = QPushButton("ROM0")
        self.rom1_button = QPushButton("ROM1")
        self.rom2_button = QPushButton("ROM2")
        self.rom3_button = QPushButton("ROM3")
        self.rom4_button = QPushButton("ROM4")
        self.rom5_button = QPushButton("ROM5")
        self.rom6_button = QPushButton("ROM6")

        assets_box = QGroupBox("Assets")
        assets_layout = QVBoxLayout()
        assets_layout.addWidget(self.portraits_button)
        assets_layout.addWidget(self.rom0_button)
        assets_layout.addWidget(self.rom1_button)
        assets_layout.addWidget(self.rom2_button)
        assets_layout.addWidget(self.rom3_button)
        assets_layout.addWidget(self.rom4_button)
        assets_layout.addWidget(self.rom5_button)
        assets_layout.addWidget(self.rom6_button)
        assets_box.setLayout(assets_layout)

        self.edit_dialogue_button = QPushButton("Edit Dialogue")

        misc_box = QGroupBox("Misc.")
        misc_layout = QVBoxLayout()
        misc_layout.setAlignment(QtGui.Qt.AlignTop)
        misc_layout.addWidget(self.edit_dialogue_button)
        misc_box.setLayout(misc_layout)

        layout = QGridLayout()
        layout.addWidget(core_box, 0, 0, 2, 1)
        layout.addWidget(assets_box, 0, 1)
        layout.addWidget(misc_box, 1, 1)

        self.setLayout(layout)
