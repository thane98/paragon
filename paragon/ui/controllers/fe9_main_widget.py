from paragon.ui.controllers.exalt_script_editor import ExaltScriptEditor
from paragon.ui.controllers.store_manager import StoreManager
from paragon.ui.views.ui_fe9_main_widget import Ui_FE9MainWidget


class FE9MainWidget(Ui_FE9MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window

        self.script_editor = None
        self.store_manager = None

        self.scripts_button.clicked.connect(self._on_scripts)
        self.store_manager_button.clicked.connect(self._on_store_manager)

    def on_close(self):
        if self.script_editor:
            self.script_editor.close()
        if self.store_manager:
            self.store_manager.close()

    def _on_scripts(self):
        if not self.script_editor:
            self.script_editor = ExaltScriptEditor(self.ms, self.gs.data)
        self.script_editor.show()

    def _on_store_manager(self):
        if not self.store_manager:
            self.store_manager = StoreManager(self.ms, self.gs)
        self.store_manager.show()
