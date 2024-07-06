from PySide6.QtWidgets import QDoubleSpinBox
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class FloatSpinBox(AbstractAutoWidget, QDoubleSpinBox):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        QDoubleSpinBox.__init__(self)
        self.field_id = field_id
        self.rid = None
        self.valueChanged.connect(self._on_edit)
        self.setRange(-1000000, 1000000)  # TODO: Add an actual f32 range here?

    def _on_edit(self, value):
        if self.rid:
            self.data.set_float(self.rid, self.field_id, value)

    def set_target(self, rid):
        self.rid = rid
        self.setValue(self.data.float(self.rid, self.field_id) if self.rid else 0.0)
        self.setEnabled(self.rid is not None)
