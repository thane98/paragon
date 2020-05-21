from typing import List

from model.conversation.command import *
from model.conversation.conversation_controller import ConversationController
from ui.views.ui_conversation_player import Ui_ConversationPlayer


class FE14ConversationPlayer(Ui_ConversationPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_controller = ConversationController(self.conversation_widget)
        self.replay_button.clicked.connect(self._replay)
        self.next_button.clicked.connect(self._play_next)
        self.position = 0
        self.commands: List[Command] = [
            PlayerMentionedCommand(),
            SetConversationTypeCommand(1),
            LoadPortraitsCommand("フローラ"),
            SetPortraitPositionCommand(3),
            SetNameCommand("フローラ"),
            SetEmotionCommand("笑"),
            PrintCommand("This is a test message."),
            PlayMessageCommand(),
            PauseCommand(),
            LoadPortraitsCommand("マークス"),
            SetPortraitPositionCommand(7),
            SetNameCommand("マークス"),
            PrintCommand("Here's another one."),
            PlayMessageCommand(),
            PauseCommand(),
            LoadPortraitsCommand("フローラ"),
            SetPortraitPositionCommand(3),
            SetNameCommand("フローラ"),
            PrintCommand("My rebuttal."),
            PlayMessageCommand(),
            PauseCommand()
        ]
        self._play_next()

    def _play_next(self):
        while not isinstance(self.commands[self.position], PauseCommand):
            self.commands[self.position].run(self.conversation_controller)
            self.position += 1
        self.position += 1
        self.next_button.setEnabled(self.position < len(self.commands))

    def _replay(self):
        self.conversation_widget.clear()
        self.position = 0
        self._play_next()
