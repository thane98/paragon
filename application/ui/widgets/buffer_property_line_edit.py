from PySide2.QtWidgets import QLineEdit
from .property_widget import PropertyWidget


class BufferPropertyLineEdit(QLineEdit, PropertyWidget):
    def __init__(self, target_property_name, length):
        QLineEdit.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.editingFinished.connect(self._on_edit)
        self.setInputMask(self._create_input_mask(length))

    def _on_edit(self):
        split_text = self.displayText().split()
        result = []
        for entry in split_text:
            result.append(int(entry, 16))
        self.commit(result)

    def _on_target_changed(self):
        if self.target:
            self.setText(self._create_formatted_str(self._get_target_value()))
        else:
            self.setText(self._create_formatted_str([0 for _ in self.text().split()]))

    @staticmethod
    def _create_input_mask(length: int) -> str:
        result = ""
        for i in range(0, length):
            result += "HH"
            if i != length - 1:
                result += " "
            else:
                result += ";0"
        return result

    @staticmethod
    def _create_formatted_str(value: list) -> str:
        result = ""
        for i in range(0, len(value)):
            result += "%02x" % value[i]
            if i != len(value) - 1:
                result += ' '
        return result
