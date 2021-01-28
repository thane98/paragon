from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import QFrame, QFormLayout, QLineEdit, QCheckBox, QMainWindow, QHBoxLayout, QPushButton, \
    QVBoxLayout, QTabWidget, QStatusBar, QWidget, QToolBar, QListView, QTextEdit, QCompleter, QToolTip

from ui.widgets.fe14_conversation_player import FE14ConversationPlayer
from ui.widgets.conversation_text_editor import ConversationTextEdit
# Need
from ui.misc.conversation_completer import ParagonConversationCompleter
import json

# Just for dirty PoC
from services.service_locator import locator


class Ui_FE14ConversationEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = FE14ConversationPlayer()
        self.visual_splitter_1 = QFrame()
        self.visual_splitter_1.setFrameShape(QFrame.HLine)
        self.visual_splitter_1.setFrameShadow(QFrame.Sunken)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setAlignment(QtGui.Qt.AlignCenter)
        self.save_button = QPushButton(text="Save")
        self.preview_button = QPushButton("Preview")
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.preview_button)
        self.visual_splitter_2 = QFrame()
        self.visual_splitter_2.setFrameShape(QFrame.HLine)
        self.visual_splitter_2.setFrameShadow(QFrame.Sunken)

        self.avatar_form = QFormLayout()
        self.avatar_name_editor = QLineEdit()
        self.avatar_is_female_check = QCheckBox()
        self.avatar_form.addRow("Avatar Name", self.avatar_name_editor)
        self.avatar_form.addRow("Avatar Is Female", self.avatar_is_female_check)

        self.visual_splitter_3 = QFrame()
        self.visual_splitter_3.setFrameShape(QFrame.HLine)
        self.visual_splitter_3.setFrameShadow(QFrame.Sunken)

        self.conversation_list = QListView()

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.player)
        self.left_layout.addWidget(self.visual_splitter_1)
        self.left_layout.addLayout(self.buttons_layout)
        self.left_layout.addWidget(self.visual_splitter_2)
        self.left_layout.addLayout(self.avatar_form)
        self.left_layout.addWidget(self.visual_splitter_3)
        self.left_layout.addWidget(self.conversation_list)
        self.left_layout.setStretch(0, 0)
        self.left_layout.setStretch(1, 0)
        self.left_layout.setStretch(2, 0)
        self.left_layout.setStretch(3, 0)
        self.left_layout.setStretch(4, 0)
        self.left_layout.setStretch(5, 0)
        self.left_layout.setStretch(6, 1)

        self.text_area = FE14ConversationTextEdit()

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addWidget(self.text_area)
        self.main_layout.setStretch(0, 0)
        self.main_layout.setStretch(1, 1)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.tool_bar = QToolBar()
        self.addToolBar(self.tool_bar)
        self.setCentralWidget(self.central_widget)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.resize(900, 500)


class FE14ConversationTextEdit(ConversationTextEdit):
    def __init__(self, parent=None):
        super(FE14ConversationTextEdit, self).__init__(parent)

        self._completer = ParagonConversationCompleter([])
        with open("Modules/ServiceData/FE14ConversationCommands.json", "r") as f:
            self._command_hints = json.load(f)

    # Called when completer is set
    def _initialize_lists(self):
        # Create list
        character_list = list()
        module: TableModule = locator.get_scoped("ModuleService").get_module("Characters")
        for x in module.children():
            character_list.append(x[1])

        # Create list from module data
        for item in self._command_hints:
            self._command_list.append(item['Command'])

        self._character_list = character_list

        # Set the initial list
        self._set_list(self._command_list)

    # Called when command is found
    # Define what lists to show based on corresponding args
    # Args are defined in module data
    def _command_args(self, args: str):
        if args == "Character":
            self._set_list(self._character_list)
