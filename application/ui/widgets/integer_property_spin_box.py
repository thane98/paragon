from PySide2.QtWidgets import QSpinBox
from .property_widget import PropertyWidget


class IntegerPropertySpinBox(QSpinBox, PropertyWidget):
    def __init__(self, target_property_name, min_value: int, max_value: int):
        QSpinBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.setRange(min_value, max_value)
        self.valueChanged.connect(self._on_edit)

    def _on_edit(self, value):
        self.commit(value)

    def _on_target_changed(self):
        if self.target:
            self.setValue(self._get_target_value())
        else:
            self.setValue(0)
