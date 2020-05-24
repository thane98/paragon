from typing import Optional, List

from model.conversation.command import Command
from model.conversation.conversation_controller import ConversationController
from ui.error_dialog import ErrorDialog
from ui.views.ui_conversation_player import Ui_ConversationPlayer

_STR = (r"$a$t1$Wmアシュラ|7$w0|$Wsアシュラ|$Wa...$k\n$Wmusername|3$w0|$Wsusername|$WaAh. So this is where you've been "
        r"hiding.$k\n$Wsアシュラ|$Wa$GLord,Lady| $Nu.$k\n$Wsusername|$WaWhy are you way out here? You know that\neveryone "
        r"else eats in the mess hall, right?$k$pYou should come over and sup with us\nsometime.$k\n$Wsアシュラ|$Wa$E笑,"
        r"|I'm fine here, thank you.$k$pI appreciate your graciousness in allowing\nme to travel with you, "
        r"milady.$k$pBut as a former outlaw, I don't think I am\nfit to dine at your table.$k\n$Wsusername|$Wa$E怒,"
        r"|What? Of course you're fit to do so. And\nI'm sure the others would all agree.$k\n$Wsアシュラ|$Wa$E通常,"
        r"|That's very kind of you. Regardless, I would\nprefer to remain "
        r"alone.$k\n$Wsusername|$WaWhy?$k\n$Wsアシュラ|$WaIt is best I remain in the shadows as much\nas "
        r"possible.$k\n$Wsusername|$WaIn the shadows? What are you talking\nabout?$k\n$Wsアシュラ|$Wa$E苦,|My face is not "
        r"unknown. Many people\nrecognize me as an outlaw.$k$pIf it became widely known I was part of your\ngroup, "
        r"it would damage your good names.$k$pEven if the mess hall is not exactly public,\nit is still large, "
        r"and rumors spread.$k$pA soldier may write to their family, who\nwould then tell their village, "
        r"and so on.$k\n$Wsusername|$Wa$Eキメ,汗|I don't think—$k\n$Wsアシュラ|$WaYou cannot deny that the possibility "
        r"exists,\ncan you?$k$p$E通常,|I have no intention of allowing my presence\nto hurt your cause.$k$pPlease try "
        r"to understand.$k\n$Wsusername|$Wa$E通常,|Shura...$k\n$Wsアシュラ|$Wa$E笑,|Now, go rejoin your people. I am sure "
        r"they\nare missing you.$k\n$Wsusername|$WaA-all right. I will. Good day.$k\n$Wsアシュラ|$Wa$E笑,|Good day, "
        r"milady.$k")


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
        while self.position < len(self.commands) and not self.commands[self.position].is_pause():
            try:
                self.commands[self.position].run(self.conversation_controller)
            except Exception as e:
                self.error_dialog = ErrorDialog("An error occured during interpreting - " + str(e))
                self.error_dialog.show()
                self.clear()
            self.position += 1
        self.conversation_controller.dump()
        self.position += 1
        self.next_button.setEnabled(self.position < len(self.commands))

    def _replay(self):
        self.conversation_controller.reset()
        self.position = 0
        self._play_next()
