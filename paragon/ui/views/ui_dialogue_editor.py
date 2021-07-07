from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QStringListModel
from PySide2.QtGui import QFont, QIcon
from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QPlainTextEdit,
    QVBoxLayout,
    QCompleter,
    QToolTip, QToolButton, QMenu, QAction, QStatusBar, QLabel,
)

from paragon.ui.controllers.dialogue_player import DialoguePlayer


class Ui_DialogueEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.keys_box = QComboBox()
        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")
        self.rename_button = QPushButton("Rename")

        self.actions_button = QToolButton()
        self.actions_button.setMinimumWidth(80)
        self.actions_button.setPopupMode(QToolButton.InstantPopup)
        self.actions_button.setDefaultAction(QAction("Actions"))
        self.actions_button.setToolButtonStyle(QtGui.Qt.ToolButtonTextBesideIcon)
        self.actions_menu = QMenu()
        self.view_assets_action = QAction("View Available Assets")
        self.view_emotions_action = QAction("View Known Emotions")
        self.actions_menu.addActions([self.view_assets_action, self.view_emotions_action])
        self.actions_button.setMenu(self.actions_menu)

        self.generic_layout = QHBoxLayout()
        self.generic_layout.addWidget(self.keys_box)
        self.generic_layout.addWidget(self.new_button)
        self.generic_layout.addWidget(self.delete_button)
        self.generic_layout.addWidget(self.rename_button)
        self.generic_layout.addWidget(self.actions_button)
        self.generic_layout.setStretch(0, 1)

        self.editor = DialogueTextEdit()
        editor_font = QFont()
        editor_font.setPointSize(11)  # TODO: Make this configurable
        self.editor.setFont(editor_font)

        self.status_bar = QStatusBar()
        self.cursor_position_label = QLabel()
        self.status_bar.addPermanentWidget(self.cursor_position_label)

        editor_layout = QVBoxLayout()
        editor_layout.addLayout(self.generic_layout)
        editor_layout.addWidget(self.editor)
        editor_layout.addWidget(self.status_bar)
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


class DialogueCompleter(QCompleter):
    def __init__(self, parent=None):
        super(DialogueCompleter, self).__init__(parent)

        self.highlighted.connect(self._tool_tip)
        self._command_hints = {}
        self.setModel(QStringListModel())

    def set_command_hints(self, hints):
        self._command_hints = hints

    def _tool_tip(self, command):
        popup = self.popup()
        point = QtCore.QPoint(popup.pos().x() + popup.width(), popup.pos().y() - 16)
        for item in self._command_hints:
            if item["Command"] == command:
                QToolTip.showText(point, item["Hint"])
                break
            else:
                QToolTip.hideText()


