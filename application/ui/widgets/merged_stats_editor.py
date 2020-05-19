import struct
from typing import List

from PySide2.QtWidgets import QSpinBox, QLabel, QWidget, QGridLayout

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


class MergedStatsEditor (QWidget):
    def __init__(self, target_properties: List[str], parent=None):
        super().__init__(parent)
        self.target_properties = target_properties
        self.target = None

        layout = QGridLayout()
        for i in range(0, 8):
            label = QLabel(text=_EDITOR_LABELS[i])
            layout.addWidget(label, 0, i + 1)
        self.editors = []
        for i in range(0, len(target_properties)):
            self.editors.append([])
            label = QLabel(target_properties[i])
            label.setFixedWidth(80)
            layout.addWidget(label, i + 1, 0)
            for j in range(0, 8):
                editor = QSpinBox()
                editor.setRange(-128, 127)
                editor.setMaximumWidth(60)
                layout.addWidget(editor, row=i + 1, column=j + 1)
                self.editors[-1].append(editor)
                editor.valueChanged.connect(lambda v=None, e=editor, r=i, c=j: self._on_edit(v, e, r, c))
        self.setLayout(layout)
        self.setFixedHeight(200)

    def _on_edit(self, value, _, row: int, column: int):
        if self.target:
            target_property_name = self.target_properties[row]
            buffer = self.target[target_property_name].value
            binary_value = struct.pack("b", value)
            unsigned_value = int(struct.unpack("B", binary_value)[0])
            buffer[column] = unsigned_value

    def update_target(self, target: PropertyContainer):
        if target:
            self.target = target
            for r in range(0, len(self.target_properties)):
                prop = self.target_properties[r]
                stats = target[prop].value
                for c in range(0, 8):
                    binary_value = struct.pack("B", stats[c])
                    value = int(struct.unpack("b", binary_value)[0])
                    editor = self.editors[r][c]
                    editor.setValue(value)
