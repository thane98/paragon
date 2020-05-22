from PySide2 import QtGui
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout

from ui.widgets.fe14_conversation_widget import FE14ConversationWidget


class Ui_ConversationPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_widget = FE14ConversationWidget()
        self.replay_button = QPushButton(text="Replay")
        self.next_button = QPushButton(text="Next")
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.replay_button)
        self.buttons_layout.addWidget(self.next_button)
        self.buttons_layout.setAlignment(QtGui.Qt.AlignCenter)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.conversation_widget)
        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)
