import logging

from PySide2.QtWidgets import QWidget

from core.bin_streams import BinArchiveReader, BinArchiveWriter
from model.qt.voice_set_model import VoiceSetEntriesModel, VoiceSetModel
from module.count import SimpleCountStrategy
from module.location import FromMappedLocationStrategy
from module.properties.buffer_property import BufferProperty
from module.properties.property_container import PropertyContainer
from module.properties.string_property import StringProperty
from services.abstract_editor_service import AbstractEditorService
from services.service_locator import locator
from ui.fe14_sound_editor import FE14SoundEditor


class SoundService(AbstractEditorService):
    def __init__(self):
        super().__init__()
        self.editor = None
        self.archive = None
        self.template = self._create_entry_template()
        self.voice_set_labels = []
        self._location_strategy = FromMappedLocationStrategy({
            "mapped_value": "RANDOM_SOUND_HEAD",
            "offset": 4
        })
        self._count_strategy = SimpleCountStrategy({
            "type": "from_mapped",
            "mapped_value": "RANDOM_SOUND_HEAD",
            "width": 4
        })
        try:
            self._load()
            self.load_succeeded = True
        except:
            logging.exception("An error occurred while loading FE14 sound service files.")
            self.load_succeeded = False
        self.voice_set_model = None

    @staticmethod
    def _create_entry_template() -> PropertyContainer:
        template = PropertyContainer()
        template["Name"] = StringProperty("Name")
        template["Tag"] = BufferProperty("Tag", length=4)
        return template

    def _load(self):
        open_files_service = locator.get_scoped("OpenFilesService")
        self.archive = open_files_service.open("sound/IndirectSound.bin.lz")

        address = self._location_strategy.read_base_address(self.archive)
        count = self._count_strategy.read_count(self.archive)
        reader = BinArchiveReader(self.archive, address)
        for i in range(0, count):
            self.voice_set_labels.append(reader.read_mapped())

            # Skip to the next set.
            reader.seek(reader.tell() + 8)
            set_count = reader.read_u32()
            reader.seek(reader.tell() + set_count * 8 + 4)

    def _get_set_table_end(self):
        return self.archive.addr_of_mapped_pointer("MULTI_SOUND_HEAD")

    def _get_reader_at_voice_set_table(self, voice_set_label: str) -> (BinArchiveReader, int):
        # Seek to the voice set's address.
        address = self.archive.addr_of_mapped_pointer(voice_set_label)
        if not address:
            raise Exception

        # Read the count and perform sanity checks.
        reader = BinArchiveReader(self.archive, address)
        if reader.read_u32() != 0xFFFF0002 or reader.read_string() != voice_set_label:
            raise Exception
        set_count = reader.read_u32()
        if reader.read_u32() != set_count:
            raise Exception
        return reader, set_count

    def get_voice_set(self, voice_set_label: str) -> VoiceSetEntriesModel:
        reader, set_count = self._get_reader_at_voice_set_table(voice_set_label)
        result = []
        for i in range(0, set_count):
            entry = self.template.duplicate()
            for prop in entry.values():
                prop.read(reader)
            result.append(entry)
        return VoiceSetEntriesModel(voice_set_label, result)

    def save_entry(self, voice_set_label: str, entry: PropertyContainer, index: int):
        reader, set_count = self._get_reader_at_voice_set_table(voice_set_label)
        if index < 0 or index >= set_count:
            raise Exception
        reader.seek(reader.tell() + index * 8)
        writer = BinArchiveWriter(self.archive, reader.tell())
        for prop in entry.values():
            prop.write(writer)

    def append_entry_to_voice_set(self, voice_set_label: str) -> PropertyContainer:
        reader, set_count = self._get_reader_at_voice_set_table(voice_set_label)
        reader.seek(reader.tell() - 8)
        writer = BinArchiveWriter(self.archive, reader.tell())
        writer.write_u32(set_count + 1)
        writer.write_u32(set_count + 1)

        entry = PropertyContainer()
        entry["Name"] = StringProperty("Name", value="Placeholder")
        entry["Tag"] = BufferProperty("Tag", value=[1, 0, 0, 0])
        writer.seek(writer.tell() + set_count * 8)
        self.archive.allocate(writer.tell(), 8, False)
        for prop in entry.values():
            prop.write(writer)
        return entry

    def remove_entry_from_voice_set(self, voice_set_label: str, index: int):
        reader, set_count = self._get_reader_at_voice_set_table(voice_set_label)
        if index < 0 or index >= set_count:
            raise Exception
        target_address = reader.tell() + index * 8
        self.archive.deallocate(target_address, 8, False)

        writer = BinArchiveWriter(self.archive, reader.tell() - 8)
        writer.write_u32(set_count - 1)
        writer.write_u32(set_count - 1)

    def create_voice_set(self, voice_set_label: str):
        if voice_set_label in self.voice_set_labels:
            raise NameError

        # Write the new entry to the end of the set table.
        address = self._get_set_table_end()
        self.archive.allocate(address, 0x10, False)
        writer = BinArchiveWriter(self.archive, address)
        writer.write_mapped(voice_set_label)
        writer.write_u32(0xFFFF0002)
        writer.write_string(voice_set_label)
        writer.write_u32(0)
        writer.write_u32(0)

        # Update the count.
        self.voice_set_labels.append(voice_set_label)
        self._count_strategy.write_count(self.archive, len(self.voice_set_labels))

    def remove_voice_set(self, voice_set_label: str):
        # Remove the entry from voice set labels. Error if it's not found.
        old_size = len(self.voice_set_labels)
        for i in range(0, len(self.voice_set_labels)):
            if self.voice_set_labels[i] == voice_set_label:
                del self.voice_set_labels[i]
                break
        if old_size == len(self.voice_set_labels):
            raise IndexError

        # Deallocate memory
        reader, set_count = self._get_reader_at_voice_set_table(voice_set_label)
        reader.seek(reader.tell() - 0x10)
        self.archive.deallocate(reader.tell(), set_count * 8 + 0x10, False)

        # Update the count.
        self._count_strategy.write_count(self.archive, len(self.voice_set_labels))

    def set_in_use(self):
        open_files_service = locator.get_scoped("OpenFilesService")
        open_files_service.set_archive_in_use(self.archive)

    def get_voice_set_model(self) -> VoiceSetModel:
        if not self.voice_set_model:
            self.voice_set_model = VoiceSetModel()
        return self.voice_set_model

    def get_editor(self) -> QWidget:
        if not self.editor:
            self.editor = FE14SoundEditor()
        return self.editor

    def get_display_name(self) -> str:
        return "Voice Sets"

    def save(self):
        pass
