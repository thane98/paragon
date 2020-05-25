import json
from typing import List, Tuple, Dict

from PySide2.QtWidgets import QWidget

from core.export_capabilities import ExportCapabilities, ExportCapability
from module.table_module import TableModule
from services.abstract_editor_service import AbstractEditorService
from services.service_locator import locator
from ui.fe14_dialogue_editor import FE14DialogueEditor


class ExportDialogueLineNode:
    def __init__(self, value: str):
        self._value = value

    def export(self):
        return self._value

    @staticmethod
    def export_capabilities() -> ExportCapabilities:
        return ExportCapabilities([ExportCapability.Selectable])


class ExportDialogueCharacterNode:
    def __init__(self, children: List[Tuple[ExportDialogueLineNode, str, str]]):
        self._children: List[Tuple[ExportDialogueLineNode, str, str]] = children

    def children(self) -> List[Tuple[ExportDialogueLineNode, str, str]]:
        return self._children

    @staticmethod
    def export_capabilities() -> ExportCapabilities:
        return ExportCapabilities([ExportCapability.Selectable])


class Dialogue:
    def __init__(self, name, path, key, localized):
        self.name = name
        self.path = path
        self.key = key
        self.localized = localized


class DialogueService(AbstractEditorService):
    def __init__(self):
        super().__init__()
        open_files_service = locator.get_scoped("OpenFilesService")
        self.archive = open_files_service.open("GameData/GameData.bin.lz")
        self.dialogues = self._read_dialogue_data()
        self.archives = {}
        self.loaded = False

    def load(self):
        if not self.loaded:
            open_files_service = locator.get_scoped("OpenFilesService")
            for dialogue in self.dialogues:
                archive = open_files_service.open_message_archive(dialogue.path, dialogue.localized)
                self.archives[dialogue] = archive
            self.loaded = True

    def get_dialogue_value_for_character(self, character, dialogue):
        archive = self.archives[dialogue]
        chopped_pid = character["PID"].value[4:]
        key = dialogue.key.format(chopped_pid)
        if archive.has_message(key):
            return archive.get_message(key)
        else:
            return ""

    def update_dialogue_value_for_character(self, character, dialogue, new_value):
        archive = self.archives[dialogue]
        chopped_pid = character["PID"].value[4:]
        key = dialogue.key.format(chopped_pid)
        archive.insert_or_overwrite_message(key, new_value)

    @staticmethod
    def _read_dialogue_data():
        elements = []
        with open("Modules/ServiceData/FE14Dialogue.json", "r", encoding="utf-8") as f:
            js = json.load(f)
            for elem in js:
                dialogue = Dialogue(elem["name"], elem["path"], elem["key"], elem.get("localized", True))
                elements.append(dialogue)
        return elements

    def get_editor(self) -> QWidget:
        pass

    def get_display_name(self) -> str:
        return "Dialogue"

    def save(self):
        pass

    def children(self):
        self.load()
        module = locator.get_scoped("ModuleService").get_module("Characters")
        result = []
        for entry in module.entries:
            node = self._create_export_node_for_character(entry)
            result.append((node, entry.get_display_name(), entry.get_key()))
        return result

    def _create_export_node_for_character(self, character):
        lines = []
        for dialogue in self.dialogues:
            dialogue_value = self.get_dialogue_value_for_character(character, dialogue)
            lines.append((ExportDialogueLineNode(dialogue_value), dialogue.name, dialogue.key))
        return ExportDialogueCharacterNode(lines)

    def import_values_from_json(self, values_json: dict):
        self.load()
        key_to_dialogue_map = self._get_key_to_dialogue_map()
        module: TableModule = locator.get_scoped("ModuleService").get_module("Characters")
        for key in values_json:
            character = module.get_element_by_key(key)
            if not character:
                raise KeyError("Cannot import dialogue for non-existent character %s." % key)
            for dialogue_key in values_json[key]:
                dialogue = key_to_dialogue_map[dialogue_key]
                new_value = values_json[key][dialogue_key]
                self.update_dialogue_value_for_character(character, dialogue, new_value)

    def _get_key_to_dialogue_map(self) -> Dict[str, Dialogue]:
        result = {}
        for dialogue in self.dialogues:
            result[dialogue.key] = dialogue
        return result

    def has_ui(self):
        return False
