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
        stat_range = self._get_range_for_project()
        for i in range(0, len(self.editors)):
            editor = self.editors[i]
            editor.setRange(stat_range[0], stat_range[1])
            layout.addRow(QLabel(labels[i]), editor)
            editor.valueChanged.connect(lambda: self._on_edit(i, editor.value()))
        self.setLayout(layout)

    @staticmethod
    def _get_labels_for_project():
        driver = service_locator.locator.get_scoped("Driver")
        project = driver.project
        if project.game == Game.FE15.value:
            return EDITOR_LABELS_SOV
        else:
            return EDITOR_LABELS

    @staticmethod
    def _get_range_for_project():
        driver = service_locator.locator.get_scoped("Driver")
        project = driver.project
        if project.game == Game.FE15.value:
            return [0, 120]
        else:
            return [0, 255]

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
