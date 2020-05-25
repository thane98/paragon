from PySide2.QtWidgets import QWidget

from model.fe14 import terrain, dispo
from model.fe14.chapter_data import ChapterData
from services.abstract_editor_service import AbstractEditorService
from services.service_locator import locator
from ui.fe14_chapter_editor import FE14ChapterEditor
from utils.chapter_utils import detect_chapter_file_sub_folder

_CONFIG_PATH = "/map/config/%s.bin"
_DISPOS_PATH = "/GameData/Dispos/%s.bin.lz"
_PERSON_PATH = "/GameData/Person/%s.bin.lz"
_TERRAIN_PATH = "/GameData/Terrain/%s.bin.lz"
_CONVERATION_PATH = "/m/%s/%s.bin.lz"


class ChapterService(AbstractEditorService):
    def __init__(self):
        super().__init__()
        self.editor = None
        self.open_chapters = {}
        terrain.load_tile_template()
        dispo.load_spawn_template()

    def get_chapter_data_from_chapter(self, chapter):
        cid = chapter["CID"].value
        if cid in self.open_chapters:
            return self.open_chapters[cid]
        chapter_data = ChapterData(chapter)
        self.open_chapters[cid] = chapter_data
        return chapter_data

    def get_editor(self) -> QWidget:
        if not self.editor:
            self.editor = FE14ChapterEditor()
        return self.editor

    def get_display_name(self) -> str:
        return "Chapters"

    def save(self):
        for chapter_data in self.open_chapters.values():
            chapter_data.save()

    @staticmethod
    def is_cid_in_use(cid):
        module_service = locator.get_scoped("ModuleService")
        entries = module_service.get_module("Chapters").entries
        for entry in entries:
            if entry["CID"].value == cid:
                return True
        return False

    @staticmethod
    def create_chapter(source, new_chapter_cid):
        # Create the new chapter entry.
        module_service = locator.get_scoped("ModuleService")
        chapter_module = module_service.get_module("Chapters")
        chapter_module.entries_model.insertRow(chapter_module.entries_model.rowCount())

        # Copy properties from the source chapter, give it the new CID.
        new_chapter = chapter_module.entries[-1]
        source.copy_to(new_chapter)
        new_chapter["Key (CID)"].value = new_chapter_cid
        new_chapter["CID"].value = new_chapter_cid

        # Create chapter files using the ones from the source chapter.
        open_files_service = locator.get_scoped("OpenFilesService")
        chapter_file_sub_folder = detect_chapter_file_sub_folder(source)
        source_suffix = chapter_file_sub_folder + source["CID"].value[4:]
        dest_suffix = chapter_file_sub_folder + new_chapter_cid[4:]
        source_conversation_data_path = open_files_service.localized_path(_CONVERATION_PATH % (source_suffix,
                                                                                               source["CID"].value[4:]))
        dest_conversation_data_path = open_files_service.localized_path(_CONVERATION_PATH
                                                                        % (dest_suffix, new_chapter_cid[4:].value[4:]))
        config_archive = open_files_service.open_archive_direct(_CONFIG_PATH % source["CID"].value[4:])
        person_archive = open_files_service.open_archive_direct(_PERSON_PATH % source_suffix)
        dispos_archive = open_files_service.open_archive_direct(_DISPOS_PATH % source_suffix)
        terrain_archive = open_files_service.open_archive_direct(_TERRAIN_PATH % source["CID"].value[4:])
        text_archive = open_files_service.open_message_archive_direct(source_conversation_data_path)
        open_files_service.register_or_overwrite_archive(_CONFIG_PATH % new_chapter_cid[4:], config_archive)
        open_files_service.register_or_overwrite_archive(_PERSON_PATH % dest_suffix, person_archive)
        open_files_service.register_or_overwrite_archive(_DISPOS_PATH % dest_suffix, dispos_archive)
        open_files_service.register_or_overwrite_archive(_TERRAIN_PATH % new_chapter_cid[4:], terrain_archive)
        open_files_service.register_or_overwrite_message_archive(dest_conversation_data_path, text_archive)
