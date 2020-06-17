from PySide2.QtWidgets import QGroupBox, QFormLayout, QCheckBox, QLabel
from .property_widget import PropertyWidget


class BitflagsEditor(QGroupBox, PropertyWidget):
    def __init__(self, target_property_name, flags):
        QGroupBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        if len(flags) > 8:
            raise ValueError
        layout = QFormLayout(self)
        self.editors = []
        for i in range(0, len(flags)):
            label = QLabel(flags[i])
            editor = QCheckBox()
            editor.stateChanged.connect(self._on_edit)
            self.editors.append(editor)
            layout.addRow(label, editor)
        self.setLayout(layout)

    def _on_edit(self, _state):
        value = 0
        for i in range(0, 8):
            if i < len(self.editors):
                checked = self.editors[i].isChecked() if 1 else 0
                value |= checked << i
        self.commit(value)

    def _on_target_changed(self):
        if self.target:
            value = self._get_target_value()
            for i in range(0, len(self.editors)):
                bit = value & (1 << i)
                self.editors[i].setChecked(bit != 0)
        else:
            for editor in self.editors:
                editor.setChecked(False)
