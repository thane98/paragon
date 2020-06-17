from PySide2.QtWidgets import QDoubleSpinBox
from .property_widget import PropertyWidget


class DoublePropertySpinBox(QDoubleSpinBox, PropertyWidget):
    def __init__(self, target_property_name):
        QDoubleSpinBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.valueChanged.connect(self._on_edit)
        self.setRange(-100000, 100000)

    def _on_edit(self, value):
        self.commit(value)

    def _on_target_changed(self):
        if self.target:
            self.setValue(self._get_target_value())
        else:
            self.setValue(0)
