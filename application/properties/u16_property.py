from PySide2.QtWidgets import QWidget

from ui.widgets.data_combo_box import DataComboBox
from ui.widgets.integer_property_spin_box import IntegerPropertySpinBox
from .abstract_property import AbstractProperty


class U16Property(AbstractProperty):
    def __init__(self, name, value=0):
        super().__init__(name)
        self.editor_factory = lambda: IntegerPropertySpinBox(self.name, -32768, 32767)
        self.value = value

    def copy_to(self, destination):
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, driver, name, json):
        result = U16Property(name)
        if "editor" in json:
            cls._parse_editor(driver, result, json["editor"])
        return result

    @staticmethod
    def _parse_editor(driver, prop, json):
        editor_type = json["type"]
        if editor_type == "spinbox":
            prop.editor_factory = lambda: IntegerPropertySpinBox(prop.name, -32768, 32767)
        elif editor_type == "combobox":
            data_type = json["data"]
            data = driver.module_data_service.entries[data_type]
            prop.editor_factory = lambda: DataComboBox(prop.name, data, int)

    def read(self, reader):
        self.value = reader.read_u16()

    def write(self, writer):
        writer.write_u16(self.value)

    def create_editor(self) -> QWidget:
        return self.editor_factory()