# Credits for base code:
# https://github.com/baoboa/pyqt5/blob/25bdb92c38d9c0a915c6366769cc00a63a1f04b2/examples/tools/customcompleter/customcompleter.py
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2012 Digia Plc
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################
class DialogueTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMouseTracking(True)
        self._completer = None
        self._cursor_word = None
        self._cur_list = []
        self.service = None

        # Lists
        self._command_list = []
        self._character_list = []
        self._emotion_list = []
        self._command_hints = {}

    def set_service(self, service):
        self._command_hints = service.dialogue_commands
        self._command_list = list(
            map(lambda c: c["Command"], service.dialogue_commands)
        )
        self._character_list = list(service.asset_translations().keys())
        self._emotion_list = list(service.emotion_translations().keys())
        self.service = service

    def refresh_completion_lists(self):
        self._character_list = self.service.asset_translations()

    def event(self, e: QtCore.QEvent):
        if e.type() == QtCore.QEvent.ToolTip:
            self._tool_tip_event(e)
            e.accept()
            return True
        else:
            return super().event(e)

    def _tool_tip_event(self, e: QtCore.QEvent):
        if self._completer:
            if not self._completer.popup().isVisible():
                prefix, base, _ = self._text_cursor_get_text(
                    self.cursorForPosition(e.pos())
                )
                for item in self._command_hints:
                    if item["Command"] == prefix + base:
                        QToolTip.showText(e.globalPos(), item["Hint"])
                        break
                    else:
                        QToolTip.hideText()
                e.accept()
        else:
            e.ignore()

    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)
        super(DialogueTextEdit, self).focusInEvent(e)

    # Watching cursor via mouse
    def mousePressEvent(self, e):
        super(DialogueTextEdit, self).mousePressEvent(e)
        self._text_under_cursor()

    def keyPressEvent(self, e):
        if self._completer is not None and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (
                QtCore.Qt.Key_Enter,
                QtCore.Qt.Key_Return,
                QtCore.Qt.Key_Escape,
                QtCore.Qt.Key_Tab,
                QtCore.Qt.Key_Backtab,
            ):
                # Let the completer do default behavior.
                e.ignore()
                return

        is_shortcut = (
            e.modifiers() & QtCore.Qt.ControlModifier
        ) != 0 and e.key() == QtCore.Qt.Key_E
        if self._completer is None or not is_shortcut:
            # Do not process the shortcut when there is a completer.
            super(DialogueTextEdit, self).keyPressEvent(e)

        ctrl_or_shift = e.modifiers() & (
            QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier
        )
        if self._completer is None or (ctrl_or_shift and len(e.text()) == 0):
            return

        has_modifier = (e.modifiers() != QtCore.Qt.NoModifier) and not ctrl_or_shift
        completion_prefix = self._text_under_cursor()

        if not is_shortcut and (
            has_modifier or len(e.text()) == 0 or len(completion_prefix) < 1
        ):
            self._completer.popup().hide()
            e.accept()
            return

        # Fix bug:
        # Problem when using shortcut once, so we don't set a prefix
        if is_shortcut:
            self._completer.popup().setCurrentIndex(
                self._completer.completionModel().index(0, 0)
            )
            self._completer.setCompletionPrefix("")

        else:
            if completion_prefix != self._completer.completionPrefix():
                # Fix bugs:
                # With backspacing into a newline shows popup
                # The command is typed out fully, but hitting enter will insert a brand new string
                if completion_prefix in self._cur_list:
                    self._completer.popup().hide()
                    return

                self._completer.setCompletionPrefix(completion_prefix)
                self._completer.popup().setCurrentIndex(
                    self._completer.completionModel().index(0, 0)
                )

        cr = self.cursorRect()
        cr.setWidth(
            self._completer.popup().sizeHintForColumn(0)
            + self._completer.popup().verticalScrollBar().sizeHint().width()
        )
        self._completer.complete(cr)
        e.accept()

    def set_completer(self, c: DialogueCompleter):
        self._completer = c
        self._cursor_word = None

        c.setWidget(self)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        c.activated.connect(self._insert_completion)

        self._completer.set_command_hints(self._command_hints)

        # For abstraction
        self._cur_list = []
        self._set_list(self._command_list)

    def completer(self):
        return self._completer

    def _insert_completion(self, completion: str):
        if self._completer.widget() is not self:
            return

        tc = self.textCursor()

        if self._completer.completionPrefix() in completion:
            extra = len(completion) - len(self._completer.completionPrefix())
            tc.insertText(completion[-extra:])
        else:
            # To have case insensitivity
            [tc.deletePreviousChar() for _ in self._completer.completionPrefix()]
            tc.insertText(completion)

        self.setTextCursor(tc)

    def _text_cursor_get_text(self, tc):
        blacklist_chars = "~!@#%$^&*()_+{}|:\"<>?,./;'[]\\-="

        # Get base word
        if not tc:
            tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
        base_pos = tc.position()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        base = tc.selection().toPlainText().strip()

        # If typing before a trailing character
        if any(char in base for char in blacklist_chars):
            # Remove trailing characters.
            while base and base[-1] in blacklist_chars:
                base = base[:-1]

            tc.setPosition(base_pos)
            tc.movePosition(
                QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.MoveAnchor
            )
            tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
            base_pos = tc.position()

            # Get prefix
            tc.movePosition(
                QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor
            )
            prefix = tc.selection().toPlainText().strip()

            # Get base
            tc.setPosition(base_pos)
            tc.select(QtGui.QTextCursor.WordUnderCursor)
            base = tc.selection().toPlainText().strip()

        # If at the end of the line with trailing character, get only the prefix
        elif base == "":
            tc.movePosition(
                QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor
            )
            prefix = tc.selection().toPlainText().strip()
        else:
            # Get prefix
            # Alternative would be to move back a character first, so we don't select the proceeding word first
            tc.setPosition(base_pos)
            tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
            tc.movePosition(
                QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor
            )
            prefix = tc.selection().toPlainText().strip()
        return prefix, base, base_pos

    def _text_under_cursor(self):
        tc = self.textCursor()
        prefix, base, base_pos = self._text_cursor_get_text(tc)

        if prefix != "$":
            # Search for the command

            # Set position of start of line
            tc.setPosition(base_pos)
            orig_pos = tc.position()
            tc.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.MoveAnchor)
            sol = tc.position()
            tc.setPosition(orig_pos)

            # arg_index = 0

            while True:
                # If reach the start of line or line doesn't exist anymore because deleting too fast, end
                if sol == tc.position() or tc.position() == 0:
                    self._set_list(self._command_list)
                    break

                tc.movePosition(
                    QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor
                )
                x = tc.selection().toPlainText()
                tc.clearSelection()
                if x == ")":
                    self._set_list(self._command_list)
                    break

                # if x == ",":
                #     arg_index += 1

                if x == "(":
                    # Move back to avoid going to start of proceeding word
                    tc.movePosition(
                        QtGui.QTextCursor.PreviousCharacter,
                        QtGui.QTextCursor.MoveAnchor,
                    )
                    tc.movePosition(
                        QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor
                    )
                    commmand_base_pos = tc.position()

                    # Get command
                    tc.select(QtGui.QTextCursor.WordUnderCursor)
                    command_base = tc.selection().toPlainText().strip()

                    # Get prefix
                    tc.setPosition(commmand_base_pos)
                    tc.movePosition(
                        QtGui.QTextCursor.PreviousCharacter,
                        QtGui.QTextCursor.KeepAnchor,
                    )
                    command_prefix = tc.selection().toPlainText()

                    # Set the appropiate list
                    # TODO: Use arg_index to set the list for the command arg
                    self._find_command(command_prefix + command_base)
                    break

        if prefix == "$":
            self._set_list(self._command_list)
            return prefix + base
        else:
            return base

    def _find_command(self, command: str):
        for item in self._command_hints:
            if item["Command"] == command:
                self._command_args(item["Args"])

    def _command_args(self, arg: str):
        if arg == "Character":
            self._set_list(self._character_list)
        elif arg == "Emotion":
            self._set_list(self._emotion_list)

    def _set_list(self, item_list: list):
        model = self._completer.model()
        model.setStringList(item_list)
        self._cur_list = item_list
