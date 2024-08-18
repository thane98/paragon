from paragon.ui.controllers.exalt_script_editor import ExaltScriptEditor
from paragon.ui.controllers.fe10_dialogue_editor import FE10DialogueEditor
from paragon.ui.controllers.gcn_top_level_map_editor import GcnTopLevelMapEditor
from paragon.ui.controllers.store_manager import StoreManager
from paragon.ui.views.ui_fe9_main_widget import Ui_FE9MainWidget


class FE9MainWidget(Ui_FE9MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window

        self.map_editor = None
        self.script_editor = None
        self.dialogue_editor = None
        self.store_manager = None

        self.maps_button.clicked.connect(self._on_maps)
        self.chapters_button.clicked.connect(
            lambda: self.main_window.open_node_by_id("chapters")
        )
        self.characters_button.clicked.connect(
            lambda: self.main_window.open_node_by_id("characters")
        )
        self.classes_button.clicked.connect(
            lambda: self.main_window.open_node_by_id("jobs")
        )
        self.items_button.clicked.connect(
            lambda: self.main_window.open_node_by_id("items")
        )
        self.skills_button.clicked.connect(
            lambda: self.main_window.open_node_by_id("skills")
        )
        self.armies_button.clicked.connect(
            lambda: self.main_window.open_node_by_id("groups")
        )
        self.tiles_button.clicked.connect(
            lambda: self.main_window.open_node_by_id("terrain_data")
        )
        self.supports_button.clicked.connect(
            lambda: self.main_window.open_node_by_id("supports")
        )
        self.portraits_button.clicked.connect(
            lambda: self.main_window.open_node_by_id("facedata")
        )
        self.scripts_button.clicked.connect(self._on_scripts)
        self.raw_dialogue_button.clicked.connect(self._on_dialogue)
        self.store_manager_button.clicked.connect(self._on_store_manager)

    def on_close(self):
        if self.script_editor:
            self.script_editor.close()
        if self.store_manager:
            self.store_manager.close()
        if self.dialogue_editor:
            self.dialogue_editor.close()

    def process_compile_result(self, compile_result) -> bool:
        if self.script_editor:
            self.script_editor.process_compile_result(compile_result)
            return self.script_editor.has_errors()
        else:
            return False

    def _on_maps(self):
        if not self.map_editor:
            self.map_editor = GcnTopLevelMapEditor(self.ms, self.gs)
        self.map_editor.show()

    def _on_scripts(self):
        if not self.script_editor:
            self.script_editor = ExaltScriptEditor(self.ms, self.gs.data)
        self.script_editor.show()

    def _on_dialogue(self):
        if not self.dialogue_editor:
            self.dialogue_editor = FE10DialogueEditor(self.ms, self.gs)
        self.dialogue_editor.show()

    def _on_store_manager(self):
        if not self.store_manager:
            self.store_manager = StoreManager(self.ms, self.gs)
        self.store_manager.show()
