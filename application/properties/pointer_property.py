from copy import deepcopy
from PySide2.QtWidgets import QWidget
from ui.widgets.pointer_property_editor import PointerPropertyEditor
from utils.properties import read_trivial_properties
from .abstract_property import AbstractProperty
from .buffer_property import BufferProperty
from .f32_property import F32Property
from .i16_property import I16Property
from .i8_property import I8Property
from .mapped_property import MappedProperty
from .message_property import MessageProperty
from .reference_property import ReferenceProperty
from .string_property import StringProperty
from .u16_property import U16Property
from .i32_property import I32Property
from .u8_property import U8Property

TRIVIAL_PROPERTIES = {
    "mapped": MappedProperty,
    "message": MessageProperty,
    "string": StringProperty,
    "buffer": BufferProperty,
    "u8": U8Property,
    "i8": I8Property,
    "u16": U16Property,
    "i16": I16Property,
    "u32": I32Property,
    "f32": F32Property,
    "reference": ReferenceProperty
}


# Pointers are complicated, so we enforce some invariants to try and simplify things.
# - No null pointers. After reading, a pointer must have a value.
# - Pointers may only hold trivial properties (strings, numbers, buffers). No nested pointers.
#
# These could be relaxed with some more work, but pointer property already
# addresses most use cases under these constraints.
class PointerProperty(AbstractProperty):
    def __init__(self, name):
        super().__init__(name)
        self.module = None
        self.target_size = 0
        self.template = {}
        self.value = {}

    def __deepcopy__(self, memo):
        result = PointerProperty(self.name)
        result.module = self.module
        result.target_size = self.target_size
        result.template = self.template
        result.value = self.value
        memo[id(self)] = result
        return result

    def copy_to(self, destination):
        destination[self.name].value = self.value

    # Temp while we wait for a redesign...
    def copy_internal_pointer(self, source, destination):
        source_pointer_address = self.offset + self.module.find_base_address_for_element(source)
        dest_pointer_address = self.offset + self.module.find_base_address_for_element(destination)
        source_pointer = self.module.archive.read_internal(source_pointer_address)
        self.module.archive.set_internal_pointer(dest_pointer_address, source_pointer)

    @classmethod
    def from_json(cls, name, json):
        result = PointerProperty(name)
        result.target_size = json["size"]
        result.template = read_trivial_properties(json["properties"])
        result.value = deepcopy(result.template)
        return result

    def make_unique(self, target):
        if not target:
            raise ValueError
        pointer_addr = self.module.find_base_address_for_element(target) + self.offset
        archive = self.module.archive
        
        archive.set_internal_pointer(pointer_addr, archive.size())
        archive.allocate_at_end(self.target_size)
        self.value = deepcopy(self.value)

    def read(self, reader):
        self.value = reader.read_object(self.template)

    def write(self, writer):
        archive = writer.get_archive()
        target_addr = archive.read_internal(writer.tell())
        end_addr = writer.tell() + 4
        writer.seek(target_addr)
        for prop in self.value.values():
            prop.write(writer)
        writer.seek(end_addr)

    def create_editor(self) -> QWidget:
        return PointerPropertyEditor(self.name, self.template)
