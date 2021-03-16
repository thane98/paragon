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
        self.tiles_button.clicked.connect(self._on_tiles)
        self.spell_lists_button.clicked.connect(self._on_spell_lists)
        self.rumors_button.clicked.connect(self._on_rumors)
        self.subquests_button.clicked.connect(self._on_subquests)
        self.food_preferences_button.clicked.connect(self._on_food_preferences)
        self.portraits_button.clicked.connect(self._on_portraits)
        self.rom0_button.clicked.connect(self._on_rom0)
        self.rom1_button.clicked.connect(self._on_rom1)
        self.rom2_button.clicked.connect(self._on_rom2)
        self.rom3_button.clicked.connect(self._on_rom3)
        self.rom4_button.clicked.connect(self._on_rom4)
        self.rom5_button.clicked.connect(self._on_rom5)
        self.rom6_button.clicked.connect(self._on_rom6)

    def on_close(self):
        for editor in self.dialogue_editors.values():
            editor.close()
        if self.chapter_editor:
            self.chapter_editor.close()

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

    def _on_spell_lists(self):
        self.main_window.open_node_by_id("spell_lists")

    def _on_tiles(self):
        self.main_window.open_node_by_id("tiles")

    def _on_rumors(self):
        self.main_window.open_node_by_id("rumors")

    def _on_subquests(self):
        self.main_window.open_node_by_id("subquests")

    def _on_food_preferences(self):
        self.main_window.open_node_by_id("food_preferences")

    def _on_portraits(self):
        self.main_window.open_node_by_id("facedata")

    def _on_rom0(self):
        self.main_window.open_node_by_id("rom0")

    def _on_rom1(self):
        self.main_window.open_node_by_id("rom1")

    def _on_rom2(self):
        self.main_window.open_node_by_id("rom2")

    def _on_rom3(self):
        self.main_window.open_node_by_id("rom3")

    def _on_rom4(self):
        self.main_window.open_node_by_id("rom4")

    def _on_rom5(self):
        self.main_window.open_node_by_id("rom5")

    def _on_rom6(self):
        self.main_window.open_node_by_id("rom6")

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
