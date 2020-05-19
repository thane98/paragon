from PySide2.QtWidgets import QWidget

from services.abstract_editor_service import AbstractEditorService
from ui.fe14_character_editor import FE14CharacterEditor


class CharactersService(AbstractEditorService):
    def __init__(self):
        self.editor = None

    def get_editor(self) -> QWidget:
        if not self.editor:
            self.editor = FE14CharacterEditor()
        return self.editor

    def get_display_name(self) -> str:
        return "Characters"

    def save(self):
        pass
