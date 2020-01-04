from bin_streams import BinArchiveReader
from services.service_locator import locator
from ui.fe14_support_editor import FE14SupportEditor


class Support:
    def __init__(self, character, support_type, tag):
        self.character = character
        self.support_type = support_type
        self.tag = tag


class SupportsService:
    def __init__(self):
        open_files_service = locator.get_scoped("OpenFilesService")
        self.archive = open_files_service.open("GameData/GameData.bin.lz")
        self.editor = FE14SupportEditor()

    def get_display_name(self):
        return "Supports"

    def get_supports_for_character(self, character):
        # Don't attempt to read a support table if one doesn't exist.
        table_number = character["Support ID"].value
        if table_number == 0xFFFF:
            return []

        # Support table exists. Read and return.
        reader = self._open_reader_at_table(table_number)
        return self._read_supports_from_table(reader)

    def _open_reader_at_table(self, table_number):
        addr = self._get_master_support_table_address() + table_number * 4 + 4
        reader = BinArchiveReader(self.archive, addr)
        reader.seek(reader.read_internal_pointer())
        return reader

    @classmethod
    def _read_supports_from_table(cls, reader: BinArchiveReader):
        reader.seek(reader.tell() + 2)  # Don't care about the owner here.
        count = reader.read_u16()
        supports = []
        for _ in range(0, count):
            support = cls._read_support(reader)
            supports.append(support)
        return supports

    @staticmethod
    def _read_support(reader: BinArchiveReader):
        characters_module = locator.get_scoped("Driver").modules["Characters"]
        characters = characters_module.entries

        character = characters[reader.read_u16()]
        reader.seek(reader.tell() + 2)  # The ID is not needed when editing.
        raw_type = reader.read_u32()
        tag = reader.read_bytes(4)
        return Support(character, raw_type, tag)

    def _get_master_support_table_address(self):
        reader = BinArchiveReader(self.archive, 8)
        reader.seek(reader.read_internal_pointer() + 8)
        return reader.read_internal_pointer()
