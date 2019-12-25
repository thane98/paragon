from PySide2.QtWidgets import QWidget

from ui.widgets.f32_property_spin_box import DoublePropertySpinBox
from .abstract_property import AbstractProperty


class F32Property(AbstractProperty):
    def __init__(self, name, value=0):
        super().__init__(name)
        self.value = value

    def copy_to(self, destination):
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, name, _json):
        return F32Property(name)

    def read(self, reader):
        self.value = reader.read_f32()

    def write(self, writer):
        writer.write_f32(self.value)

    def create_editor(self) -> QWidget:
        return DoublePropertySpinBox(self.name)
