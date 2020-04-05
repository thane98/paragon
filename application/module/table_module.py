import logging
from copy import deepcopy

from core.bin_streams import BinArchiveWriter, BinArchiveReader
from model.qt.module_entry_model import ModuleEntryModel
from module.count import count_strategy_from_json
from module.module import Module
from module.properties.pointer_property import PointerProperty
from utils.checked_json import read_key_optional


class TableModule(Module):
    def __init__(self, js):
        super().__init__(js)
        self.entry_size = js["entry_size"]
        self.count_strategy = count_strategy_from_json(js["count"])
        self.entries = []
        self.entries_model: ModuleEntryModel = ModuleEntryModel(self)
        self.disable_add_remove = read_key_optional(js, "disable_add_remove", False)

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
            elem = self.element_template.duplicate(new_owner=self)
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

        # Update the ID if it exists.
        if self.id_property:
            new_elem[self.id_property].value = len(self.entries) - 1

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

        # Adjust IDs
        if self.id_property:
            for i in range(begin, len(self.entries)):
                self.entries[i][self.id_property].value -= end - begin

    def remove_elem(self, index):
        self.remove_range(index, index + 1)

    def update_post_shallow_copy_fields(self):
        self.entries = []
        self.entries_model = ModuleEntryModel(self)
        for prop in self.element_template.values():
            if type(prop) == PointerProperty:
                prop.module = self
