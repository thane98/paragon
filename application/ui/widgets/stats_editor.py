from PySide2.QtWidgets import QWidget, QVBoxLayout, QSpinBox, QLabel
from ui.widgets.property_widget import PropertyWidget

EDITOR_LABELS = [
    "Health",
    "Strength",
    "Magic",
    "Skill",
    "Speed",
    "Luck",
    "Defense",
    "Resistance"
]


class StatsEditor (QWidget, PropertyWidget):
    def __init__(self, target_property_name):
        QWidget.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.health_editor = QSpinBox()
        self.strength_editor = QSpinBox()
        self.magic_editor = QSpinBox()
        self.skill_editor = QSpinBox()
        self.speed_editor = QSpinBox()
        self.luck_editor = QSpinBox()
        self.defense_editor = QSpinBox()
        self.resistance_editor = QSpinBox()
        self.editors = [
            self.health_editor,
            self.strength_editor,
            self.magic_editor,
            self.skill_editor,
            self.speed_editor,
            self.luck_editor,
            self.defense_editor,
            self.resistance_editor
        ]
        for i in range(0, len(self.editors)):
            editor = self.editors[i]
            layout.addWidget(QLabel(EDITOR_LABELS[i]))
            layout.addWidget(editor)
            editor.valueChanged.connect(lambda: self._on_edit(i, editor.value()))
        self.setLayout(layout)

    def _on_edit(self, index, value):
        if self.target:
            buffer = self._get_target_value()
            buffer[index] = value

    def _on_target_changed(self):
        if self.target:
            buffer = self._get_target_value()
            for i in range(0, len(self.editors)):
                self.editors[i].setValue(buffer[i])
        else:
            for editor in self.editors:
                editor.setValue(0)
