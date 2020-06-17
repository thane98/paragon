import struct
from PySide2.QtWidgets import QSpinBox, QLabel, QFormLayout, QGroupBox
from model.project import Game
from services import service_locator
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

EDITOR_LABELS_SOV = [
    "Health",
    "Attack",
    "Skill",
    "Speed",
    "Luck",
    "Defense",
    "Resistance",
    "Movement"
]


class StatsEditor (QGroupBox, PropertyWidget):
    def __init__(self, target_property_name):
        QGroupBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.editors = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox()
        ]

        labels = self._get_labels_for_project()
        for i in range(0, 8):
            editor = self.editors[i]
            editor.setRange(-128, 127)
            layout.addRow(QLabel(labels[i]), editor)
            self.setLayout(layout)

        self.editors[0].valueChanged.connect(lambda: self._on_edit(0, self.editors[0].value()))
        self.editors[1].valueChanged.connect(lambda: self._on_edit(1, self.editors[1].value()))
        self.editors[2].valueChanged.connect(lambda: self._on_edit(2, self.editors[2].value()))
        self.editors[3].valueChanged.connect(lambda: self._on_edit(3, self.editors[3].value()))
        self.editors[4].valueChanged.connect(lambda: self._on_edit(4, self.editors[4].value()))
        self.editors[5].valueChanged.connect(lambda: self._on_edit(5, self.editors[5].value()))
        self.editors[6].valueChanged.connect(lambda: self._on_edit(6, self.editors[6].value()))
        self.editors[7].valueChanged.connect(lambda: self._on_edit(7, self.editors[7].value()))

    @staticmethod
    def _get_labels_for_project():
        driver = service_locator.locator.get_scoped("Driver")
        project = driver.get_project()
        if project.game == Game.FE15.value:
            return EDITOR_LABELS_SOV
        else:
            return EDITOR_LABELS

    def _on_edit(self, index, value):
        if self.target:
            buffer = self._get_target_value()
            binary_value = struct.pack("b", value)
            unsigned_value = int(struct.unpack("B", binary_value)[0])
            buffer[index] = unsigned_value

    def _on_target_changed(self):
        if self.target:
            buffer = self._get_target_value()
            for i in range(0, 8):
                binary_value = struct.pack("B", buffer[i])
                value = int(struct.unpack("b", binary_value)[0])
                self.editors[i].setValue(value)
        else:
            for editor in self.editors:
                editor.setValue(0)
