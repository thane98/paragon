from core.conversation.game_script_scanner import GameScriptScanner
from model.conversation.conversation_controller import ConversationController
from ui.views.ui_conversation_player import Ui_ConversationPlayer


class FE14ConversationPlayer(Ui_ConversationPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_controller = ConversationController(self.conversation_widget)
        self.replay_button.clicked.connect(self._replay)
        self.next_button.clicked.connect(self._play_next)
        self.position = 0
        scanner = GameScriptScanner()
        self.commands = scanner.scan(r"")

        self._play_next()

    def _play_next(self):
        while self.position < len(self.commands) and not self.commands[self.position].is_pause():
            self.commands[self.position].run(self.conversation_controller)
            self.position += 1
        self.position += 1
        self.next_button.setEnabled(self.position < len(self.commands))

    def _replay(self):
        self.conversation_controller.reset()
        self.position = 0
        self._play_next()
