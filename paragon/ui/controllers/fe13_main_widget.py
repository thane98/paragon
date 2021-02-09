from PySide2.QtWidgets import QInputDialog
from paragon.model.game import Game

from paragon.ui.controllers.dialogue_editor import DialogueEditor
from paragon.ui.views.ui_fe13_main_widget import Ui_FE13MainWidget


class FE13MainWidget(Ui_FE13MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window

        self.dialogue_editors = {}

        self.characters_button.clicked.connect(self._on_characters)
        self.items_button.clicked.connect(self._on_items)
        self.skills_button.clicked.connect(self._on_skills)
        self.classes_button.clicked.connect(self._on_classes)
        self.armies_button.clicked.connect(self._on_armies)
        self.tiles_button.clicked.connect(self._on_tiles)
        self.asset_definitions_button.clicked.connect(self._on_asset_definitions)
        self.presets_button.clicked.connect(self._on_presets)
        self.portraits_button.clicked.connect(self._on_portraits)
        self.sound_sets_button.clicked.connect(self._on_sound_sets)
        self.sound_parameters_button.clicked.connect(self._on_sound_parameters)
        self.edit_dialogue_button.clicked.connect(self._on_edit_dialogue)

    def _on_characters(self):
        self.main_window.open_node_by_id("characters")

    def _on_items(self):
        self.main_window.open_node_by_id("items")

    def _on_skills(self):
        self.main_window.open_node_by_id("skills")

    def _on_classes(self):
        self.main_window.open_node_by_id("classes")

    def _on_armies(self):
        self.main_window.open_node_by_id("belong")

    def _on_tiles(self):
        self.main_window.open_node_by_id("tiles")

    def _on_asset_definitions(self):
        self.main_window.open_node_by_id("asset_definitions")

    def _on_presets(self):
        self.main_window.open_node_by_id("preset_asset_definitions")

    def _on_portraits(self):
        self.main_window.open_node_by_id("facedata")

    def _on_sound_sets(self):
        self.main_window.open_node_by_id("sound_sets")

    def _on_sound_parameters(self):
        self.main_window.open_node_by_id("sound_parameters")

    def _on_edit_dialogue(self):
        choices = self.gs.data.enumerate_text_archives()
        choice, ok = QInputDialog.getItem(self, "Select Text", "Path", choices, 0)
        if ok:
            if choice in self.dialogue_editors:
                self.dialogue_editors[choice].show()
            else:
                editor = DialogueEditor(self.gs.data, self.gs.dialogue, Game.FE13)
                editor.set_archive(choice, False)
                self.dialogue_editors[choice] = editor
                editor.show()
