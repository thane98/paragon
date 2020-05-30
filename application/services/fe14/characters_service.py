from PySide2.QtWidgets import QWidget

from services.abstract_editor_service import AbstractEditorService
from services.service_locator import locator
from ui.fe14_character_editor import FE14CharacterEditor


class CharactersService(AbstractEditorService):
    def __init__(self):
        self.editor = None

    def get_editor(self) -> QWidget:
        if not self.editor:
            self.editor = FE14CharacterEditor()
            self.set_in_use()
        return self.editor

    @staticmethod
    def set_in_use():
        character_module = locator.get_scoped("ModuleService").get_module("Characters")
        locator.get_scoped("ModuleService").set_module_in_use(character_module)

    def get_display_name(self) -> str:
        return "Characters"

    def save(self):
        pass
