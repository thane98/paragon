import json
from copy import deepcopy

import fefeditor2

from bin_streams import BinArchiveReader, BinArchiveWriter
from properties.i32_property import I32Property
from properties.string_property import StringProperty
from utils.properties import read_trivial_properties


def read_tile_template():
    with open("Modules/ServiceData/FE14Tile.json", "r") as f:
        js = json.load(f)
        return read_trivial_properties(js)


TILE_TEMPLATE = read_tile_template()
_GRID_SIZE = 1048
_TILE_SIZE = 0x28
_HEADER_SIZE = 0x10
_NAME_TO_ATTR = {
    "Map Model": "map_model",
    "Map Size X": "map_size_x",
    "Map Size Y": "map_size_y",
    "Border Size X": "border_size_x",
    "Border Size Y": "border_size_y",
    "Trimmed Size X": "trimmed_size_x",
    "Trimmed Size Y": "trimmed_size_y"
}


class Terrain:
    def __init__(self):
        self.tiles = []
        self.grid = [[0 for _ in range(32)] for _ in range(32)]
        self.map_model = StringProperty("Map Model")
        self.map_size_x = I32Property("Map Size X")
        self.map_size_y = I32Property("Map Size Y")
        self.border_size_x = I32Property("Border Size X")
        self.border_size_y = I32Property("Border Size Y")
        self.trimmed_size_x = I32Property("Trimmed Size X")
        self.trimmed_size_y = I32Property("Trimmed Size Y")

    def read(self, archive):
        reader = BinArchiveReader(archive)
        tile_table_address = reader.read_internal_pointer()
        tile_count = reader.read_u32()
        self.map_model.read(reader)
        grid_address = reader.read_internal_pointer()

        self.tiles.clear()
        reader.seek(tile_table_address)
        for _ in range(0, tile_count):
            tile = self._read_tile(reader)
            self.tiles.append(tile)

        reader.seek(grid_address)
        self.map_size_x.read(reader)
        self.map_size_y.read(reader)
        self.border_size_x.read(reader)
        self.border_size_y.read(reader)
        self.trimmed_size_x.read(reader)
        self.trimmed_size_y.read(reader)
        for r in range(0, 32):
            for c in range(0, 32):
                self.grid[r][c] = reader.read_u8()

    @staticmethod
    def _read_tile(reader):
        tile = deepcopy(TILE_TEMPLATE)
        for prop in tile.values():
            prop.read(reader)
        return tile

    def to_bin(self):
        archive = fefeditor2.create_bin_archive()
        archive.allocate_at_end(self._calculate_binary_size())
        writer = BinArchiveWriter(archive)
        writer.write_pointer(_HEADER_SIZE)
        writer.write_u32(len(self.tiles))
        self.map_model.write(writer)
        writer.write_pointer(self._grid_address())
        for tile in self.tiles:
            for prop in tile.values():
                prop.write(writer)
        self.map_size_x.write(writer)
        self.map_size_y.write(writer)
        self.border_size_x.write(writer)
        self.border_size_y.write(writer)
        self.trimmed_size_x.write(writer)
        self.trimmed_size_y.write(writer)
        for row in self.grid:
            writer.write_bytes(row)
        print("Done!")
        return archive

    def _calculate_binary_size(self):
        return _HEADER_SIZE + len(self.tiles) * _TILE_SIZE + _GRID_SIZE

    def _grid_address(self):
        return _HEADER_SIZE + len(self.tiles) * _TILE_SIZE

    def __getitem__(self, item):
        return self.__getattribute__(_NAME_TO_ATTR[item])
