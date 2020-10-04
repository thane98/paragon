import logging
from typing import Optional

from PySide2 import QtCore, QtGui
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QIcon, QTextCursor
from PySide2.QtWidgets import QAction, QInputDialog, QMessageBox

from core.conversation import convert
from core.conversation.convert import paragon_to_commands, paragon_to_game, commands_to_game
from model.conversation.transpiler_error import TranspilerError
from model.message_archive import MessageArchive
from model.qt.messages_model import MessagesModel
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
        self.key = None
        self.model: Optional[MessagesModel] = None
        self.conversation_list.setModel(self.model)

        self.text_area.setFontPointSize(10)
        self.highlighter = ParagonScriptHighlighter(self.text_area.document())

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

        self.conversation_list.selectionModel().currentRowChanged.connect(self._update_selection)
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
            self.model = MessagesModel(self.archive)
        else:
            self.setEnabled(False)
            self.model = None
        self.conversation_list.setModel(self.model)
        self.conversation_list.selectionModel().currentRowChanged.connect(self._update_selection)

    def clear(self):
        self.player.clear()
        self.text_area.clear()
        self.model = None
        self.archive = None
        self.key = None

    def _update_selection(self, index: QModelIndex):
        if not self.model or not self.archive or not index.isValid():
            self.player.clear()
            self.text_area.clear()
            self._update_actions(False)
        else:
            message_data = self.model.data(index, QtCore.Qt.UserRole)
            try:
                paragon_script = convert.game_to_paragon(message_data)
                self.text_area.setText(paragon_script)
                self._update_actions(True)
                self.key = self.model.data(index, QtCore.Qt.DisplayRole)
            except:
                logging.exception("Failed to decompile game script.")
                self._update_actions(False)
                return
        self.player.clear()

    def closeEvent(self, event: QtGui.QCloseEvent):
        event.accept()
        if self.owner:
            self.owner.delete_conversation_editor(self)

    def _update_actions(self, valid):
        self.rename_action.setEnabled(valid)
        self.remove_action.setEnabled(valid)
        self.preview_button.setEnabled(valid)
        self.save_button.setEnabled(valid)

    def _on_preview_pressed(self):
        try:
            paragon_script = self.text_area.document().toPlainText()
            commands = paragon_to_commands(paragon_script)
            game_script = commands_to_game(commands)
            self.model.save_message(self.key, game_script)
            self.statusBar().showMessage("Transpiling for %s succeeded!" % self.key)

            self.player.set_commands(commands)
            self.highlighter.error_line = None
            self.highlighter.rehighlight()
        except TranspilerError as e:
            self._update_ui_for_error(e)

    def _on_save_pressed(self):
        if not self.model or not self.archive:
            return

        try:
            paragon_script = self.text_area.document().toPlainText()
            game_script = paragon_to_game(paragon_script)
            self.model.save_message(self.key, game_script)
            self.statusBar().showMessage("Transpiling for %s succeeded!" % self.key)
            self.highlighter.error_line = None
            self.highlighter.rehighlight()
        except TranspilerError as e:
            self._update_ui_for_error(e)

    def _update_ui_for_error(self, error: TranspilerError):
        self.statusBar().showMessage(str(error))
        self.player.clear()
        line_number = error.source_position.line_number - 1
        block = self.text_area.document().findBlockByLineNumber(line_number)
        self.highlighter.error_line = line_number
        self.highlighter.rehighlightBlock(block)

        scroll_line = line_number - 5 if line_number >= 5 else line_number
        cursor = QTextCursor(self.text_area.document().findBlockByNumber(scroll_line))
        self.text_area.moveCursor(QTextCursor.End)
        self.text_area.setTextCursor(cursor)

    def _on_avatar_name_changed(self):
        conversation_service = locator.get_scoped("ConversationService")
        conversation_service.set_avatar_name(self.avatar_name_editor.text())

    def _on_avatar_gender_changed(self, _):
        conversation_service = locator.get_scoped("ConversationService")
        conversation_service.set_avatar_is_female(self.avatar_is_female_check.isChecked())

    def _on_add_s_support_activated(self):
        if not self.archive or not self.model:
            return

        base_key = self.model.data(self.model.index(0, 0), QtCore.Qt.DisplayRole)
        new_key = base_key.replace("Ｃ", "Ｓ")
        if self.archive.has_message(new_key):
            return
        self.model.add_message(new_key)

    def _on_add_pressed(self):
        if not self.archive or not self.model:
            return

        (desired_key, ok) = QInputDialog.getText(self, "Enter a key for the message.", "Key")
        if not ok:
            return
        if self.archive.has_message(desired_key):
            self.key_not_unique_dialog.show()
            return
        self.model.add_message(desired_key)

    def _on_remove_pressed(self):
        if not self.archive or not self.model:
            return
        self.model.remove_message(self.key)

    def _on_rename_pressed(self):
        if not self.archive or not self.model:
            return

        (desired_key, ok) = QInputDialog.getText(self, "Enter a new key.", "Key")
        if not ok:
            return
        if self.archive.has_message(desired_key):
            self.key_not_unique_dialog.show()
            return
        self.model.rename_message(self.key, desired_key)
