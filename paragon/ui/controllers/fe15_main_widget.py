from PySide2.QtWidgets import QInputDialog
from paragon.model.game import Game

from paragon.ui.controllers.dialogue_editor import DialogueEditor
from paragon.ui.views.ui_fe15_main_widget import Ui_FE15MainWidget


class FE15MainWidget(Ui_FE15MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window

        self.dialogue_editors = {}

        self.characters_button.clicked.connect(self._on_characters)
        self.items_button.clicked.connect(self._on_items)
        self.classes_button.clicked.connect(self._on_classes)
        self.skills_button.clicked.connect(self._on_skills)
        self.edit_dialogue_button.clicked.connect(self._on_edit_dialogue)

    def _on_characters(self):
        self.main_window.open_node_by_id("characters")

    def _on_items(self):
        self.main_window.open_node_by_id("items")

    def _on_classes(self):
        self.main_window.open_node_by_id("classes")

    def _on_skills(self):
        self.main_window.open_node_by_id("skills")

    def _on_edit_dialogue(self):
        choices = self.gs.data.enumerate_text_archives()
        choice, ok = QInputDialog.getItem(self, "Select Text", "Path", choices, 0)
        if ok:
            if choice in self.dialogue_editors:
                self.dialogue_editors[choice].show()
            else:
                editor = DialogueEditor(self.gs.data, self.gs.dialogue, Game.FE15)
                editor.set_archive(choice, False)
                self.dialogue_editors[choice] = editor
                editor.show()
