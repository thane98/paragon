import logging

from PySide2.QtWidgets import QInputDialog

from paragon.model.game import Game
from paragon.ui import utils
from paragon.ui.controllers.chapter_editor import ChapterEditor
from paragon.ui.controllers.dialogue_editor import DialogueEditor
from paragon.ui.controllers.fe14_avatar_config_window import FE14AvatarConfigWindow
from paragon.ui.controllers.fe14_field_editor import FE14FieldEditor
from paragon.ui.controllers.quick_dialogue_generator import QuickDialogueGenerator
from paragon.ui.views.ui_fe14_main_widget import Ui_FE14MainWidget


class FE14MainWidget(Ui_FE14MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window
        self.chapter_editor = None
        self.avatar_editor = None
        self.quick_dialogue_dialog = None

        self.field_editors = {}
        self.dialogue_editors = {}

        self.chapters_button.clicked.connect(self._on_chapters)
        self.characters_button.clicked.connect(self._on_characters)
        self.items_button.clicked.connect(self._on_items)
        self.classes_button.clicked.connect(self._on_classes)
        self.skills_button.clicked.connect(self._on_skills)
        self.forge_button.clicked.connect(self._on_forge)
        self.armies_button.clicked.connect(self._on_armies)
        self.weapon_bonuses_button.clicked.connect(self._on_weapon_bonuses)
        self.weapon_interactions_button.clicked.connect(self._on_weapon_interactions)
        self.weapon_ranks_button.clicked.connect(self._on_weapon_ranks)
        self.move_costs_button.clicked.connect(self._on_move_costs)
        self.path_bonuses_button.clicked.connect(self._on_path_bonuses)
        self.visit_bonuses_button.clicked.connect(self._on_visit_bonuses)
        self.battle_bonuses_button.clicked.connect(self._on_battle_bonuses)
        self.accessories_button.clicked.connect(self._on_accessories)
        self.buildings_button.clicked.connect(self._on_buildings)
        self.init_buildings_button.clicked.connect(self._on_init_buildings)
        self.castle_recruitment_button.clicked.connect(self._on_castle_recruitment)
        self.butlers_button.clicked.connect(self._on_butlers)
        self.butler_voice_button.clicked.connect(lambda: self.main_window.open_node_by_id("castle_butler_voice"))
        self.arena_combatants_low_button.clicked.connect(self._on_arena_combatants_low)
        self.arena_combatants_high_button.clicked.connect(self._on_arena_combatants_high)
        self.castle_position_button.clicked.connect(lambda: self.main_window.open_node_by_id("castle_position"))
        self.dining_data_title_button.clicked.connect(lambda: self.main_window.open_node_by_id("dining_data_title"))
        self.dining_data_cooking_button.clicked.connect(lambda: self.main_window.open_node_by_id("dining_data_cooking"))
        self.animation_sets_button.clicked.connect(lambda: self.main_window.open_node_by_id("aset"))
        self.cameras_button.clicked.connect(self._on_cameras)
        self.effects_button.clicked.connect(self._on_effects)
        self.ground_attributes_button.clicked.connect(self._on_ground_attributes)
        self.portraits_button.clicked.connect(self._on_portraits)
        self.field_button.clicked.connect(self._on_field)
        self.rom0_button.clicked.connect(self._on_rom0)
        self.rom1_button.clicked.connect(self._on_rom1)
        self.rom2_button.clicked.connect(self._on_rom2)
        self.rom3_button.clicked.connect(self._on_rom3)
        self.rom4_button.clicked.connect(self._on_rom4)
        self.rom5_button.clicked.connect(self._on_rom5)
        self.rom6_button.clicked.connect(self._on_rom6)
        self.sound_sets_button.clicked.connect(self._on_sound_sets)
        self.multi_sound_sets_button.clicked.connect(self._on_multi_sound_sets)
        self.sound_parameters_button.clicked.connect(self._on_sound_parameters)
        self.support_music_button.clicked.connect(self._on_support_music)
        self.edit_dialogue_button.clicked.connect(self._on_edit_dialogue)
        self.configure_avatar_button.clicked.connect(self._on_configure_avatar)
        self.quick_dialogue_button.clicked.connect(self._on_quick_dialogue)

    def on_close(self):
        for editor in self.dialogue_editors.values():
            editor.close()
        for editor in self.field_editors.values():
            editor.close()
        if self.chapter_editor:
            self.chapter_editor.close()
        if self.avatar_editor:
            self.avatar_editor.close()
        if self.quick_dialogue_dialog:
            self.quick_dialogue_dialog.close()

    def _on_quick_dialogue(self):
        if not self.quick_dialogue_dialog:
            self.quick_dialogue_dialog = QuickDialogueGenerator(self.gs)
        self.quick_dialogue_dialog.show()

    def _on_chapters(self):
        try:
            if self.chapter_editor:
                self.chapter_editor.show()
            else:
                self.gs.data.set_store_dirty("gamedata", True)
                self.chapter_editor = ChapterEditor(self.ms, self.gs)
                self.chapter_editor.show()
        except:
            logging.exception("Failed to create FE14 chapter editor.")
            utils.error(self)

    def _on_field(self):
        try:
            keys = self.gs.data.multi_keys("field_files")
            choice, ok = QInputDialog.getItem(self, "Select File", "File", keys, -1)
            if not ok:
                return
            if choice in self.field_editors:
                self.field_editors[choice].show()
            else:
                self.field_editors[choice] = FE14FieldEditor(self.ms, self.gs, choice)
                self.field_editors[choice].show()
        except:
            logging.exception("Failed to create FE14 field editor.")
            utils.error(self)

    def _on_characters(self):
        self.main_window.open_node_by_id("characters")

    def _on_items(self):
        self.main_window.open_node_by_id("items")

    def _on_classes(self):
        self.main_window.open_node_by_id("classes")

    def _on_skills(self):
        self.main_window.open_node_by_id("skills")

    def _on_forge(self):
        self.main_window.open_node_by_id("forge")

    def _on_armies(self):
        self.main_window.open_node_by_id("belong")

    def _on_weapon_bonuses(self):
        self.main_window.open_node_by_id("weapon_bonuses")

    def _on_weapon_interactions(self):
        self.main_window.open_node_by_id("weapon_interactions")

    def _on_weapon_ranks(self):
        self.main_window.open_node_by_id("weapon_ranks")

    def _on_move_costs(self):
        self.main_window.open_node_by_id("move_costs")

    def _on_path_bonuses(self):
        self.main_window.open_node_by_id("path_bonuses")

    def _on_visit_bonuses(self):
        self.main_window.open_node_by_id("visit_bonuses")

    def _on_battle_bonuses(self):
        self.main_window.open_node_by_id("battle_bonuses")

    def _on_accessories(self):
        self.main_window.open_node_by_id("accessories")

    def _on_buildings(self):
        self.main_window.open_node_by_id("castle_buildings")

    def _on_init_buildings(self):
        self.main_window.open_node_by_id("castle_init_buildings")

    def _on_castle_recruitment(self):
        self.main_window.open_node_by_id("castle_join")

    def _on_butlers(self):
        self.main_window.open_node_by_id("butlers")

    def _on_arena_combatants_low(self):
        self.main_window.open_node_by_id("arena_low")

    def _on_arena_combatants_high(self):
        self.main_window.open_node_by_id("arena_high")

    def _on_cameras(self):
        self.main_window.open_node_by_id("cameras")

    def _on_effects(self):
        self.main_window.open_node_by_id("game_effects")

    def _on_ground_attributes(self):
        self.main_window.open_node_by_id("ground_attributes")

    def _on_portraits(self):
        self.main_window.open_node_by_id("portraits")

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

    def _on_sound_sets(self):
        self.main_window.open_node_by_id("sound_sets")

    def _on_multi_sound_sets(self):
        self.main_window.open_node_by_id("multi_sound_sets")

    def _on_sound_parameters(self):
        self.main_window.open_node_by_id("sound_parameters")

    def _on_support_music(self):
        self.main_window.open_node_by_id("support_music")

    def _on_edit_dialogue(self):
        choices = self.gs.data.enumerate_text_archives()
        choice, ok = QInputDialog.getItem(self, "Select Text", "Path", choices, 0)
        if ok:
            if choice in self.dialogue_editors:
                self.dialogue_editors[choice].show()
            else:
                editor = DialogueEditor(
                    self.gs.data, self.gs.dialogue, self.gs.sprite_animation, Game.FE14
                )
                editor.set_archive(choice, False)
                self.dialogue_editors[choice] = editor
                editor.show()

    def _on_configure_avatar(self):
        if not self.avatar_editor:
            self.avatar_editor = FE14AvatarConfigWindow(self.ms, self.gs)
        self.avatar_editor.show()
