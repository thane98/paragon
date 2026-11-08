import os

from paragon.ui.controllers.layered_dir_editor import LayeredDirEditor
from paragon.core.dialogue.fe10_script_parser import Fe10ScriptParser 
from paragon.ui.misc.fe10_dialogue_highlighter import FE10DialogueHighlighter

class FE10DialogueEditor(LayeredDirEditor):
    def __init__(self, ms, gs):
        super().__init__(ms, gs, True)
        
        self.highlighter = FE10DialogueHighlighter(self.editor.document())

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

    def verify_convert_accuracy(self, message):
        converted = Fe10ScriptParser().convert_raw_message_to_pretty(message)
        reconverted = Fe10ScriptParser().convert_pretty_to_raw_message(converted)
        return message == reconverted

    def _load_entry(self, path, entry):
        path = os.path.join("Mess", path)
        message = self.gd.message(path, False, entry)
        if message:
            for i in range(0, 0x12):
                message = message.replace(chr(i), f"$({i})")
        message = Fe10ScriptParser().convert_raw_message_to_pretty(message)
        
        return message

    def _save(self, path, entry, text):
        path = os.path.join("Mess", path)
        text = Fe10ScriptParser().convert_pretty_to_raw_message(text)
        for i in range(0, 0x12):
            text = text.replace(f"$({i})", chr(i))
        self.gd.set_message(path, False, entry, text)

    def _add(self, path, key):
        path = os.path.join("Mess", path)
        self.gd.set_message(path, False, key, "Placeholder")

    def _delete(self, path, key):
        path = os.path.join("Mess", path)
        self.gd.set_message(path, False, key, None)
