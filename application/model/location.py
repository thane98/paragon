import logging
from abc import ABC, abstractmethod
from bin_streams import BinArchiveReader
from utils.checked_json import read_key_optional


def location_strategy_from_json(js):
    strategy_type = js["type"]
    if strategy_type == "static":
        return StaticLocationStrategy(js)
    if strategy_type == "dynamic":
        return DynamicLocationStrategy(js)
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
        return reader.read_u32() + self.offset
