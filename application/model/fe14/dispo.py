import fefeditor2

from core.bin_streams import BinArchiveReader, BinArchiveWriter
from module.properties.property_container import PropertyContainer

SPAWN_TEMPLATE = None


def load_spawn_template():
    global SPAWN_TEMPLATE
    SPAWN_TEMPLATE = PropertyContainer.from_file("Modules/ServiceData/FE14Spawn.json")


def get_spawn_template():
    global SPAWN_TEMPLATE
    return SPAWN_TEMPLATE


class Faction:
    def __init__(self):
        self.name = None
        self.spawns = None

    def read(self, reader: BinArchiveReader):
        self.name = reader.read_string()
        spawn_address = reader.read_internal_pointer()
        spawn_count = reader.read_u32()
        end_address = reader.tell()
        self.spawns = []
        reader.seek(spawn_address)
        for _ in range(0, spawn_count):
            self.spawns.append(self._read_spawn(reader))
        reader.seek(end_address)

    def write(self, writer: BinArchiveWriter, spawn_address):
        writer.write_string(self.name)
        writer.write_pointer(spawn_address)
        writer.write_u32(len(self.spawns))
        end_address = writer.tell()
        writer.seek(spawn_address)
        for spawn in self.spawns:
            for prop in spawn.values():
                prop.write(writer)
        writer.seek(end_address)

    @staticmethod
    def _read_spawn(reader):
        if not SPAWN_TEMPLATE:
            load_spawn_template()
        spawn = SPAWN_TEMPLATE.duplicate()
        for prop in spawn.values():
            prop.read(reader)
        return spawn


class Dispo:
    def __init__(self):
        self.factions = []

    def read(self, archive):
        self.factions.clear()
        reader = BinArchiveReader(archive)
        next_bytes = reader.read_bytes(12)
        while any(next_bytes):
            reader.seek(reader.tell() - 12)
            faction = Faction()
            faction.read(reader)
            self.factions.append(faction)
            next_bytes = reader.read_bytes(12)

    def to_bin(self):
        archive = fefeditor2.create_bin_archive()
        archive.allocate_at_end(self._calculate_binary_size())
        self._write_factions(archive)
        return archive

    def _calculate_binary_size(self):
        header_size = self._calculate_header_size()
        spawn_size = self._calculate_total_spawn_count() * 0x8C
        return header_size + spawn_size

    def _calculate_header_size(self):
        return (len(self.factions) + 1) * 12

    def _calculate_total_spawn_count(self):
        total = 0
        for faction in self.factions:
            total += len(faction.spawns)
        return total

    def _write_factions(self, archive):
        writer = BinArchiveWriter(archive)
        next_spawn_address = self._calculate_header_size()
        for faction in self.factions:
            faction.write(writer, next_spawn_address)
            next_spawn_address += len(faction.spawns) * 0x8C

    def delete_spawn(self, spawn):
        faction = self.find_faction_from_spawn(spawn)
        faction.spawns.remove(spawn)

    def find_faction_from_spawn(self, spawn: PropertyContainer):
        for faction in self.factions:
            if spawn in faction.spawns:
                return faction
        raise ValueError
