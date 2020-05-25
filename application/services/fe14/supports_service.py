from typing import List

from PySide2.QtWidgets import QWidget

from core.bin_streams import BinArchiveWriter, BinArchiveReader
from core.export_capabilities import ExportCapabilities, ExportCapability
from model.message_archive import MessageArchive
from module.properties.property_container import PropertyContainer
from module.table_module import TableModule
from services.abstract_editor_service import AbstractEditorService
from services.service_locator import locator
from ui.fe14_conversation_editor import FE14ConversationEditor


class SupportIDInUseException(Exception):
    def __init__(self, support_id: int):
        super().__init__("Support ID 0x%x is already in use." % support_id)


class OutOfBoundsSupportIDException(Exception):
    def __init__(self, support_id: int):
        super().__init__("Support ID 0x%x is out of bounds." % support_id)


class Support:
    def __init__(self, character, support_type, tag):
        self.character = character
        self.support_type = support_type
        self.tag = tag

    def export(self):
        return {
            "character": self.character.get_key(),
            "support_type": self.support_type
        }

    @staticmethod
    def export_capabilities() -> ExportCapabilities:
        return ExportCapabilities([ExportCapability.Selectable])


class ExportSupportTableNode:
    def __init__(self, character, get_supports_function):
        self._character = character
        self._get_supports = get_supports_function

    def children(self):
        supports = self._get_supports(self._character)
        return [(support, support.character.get_display_name(), support.character.get_key()) for support in supports]

    @staticmethod
    def export_capabilities() -> ExportCapabilities:
        return ExportCapabilities([ExportCapability.Selectable])


class SupportsService(AbstractEditorService):
    def __init__(self):
        super().__init__()
        open_files_service = locator.get_scoped("OpenFilesService")
        self.archive = open_files_service.open("GameData/GameData.bin.lz")
        self._conversation_editors = []

    def set_in_use(self):
        open_files_service = locator.get_scoped("OpenFilesService")
        open_files_service.set_archive_in_use(self.archive)

    def get_editor(self) -> QWidget:
        pass

    def get_display_name(self):
        return "Supports"

    def get_supports_for_character(self, character):
        # Don't attempt to read a support table if one doesn't exist.
        table_number = character["Support ID"].value
        if not self._has_support_table(character):
            return []

        # Support table exists. Read and return.
        reader = self._open_reader_at_table(table_number)
        return self._read_supports_from_table(reader)

    def check_support_id_validity(self):
        module_service = locator.get_scoped("ModuleService")
        characters = module_service.get_module("Characters").entries
        reader = BinArchiveReader(self.archive, self._get_master_support_table_address())
        table_count = reader.read_u32()
        encountered_ids = set()
        for character in characters:
            support_id = character["Support ID"].value
            if support_id == 0xFFFF:
                continue
            if support_id in encountered_ids:
                raise SupportIDInUseException(support_id)
            elif support_id >= table_count:
                raise OutOfBoundsSupportIDException(support_id)
            encountered_ids.add(support_id)

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

    def _add_support_to_table(self, character1, character2, support_type):
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
        writer.write_u32(0x1)  # Support tag. Still figuring this part out.

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
            self.set_support_type_from_characters(character, other, new_support_type)
            support.support_type = new_support_type

    def set_support_type_from_characters(self, character1, character2, new_support_type):
        self._set_support_type_helper(character1, character2, new_support_type)
        self._set_support_type_helper(character2, character1, new_support_type)

    def _set_support_type_helper(self, owner, other, new_support_type):
        reader = self._open_reader_at_table(owner["Support ID"].value)
        reader.seek(reader.tell() + 2)
        count = reader.read_u16()
        supports_start = reader.tell()
        target_index = self._find_index_of_support_with_character(reader, other, count)
        target_address = supports_start + target_index * 0xC + 0x4

        writer = BinArchiveWriter(self.archive, target_address)
        writer.write_u32(new_support_type)

    def _support_exists_between_characters(self, character1, character2) -> bool:
        supports = self.get_supports_for_character(character1)
        for support in supports:
            if support.character == character2:
                return True
        return False

    def get_supported_characters(self, character) -> List[PropertyContainer]:
        supports = self.get_supports_for_character(character)
        result = []
        for support in supports:
            result.append(support.character)
        return result

    def get_unsupported_characters(self, character) -> List[PropertyContainer]:
        module = locator.get_scoped("ModuleService").get_module("Characters")
        characters = module.entries
        supported_characters = self.get_supported_characters(character)
        result = []
        for character in characters:
            if character not in supported_characters:
                result.append(character)
        return result

    def save(self):
        pass

    def children(self):
        module = locator.get_scoped("ModuleService").get_module("Characters")
        characters = module.entries
        return [(ExportSupportTableNode(character, self.get_supports_for_character),
                 character.get_display_name(),
                 character.get_key())
                for character in characters if self._has_support_table(character)]

    def import_values_from_json(self, values_json: dict):
        module: TableModule = locator.get_scoped("ModuleService").get_module("Characters")
        for character1_key in values_json:
            character1 = module.get_element_by_key(character1_key)
            for character2_key in values_json[character1_key]:
                character2 = module.get_element_by_key(character2_key)
                support_type = values_json[character1_key][character2_key]["support_type"]
                if self._support_exists_between_characters(character1, character2):
                    self.set_support_type_from_characters(character1, character2, support_type)
                else:
                    self.add_support_between_characters(character1, character2, support_type)
        self.set_in_use()

    def open_support_conversation_for_characters(self, character1, character2):
        part1 = character1["PID"].value[4:]
        part2 = character2["PID"].value[4:]
        path1 = "m/%s_%s.bin.lz" % (part1, part2)
        path2 = "m/%s_%s.bin.lz" % (part2, part1)
        archive = self._try_open_conversation(path1)
        if not archive:
            archive = self._try_open_conversation(path2)
            if not archive:
                archive = MessageArchive()
                archive.title = "MESS_ARCHIVE_%s_%s" % (part1, part2)
                archive.insert_or_overwrite_message("MID_支援_%s_%s_Ｃ" % (part1, part2), "")
                archive.insert_or_overwrite_message("MID_支援_%s_%s_Ｂ" % (part1, part2), "")
                archive.insert_or_overwrite_message("MID_支援_%s_%s_Ａ" % (part1, part2), "")
                archive.insert_or_overwrite_message("MID_支援_%s_%s_Ｓ" % (part1, part2), "")
                locator.get_scoped("OpenFilesService").register_or_overwrite_message_archive(path1, archive)
        editor_title = "Support - %s and %s" % (character1.get_display_name(), character2.get_display_name())
        editor = FE14ConversationEditor(archive, title=editor_title, owner=self, is_support=True)
        self._conversation_editors.append(editor)
        editor.show()

    def delete_conversation_editor(self, editor):
        self._conversation_editors.remove(editor)

    @staticmethod
    def _try_open_conversation(path: str):
        try:
            return locator.get_scoped("OpenFilesService").open_message_archive(path)
        except:
            return None

    def has_ui(self):
        return False
