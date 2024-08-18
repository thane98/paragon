import os

from paragon.ui.controllers.layered_dir_editor import LayeredDirEditor


class FE10DialogueEditor(LayeredDirEditor):
    def __init__(self, ms, gs):
        super().__init__(ms, gs, True)

    def _get_initial_model_items(self):
        files = self.gd.list_files("Mess", "*.m", False)
        return list(map(lambda p: os.path.basename(p), files))

    def _get_window_title(self):
        return "Paragon - Raw Dialogue Editor"

    def _load_file(self, path):
        path = os.path.join("Mess", path)
        self.gd.open_text_data(path, False)
        messages = self.gd.enumerate_messages(path, False)
        return messages

    def _load_entry(self, path, entry):
        path = os.path.join("Mess", path)
        message = self.gd.message(path, False, entry)
        if message:
            for i in range(0, 0x12):
                message = message.replace(chr(i), f"$({i})")
            message = message.replace("\\n", "\n")
        return message

    def _save(self, path, entry, text):
        path = os.path.join("Mess", path)
        text = text.replace("\n", "\\n")
        for i in range(0, 0x12):
            text = text.replace(f"$({i})", chr(i))
        self.gd.set_message(path, False, entry, text)

    def _add(self, path, key):
        path = os.path.join("Mess", path)
        self.gd.set_message(path, False, key, "Placeholder")

    def _delete(self, path, key):
        path = os.path.join("Mess", path)
        self.gd.set_message(path, False, key, None)
