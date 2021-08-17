import os

from paragon.ui.controllers.layered_dir_editor import LayeredDirEditor


class FE10ScriptEditor(LayeredDirEditor):
    def _get_initial_model_items(self):
        scripts = self.gs.data.list_files("Scripts", "*.cmb", False)
        return list(map(lambda p: os.path.basename(p), scripts))

    def _get_window_title(self):
        return "Paragon - Script Editor"

    def _load_file(self, path):
        return ["PLACEHOLDER"]

    def _load_entry(self, path, entry):
        return self.gd.open_script(os.path.join("Scripts", path))

    def _save(self, path, entry, text):
        # TODO: Can we validate the syntax before writing this back?
        self.gd.set_script(os.path.join("Scripts", path), text)
