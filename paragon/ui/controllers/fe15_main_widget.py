import logging

from PySide2.QtWidgets import QInputDialog
from paragon.ui import utils

from paragon.model.game import Game
from paragon.ui.controllers.chapter_editor import ChapterEditor

from paragon.ui.controllers.dialogue_editor import DialogueEditor
from paragon.ui.views.ui_fe15_main_widget import Ui_FE15MainWidget


class FE15MainWidget(Ui_FE15MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window
        self.chapter_editor = None

        self.dialogue_editors = {}

        self.chapters_button.clicked.connect(self._on_chapters)
        self.characters_button.clicked.connect(self._on_characters)
        self.items_button.clicked.connect(self._on_items)
        self.classes_button.clicked.connect(self._on_classes)
        self.skills_button.clicked.connect(self._on_skills)
        self.edit_dialogue_button.clicked.connect(self._on_edit_dialogue)
        self.armies_button.clicked.connect(self._on_armies)

    def _on_chapters(self):
        try:
            if self.chapter_editor:
                self.chapter_editor.show()
            else:
                self.gs.data.set_store_dirty("chapters", True)
                self.gs.data.set_store_dirty("terrain", True)
                self.chapter_editor = ChapterEditor(self.ms, self.gs)
                self.chapter_editor.show()
        except:
            logging.exception("Failed to create FE14 chapter editor.")
            utils.error(self)

    def _on_characters(self):
        self.main_window.open_node_by_id("characters")

    def _on_items(self):
        self.main_window.open_node_by_id("items")

    def _on_classes(self):
        self.main_window.open_node_by_id("classes")

    def _on_skills(self):
        self.main_window.open_node_by_id("skills")

    def _on_armies(self):
        self.main_window.open_node_by_id("belong")

    def _on_edit_dialogue(self):
        choices = self.gs.data.enumerate_text_archives()
        choice, ok = QInputDialog.getItem(self, "Select Text", "Path", choices, 0)
        if ok:
            if choice in self.dialogue_editors:
                self.dialogue_editors[choice].show()
            else:
                editor = DialogueEditor(
                    self.gs.data, self.gs.dialogue, self.gs.sprite_animation, Game.FE15
                )
                editor.set_archive(choice, False)
                self.dialogue_editors[choice] = editor
                editor.show()
