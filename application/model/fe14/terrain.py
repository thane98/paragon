from bin_streams import BinArchiveReader, BinArchiveWriter


class Tile:
    def __init__(self):
        pass

    def read(self, reader: BinArchiveReader):
        pass

    def write(self, writer: BinArchiveWriter, spawn_address):
        pass


class Terrain:
    def __init__(self):
        self.factions = []

    def read(self, archive):
        pass

    def to_bin(self):
        pass
