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
        self._load()
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
