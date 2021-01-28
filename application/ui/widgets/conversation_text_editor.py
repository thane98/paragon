from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import QTextEdit, QCompleter, QToolTip

from ui.misc.conversation_completer import ParagonConversationCompleter

# Credits for base code: https://github.com/baoboa/pyqt5/blob/25bdb92c38d9c0a915c6366769cc00a63a1f04b2/examples/tools/customcompleter/customcompleter.py
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
class ConversationTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(ConversationTextEdit, self).__init__(parent)

        self.setMouseTracking(True)
        self._completer = None
        self._command_hints = dict()
    
    def event(self, e: QtCore.QEvent):
        if e.type() == QtCore.QEvent.ToolTip:
            self.toolTipEvent(e)
        else:
            return super(ConversationTextEdit, self).event(e)

    def toolTipEvent(self, e: QtCore.QEvent):
        if not self._completer.popup().isVisible():
            prefix, base, _ = self._textCursorGetText(self.cursorForPosition(e.pos()))
            for item in self._command_hints:
                if item['Command'] == prefix + base:
                    QToolTip.showText(e.globalPos(), item['Hint'])
                    break
                else:
                    QToolTip.hideText()

    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)

        super(ConversationTextEdit, self).focusInEvent(e)

    # Watching cursor via mouse
    def mousePressEvent(self, e):
        super(ConversationTextEdit, self).mousePressEvent(e)
        self._textUnderCursor()

    def keyPressEvent(self, e):
        if self._completer is not None and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab):
                e.ignore()
                # Let the completer do default behavior.
                return

        isShortcut = ((e.modifiers() & QtCore.Qt.ControlModifier) != 0 and e.key() == QtCore.Qt.Key_E)
        if self._completer is None or not isShortcut:
            # Do not process the shortcut when we have a completer.
            super(ConversationTextEdit, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        hasModifier = (e.modifiers() != QtCore.Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self._textUnderCursor()

        if not isShortcut and (hasModifier or len(e.text()) == 0 or len(completionPrefix) < 1):
            self._completer.popup().hide()
            return

        # Fix bug:
        # Problem when using shortcut once, so we don't set a prefix
        if isShortcut:
            self._completer.popup().setCurrentIndex(
                    self._completer.completionModel().index(0, 0))
            self._completer.setCompletionPrefix("")

        else:
            if completionPrefix != self._completer.completionPrefix():
                # Fix bugs:
                # With backspacing into a newline shows popup
                # The command is typed out fully, but hitting enter will insert a brand new string
                if completionPrefix in self._cur_list:
                    self._completer.popup().hide()
                    return

                self._completer.setCompletionPrefix(completionPrefix)
                self._completer.popup().setCurrentIndex(
                        self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)
                
    def setCompleter(self, c: ParagonConversationCompleter):
        self._completer = c
        self._cursor_word = None 

        c.setWidget(self)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.setCaseSensitivity(QtCore.Qt.CaseSensitive)
        c.activated.connect(self._insertCompletion)

        if self._command_hints != None:
            self._completer.set_command_hints(self._command_hints)

        # Command list
        self._command_list = list()

        # For abstraction
        self._cur_list = list()

        self._initialize_lists()

    def _initialize_lists(self):
        return

    def completer(self):
        return self._completer

    def _insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return

        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def _textCursorGetText(self, tc):
        prefix = ""
        blacklist_chars = "~!@#%^&*()_+{}|:\"<>?,./;'[]\\-="

        # Get base word
        if tc == None:
            tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
        base_pos = tc.position()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        base = tc.selection().toPlainText().strip()

        # If typing before a trailing character
        if any(char in base for char in blacklist_chars):
            # Remove trailing characters. Nobody should be using these in their IDs hopefully
            for char in blacklist_chars:
                base.replace(char, "")

            tc.setPosition(base_pos)
            tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.MoveAnchor)
            tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
            base_pos = tc.position()

            # Get prefix
            tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
            prefix = tc.selection().toPlainText().strip()

            # Get base
            tc.setPosition(base_pos)
            tc.select(QtGui.QTextCursor.WordUnderCursor)
            base = tc.selection().toPlainText().strip()

        # If at the end of the line with trailing character, get only the prefix
        elif base == "":
            tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
            prefix = tc.selection().toPlainText().strip()
        else:
            # Get prefix
            # Alternative would be to move back a character first, so we don't select the proceeding word first
            tc.setPosition(base_pos)
            tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
            tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
            prefix = tc.selection().toPlainText().strip()
        return prefix, base, base_pos


    def _textUnderCursor(self):
        tc = self.textCursor()
        prefix, base, base_pos = self._textCursorGetText(tc)

        if prefix != "$":
            # Search for the command

            # Set position of start of line
            tc.setPosition(base_pos)
            orig_pos = tc.position()
            tc.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.MoveAnchor)
            sol = tc.position()
            tc.setPosition(orig_pos)
            while True:
                # If reach the start of line or line doesn't exist anymore because deleting too fast, end
                if sol == tc.position() or tc.position() == 0:
                    self._set_list(self._command_list)
                    break

                tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
                x = tc.selection().toPlainText()
                tc.clearSelection()
                if x == "(":
                    # Move back to avoid going to start of proceeding word
                    tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.MoveAnchor)
                    tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
                    commmand_base_pos = tc.position()

                    # Get command
                    tc.select(QtGui.QTextCursor.WordUnderCursor)
                    command_base = tc.selection().toPlainText().strip()

                    # Get prefix
                    tc.setPosition(commmand_base_pos)
                    tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
                    command_prefix = tc.selection().toPlainText()

                    # Set the appropiate list
                    self._find_command(command_prefix + command_base)
                    break
                if x == ")":
                    self._set_list(self._command_list)
                    break

        if prefix == "$":
            self._set_list(self._command_list)
            return prefix + base
        else:
            return base
                
    def _find_command(self, command: str):
        for item in self._command_hints:
            if item['Command'] == command:
                self._command_args(item['Args'])

    def _command_args(self, args: str):
        return

    def _set_list(self, item_list: list):
        model = self._completer.model()
        model.setStringList(item_list)
        self._cur_list = item_list
