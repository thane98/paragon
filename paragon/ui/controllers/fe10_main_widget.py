from paragon.ui.controllers.fe10_dialogue_editor import FE10DialogueEditor
from paragon.ui.controllers.fe10_script_editor import FE10ScriptEditor
from paragon.ui.controllers.layered_dir_editor import LayeredDirEditor
from paragon.ui.views.ui_fe10_main_widget import Ui_FE10MainWidget


class FE10MainWidget(Ui_FE10MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window

        self.script_editor = None
        self.dialogue_editor = None

        self.chapters_button.clicked.connect(lambda: self.main_window.open_node_by_id("chapters"))
        self.characters_button.clicked.connect(lambda: self.main_window.open_node_by_id("characters"))
        self.classes_button.clicked.connect(lambda: self.main_window.open_node_by_id("jobs"))
        self.items_button.clicked.connect(lambda: self.main_window.open_node_by_id("items"))
        self.skills_button.clicked.connect(lambda: self.main_window.open_node_by_id("skills"))
        self.armies_button.clicked.connect(lambda: self.main_window.open_node_by_id("groups"))
        self.tiles_button.clicked.connect(lambda: self.main_window.open_node_by_id("tiles"))
        self.supports_button.clicked.connect(lambda: self.main_window.open_node_by_id("main_support_table"))
        self.no_battle_button.clicked.connect(lambda: self.main_window.open_node_by_id("no_battle"))
        self.portraits_button.clicked.connect(lambda: self.main_window.open_node_by_id("facedata"))
        self.scripts_button.clicked.connect(self._on_scripts)
        self.dialogue_button.clicked.connect(self._on_dialogue)

    def on_close(self):
        if self.script_editor:
            self.script_editor.close()
        if self.dialogue_editor:
            self.dialogue_editor.close()

    def _on_scripts(self):
        if not self.script_editor:
            self.script_editor = FE10ScriptEditor(self.ms, self.gs)
        self.script_editor.show()

    def _on_dialogue(self):
        if not self.dialogue_editor:
            self.dialogue_editor = FE10DialogueEditor(self.ms, self.gs)
        self.dialogue_editor.show()
