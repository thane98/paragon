from typing import Any

from PySide2.QtWidgets import QWidget

from core.bin_streams import BinArchiveReader
from ui.widgets.pointer_property_editor import PointerPropertyEditor
from .abstract_property import AbstractProperty
from .property_container import PropertyContainer
from ..module import Module


class PointerProperty(AbstractProperty):
    def __init__(self, name):
        super().__init__(name)
        self.target_size = 0
        self.template = PropertyContainer()
        self.value = None

    def __deepcopy__(self, memo):
        result = PointerProperty(self.name)
        result.target_size = self.target_size
        result.template = self.template
        result.value = self.value  # Do not deepcopy the object this points to.
        result.offset = self.offset
        memo[id(self)] = result
        return result

    def get_property_address(self):
        if issubclass(type(self.parent.owner), Module):
            property_address = self.parent.owner.find_base_address_for_element(self.parent) + self.offset
            return property_address, self.parent.owner.archive
        else:
            parent_property_address, archive = self.parent.owner.get_property_address()
            reader = BinArchiveReader(archive, parent_property_address)
            return (reader.read_internal_pointer() + self.offset), archive

    def copy_to(self, destination):
        destination.value = self.value
        if self.value is not None:
            source_pointer_address, archive = self.get_property_address()
            dest_pointer_address, _ = destination.get_property_address()
            source_pointer = archive.read_internal(source_pointer_address)
            archive.set_internal_pointer(dest_pointer_address, source_pointer)

    @classmethod
    def _from_json(cls, name, json):
        result = PointerProperty(name)
        result.target_size = json["size"]
        result.template = PropertyContainer.from_json(json["properties"])
        result.offset = json.get("offset")
        result.value = None
        return result

    def make_unique(self):
        pointer_addr, archive = self.get_property_address()
        archive.set_internal_pointer(pointer_addr, archive.size())
        archive.allocate_at_end(self.target_size)
        if self.value is not None:
            self.value = self.value.duplicate(new_owner=self)
            self.value.owner = self
            for pointer_property in self.value.pointer_properties:
                if self.value[pointer_property].value is not None:
                    self.value[pointer_property].make_unique()
        else:
            self.value = self.template.duplicate(new_owner=self)

    def clear_value(self):
        if self.value is not None:
            pointer_addr, archive = self.get_property_address()
            archive.clear_internal_pointer(pointer_addr)
            self.value = None

    def read(self, reader):
        self.value = reader.read_object(self.template)
        if self.value is not None:
            self.value.owner = self

    def write(self, writer):
        if self.value is None:
            writer.write_pointer(None)
        else:
            reader = BinArchiveReader(writer.get_archive(), writer.tell())
            target_address = reader.read_internal_pointer()
            end_address = writer.tell() + 4
            writer.seek(target_address)
            for prop in self.value.values():
                prop.write(writer)
            writer.seek(end_address)

    def create_editor(self) -> QWidget:
        return PointerPropertyEditor(self.name, self.template)

    def export(self) -> Any:
        if self.value is None:
            return None
        else:
            return self.value.export()

    def import_values(self, values_json: Any):
        if values_json is None:
            self.value = None
        else:
            if self.parent.owner is not PointerProperty:
                self.make_unique()
            self.value.import_values(values_json)
