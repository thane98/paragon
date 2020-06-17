import logging
from typing import Optional

from PySide2 import QtCore, QtGui
from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QIcon, QTextCursor
from PySide2.QtWidgets import QTextEdit, QAction, QInputDialog, QMessageBox

from core.conversation import convert
from core.conversation.convert import paragon_to_commands, paragon_to_game, commands_to_game
from model.conversation.transpiler_error import TranspilerError
from model.message_archive import MessageArchive
from services.service_locator import locator
from ui.views.ui_fe14_conversation_editor import Ui_FE14ConversationEditor


class ParagonScriptHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.error_line = None
        self.command_format = QTextCharFormat()
        self.command_format.setForeground(QtCore.Qt.darkMagenta)
        self.error_format = QTextCharFormat()
        self.error_format.setUnderlineColor(QtCore.Qt.darkRed)
        self.error_format.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
        self.error_format.setBackground(QtCore.Qt.red)

    def highlightBlock(self, text: str):
        if text.startswith("$") and not text.startswith("$G") and not text.startswith("$Nu"):
            self.setFormat(0, len(text), self.command_format)
        if self.currentBlock().blockNumber() == self.error_line:
            self.setFormat(0, len(text), self.error_format)


class FE14ConversationEditor(Ui_FE14ConversationEditor):
    def __init__(self, archive: MessageArchive = None, title="Conversation Editor",
                 owner=None, parent=None, is_support=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("paragon.ico"))
        self.archive = archive
        self.owner = owner
        self.editors = []
        self.highlighters = []
        self.keys = []

        self.key_not_unique_dialog = self._create_key_not_unique_dialog()

        self.add_s_support_action = QAction(text="Add S Support")
        self.add_s_support_action.triggered.connect(self._on_add_s_support_activated)
        self.add_action = QAction(text="Add")
        self.add_action.triggered.connect(self._on_add_pressed)
        self.remove_action = QAction(text="Remove")
        self.remove_action.triggered.connect(self._on_remove_pressed)
        self.rename_action = QAction(text="Rename")
        self.rename_action.triggered.connect(self._on_rename_pressed)
        if is_support:
            self.tool_bar.addAction(self.add_s_support_action)
        else:
            self.tool_bar.addActions([self.add_action, self.remove_action, self.rename_action])

        self.set_archive(archive)

        conversation_service = locator.get_scoped("ConversationService")
        self.avatar_name_editor.setText(conversation_service.get_avatar_name())
        self.avatar_is_female_check.setChecked(conversation_service.avatar_is_female())

        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.save_button.clicked.connect(self._on_save_pressed)
        self.preview_button.clicked.connect(self._on_preview_pressed)
        self.avatar_name_editor.editingFinished.connect(self._on_avatar_name_changed)
        self.avatar_is_female_check.stateChanged.connect(self._on_avatar_gender_changed)

    @staticmethod
    def _create_key_not_unique_dialog():
        dialog = QMessageBox()
        dialog.setText("The chosen key is not unique.")
        dialog.setWindowTitle("Paragon")
        dialog.setWindowIcon(QIcon("paragon.ico"))
        return dialog

    def set_archive(self, archive: Optional[MessageArchive]):
        self.clear()
        self.archive = archive
        if self.archive:
            self.setEnabled(True)
            for key, value in self.archive.messages():
                self._create_tab(key, value)
        else:
            self.setEnabled(False)

    def clear(self):
        self.editors.clear()
        self.keys.clear()
        self.highlighters.clear()
        self.tab_widget.clear()
        self.player.clear()
        self.archive = None

    def _create_tab(self, key, value):
        try:
            paragon_script = convert.game_to_paragon(value)
        except:
            logging.exception("Failed to decompile game script.")
            return
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

    def _on_tab_changed(self, index: int):
        valid = self.archive and index in range(0, len(self.editors))
        self.rename_action.setEnabled(valid)
        self.remove_action.setEnabled(valid)
        self.preview_button.setEnabled(valid)
        self.save_button.setEnabled(valid)

    def _on_preview_pressed(self):
        current_index = self.tab_widget.currentIndex()
        try:
            paragon_script = self.editors[current_index].document().toPlainText()
            commands = paragon_to_commands(paragon_script)
            game_script = commands_to_game(commands)
            self.archive.insert_or_overwrite_message(self.keys[self.tab_widget.currentIndex()], game_script)
            self.statusBar().showMessage("Transpiling for %s succeeded!" % self.keys[current_index])

            self.player.set_commands(commands)
            self.highlighters[current_index].error_line = None
            self.highlighters[current_index].rehighlight()
        except TranspilerError as e:
            self._update_ui_for_error(e, current_index)

    def _on_save_pressed(self):
        current_index = self.tab_widget.currentIndex()
        try:
            paragon_script = self.editors[self.tab_widget.currentIndex()].document().toPlainText()
            game_script = paragon_to_game(paragon_script)
            self.archive.insert_or_overwrite_message(self.keys[self.tab_widget.currentIndex()], game_script)
            self.statusBar().showMessage("Transpiling for %s succeeded!" % self.keys[current_index])
            self.highlighters[current_index].error_line = None
            self.highlighters[current_index].rehighlight()
        except TranspilerError as e:
            self._update_ui_for_error(e, current_index)

    def _update_ui_for_error(self, error: TranspilerError, editor_index: int):
        self.statusBar().showMessage(str(error))
        self.player.clear()
        line_number = error.source_position.line_number - 1
        editor: QTextEdit = self.editors[editor_index]
        block = editor.document().findBlockByLineNumber(line_number)
        self.highlighters[editor_index].error_line = line_number
        self.highlighters[editor_index].rehighlightBlock(block)

        scroll_line = line_number - 5 if line_number >= 5 else line_number
        cursor = QTextCursor(editor.document().findBlockByNumber(scroll_line))
        editor.moveCursor(QTextCursor.End)
        editor.setTextCursor(cursor)

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

    def _on_add_pressed(self):
        if not self.archive:
            return

        (desired_key, ok) = QInputDialog.getText(self, "Enter a key for the message.", "Key")
        if not ok:
            return
        if self.archive.has_message(desired_key):
            self.key_not_unique_dialog.show()
            return
        self.archive.insert_or_overwrite_message(desired_key, "")
        self._create_tab(desired_key, "")

    def _on_remove_pressed(self):
        if not self.archive:
            return
        current_index = self.tab_widget.currentIndex()
        key = self.keys[current_index]
        self.archive.erase_message(key)
        self.tab_widget.removeTab(current_index)
        del self.editors[current_index]
        del self.highlighters[current_index]
        del self.keys[current_index]
        self.player.clear()

    def _on_rename_pressed(self):
        if not self.archive:
            return

        (desired_key, ok) = QInputDialog.getText(self, "Enter a new key.", "Key")
        if not ok:
            return
        if self.archive.has_message(desired_key):
            self.key_not_unique_dialog.show()
            return
        current_index = self.tab_widget.currentIndex()
        key = self.keys[current_index]
        value = self.archive.get_message(key)
        self.archive.erase_message(key)
        self.archive.insert_or_overwrite_message(desired_key, value)
        self.keys[current_index] = desired_key
        self.tab_widget.setTabText(current_index, desired_key)
