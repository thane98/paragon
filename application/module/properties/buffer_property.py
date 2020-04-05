from ui.widgets.stats_editor import StatsEditor
from .abstract_property import AbstractProperty
from PySide2.QtWidgets import QWidget
from ui.widgets.buffer_property_line_edit import BufferPropertyLineEdit


class BufferProperty(AbstractProperty):
    def __init__(self, name, length=0, value=None):
        super().__init__(name)
        self.editor_factory = lambda: BufferPropertyLineEdit(self.name, self.length)
        if value:
            self.value = value
        else:
            self.value = [0] * length
        self.length = len(self.value)

    def copy_to(self, destination):
        destination_buffer = destination.value
        for i in range(0, len(self.value)):
            destination_buffer[i] = self.value[i]

    @classmethod
    def from_json(cls, name, json):
        length = json["length"]
        result = BufferProperty(name, length)
        if "editor" in json:
            cls._parse_editor(result, json["editor"])
        return result

    @staticmethod
    def _parse_editor(prop, json):
        editor_type = json["type"]
        if editor_type == "hexfield":
            prop.editor_factory = lambda: BufferPropertyLineEdit(prop.name, prop.length)
        elif editor_type == "stats":
            if prop.length != 8:
                raise IndexError
            prop.editor_factory = lambda: StatsEditor(prop.name)

    def read(self, reader):
        self.value = reader.read_bytes(self.length)

    def write(self, writer):
        writer.write_bytes(self.value)

    def create_editor(self) -> QWidget:
        return self.editor_factory()
