from bin_streams import BinArchiveReader, BinArchiveWriter
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

    def add_support_between_characters(self, character1, character2, support_type):
        if not self._has_support_table(character1):
            self._create_support_table(character1)
        if not self._has_support_table(character2):
            self._create_support_table(character2)
        self._add_support_to_table(character1, character2, support_type)
        self._add_support_to_table(character2, character1, support_type)

    @staticmethod
    def _has_support_table(character):
        return character["Support ID"].value != 0xFFFF

    def _create_support_table(self, character):
        # First, increment master support table count.
        master_support_table_address = self._get_master_support_table_address()
        writer = BinArchiveWriter(self.archive, master_support_table_address)
        reader = BinArchiveReader(self.archive, master_support_table_address)
        old_count = reader.read_u32()
        writer.write_u32(old_count + 1)

        # Next, create a pointer to the new table.
        destination = self.archive.size()
        pointer_address = master_support_table_address + old_count * 4 + 4
        self.archive.allocate(pointer_address, 4, False)
        self.archive.set_internal_pointer(pointer_address, destination)

        # Generate and assign a support ID for the character
        support_id = self._find_next_support_id()
        character["Support ID"].value = support_id

        # Allocate and format the new table.
        writer.seek(self.archive.size())
        self.archive.allocate_at_end(4)
        writer.write_u16(support_id)

    def _add_support_to_table(self, character1, character2, support_type):
        # Jump to the target support table.
        master_support_table_address = self._get_master_support_table_address()
        reader = BinArchiveReader(self.archive, master_support_table_address)
        target_support_id = character1["Support ID"].value
        reader.seek(reader.tell() + target_support_id * 4 + 4)
        reader.seek(reader.read_internal_pointer() + 2)  # Skip the owner id.

        # Update the support count.
        writer = BinArchiveWriter(reader.tell())
        old_count = reader.read_u16()
        writer.write_u16(old_count + 1)

        # Create the new support.
        new_support_address = writer.tell() + old_count * 0xC
        self.archive.allocate(new_support_address, 0xC, False)
        writer.seek(new_support_address)
        writer.write_u16(character2["ID"].value)
        writer.write_u32(support_type)
        writer.write_u32(0)

    @staticmethod
    def _find_next_support_id() -> int:
        characters_module = locator.get_scoped("Driver").modules["Characters"]
        characters = characters_module.entries
        max_support_id = -1
        for character in characters:
            if character["Support ID"].value != 0xFFFF:
                max_support_id = max(max_support_id, character["Support ID"].value)
        return max_support_id + 1

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
