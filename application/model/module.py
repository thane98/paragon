import logging
from abc import ABC, abstractmethod
from copy import deepcopy
from json import load
from typing import Dict

from bin_streams import BinArchiveReader, BinArchiveWriter
from model.count import count_strategy_from_json
from model.location import location_strategy_from_json
from model.module_entry_model import ModuleEntryModel
from properties.abstract_property import AbstractProperty
from properties.buffer_property import BufferProperty
from properties.f32_property import F32Property
from properties.i16_property import I16Property
from properties.i8_property import I8Property
from properties.mapped_property import MappedProperty
from properties.message_property import MessageProperty
from properties.pointer_property import PointerProperty
from properties.reference_property import ReferenceProperty
from properties.string_property import StringProperty
from properties.u16_property import U16Property
from properties.i32_property import I32Property
from properties.u8_property import U8Property
from utils.checked_json import read_key_optional

PROPERTIES = {
    "pointer": PointerProperty,
    "mapped": MappedProperty,
    "message": MessageProperty,
    "string": StringProperty,
    "buffer": BufferProperty,
    "u8": U8Property,
    "i8": I8Property,
    "u16": U16Property,
    "i16": I16Property,
    "i32": I32Property,
    "f32": F32Property,
    "reference": ReferenceProperty
}


def create_module_from_path(path):
    with open(path, "r", encoding='utf-8') as f:
        js = load(f)
        if js["type"] == "table":
            return TableModule(js)
        elif js["type"] == "object":
            return ObjectModule(js)
        else:
            logging.error("Unrecognized module type. Aborting module creation.")
            raise NotImplementedError


class Module(ABC):
    def __init__(self, js):
        self.name = js["name"]
        self.unique = read_key_optional(js, "unique", False)
        if self.unique:
            self.file = js["file"]
        else:
            self.file = None
        self.type = js["type"]
        self.location_strategy = location_strategy_from_json(js["location"])
        self.archive = None

        self.element_template: Dict[str: AbstractProperty] = {}
        module_properties = js["properties"]
        for key in module_properties:
            logging.info("Parsing property " + key + ".")
            property_config = module_properties[key]
            property_type = PROPERTIES[property_config["type"]]
            prop = property_type.from_json(key, property_config)
            if property_type is PointerProperty:
                prop.module = self
            self.element_template[key] = prop

        self.display_property = None
        self.fallback_display_property = None
        for (key, prop) in self.element_template.items():
            if prop.is_display:
                self.display_property = key
            elif prop.is_fallback_display:
                self.fallback_display_property = key

    @abstractmethod
    def find_base_address_for_element(self, element):
        raise NotImplementedError

    @abstractmethod
    def attach_to(self, archive):
        raise NotImplementedError

    @abstractmethod
    def commit_changes(self):
        raise NotImplementedError

    @abstractmethod
    def update_post_shallow_copy_fields(self):
        raise NotImplementedError


class TableModule(Module):
    def __init__(self, js):
        super().__init__(js)
        self.entry_size = js["entry_size"]
        self.count_strategy = count_strategy_from_json(js["count"])
        self.entries = []
        self.entries_model: ModuleEntryModel = ModuleEntryModel(self)

    def find_base_address_for_element(self, element):
        if not self.archive:
            raise ValueError

        table_base = self.location_strategy.read_base_address(self.archive)
        for i in range(0, len(self.entries)):
            if self.entries[i] == element:
                return table_base + self.entry_size * i
        raise ValueError

    def attach_to(self, archive):
        self.entries.clear()
        location = self.location_strategy.read_base_address(archive)
        count = self.count_strategy.read_count(archive)
        reader = BinArchiveReader(archive)
        for i in range(0, count):
            reader.seek(location + i * self.entry_size)
            base = reader.tell()
            elem = deepcopy(self.element_template)
            for (_, prop) in elem.items():
                prop.offset = reader.tell() - base
                prop.read(reader)
            self.entries.append(elem)
        self.archive = archive

    def commit_changes(self):
        base_location = self.location_strategy.read_base_address(self.archive)
        writer = BinArchiveWriter(self.archive, base_location)
        for elem in self.entries:
            for (_, prop) in elem.items():
                prop.write(writer)

    def add_elem(self):
        # Allocate space for the new element.
        base_location = self.location_strategy.read_base_address(self.archive)
        new_element_address = base_location + self.entry_size * len(self.entries)
        self.archive.allocate(new_element_address, self.entry_size, False)

        # Update count in the archive.
        self.count_strategy.write_count(self.archive, len(self.entries) + 1)

        # Add the new element to the list.
        new_elem = deepcopy(self.element_template)
        self.entries.append(new_elem)

    def remove_range(self, begin: int, end: int):
        logging.info(self.name + " removing range [" + str(begin) + ", " + str(end) + ")")

        # Deallocate removed elements from the archive.
        base_location = self.location_strategy.read_base_address(self.archive)
        start_address = base_location + self.entry_size * begin
        amount = self.entry_size * (end - begin)
        self.archive.deallocate(start_address, amount, False)

        # Update count in the archive.
        self.count_strategy.write_count(self.archive, len(self.entries) - (end - begin))

        # Remove elements from the module's entries.
        del self.entries[begin:end]

    def remove_elem(self, index):
        self.remove_range(index, index + 1)

    def update_post_shallow_copy_fields(self):
        self.entries = []
        self.entries_model = ModuleEntryModel(self)
        for prop in self.element_template.values():
            if prop is PointerProperty:
                prop.module = self


class ObjectModule(Module):
    def __init__(self, js):
        super().__init__(js)
        self.element = deepcopy(self.element_template)

    def find_base_address_for_element(self, element):
        if not self.archive:
            raise ValueError
        if element != self.element:
            raise ValueError
        return self.location_strategy.read_base_address(self.archive)

    def attach_to(self, archive):
        location = self.location_strategy.read_base_address(archive)
        reader = BinArchiveReader(archive, location)
        for prop in self.element.values():
            prop.read(reader)
        self.archive = archive

    def commit_changes(self):
        location = self.location_strategy.read_base_address(self.archive)
        writer = BinArchiveWriter(self.archive, location)
        for prop in self.element.values():
            prop.write(writer)

    def update_post_shallow_copy_fields(self):
        self.element = deepcopy(self.element_template)
        for prop in self.element_template.values():
            if prop is PointerProperty:
                prop.module = self
