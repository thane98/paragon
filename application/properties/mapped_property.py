from PySide2.QtWidgets import QWidget

from utils.checked_json import read_key_optional
from .abstract_property import AbstractProperty
from ui.widgets.string_property_line_edit import StringPropertyLineEdit


class MappedProperty(AbstractProperty):
    def __init__(self, name, value=None):
        super().__init__(name)
        self.editor_factory = lambda: StringPropertyLineEdit(self.name)
        self.value = value

    def copy_to(self, destination):
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, driver, name, json):
        result = MappedProperty(name)
        result.is_display = read_key_optional(json, "display", False)
        return result

    def read(self, reader):
        self.value = reader.read_mapped()

    def write(self, writer):
        writer.write_mapped(self.value)

    def create_editor(self) -> QWidget:
        return self.editor_factory()
