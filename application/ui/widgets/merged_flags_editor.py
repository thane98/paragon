import struct
from typing import List

from PySide2.QtWidgets import QSpinBox, QLabel, QWidget, QGridLayout, QHBoxLayout

from module.properties.property_container import PropertyContainer

_EDITOR_LABELS = [
    "Health",
    "Strength",
    "Magic",
    "Skill",
    "Speed",
    "Luck",
    "Defense",
    "Resistance"
]


class MergedFlagsEditor(QWidget):
    def __init__(self, target_properties: List[str], template: PropertyContainer, parent=None):
        super().__init__(parent)
        self.target_properties = target_properties
        self.target = None
        self.editors = []
        self.layout = QHBoxLayout()
        for key in target_properties:
            prop = template[key]
            editor = prop.create_editor()
            self.editors.append(editor)
            self.layout.addWidget(editor)
        self.setLayout(self.layout)

    def update_target(self, target: PropertyContainer):
        if target:
            for editor in self.editors:
                editor.update_target(target)
