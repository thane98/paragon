from typing import Optional, List

from model.conversation.command import Command
from model.conversation.conversation_controller import ConversationController
from ui.error_dialog import ErrorDialog
from ui.views.ui_conversation_player import Ui_ConversationPlayer


class FE14ConversationPlayer(Ui_ConversationPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_controller = ConversationController(self.conversation_widget)
        self.replay_button.clicked.connect(self._replay)
        self.next_button.clicked.connect(self._play_next)
        self.position = 0
        self.commands: Optional[List[Command]] = None
        self.error_dialog = None
        self.clear()

    def set_commands(self, commands: Optional[List[Command]]):
        self.clear()
        self.commands = commands
        if self.commands:
            self.next_button.setEnabled(True)
            self.replay_button.setEnabled(True)
            self._replay()

    def clear(self):
        self.commands = None
        self.conversation_controller.reset()
        self.position = 0
        self.next_button.setEnabled(False)
        self.replay_button.setEnabled(False)

    def _play_next(self):
        while self.commands and self.position < len(self.commands) and not self.commands[self.position].is_pause():
            try:
                self.commands[self.position].run(self.conversation_controller)
            except Exception as e:
                self.error_dialog = ErrorDialog("An error occured during interpreting - " + str(e))
                self.error_dialog.show()
                self.clear()
            self.position += 1
        self.conversation_controller.dump()
        self.position += 1
        self.next_button.setEnabled(self.commands and self.position < len(self.commands))

    def _replay(self):
        self.conversation_controller.reset()
        self.position = 0
        self._play_next()
