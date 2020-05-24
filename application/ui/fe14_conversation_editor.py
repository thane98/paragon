from PySide2 import QtCore, QtGui
from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QIcon
from PySide2.QtWidgets import QTextEdit, QAction

from core.conversation import convert
from core.conversation.convert import paragon_to_commands, paragon_to_game
from model.message_archive import MessageArchive
from services.service_locator import locator
from ui.views.ui_fe14_conversation_editor import Ui_FE14ConversationEditor


class ParagonScriptHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text: str):
        if text.startswith("$") and not text.startswith("$G") and not text.startswith("$Nu"):
            command_format = QTextCharFormat()
            command_format.setForeground(QtCore.Qt.darkMagenta)
            self.setFormat(0, len(text), command_format)


class FE14ConversationEditor(Ui_FE14ConversationEditor):
    def __init__(self, archive: MessageArchive, title="Conversation Editor", owner=None, parent=None, is_support=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("paragon.ico"))
        self.archive = archive
        self.owner = owner
        self.editors = []
        self.highlighters = []
        self.keys = []

        if is_support:
            self.add_s_support_action = QAction(text="Add S Support")
            self.add_s_support_action.triggered.connect(self._on_add_s_support_activated)
            self.tool_bar.addAction(self.add_s_support_action)

        conversation_service = locator.get_scoped("ConversationService")
        self.avatar_name_editor.setText(conversation_service.get_avatar_name())
        self.avatar_is_female_check.setChecked(conversation_service.avatar_is_female())

        for key, value in self.archive.messages():
            self._create_tab(key, value)

        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.save_button.clicked.connect(self._on_save_pressed)
        self.preview_button.clicked.connect(self._on_preview_pressed)
        self.avatar_name_editor.editingFinished.connect(self._on_avatar_name_changed)
        self.avatar_is_female_check.stateChanged.connect(self._on_avatar_gender_changed)

    def _create_tab(self, key, value):
        paragon_script = convert.game_to_paragon(value)
        editor = QTextEdit()
        editor.setFontPointSize(10)
        highlighter = ParagonScriptHighlighter(editor.document())
        editor.setText(paragon_script)
        self.editors.append(editor)
        self.highlighters.append(highlighter)
        self.keys.append(key)
        self.tab_widget.addTab(editor, key)

    def closeEvent(self, event: QtGui.QCloseEvent):
        event.accept()
        if self.owner:
            self.owner.delete_conversation_editor(self)

    def _on_preview_pressed(self):
        self._on_save_pressed()
        paragon_script = self.editors[self.tab_widget.currentIndex()].document().toPlainText()
        commands = paragon_to_commands(paragon_script)
        self.player.set_commands(commands)

    def _on_save_pressed(self):
        paragon_script = self.editors[self.tab_widget.currentIndex()].document().toPlainText()
        game_script = paragon_to_game(paragon_script)
        self.archive.insert_or_overwrite_message(self.keys[self.tab_widget.currentIndex()], game_script)

    def _on_tab_changed(self, index: int):
        if not self.editors[index].isEnabled():
            self.preview_button.setEnabled(False)
            self.save_button.setEnabled(False)
        else:
            self.preview_button.setEnabled(True)
            self.save_button.setEnabled(True)

    def _on_avatar_name_changed(self):
        conversation_service = locator.get_scoped("ConversationService")
        conversation_service.set_avatar_name(self.avatar_name_editor.text())

    def _on_avatar_gender_changed(self, _):
        conversation_service = locator.get_scoped("ConversationService")
        conversation_service.set_avatar_is_female(self.avatar_is_female_check.isChecked())

    def _on_add_s_support_activated(self):
        for key in self.keys:
            if key.endswith("Ｓ"):
                return
        new_key = self.keys[0].replace("Ｃ", "Ｓ")
        self.archive.insert_or_overwrite_message(new_key, "")
        self._create_tab(new_key, "")
