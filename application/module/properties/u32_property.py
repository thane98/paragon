from PySide2.QtWidgets import QWidget

from .plain_value_property import PlainValueProperty


class U32Property(PlainValueProperty):
    def __init__(self, name, value=0):
        super().__init__(name)
        self.value = value

    def copy_to(self, destination):
        destination.value = self.value

    @classmethod
    def _from_json(cls, name, json):
        result = U32Property(name)
        return result

    def read(self, reader):
        self.value = reader.read_u32()

    def write(self, writer):
        writer.write_u32(self.value)

    def create_editor(self) -> QWidget:
        raise NotImplementedError
