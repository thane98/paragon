from PySide2.QtWidgets import QWidget

from ui.widgets.bitflags_editor import BitflagsEditor
from ui.widgets.data_combo_box import DataComboBox
from .abstract_property import AbstractProperty
from ui.widgets.integer_property_spin_box import IntegerPropertySpinBox


class U8Property(AbstractProperty):
    def __init__(self, name, value=0):
        super().__init__(name)
        self.editor_factory = lambda: IntegerPropertySpinBox(self.name, -128, 127)
        self.value = value

    def copy_to(self, destination):
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, driver, name, json):
        result = U8Property(name)
        if "editor" in json:
            cls._parse_editor(driver, result, json["editor"])
        return result

    @staticmethod
    def _parse_editor(driver, prop, json):
        editor_type = json["type"]
        if editor_type == "spinbox":
            prop.editor_factory = lambda: IntegerPropertySpinBox(prop.name, -128, 127)
        elif editor_type == "combobox":
            data_type = json["data"]
            data = driver.module_data_service.entries[data_type]
            prop.editor_factory = lambda: DataComboBox(prop.name, data, int)
        elif editor_type == "bitflags":
            flags = json["flags"]
            if not type(flags) is list:
                raise TypeError
            prop.editor_factory = lambda: BitflagsEditor(prop.name, flags)

    def read(self, reader):
        self.value = reader.read_u8()

    def write(self, writer):
        writer.write_u8(self.value)

    def create_editor(self) -> QWidget:
        return self.editor_factory()
