import logging
from typing import Optional

from PySide6.QtWidgets import QPushButton

from paragon.model.game import Game
from paragon.ui import utils
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.controllers.dialogue_editor import DialogueEditor


class FE15BaseConversationButton(AbstractAutoWidget, QPushButton):
    def __init__(self, state):
        AbstractAutoWidget.__init__(self, state)
        QPushButton.__init__(self, "Open Base Conversations")

        self.rid = None
        self.editors = {}

        self.clicked.connect(self._on_clicked)

    def set_target(self, rid):
        self.rid = rid

    def _on_clicked(self):
        if not self.rid:
            return None
        pid = self.data.key(self.rid)
        if not pid or not pid.startswith("PID_"):
            utils.info("Cannot open base conversations without a valid PID.", "Bad PID")
            return
        part = pid[4:]
        try:
            path = self._get_archive(part)
            if path in self.editors:
                self.editors[path].show()
                return
            editor = DialogueEditor(
                self.data, self.gs.dialogue, self.gs.sprite_animation, Game.FE15
            )
            editor.set_archive(path, True)
            self.editors[path] = editor
            editor.show()
        except:
            logging.exception("Failed to open base conversations.")
            utils.error(self)

    def _get_archive(self, part) -> Optional[str]:
        if not self.rid:
            return None
        path = f"m/拠点会話_{part}.bin.lz"
        if not self.data.file_exists(path, True):
            self.data.new_text_data(path, True)
        return path
