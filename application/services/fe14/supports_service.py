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

        if self.archive:
            open_files_service.set_archive_in_use(self.archive)

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
        tag = hash(character1["PID"].value + character2["PID"].value) & 0xFFFFFF
        self._add_support_to_table(character1, character2, support_type, tag)
        self._add_support_to_table(character2, character1, support_type, tag)

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
        pointer_address = master_support_table_address + old_count * 4 + 4
        self.archive.allocate(pointer_address, 4, False)
        destination = self.archive.size()
        self.archive.set_internal_pointer(pointer_address, destination)

        # Generate and assign a support ID for the character
        support_id = self._find_next_support_id()
        character["Support ID"].value = support_id

        # Allocate and format the new table.
        writer.seek(destination)
        self.archive.allocate_at_end(4)
        writer.write_u16(support_id)

    def _add_support_to_table(self, character1, character2, support_type, tag):
        # Jump to the target support table.
        master_support_table_address = self._get_master_support_table_address()
        reader = BinArchiveReader(self.archive, master_support_table_address)
        target_support_id = character1["Support ID"].value
        reader.seek(reader.tell() + target_support_id * 4 + 4)
        reader.seek(reader.read_internal_pointer() + 2)  # Skip the owner id.

        # Update the support count.
        writer = BinArchiveWriter(self.archive, reader.tell())
        old_count = reader.read_u16()
        writer.write_u16(old_count + 1)

        # Create the new support.
        new_support_address = writer.tell() + old_count * 0xC
        self.archive.allocate(new_support_address, 0xC, False)
        writer.seek(new_support_address)
        writer.write_u16(character2["ID"].value)
        writer.write_u16(old_count)
        writer.write_u32(support_type)
        writer.write_u32(tag)

    @staticmethod
    def _find_next_support_id() -> int:
        module_service = locator.get_scoped("ModuleService")
        characters_module = module_service.get_module("Characters")
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
        module_service = locator.get_scoped("ModuleService")
        characters = module_service.get_module("Characters").entries

        character = characters[reader.read_u16()]
        reader.seek(reader.tell() + 2)  # The ID is not needed when editing.
        raw_type = reader.read_u32()
        tag = reader.read_bytes(4)
        return Support(character, raw_type, tag)

    def _get_master_support_table_address(self):
        reader = BinArchiveReader(self.archive, 8)
        reader.seek(reader.read_internal_pointer() + 8)
        return reader.read_internal_pointer()

    def remove_support(self, owner, support):
        other = support.character
        self._remove_support_from_table(owner, other)
        self._remove_support_from_table(other, owner)

    def _remove_support_from_table(self, owner, other):
        # Update count.
        reader = self._open_reader_at_table(owner["Support ID"].value)
        reader.seek(reader.tell() + 2)
        writer = BinArchiveWriter(self.archive, reader.tell())
        old_count = reader.read_u16()
        writer.write_u16(old_count - 1)

        # Deallocate the support.
        target_index = self._find_index_of_support_with_character(reader, other, old_count)
        target_address = writer.tell() + target_index * 0xC
        self.archive.deallocate(target_address, 0xC, False)

        # Shift supports numbers back.
        writer.seek(target_address + 2)
        for i in range(target_index, old_count - 1):
            writer.write_u16(i)
            writer.seek(writer.tell() + 0xA)

    @staticmethod
    def _find_index_of_support_with_character(reader, other, count) -> int:
        for i in range(0, count):
            character_id = reader.read_u16()
            if character_id == other["ID"].value:
                return i
            reader.seek(reader.tell() + 0xA)
        return -1

    def set_support_type(self, character, support, new_support_type):
        if new_support_type != support.support_type:
            other = support.character
            self._set_support_type_helper(character, other, new_support_type)
            self._set_support_type_helper(other, character, new_support_type)
            support.support_type = new_support_type

    def _set_support_type_helper(self, owner, other, new_support_type):
        reader = self._open_reader_at_table(owner["Support ID"].value)
        reader.seek(reader.tell() + 2)
        count = reader.read_u16()
        supports_start = reader.tell()
        target_index = self._find_index_of_support_with_character(reader, other, count)
        target_address = supports_start + target_index * 0xC + 0x4

        writer = BinArchiveWriter(self.archive, target_address)
        writer.write_u32(new_support_type)

    def save(self):
        pass
