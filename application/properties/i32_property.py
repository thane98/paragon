from PySide2.QtWidgets import QWidget
from ui.widgets.integer_property_spin_box import IntegerPropertySpinBox
from .abstract_property import AbstractProperty


class I32Property(AbstractProperty):
    def __init__(self, name, value=0):
        super().__init__(name)
        self.value = value

    def copy_to(self, destination):
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, name, json):
        return I32Property(name)

    def read(self, reader):
        self.value = reader.read_i32()

    def write(self, writer):
        writer.write_i32(self.value)

    def create_editor(self) -> QWidget:
        return IntegerPropertySpinBox(self.name)
