import logging

from PySide6.QtWidgets import QInputDialog
from paragon.ui import utils

from paragon.model.game import Game
from paragon.ui.controllers.auto.fe15_dungeon_editor import FE15DungeonEditor
from paragon.ui.controllers.chapter_editor import ChapterEditor
from paragon.ui.controllers.exalt_script_editor import ExaltScriptEditor
from paragon.ui.controllers.quick_dialogue_generator import QuickDialogueGenerator
from paragon.ui.controllers.dialogue_editor import DialogueEditor
from paragon.ui.controllers.store_manager import StoreManager
from paragon.ui.views.ui_fe15_main_widget import Ui_FE15MainWidget


class FE15MainWidget(Ui_FE15MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window
        self.chapter_editor = None
        self.dungeon_editor = None
        self.quick_dialogue_dialog = None
        self.store_manager = None
        self.script_editor = ExaltScriptEditor(ms, gs.data)

        self.dialogue_editors = {}

        self.chapters_button.clicked.connect(self._on_chapters)
        self.dungeons_button.clicked.connect(self._on_dungeons)
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
        self.scripts_button.clicked.connect(self._on_scripts)
        self.quick_dialogue_button.clicked.connect(self._on_quick_dialogue)
        self.store_manager_button.clicked.connect(self._on_store_manager)

    def on_close(self):
        for editor in self.dialogue_editors.values():
            editor.close()
        if self.chapter_editor:
            self.chapter_editor.close()
        if self.dungeon_editor:
            self.dungeon_editor.close()
        if self.quick_dialogue_dialog:
            self.quick_dialogue_dialog.close()
        if self.store_manager:
            self.store_manager.close()
        self.script_editor.close()

    def process_compile_result(self, compile_result) -> bool:
        self.script_editor.process_compile_result(compile_result)
        return self.script_editor.has_errors()

    def _on_store_manager(self):
        if not self.store_manager:
            self.store_manager = StoreManager(self.ms, self.gs)
        self.store_manager.show()

    def _on_quick_dialogue(self):
        if not self.quick_dialogue_dialog:
            self.quick_dialogue_dialog = QuickDialogueGenerator(self.ms, self.gs)
        self.quick_dialogue_dialog.show()

    def _on_chapters(self):
        try:
            if self.chapter_editor:
                self.chapter_editor.show()
            else:
                self.chapter_editor = ChapterEditor(
                    self.ms, self.gs, self.script_editor.model.sourceModel()
                )
                self.chapter_editor.show()
        except:
            logging.exception("Failed to create FE15 chapter editor.")
            utils.error(self)

    def _on_dungeons(self):
        try:
            if self.dungeon_editor:
                self.dungeon_editor.show()
            else:
                self.dungeon_editor = FE15DungeonEditor(self.gs, self.ms)
                self.dungeon_editor.show()
        except:
            logging.exception("Failed to create FE15 dungeon editor.")
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

    def _on_scripts(self):
        self.script_editor.show()

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
