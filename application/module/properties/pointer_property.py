from copy import deepcopy
from PySide2.QtWidgets import QWidget
from ui.widgets.pointer_property_editor import PointerPropertyEditor
from .abstract_property import AbstractProperty


# Pointers are complicated, so we enforce some invariants to try and simplify things.
# - No null pointers. After reading, a pointer must have a value.
# - Pointers may only hold trivial properties (strings, numbers, buffers). No nested pointers.
#
# These could be relaxed with some more work, but pointer property already
# addresses most use cases under these constraints.
from .property_container import PropertyContainer


class PointerProperty(AbstractProperty):
    def __init__(self, name):
        super().__init__(name)
        self.target_size = 0
        self.template = PropertyContainer()
        self.value = {}

    def __deepcopy__(self, memo):
        result = PointerProperty(self.name)
        result.target_size = self.target_size
        result.template = self.template
        result.value = self.value
        result.offset = self.offset
        memo[id(self)] = result
        return result

    def copy_to(self, destination):
        destination.value = self.value

    # Temp while we wait for a redesign...
    def copy_internal_pointer(self, source, destination):
        module = self.parent.owner
        source_pointer_address = self.offset + module.find_base_address_for_element(source)
        dest_pointer_address = self.offset + module.find_base_address_for_element(destination)
        source_pointer = module.archive.read_internal(source_pointer_address)
        module.archive.set_internal_pointer(dest_pointer_address, source_pointer)

    @classmethod
    def from_json(cls, name, json):
        result = PointerProperty(name)
        result.target_size = json["size"]
        result.template = PropertyContainer.from_json(json["properties"])
        result.value = deepcopy(result.template)
        return result

    def make_unique(self, target):
        if not target:
            raise ValueError
        module = self.parent.owner
        pointer_addr = module.find_base_address_for_element(target) + self.offset
        archive = module.archive
        
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
