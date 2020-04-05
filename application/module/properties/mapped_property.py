from PySide2.QtWidgets import QWidget
from utils.checked_json import read_key_optional
from .abstract_property import AbstractProperty
from ui.widgets.string_property_line_edit import StringPropertyLineEdit


class MappedProperty(AbstractProperty):
    def __init__(self, name, value=None):
        super().__init__(name)
        self.editor_factory = lambda: StringPropertyLineEdit(self.name)
        self.value = value
        self.old_values = []

    def copy_to(self, destination):
        destination.value = self.value

    def set_value(self, new_value):
        self.old_values.append(self.value)
        self.value = new_value

    @classmethod
    def from_json(cls, name, json):
        result = MappedProperty(name)
        result.is_display = read_key_optional(json, "display", False)
        result.is_fallback_display = read_key_optional(json, "fallback_display", False)
        return result

    def read(self, reader):
        self.value = reader.read_mapped()

    def write(self, writer):
        archive = writer.archive
        for old_value in self.old_values:
            archive.clear_mapped_pointer(writer.tell(), old_value)
        self.old_values.clear()
        writer.write_mapped(self.value)

    def create_editor(self) -> QWidget:
        return self.editor_factory()
