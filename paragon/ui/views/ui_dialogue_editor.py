from PySide2 import QtGui
from PySide2.QtGui import QFont, QIcon
from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QPlainTextEdit,
    QVBoxLayout,
)

from paragon.ui.controllers.dialogue_player import DialoguePlayer


class Ui_DialogueEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.keys_box = QComboBox()
        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")
        self.rename_button = QPushButton("Rename")

        self.generic_layout = QHBoxLayout()
        self.generic_layout.addWidget(self.keys_box)
        self.generic_layout.addWidget(self.new_button)
        self.generic_layout.addWidget(self.delete_button)
        self.generic_layout.addWidget(self.rename_button)
        self.generic_layout.setStretch(0, 1)

        self.editor = QPlainTextEdit()
        editor_font = QFont()
        editor_font.setPointSize(11)  # TODO: Make this configurable
        self.editor.setFont(editor_font)

        editor_layout = QVBoxLayout()
        editor_layout.addLayout(self.generic_layout)
        editor_layout.addWidget(self.editor)
        editor_layout.setStretch(1, 1)

        self.player = DialoguePlayer()
        self.preview_button = QPushButton("Save / Preview")

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.player)
        left_layout.addWidget(self.preview_button)
        left_layout.setAlignment(QtGui.Qt.AlignCenter)
        left_layout.addStretch()
        left_layout.setStretch(2, 1)

        layout = QHBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(editor_layout)
        layout.setStretch(1, 1)
        self.setLayout(layout)
        self.resize(1000, 600)

        self.setWindowIcon(QIcon("paragon.ico"))
