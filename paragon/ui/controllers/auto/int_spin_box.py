from PySide2.QtWidgets import QSpinBox

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class IntSpinBox(AbstractAutoWidget, QSpinBox):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QSpinBox.__init__(self)
        self.field_id = field_id
        self.rid = None
        if spec.hex:
            self.setDisplayIntegerBase(16)
            self.setPrefix("0x")
        fm = state.field_metadata[field_id]
        min_value, max_value = fm["range"]
        self.setRange(min_value, max_value)
        self.valueChanged.connect(self._on_edit)

    def set_target(self, rid):
        self.rid = rid
        if rid:
            self.setValue(self.data.int(rid, self.field_id))
        else:
            self.setValue(0)
        self.setEnabled(self.rid is not None)

    def _on_edit(self):
        if self.rid:
            self.data.set_int(self.rid, self.field_id, self.value())
