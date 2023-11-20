from PySide6.QtWidgets import QCheckBox
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class CheckBox(AbstractAutoWidget, QCheckBox):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QCheckBox.__init__(self)
        self.field_id = field_id
        self.rid = None
        self.spec = spec
        self.stateChanged.connect(self._on_state_changed)

    def set_target(self, rid):
        self.rid = rid
        if self.rid:
            value = self.data.bool(self.rid, self.field_id)
            value = not value if self.spec.invert else value
            self.setChecked(value)
        else:
            self.setChecked(False)
        self.setEnabled(self.rid is not None)

    def _on_state_changed(self):
        if self.rid:
            value = not self.isChecked() if self.spec.invert else self.isChecked()
            self.data.set_bool(self.rid, self.field_id, value)
