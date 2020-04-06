from PySide2.QtWidgets import QWidget
from ui.widgets.data_combo_box import DataComboBox
from ui.widgets.integer_property_spin_box import IntegerPropertySpinBox
from .abstract_property import AbstractProperty


class I16Property(AbstractProperty):
    def __init__(self, name, value=0):
        super().__init__(name)
        self.editor_factory = lambda: IntegerPropertySpinBox(self.name, -32768, 32767)
        self.value = value

    def copy_to(self, destination):
        destination.value = self.value

    @classmethod
    def _from_json(cls, name, json):
        result = I16Property(name)
        if "editor" in json:
            cls._parse_editor(result, json["editor"])
        return result

    @staticmethod
    def _parse_editor(prop, json):
        editor_type = json["type"]
        if editor_type == "combobox":
            data_type = json["data"]
            prop.editor_factory = lambda: DataComboBox(prop.name, data_type, int)

    def read(self, reader):
        self.value = reader.read_i16()

    def write(self, writer):
        writer.write_i16(self.value)

    def create_editor(self) -> QWidget:
        return self.editor_factory()
