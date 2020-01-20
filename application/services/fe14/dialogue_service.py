import json
from services.service_locator import locator
from ui.fe14_dialogue_editor import FE14DialogueEditor


class Dialogue:
    def __init__(self, name, path, key):
        self.name = name
        self.path = path
        self.key = key


class DialogueService:
    def __init__(self):
        open_files_service = locator.get_scoped("OpenFilesService")
        self.archive = open_files_service.open("GameData/GameData.bin.lz")
        self.editor = FE14DialogueEditor()
        self.dialogues = self._read_dialogue_data()
        self.archives = {}
        self.loaded = False

    def load(self):
        if not self.loaded:
            open_files_service = locator.get_scoped("OpenFilesService")
            for dialogue in self.dialogues:
                archive = open_files_service.open_message_archive(dialogue.path)
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
                dialogue = Dialogue(elem["name"], elem["path"], elem["key"])
                elements.append(dialogue)
        return elements

    def get_display_name(self):
        return "Dialogue"

    def save(self):
        pass
