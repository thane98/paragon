import logging
import traceback

from PySide6 import QtGui, QtCore
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QInputDialog, QMessageBox

from paragon.core.scanner import ScannerError
from paragon.ui.controllers.dialogue_assets_dialog import DialogueAssetsDialog
from paragon.ui.controllers.dialogue_emotions_dialog import DialogueEmotionsDialog
from paragon.ui.controllers.error_dialog import ErrorDialog
from paragon.ui.views.ui_dialogue_editor import Ui_DialogueEditor, DialogueCompleter


class DialogueEditor(Ui_DialogueEditor):
    def __init__(self, data, service, sprite_animation_svc, game):
        super().__init__()
        self.data = data
        self.service = service
        self.sprite_animation_svc = sprite_animation_svc
        self.path = None
        self.localized = None
        self.message = None
        self.error_dialog = None
        self.assets_dialog = None
        self.emotions_dialog = None

        self.setWindowTitle("Paragon")

        self.keys_box.setCurrentIndex(-1)

        backgrounds = self.service.backgrounds()
        windows = self.service.windows()

        self.player.set_backgrounds(backgrounds)
        self.player.set_game(game)
        self.player.set_windows(windows)
        self.player.set_service(self.service, sprite_animation_svc)

        self.editor.set_service(service)
        self.editor.set_completer(DialogueCompleter())

        self.player.redraw()
        self.refresh_buttons()

        self.keys_box.currentIndexChanged.connect(self._on_selection)
        self.preview_button.clicked.connect(self._on_save_and_preview)
        self.new_button.clicked.connect(self._on_new)
        self.delete_button.clicked.connect(self._on_delete)
        self.rename_button.clicked.connect(self._on_rename)
        self.view_assets_action.triggered.connect(self.show_assets_dialog)
        self.view_emotions_action.triggered.connect(self.show_emotions_dialog)
        self.editor.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.editor.lostFocus.connect(self._on_lost_focus)

    def set_archive(self, path, localized):
        self.keys_box.clear()
        self.path = path
        self.localized = localized
        if not path:
            self.setWindowTitle("Paragon")
        else:
            self.setWindowTitle("Paragon - " + path)
            self.data.open_text_data(path, localized)
            keys = self.data.enumerate_messages(path, localized)
            for key in keys:
                self.keys_box.addItem(key)
        self.refresh_buttons()

    def event(self, e: QtCore.QEvent):
        if e.type() == QtCore.QEvent.WindowActivate:
            self.editor.refresh_completion_lists()
            return True
        else:
            return super(DialogueEditor, self).event(e)

    def refresh_buttons(self):
        has_selection = self._has_valid_selection()
        self.new_button.setEnabled(self.path is not None)
        self.preview_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.rename_button.setEnabled(has_selection)

    def show_assets_dialog(self):
        if not self.assets_dialog:
            self.assets_dialog = DialogueAssetsDialog(self.service)
        self.assets_dialog.show()

    def show_emotions_dialog(self):
        if not self.emotions_dialog:
            self.emotions_dialog = DialogueEmotionsDialog(self.service)
        self.emotions_dialog.show()

    def _select_line(self, line):
        doc = self.editor.document()
        block = doc.findBlockByLineNumber(line)
        if block:
            cursor = QTextCursor(block)
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            self.editor.setTextCursor(cursor)

    def _on_cursor_position_changed(self):
        block = self.editor.textCursor().blockNumber() + 1
        pos = self.editor.textCursor().positionInBlock() + 1
        self.cursor_position_label.setText(f"{block} : {pos}")

    def _on_selection(self):
        if self._has_valid_selection():
            key = self.keys_box.currentText()
            value = self.data.message(self.path, self.localized, key)
            pretty = self.service.game_to_pretty(value)
            self.editor.setPlainText(pretty)
        else:
            self.editor.setPlainText("")
        self._preview()
        self.refresh_buttons()

    def _on_save_and_preview(self):
        if self._has_valid_selection():
            self._preview()

    def _on_lost_focus(self):
        if self.isActiveWindow() and self._has_valid_selection():
            self._save()

    def _preview(self):
        try:
            text = self.editor.toPlainText()
            snapshots = self.service.interpret(text)
            self.player.set_snapshots(snapshots)
            return True
        except ScannerError as e:
            self.error_dialog = ErrorDialog(str(e))
            self.error_dialog.show()
            self._select_line(e.line - 1)
        except Exception as e:
            logging.exception("Previewing failed.")
            trace = traceback.format_exception(type(e), e, e.__traceback__)
            self.error_dialog = ErrorDialog("".join(trace))
            self.error_dialog.show()
        return False

    def _save(self):
        try:
            text = self.editor.toPlainText()
            game_text = self.service.pretty_to_game(text)
            original = self.data.message(
                self.path, self.localized, self.keys_box.currentText()
            )
            if original != game_text:
                self.data.set_message(
                    self.path, self.localized, self.keys_box.currentText(), game_text
                )
                self.status_bar.showMessage(
                    f"Saved changes to message {self.keys_box.currentText()}", 5000
                )
        except ScannerError as e:
            self.error_dialog = ErrorDialog(str(e))
            self.error_dialog.show()
            self._select_line(e.line - 1)
        except Exception as e:
            logging.exception("Previewing failed.")
            trace = traceback.format_exception(type(e), e, e.__traceback__)
            self.error_dialog = ErrorDialog("".join(trace))
            self.error_dialog.show()

    def _on_new(self):
        if not self.path:
            return

        # TODO: Validate naming scheme?
        choice, ok = QInputDialog.getText(self, "Enter Key", "Key")
        if ok:
            self.data.set_message(
                self.path,
                self.localized,
                choice,
                "This is a placeholder message.\\nSee the guide for info on formatting.",
            )
            self.keys_box.addItem(choice)
            self.keys_box.setCurrentIndex(self.keys_box.count() - 1)

    def _on_delete(self):
        if self._has_valid_selection():
            key = self.keys_box.currentText()
            self.data.set_message(self.path, self.localized, key, None)
            self.keys_box.removeItem(self.keys_box.currentIndex())

    def _on_rename(self):
        if self._has_valid_selection():
            choice, ok = QInputDialog.getText(
                self, "Enter Key", "Key", text=self.keys_box.currentText()
            )
            if ok:
                # Verify that the key is unique.
                if not self._key_is_unique(choice):
                    self.message = QMessageBox()
                    self.message.setText(f"The key {choice} is already in use.")
                    self.message.exec_()
                    return
                key = self.keys_box.currentText()
                value = self.data.message(self.path, self.localized, key)
                self.data.set_message(self.path, self.localized, choice, value)
                self.data.set_message(self.path, self.localized, key, None)
                self.keys_box.setItemText(self.keys_box.currentIndex(), choice)

    def _key_is_unique(self, key) -> bool:
        return key not in self.data.enumerate_messages(self.path, self.localized)

    def _has_valid_selection(self):
        return bool(self.path and self.keys_box.currentText())
