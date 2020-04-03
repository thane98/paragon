import logging
from abc import ABC, abstractmethod

from core.bin_streams import BinArchiveReader
from utils.checked_json import read_key_optional


def location_strategy_from_json(js):
    strategy_type = js["type"]
    if strategy_type == "static":
        return StaticLocationStrategy(js)
    if strategy_type == "dynamic":
        return DynamicLocationStrategy(js)
    if strategy_type == "sov_skip":
        return SOVSkipLocationStrategy(js)
    if strategy_type == "dynamic_sov_skip":
        return DynamicSOVSkipLocationStrategy(js)
    if strategy_type == "from_mapped":
        return FromMappedLocationStrategy(js)
    logging.error("Unrecognized location strategy.")
    raise NotImplementedError


class LocationStrategy(ABC):
    @abstractmethod
    def read_base_address(self, archive) -> int:
        raise NotImplementedError


class StaticLocationStrategy(LocationStrategy):
    def __init__(self, js):
        super().__init__()
        self.address = js["address"]

    def read_base_address(self, _archive) -> int:
        return self.address


class DynamicLocationStrategy(LocationStrategy):
    def __init__(self, js):
        super().__init__()
        self.address = js["address"]
        self.offset = read_key_optional(js, "offset", 0)

    def read_base_address(self, archive) -> int:
        reader = BinArchiveReader(archive, self.address)
        return reader.read_internal_pointer() + self.offset


class SOVSkipLocationStrategy(LocationStrategy):
    def __init__(self, js):
        self.offset = read_key_optional(js, "offset", 0)

    def read_base_address(self, archive) -> int:
        reader = BinArchiveReader(archive)
        num_fields = reader.read_u32()
        return num_fields * 0x14 + self.offset + 4


class DynamicSOVSkipLocationStrategy(LocationStrategy):
    def __init__(self, js):
        self.offset_to_pointer = js["offset_to_pointer"]
        self.offset = read_key_optional(js, "offset", 0)

    def read_base_address(self, archive) -> int:
        reader = BinArchiveReader(archive)
        num_fields = reader.read_u32()
        reader.seek(num_fields * 0x14 + self.offset_to_pointer + 4)
        return reader.read_internal_pointer() + self.offset_to_pointer


class FromMappedLocationStrategy(LocationStrategy):
    def __init__(self, js):
        self.mapped_value = js["mapped_value"]
        self.offset = read_key_optional(js, "offset", 0)

    def read_base_address(self, archive) -> int:
        return archive.addr_of_mapped_pointer(self.mapped_value) + self.offset
