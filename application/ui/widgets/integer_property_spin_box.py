from PySide2.QtGui import QValidator
from PySide2.QtWidgets import QSpinBox
from .property_widget import PropertyWidget


class IntegerPropertySpinBox(QSpinBox, PropertyWidget):
    def __init__(self, target_property_name, min_value: int = -1, max_value: int = -1, hexadecimal=False):
        QSpinBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.hexadecimal = hexadecimal
        if self.hexadecimal:
            self.setPrefix("0x")
        if min_value != -1 or max_value != -1:
            self.setRange(min_value, max_value)
        self.valueChanged.connect(self._on_edit)

    def validate(self, input: str, pos: int) -> QValidator.State:
        if not self.hexadecimal:
            return super().validate(input, pos)

        if input == "0x":
            return QValidator.Intermediate
        try:
            value = int(input, 16)
            if value not in range(self.minimum(), self.maximum() + 1):
                return QValidator.Invalid
            return QValidator.Acceptable
        except:
            return QValidator.Invalid

    def textFromValue(self, val: int) -> str:
        if not self.hexadecimal:
            return super().textFromValue(val)
        return hex(val)[2:].upper()

    def valueFromText(self, text: str) -> int:
        if not self.hexadecimal:
            return super().valueFromText(text)
        return int(text, 16)

    def _on_edit(self, value):
        self.commit(value)

    def _on_target_changed(self):
        if self.target:
            self.setValue(self._get_target_value())
        else:
            self.setValue(0)
