from abc import ABC, abstractmethod
from bin_streams import BinArchiveReader, BinArchiveWriter
from model.location import location_strategy_from_json
from utils.checked_json import read_key_optional


def count_strategy_from_json(js):
    count_type = read_key_optional(js, "count_type", "simple")
    if count_type == "simple":
        return SimpleCountStrategy(js)
    elif count_type == "null_terminated":
        return NullTerminatedCountStrategy(js)
    raise KeyError


class CountStrategy(ABC):
    @abstractmethod
    def read_count(self, archive) -> int:
        raise NotImplementedError

    @abstractmethod
    def write_count(self, archive, count: int):
        raise NotImplementedError


class SimpleCountStrategy(CountStrategy):
    def __init__(self, json):
        self.location_strategy = location_strategy_from_json(json)
        self.width = json["width"]
        if self.width not in [1, 2, 4]:
            raise NotImplementedError

    def read_count(self, archive) -> int:
        count_address = self.location_strategy.read_base_address(archive)
        reader = BinArchiveReader(archive, count_address)
        if self.width == 1:
            return reader.read_u8()
        elif self.width == 2:
            return reader.read_u16()
        else:
            return reader.read_u32()

    def write_count(self, archive, count: int):
        count_address = self.location_strategy.read_base_address(archive)
        writer = BinArchiveWriter(archive, count_address)
        if self.width == 1:
            writer.write_u8(count)
        elif self.width == 2:
            writer.write_u16(count)
        else:
            writer.write_u32(count)


class NullTerminatedCountStrategy(CountStrategy):
    def __init__(self, json):
        self.location_strategy = location_strategy_from_json(json)
        self.entry_size = json["entry_size"]

    def read_count(self, archive) -> int:
        base_address = self.location_strategy.read_base_address(archive)
        reader = BinArchiveReader(archive, base_address)
        next_bytes = reader.read_bytes(self.entry_size)
        count = 0
        while any(next_bytes):
            count += 1
            next_bytes = reader.read_bytes(self.entry_size)
        return count

    # NO-OP
    def write_count(self, archive, count: int):
        pass
