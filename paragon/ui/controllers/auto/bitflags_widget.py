from PySide2 import QtGui
from PySide2.QtWidgets import QWidget, QVBoxLayout, QCheckBox
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class BitflagsWidget(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.field_id = field_id
        self.rid = None
        self.editors = []
        for i in range(0, min(8, len(spec.flags))):
            editor = QCheckBox(spec.flags[i])
            editor.stateChanged.connect(self._on_edit)
            self.editors.append(editor)
            layout.addWidget(editor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtGui.Qt.AlignTop)
        self.setLayout(layout)

    def _on_edit(self):
        if self.rid:
            value = 0
            for i in range(0, len(self.editors)):
                checked = self.editors[i].isChecked() if 1 else 0
                value |= checked << i
            self.data.set_int(self.rid, self.field_id, value)

    def set_target(self, rid):
        self.rid = rid
        if self.rid:
            value = self.data.int(rid, self.field_id)
            for i in range(0, len(self.editors)):
                bit = value & (1 << i)
                self.editors[i].setChecked(bit != 0)
        else:
            for editor in self.editors:
                editor.setChecked(False)
        self.setEnabled(self.rid is not None)
