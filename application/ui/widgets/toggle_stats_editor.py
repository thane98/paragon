import struct
from PySide2.QtWidgets import QSpinBox, QLabel, QFormLayout, QGroupBox, QPushButton, QLineEdit, QWidget
from model.project import Game
from services import service_locator
from ui.widgets.property_widget import PropertyWidget
from .stats_editor import EDITOR_LABELS, EDITOR_LABELS_SOV

class ToggleStatsEditor (QGroupBox, PropertyWidget):
    def __init__(self, target_property_name):
        QGroupBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.main_layout = QFormLayout(self)

        self.buffer_editor = QLineEdit()
        self.buffer_editor.editingFinished.connect(self._on_buffer_edit)
        self.buffer_editor.setInputMask("HH HH HH HH HH HH HH HH;0")
        self.buffer_editor.setVisible(False)

        self.stats_layout = QFormLayout()
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stat_editors = [
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
            editor = self.stat_editors[i]
            editor.setRange(-128, 127)
            self.stats_layout.addRow(QLabel(labels[i]), editor)

        self.stats_widget = QWidget()
        self.stats_widget.setLayout(self.stats_layout)

        self.editor_toggle = QPushButton("Toggle Stats/Hex Editor")
        self.editor_toggle.clicked.connect(self._on_editor_toggle)

        self.main_layout.addRow(self.editor_toggle)
        self.main_layout.addRow(self.stats_widget)

        self.stat_editors[0].valueChanged.connect(lambda: self._on_stat_edit(0))
        self.stat_editors[1].valueChanged.connect(lambda: self._on_stat_edit(1))
        self.stat_editors[2].valueChanged.connect(lambda: self._on_stat_edit(2))
        self.stat_editors[3].valueChanged.connect(lambda: self._on_stat_edit(3))
        self.stat_editors[4].valueChanged.connect(lambda: self._on_stat_edit(4))
        self.stat_editors[5].valueChanged.connect(lambda: self._on_stat_edit(5))
        self.stat_editors[6].valueChanged.connect(lambda: self._on_stat_edit(6))
        self.stat_editors[7].valueChanged.connect(lambda: self._on_stat_edit(7))

    @staticmethod
    def _get_labels_for_project():
        driver = service_locator.locator.get_scoped("Driver")
        project = driver.get_project()
        if project.game == Game.FE15.value:
            return EDITOR_LABELS_SOV
        else:
            return EDITOR_LABELS

    def _on_editor_toggle(self):
        show_stats = self.buffer_editor.isVisible()
        self.buffer_editor.setVisible(not show_stats)
        self.stats_widget.setVisible(show_stats)
        self.main_layout.takeAt(1)
        if show_stats:
            self.main_layout.addRow(self.stats_widget)
        else:
            self.main_layout.addRow(self.buffer_editor)

    def _on_buffer_edit(self):
        if self.target:
            buffer = self._get_target_value()
            split_text = self.buffer_editor.displayText().split()
            for j in range(8):
                buffer[j] = int(split_text[j], 16)
            self._on_target_changed()

    def _on_stat_edit(self, index):
        if self.target:
            buffer = self._get_target_value()
            value = self.stat_editors[index].value()
            binary_value = struct.pack("b", value)
            unsigned_value = int(struct.unpack("B", binary_value)[0])
            buffer[index] = unsigned_value
            self._on_target_changed()

    def _on_target_changed(self):
        if self.target:
            buffer = self._get_target_value()
            self.buffer_editor.setText(" ".join("%02x" % x for x in buffer))
            for i in range(0, 8):
                binary_value = struct.pack("B", buffer[i])
                value = int(struct.unpack("b", binary_value)[0])
                self.stat_editors[i].setValue(value)
        else:
            self.buffer_editor.setText("00 00 00 00 00 00 00 00")
            for editor in self.stat_editors:
                editor.setValue(0)
