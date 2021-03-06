from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import QFrame, QFormLayout, QLineEdit, QCheckBox, QMainWindow, QHBoxLayout, QPushButton, \
    QVBoxLayout, QTabWidget, QStatusBar, QWidget, QToolBar, QListView, QTextEdit, QCompleter, QPlainTextEdit

from ui.widgets.fe14_conversation_player import FE14ConversationPlayer

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

    def setCompleter(self, c, word_list):
        if self._completer is not None:
            self._completer.activated.disconnect()

        self._completer = c
        self._cursor_word = None 

        c.setWidget(self)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.setCaseSensitivity(QtCore.Qt.CaseSensitive)
        c.activated.connect(self.insertCompletion)

        self.word_list = word_list

    def completer(self):
        return self._completer

    def insertCompletion(self, completion):
        if self._completer.widget() is not self or completion == self._completer.completionPrefix:
            return

        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()

        # Get prefix
        tc.movePosition(QtGui.QTextCursor.StartOfWord, QtGui.QTextCursor.MoveAnchor)
        tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
        prefix = tc.selection().toPlainText()

        # Get command
        tc.movePosition(QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.MoveAnchor)
        tc.movePosition(QtGui.QTextCursor.EndOfWord, QtGui.QTextCursor.KeepAnchor)
        tc.select(QtGui.QTextCursor.WordUnderCursor)

        if prefix == None:
            return tc.selection().toPlainText()

        command = tc.selectedText()
        return prefix + command


    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)

        super(ConversationTextEdit, self).focusInEvent(e)

    def keyPressEvent(self, e):
        if self._completer is not None and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab):
                e.ignore()
                # Let the completer do default behavior.
                return

        # Assign shortcuts
        isShortcut = ((e.modifiers() & QtCore.Qt.ControlModifier) != 0 and e.key() == QtCore.Qt.Key_E)
        
        # If key is not a shortcut, write key to text area
        if self._completer is None or not isShortcut:
            # Do not process the shortcut when we have a completer.
            super(ConversationTextEdit, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        hasModifier = (e.modifiers() != QtCore.Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        if not isShortcut and (hasModifier or len(e.text()) == 0):
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            # Fix bugs:
            # With backspacing into a newline shows popup
            # The command is typed out fully, but hitting enter adds
            if completionPrefix in self.word_list:
                self._completer.popup().hide()
                return

            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(
                    self._completer.completionModel().index(0, 0))
            
        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)