from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import QFrame, QFormLayout, QLineEdit, QCheckBox, QMainWindow, QHBoxLayout, QPushButton, \
    QVBoxLayout, QTabWidget, QStatusBar, QWidget, QToolBar, QListView, QTextEdit, QCompleter

from ui.widgets.fe14_conversation_player import FE14ConversationPlayer

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

        self.text_area = ConversationTextEdit()

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

        self._completer = None

    def setCompleter(self, c):
        if self._completer is not None:
            self._completer.activated.disconnect()

        self._completer = c
        self._cursor_word = None 

        c.setWidget(self)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.setCaseSensitivity(QtCore.Qt.CaseSensitive)
        c.activated.connect(self.insertCompletion)

        # Dirty PoC
        character_list = list()
        module: TableModule = locator.get_scoped("ModuleService").get_module("Characters")
        for x in module.children():
            character_list.append(x[1])

        # List of items
        self._command_list = ["$HasPermanents", "$ConversationType", "$Color", "$NewSpeaker", "$Reposition", "$SetSpeaker", "$Emotions", "$PlayVoice", "$PlaySoundEffect", "$PlayMusic", "$StopMusic", "$Alias", "$Await", "$AwaitAndClear", "$Clear", "$DeleteSpeaker", "$Panicked", "$Scrolling", "$CutsceneAction", "$Wait", "$Volume", "$Dramatic", "$DramaticMusic", "$OverridePortrait", "$ShowMarriageScene", "$Ramp", "$StopRamp", "$SetRampVolume", "$FadeIn", "$FadeOut", "$FadeWhite", "$nl", "$Nu", "$G", "$arg", "$VisualEffect"]
        self._character_list = character_list
        # self._emotion_list =
        # Other list ideas:
        # Static ints for Ramp and etc.
        # Music

        # Set the initial list
        model = self._completer.model()
        model.setStringList(self._command_list)

        # For abstraction
        self._cur_list = self._command_list

    def completer(self):
        return self._completer

    def insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return

        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        prefix = ""
        blacklist_chars = "~!@#%^&*()_+{}|:\"<>?,./;'[]\\-="

        # Get base word
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

        if prefix != "$":
            # Search for the command

            # Set position of start of line
            tc.setPosition(base_pos)
            orig_pos = tc.position()
            tc.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.MoveAnchor)
            sol = tc.position()
            tc.setPosition(orig_pos)
            while True:
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

                    if command_prefix + command_base == ("$SetSpeaker" or "$NewSpeaker"):
                        model = self._completer.model()
                        model.setStringList(self._character_list)
                        self._cur_list = self._character_list

                # If reach the start of line or line doesn't exist anymore because backspacing too fast, end
                if sol == tc.position() or tc.position() == 0:
                    break

        # Don't return base
        if prefix == "$":
            model = self._completer.model()
            model.setStringList(self._command_list)
            self._cur_list = self._command_list
            return prefix + base
        else:
            return base

    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)

        super(ConversationTextEdit, self).focusInEvent(e)

    # Watching cursor via mouse
    def mousePressEvent(self, e):
        super(ConversationTextEdit, self).mousePressEvent(e)
        self.textUnderCursor()

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
        completionPrefix = self.textUnderCursor()

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


# Algorithm doesn't account for a lot of factors
    # def textUnderCursor(self):
    #     prefix = ""
    #     suffix = ""
    #     eow = "),"

    #     # Get base word
    #     tc = self.textCursor()
    #     tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
    #     base_pos = tc.position()
    #     tc.select(QtGui.QTextCursor.WordUnderCursor)
    #     base = tc.selection().toPlainText().strip()

    #     # If typing before a trailing character
    #     if any(char in base for char in eow):
    #         tc.setPosition(base_pos)
    #         tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.MoveAnchor)
    #         tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
    #         tc.select(QtGui.QTextCursor.WordUnderCursor)
    #         base = tc.selection().toPlainText().strip()

    #     # If at the end of the line with trailing character, get only the prefix
    #     if base == "":
    #         tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
    #         prefix = tc.selection().toPlainText().strip()
    #     else:
    #         # Get prefix
    #         # Alternative would be to move back a character first, so we don't select the proceeding word first
    #         tc.setPosition(base_pos)
    #         tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
    #         tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
    #         prefix = tc.selection().toPlainText().strip()

    #         # Get suffix
    #         # Alternative would be to move to the next character, to go back to base word
    #         tc.setPosition(base_pos)
    #         tc.movePosition(QtGui.QTextCursor.EndOfWord, QtGui.QTextCursor.MoveAnchor)
    #         tc.movePosition(QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.KeepAnchor)
    #         suffix = tc.selection().toPlainText().strip()


    #     # Algorithm
    #     # Check if this is an arg
    #     if prefix == "(":            
    #         # Move back 2x and go to start
    #         tc.setPosition(base_pos)
    #         tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.MoveAnchor, 2)
    #         tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
    #         commmand_base_pos = tc.position()

    #         # Get command
    #         tc.select(QtGui.QTextCursor.WordUnderCursor)
    #         command_base = tc.selection().toPlainText().strip()

    #         # Get prefix
    #         tc.setPosition(commmand_base_pos)
    #         tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
    #         command_prefix = tc.selection().toPlainText().strip()

    #         # If it's a command, change list
    #         # TO-DO: Add other args for other commands
    #         command_word = command_prefix + command_base
    #         if command_word == "$SetSpeaker":
    #             model = self._completer.model()
    #             model.setStringList(self._character_list)
    #             self._cur_list = self._character_list

    #     # Check if this is another arg
    #     if any(char in prefix for char in eow) or any(char in base for char in eow) or any(char in suffix for char in eow):
    #         # Search for the command

    #         # Set position of start of line
    #         tc.setPosition(base_pos)
    #         orig_pos = tc.position()
    #         tc.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.MoveAnchor)
    #         sol = tc.position()
    #         tc.setPosition(orig_pos)
    #         while True:
    #             tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
    #             x = tc.selection().toPlainText()
    #             tc.clearSelection()
    #             if x == "(":
    #                 # Move back to avoid going to start of proceeding word
    #                 tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.MoveAnchor)
    #                 tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
    #                 commmand_base_pos = tc.position()

    #                 # Get command
    #                 tc.select(QtGui.QTextCursor.WordUnderCursor)
    #                 command_base = tc.selection().toPlainText().strip()

    #                 # Get prefix
    #                 tc.setPosition(commmand_base_pos)
    #                 tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
    #                 command_prefix = tc.selection().toPlainText()

    #                 if command_prefix + command_base == ("$SetSpeaker" or "$NewSpeaker"):
    #                     model = self._completer.model()
    #                     model.setStringList(self._character_list)
    #                     self._cur_list = self._character_list

    #             # If reach the start of line or line doesn't exist anymore because backspacing too fast, end
    #             if sol == tc.position() or tc.position() == 0:
    #                 break
        
    #     # If a command, change list and return command
    #     if prefix == "$":
    #         model = self._completer.model()
    #         model.setStringList(self._command_list)
    #         self._cur_list = self._command_list
    #         return prefix + base
    #     else:
    #         return base