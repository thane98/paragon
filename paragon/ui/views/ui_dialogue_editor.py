from PySide2 import QtGui, QtCore
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
    QToolTip,
)

from paragon.ui.controllers.dialogue_player import DialoguePlayer

from PySide2.QtGui import QPixmap, QImage, QPainter, QMouseEvent, QCursor, QPalette
from PySide2.QtWidgets import QGraphicsScene, QLabel, QGraphicsItem, QStyleOptionGraphicsItem, QGraphicsView, QMenu, QAction, QFrame, QActionGroup
from PySide2.QtCore import QRectF, QRect, QTimer, QPoint, QEvent, Qt
from PySide2 import QtCore

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

        self.editor = DialogueTextEdit()
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

        #         # https://evileg.com/en/post/92/
                # Garbage testing
        sprite = FE13UnitSpriteItem("C:/Users/Karl/Downloads/tmp.png")
        sprite1 = FE13UnitSpriteItem("C:/Users/Karl/Downloads/Games/3DS/FE/FEAT/魔道士リヒト赤/魔道士リヒト赤.png")
        sprite2 = FE13UnitSpriteItem("C:/Users/Karl/Downloads/Games/3DS/FE/FEAT/魔道士リヒト緑/魔道士リヒト緑.png")

        self.scene = FE13SpriteContainer()
        self.scene.load_sprite(sprite, sprite1, sprite2)
        self.graphics = QGraphicsView()
        self.graphics.setScene(self.scene)

        self.graphics.setAutoFillBackground(False)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Base, Qt.transparent)
        self.graphics.setPalette(palette)
        self.graphics.setFrameShape(QFrame.NoFrame)

        self.graphics.setFixedSize(self.scene.height(), self.scene.width())
        self.graphics.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_layout.addWidget(self.graphics)

        # sprite = FE14UnitSpriteItem(None, "C:/Users/Karl/Downloads/Release/azura_layer3.png", None, None)
        # sprite1 = FE14UnitSpriteItem(None, "C:/Users/Karl/Downloads/Release/azura_layer2.png", None, None)
        # sprite2 = FE14UnitSpriteItem(None, "C:/Users/Karl/Downloads/Release/azura_layer2.png", None, None)
        # sprite3 = FE14UnitSpriteItem(None, "C:/Users/Karl/Downloads/Release/azura_layer2.png", None, None)

        # scene = FE14SpriteContainer()
        # scene.load_sprite(sprite, sprite1, sprite2, sprite3)
        # graphics = QGraphicsView()
        # graphics.setScene(scene)
        # left_layout.addWidget(graphics)

from PySide2.QtWidgets import QTabWidget, QTableView, QListView, QFormLayout, QRadioButton, QLineEdit, QTableWidget, QMenu, QButtonGroup
from PySide2.QtGui import QIcon

class DialogueCompleter(QCompleter):
    def __init__(self, parent=None):
        super(DialogueCompleter, self).__init__(parent)

        self.highlighted.connect(self._tool_tip)
        self._command_hints = {}
        self.setModel(QStringListModel())

        self.popup().setStyleSheet("padding: 0px 0px 30px 0px; border-bottom: 0px")

        self.button = QPushButton()
        self.button.clicked.connect(self.ok)
        self.button1 = QPushButton()
        self.button1.clicked.connect(self.ok)


        lo = QPixmap()
        lo.load("C:/Users/Karl/Downloads/Method_16x.png")
        self.button.setStyleSheet("border: 0px; padding-top: 14px;")

        ok = QPixmap()
        ok.load("C:/Users/Karl/Downloads/VariableExpression_16x.png")
        self.button1.setStyleSheet("border: 0px; padding-top: 14px;")

        self.button.setIcon(QIcon(lo))
        self.button.setFixedSize(30, 30)

        self.button1.setIcon(QIcon(ok))
        self.button1.setFixedSize(30, 30)

        self.widget = QWidget(self.popup())
        self.widget.setFixedSize(200, 30)
        # self.widget.setStyleSheet("background-color: #000000; border: 0px")

        self.widget.setStyleSheet("border: 0px")

        self.layout = QHBoxLayout(self.widget)

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.button1)

        self.layout.addStretch()
        self.layout.setSpacing(0)


    def ok(self):
        self.popup().update()
        self.button.clearFocus()
        self.button1.clearFocus()

    def complete(self, cr):
        super().complete(cr)
        
        self.popup().resize(self.popup().width(), self.popup().height() + 30)
        self.widget.move(0, self.popup().height() - 30)


    def set_command_hints(self, hints):
        self._command_hints = hints

    def _tool_tip(self, command):
        popup = self.popup()

        popup.setFixedWidth(200)
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









class AbstractSpriteItem(QGraphicsItem):
    """Spritesheet widget"""
    def __init__(self):
        super(AbstractSpriteItem, self).__init__()
        self._timer = QTimer()
        self._current_frame = QPoint(0,0)
        self._timer.timeout.connect(self._next_frame)
        self._loop = True
        # Assumed that these are hardcoded
        # These are in fact not hardcoded for fates
        self._end_frame_pos_x = 96
        self._frame_height = 32
        self._frame_width = 32

    def animation_on(self):
        # Game runs @30 FPS, so half frame count b/c that's 60fps
        """Animate frames"""
        self._timer.start(1000/5)

    def is_animating(self) -> bool:
        return self._timer.isActive()

    def animation_off(self):
        """Draw static frame"""
        self._timer.stop()

    def boundingRect(self) -> QRectF:
        return QRectF(
            0, 
            0, 
            self._frame_width, 
            self._frame_height
        )

    def _next_frame(self):
        return

class FE14UnitSpriteFrameData():
    def __init__(self, source_x_pos, source_y_pos, width, height, draw_x_pos, draw_y_pos, frame_delay):
        self.source_x_pos = source_x_pos
        self.source_y_pos = source_y_pos
        self.width = width
        self.height = height
        self.draw_x_pos = draw_x_pos
        self.draw_y_pos = draw_y_pos

        # Frame delay at 60 FPS
        # Game renders at 30 FPS, so half the frame delay to get sec/frames for the timer
        self.frame_delay = frame_delay

class FE14UnitSpriteAnimationData():
    def __init__(self):
        self.frame_count = None
        self.body = FE14UnitSpriteFrameData()
        self.head = FE14UnitSpriteFrameData()

class FE13UnitSpriteItem(AbstractSpriteItem):
    def __init__(self, spritesheet):
        super().__init__()
        self._spritesheet = QPixmap()

        self._spritesheet.load(spritesheet)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        painter.drawPixmap(
            0,
            0, 
            self._spritesheet, 
            self._current_frame.x(), 
            self._current_frame.y(), 
            self._frame_width, 
            self._frame_height
        )

    def _next_frame(self):
        # Loop frames backwards:
        # `Idle` and `Use` animation
        if self._current_frame.y() in [0, 32]:

            # Start looping back at the end of frame
            if self._current_frame.x() == self._end_frame_pos_x and self._loop == False:
                self._current_frame.setX(
                    self._current_frame.x() - self._frame_width
                )
                self._loop = True
                
            # End loop at the start of frame
            elif self._current_frame.x() == 0 and self._loop == True:
                self._current_frame.setX(
                    self._current_frame.x() + self._frame_width
                )
                self._loop = False

            # When looping back, go back a frame
            elif 0 < self._current_frame.x() < self._end_frame_pos_x and self._loop == True:
                self._current_frame.setX(
                    self._current_frame.x() - self._frame_width
                )

            # When not looping, go forward a frame 
            elif self._current_frame.x() < self._end_frame_pos_x and self._loop == False:
                self._current_frame.setX(
                    self._current_frame.x() + self._frame_width
                )

        # Loop normally
        else:
            if self._current_frame.x() == self._end_frame_pos_x:
                self._current_frame.setX(0)
            elif self._current_frame.x() < self._end_frame_pos_x:
                self._current_frame.setX(
                    self._current_frame.x() + self._frame_width
                )

        # Redraw new frame
        self.update(
            0, 
            0, 
            self._frame_width, 
            self._frame_height
        )

class FE14UnitSpriteAbstractItem(AbstractSpriteItem):
    def __init__(self):
        super().__init__()

        # Default animation
        # Why IS doesn't just put it in one spritesheet? Who knows.
        self._is_idle = True
        
    def _next_frame(self):
        # This is all wrong


        # Loop frames backwards:
        # Idle animation

        # Start looping back at the end of frame
        if self._is_idle:
            if self._current_frame.x() == self._end_frame_pos_x and self._loop == False:
                self._current_frame.setX(
                    self._current_frame.x() - self._frame_width
                )
                self._loop = True
                
            # End loop at the start of frame
            elif self._current_frame.x() == 0 and self._loop == True:
                self._current_frame.setX(
                    self._current_frame.x() + self._frame_width
                )
                self._loop = False

            # When looping back, go back a frame
            elif 0 < self._current_frame.x() < self._end_frame_pos_x and self._loop == True:
                self._current_frame.setX(
                    self._current_frame.x() - self._frame_width
                )

            # When not looping, go forward a frame 
            elif self._current_frame.x() < self._end_frame_pos_x and self._loop == False:
                self._current_frame.setX(
                    self._current_frame.x() + self._frame_width
                )

        # Loop normally
        else:
            if self._current_frame.x() == self._end_frame_pos_x:
                self._current_frame.setX(0)
            elif self._current_frame.x() < self._end_frame_pos_x:
                self._current_frame.setX(
                    self._current_frame.x() + self._frame_width
                )

        # Redraw new frame
        self.update(
            0, 
            0, 
            self._frame_width, 
            self._frame_height
        )

class FE14UnitSpriteItem(FE14UnitSpriteAbstractItem):
# We want to receive the preprocessed sprite and process it here
    def __init__(self, head, body, idle_head, idle_body):
        super().__init__()
        # Lowest index is the most bottom layer
        self.body_spritesheet = [QPixmap() for layer in range(3)]
        self.head_spritesheet = [QPixmap() for layer in range(3)]

        self.idle_body_spritesheet = [QPixmap() for layer in range(3)]
        self.idle_head_spritesheet: [QPixmap() for layer in range(3)]

        # Load images
        # self.body_spritesheet[0].load("C:/Users/Karl/Downloads/Release/gk_layer3.png")
        # self.body_spritesheet[1].load("C:/Users/Karl/Downloads/Release/gk_layer2.png")
        # self.body_spritesheet[2].load(None)

        # self.head_spritesheet[0].load("C:/Users/Karl/Downloads/Release/azura_layer3.png")
        # self.head_spritesheet[1].load("C:/Users/Karl/Downloads/Release/azura_layer2.png")
        # self.head_spritesheet[2].load(None)

        self.body_spritesheet[0].load(body)

        self.head_spritesheet[0].load(head)

        # self.idle_body_spritesheet[0].load()
        # self.idle_body_spritesheet[1].load()
        # self.idle_body_spritesheet[2].load()

        # self.idle_head_spritesheet[0].load()
        # self.idle_head_spritesheet[1].load()
        # self.idle_head_spritesheet[2].load()

        # Fix this to be true when cleaning up

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        # Draw order is prioritized by lowest alpha, and then, head first and body second
        # drawPixmap()
        # arg1: x-position to draw on canvas
        # arg2: y-position to draw on canvas
        # arg3: source image
        # arg4: source image x-position
        # arg5: source image y-position
        # arg6: source image width bound to copy
        # arg7: source image height bound to copy

        # TODO: configure draw position for head_layer
        # TODO: Configure this in accordance to anime.bin

        # Loops frames backwards
        # Idle animation
        if self._is_idle:
            if self.idle_head_spritesheet[0]:
                painter.drawPixmap(
                    0, 
                    0, 
                    self.idle_head_spritesheet[0], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.idle_body_spritesheet[0]:
                painter.drawPixmap(
                    0, 
                    0, 
                    self.idle_body_spritesheet[0], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.idle_head_spritesheet[1]:
                painter.drawPixmap(
                    0, 
                    0, 
                    self.idle_head_spritesheet[1], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.idle_body_spritesheet[1]:
                painter.drawPixmap(
                    0, 
                    0, 
                    self.idle_body_spritesheet[1], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.idle_head_spritesheet[2]:
                painter.drawPixmap(
                    0, 
                    0, 
                    self.idle_head_spritesheet[2], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.idle_body_spritesheet[2]:
                painter.drawPixmap(
                    0, 
                    0, 
                    self.idle_body_spritesheet[2], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
        else:
            if self.head_spritesheet[0]:
                painter.drawPixmap(
                    3, 
                    -6, 
                    self.head_spritesheet[0], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.body_spritesheet[0]:
                painter.drawPixmap(
                    0, 
                    0, 
                    self.body_spritesheet[0], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.head_spritesheet[1]:
                painter.drawPixmap(
                    3, 
                    -6, 
                    self.head_spritesheet[1], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.body_spritesheet[1]:
                painter.drawPixmap(
                    0, 
                    0, 
                    self.body_spritesheet[1], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.head_spritesheet[2]:
                painter.drawPixmap(
                    3, 
                    -6, 
                    self.head_spritesheet[2], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )
            if self.body_spritesheet[2]:
                painter.drawPixmap(
                    0, 
                    0, 
                    self.body_spritesheet[2], 
                    self._current_frame.x(), 
                    self._current_frame.y(), 
                    self._frame_width, 
                    self._frame_height
                )

class FE14UniqueUnitSpriteItem(FE14UnitSpriteAbstractItem):
    def __init__(self, unique, idle_unique):
        self.unique_spritesheet = [QPixmap() for layer in range(3)]
        self.idle_unique_spritesheet = [QPixmap() for layer in range(3)]

        # self.unique.load(unique)
        # self.idle_unique.load(idle_unique)

class FE14SpriteContainer(QGraphicsScene):
    def __init__(self):
        super(FE14SpriteContainer, self).__init__()
        self._menu = QMenu()

        # If class is a flier then do this

        # idle_action_flier = QAction('Idle', self)
        # moving_west_action_flier = QAction('Moving West', self)
        # moving_east_action_flier = QAction('Moving East', self)
        # moving_south_action_flier = QAction('Moving South', self)
        # moving_north_action_flier = QAction('Moving North', self)
        # moving_southwest_action_flier = QAction('Moving Southwest', self)
        # moving_southeast_action_flier = QAction('Moving Southeast', self)
        # moving_northwest_action_flier = QAction('Moving Northwest', self)
        # moving_northeast_action_flier = QAction('Moving Northeast', self)

        # idle_action_flier.setCheckable(True)
        # moving_west_action_flier.setCheckable(True)
        # moving_east_action_flier.setCheckable(True)
        # moving_south_action_flier.setCheckable(True)
        # moving_north_action_flier.setCheckable(True)
        # moving_southwest_action_flier.setCheckable(True)
        # moving_southeast_action_flier.setCheckable(True)
        # moving_northwest_action_flier.setCheckable(True)
        # moving_northeast_action_flier.setCheckable(True)

        # idle_action_flier.setChecked(True)        

        # self._menu.addAction(idle_action_flier)
        # self._menu.addAction(moving_west_action_flier)
        # self._menu.addAction(moving_east_action_flier)
        # self._menu.addAction(moving_south_action_flier)
        # self._menu.addAction(moving_north_action_flier)
        # self._menu.addAction(moving_southwest_action_flier)
        # self._menu.addAction(moving_southeast_action_flier)
        # self._menu.addAction(moving_northwest_action_flier)
        # self._menu.addAction(moving_northeast_action_flier)

        # idle_action_flier.triggered.connect(self._idle_action_flier)
        # moving_west_action_flier.triggered.connect(self._moving_west_action_flier)
        # moving_east_action_flier.triggered.connect(self._moving_east_action_flier)
        # moving_south_action_flier.triggered.connect(self._moving_south_action_flier)
        # moving_north_action_flier.triggered.connect(self._moving_north_action_flier)
        # moving_southwest_action_flier.triggered.connect(self._moving_southwest_action_flier)
        # moving_southeast_action_flier.triggered.connect(self._moving_southeast_action_flier)
        # moving_northwest_action_flier.triggered.connect(self._moving_northwest_action_flier)
        # moving_northeast_action_flier.triggered.connect(self._moving_northeast_action_flier)

        idle_action = QAction('Idle', self)
        moving_west_action = QAction('Moving West', self)
        moving_east_action = QAction('Moving East', self)
        moving_south_action = QAction('Moving South', self)
        moving_north_action = QAction('Moving North', self)
        moving_southwest_action = QAction('Moving Southwest', self)
        moving_southeast_action = QAction('Moving Southeast', self)
        moving_northwest_action = QAction('Moving Northwest', self)
        moving_northeast_action = QAction('Moving Northeast', self)

        idle_action.setCheckable(True)
        moving_west_action.setCheckable(True)
        moving_east_action.setCheckable(True)
        moving_south_action.setCheckable(True)
        moving_north_action.setCheckable(True)
        moving_southwest_action.setCheckable(True)
        moving_southeast_action.setCheckable(True)
        moving_northwest_action.setCheckable(True)
        moving_northeast_action.setCheckable(True)

        # WE NEED CONDITIONALS AH
        idle_action.setChecked(True)        

        self._menu.addAction(idle_action)
        self._menu.addAction(moving_west_action)
        self._menu.addAction(moving_east_action)
        self._menu.addAction(moving_south_action)
        self._menu.addAction(moving_north_action)
        self._menu.addAction(moving_southwest_action)
        self._menu.addAction(moving_southeast_action)
        self._menu.addAction(moving_northwest_action)
        self._menu.addAction(moving_northeast_action)

        idle_action.triggered.connect(self._idle_action)
        moving_west_action.triggered.connect(self._moving_west_action)
        moving_east_action.triggered.connect(self._moving_east_action)
        moving_south_action.triggered.connect(self._moving_south_action)
        moving_north_action.triggered.connect(self._moving_north_action)
        moving_southwest_action.triggered.connect(self._moving_southwest_action)
        moving_southeast_action.triggered.connect(self._moving_southeast_action)
        moving_northwest_action.triggered.connect(self._moving_northwest_action)
        moving_northeast_action.triggered.connect(self._moving_northeast_action)

    def load_sprite(
        self, 
        blue: FE14UnitSpriteAbstractItem, 
        green: FE14UnitSpriteAbstractItem, 
        red: FE14UnitSpriteAbstractItem, 
        purple: FE14UnitSpriteAbstractItem
        ):
        """Load unit sprite factions"""

        self.blue = blue
        self.green = green
        self.red = red
        self.purple = purple

        # Bless pointers
        self.addItem(self.blue)
        self.addItem(self.green)
        self.addItem(self.red)
        self.addItem(self.purple)

        # Default color will be blue
        if not blue.isVisible():
            self.blue.setVisible(True)
        if self.green.isVisible():
            self.green.setVisible(False)
        if self.red.isVisible():
            self.red.setVisible(False)
        if self.purple.isVisible():
            self.purple.setVisible(False)

        if not blue.is_animating():
            self.blue.animation_on()
        if self.green.is_animating():
            self.green.animation_off()
        if self.red.is_animating():
            self.red.animation_off()
        if self.purple.is_animating():
            self.purple.animation_off()

    # To do fix the text for these cause they're not true 
    @QtCore.Slot(bool)
    def _idle_action(self, triggered):
        self._uncheck_actions(triggered, "Idle")
        self.blue._is_idle = True
        self.green._is_idle = True
        self.red._is_idle = True
        self.purple._is_idle = True
        self._draw_new_animation(0)

    @QtCore.Slot(bool)
    def _moving_west_action(self, triggered):
        self._uncheck_actions(triggered, "Moving West")
        self._not_idle()
        self._draw_new_animation(0)

    @QtCore.Slot(bool)
    def _moving_east_action(self, triggered):
        self._uncheck_actions(triggered, "Moving East")
        self._not_idle()
        self._draw_new_animation(32)

    @QtCore.Slot(bool)
    def _moving_south_action(self, triggered):
        self._uncheck_actions(triggered, "Moving South")
        self._not_idle()
        self._draw_new_animation(64)

    @QtCore.Slot(bool)
    def _moving_north_action(self, triggered):
        self._uncheck_actions(triggered, "Moving North")
        self._not_idle()
        self._draw_new_animation(96)

    @QtCore.Slot(bool)
    def _moving_southwest_action(self, triggered):
        self._uncheck_actions(triggered, "Moving Southwest")
        self._not_idle()
        self._draw_new_animation(128)

    @QtCore.Slot(bool)
    def _moving_southeast_action(self, triggered):
        self._uncheck_actions(triggered, "Moving Southeast")
        self._not_idle()
        self._draw_new_animation(160)

    @QtCore.Slot(bool)
    def _moving_northwest_action(self, triggered):
        self._uncheck_actions(triggered, "Moving Northwest")
        self._not_idle()
        self._draw_new_animation(192)

    @QtCore.Slot(bool)
    def _moving_northeast_action(self, triggered):
        self._uncheck_actions(triggered, "Moving Northeast")
        self._not_idle()
        self._draw_new_animation(224)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self._context_menu(e)
        if e.button() == Qt.MouseButton.LeftButton:
            self._change_faction()
        else:
            return super(FE14SpriteContainer, self).mousePressEvent(e)

    def _context_menu(self, e: QMouseEvent):
        self._menu.exec_(QCursor().pos())

    def _uncheck_actions(self, triggered: bool, text: str):
        for action in self._menu.actions():
            action: QAction
            if triggered == True:
                if action.text() != text and action.isChecked():
                    action.setChecked(False)
            elif triggered == False:
                if action.text() == text:
                    action.setChecked(True)

    def _not_idle(self):
        self.blue._is_idle = False
        self.green._is_idle = False
        self.red._is_idle = False
        self.purple._is_idle = False

    def _draw_new_animation(self, y_pos):
        self.blue._current_frame.setX(0)
        self.green._current_frame.setX(0)
        self.red._current_frame.setX(0)
        self.purple._current_frame.setX(0)
        
        self.blue._current_frame.setY(y_pos)
        self.green._current_frame.setY(y_pos)
        self.red._current_frame.setY(y_pos)
        self.purple._current_frame.setY(y_pos)

    def _change_faction(self):
        if self.blue.is_animating():
            self.blue.animation_off()
            self.blue.setVisible(False)

            self.green.animation_on()
            self.green.setVisible(True)

        elif self.green.is_animating():
            self.green.animation_off()
            self.green.setVisible(False)

            self.red.animation_on()
            self.red.setVisible(True)

        elif self.red.is_animating():
            self.red.animation_off()
            self.red.setVisible(False)

            self.purple.animation_on()
            self.purple.setVisible(True)

        elif self.purple.is_animating():
            self.purple.animation_off()
            self.purple.setVisible(False)

            self.blue.animation_on()
            self.blue.setVisible(True)

# self.gs.project.game == Game.FE13
class FE13SpriteContainer(QGraphicsScene):
    def __init__(self):
        super(FE13SpriteContainer, self).__init__()
        self._menu = QMenu()
        idle_action = QAction('Idle', self)
        use_action = QAction('Use', self)
        moving_west_action = QAction('Moving West', self)
        moving_east_action = QAction('Moving East', self)
        moving_south_action = QAction('Moving South', self)
        moving_north_action = QAction('Moving North', self)
        moving_southwest_action = QAction('Moving Southwest', self)
        moving_southeast_action = QAction('Moving Southeast', self)
        moving_northwest_action = QAction('Moving Northwest', self)
        moving_northeast_action = QAction('Moving Northeast', self)

        idle_action.setCheckable(True)
        use_action.setCheckable(True)
        moving_west_action.setCheckable(True)
        moving_east_action.setCheckable(True)
        moving_south_action.setCheckable(True)
        moving_north_action.setCheckable(True)
        moving_southwest_action.setCheckable(True)
        moving_southeast_action.setCheckable(True)
        moving_northwest_action.setCheckable(True)
        moving_northeast_action.setCheckable(True)

        idle_action.setChecked(True)        
        self._menu.addAction(idle_action)
        self._menu.addAction(use_action)
        self._menu.addAction(moving_west_action)
        self._menu.addAction(moving_east_action)
        self._menu.addAction(moving_south_action)
        self._menu.addAction(moving_north_action)
        self._menu.addAction(moving_southwest_action)
        self._menu.addAction(moving_southeast_action)
        self._menu.addAction(moving_northwest_action)
        self._menu.addAction(moving_northeast_action)

        idle_action.triggered.connect(self._idle_action)
        use_action.triggered.connect(self._use_action)
        moving_west_action.triggered.connect(self._moving_west_action)
        moving_east_action.triggered.connect(self._moving_east_action)
        moving_south_action.triggered.connect(self._moving_south_action)
        moving_north_action.triggered.connect(self._moving_north_action)
        moving_southwest_action.triggered.connect(self._moving_southwest_action)
        moving_southeast_action.triggered.connect(self._moving_southeast_action)
        moving_northwest_action.triggered.connect(self._moving_northwest_action)
        moving_northeast_action.triggered.connect(self._moving_northeast_action)

    def load_sprite(
        self, 
        blue: FE13UnitSpriteItem, 
        green: FE13UnitSpriteItem, 
        red: FE13UnitSpriteItem
        ):
        """Load unit sprite factions"""

        self.blue = blue
        self.green = green
        self.red = red
        
        # Bless pointers
        self.addItem(self.blue)
        self.addItem(self.green)
        self.addItem(self.red)

        # Default color will be blue
        if not blue.isVisible():
            self.blue.setVisible(True)
        if self.green.isVisible():
            self.green.setVisible(False)
        if self.red.isVisible():
            self.red.setVisible(False)

        if not blue.is_animating():
            self.blue.animation_on()
        if self.green.is_animating():
            self.green.animation_off()
        if self.red.is_animating():
            self.red.animation_off()

    @QtCore.Slot(bool)
    def _idle_action(self, triggered):
        self._uncheck_actions(triggered, "Idle")
        self._draw_new_animation(0)

    @QtCore.Slot(bool)
    def _use_action(self, triggered):
        self._uncheck_actions(triggered, "Use")
        self._draw_new_animation(32)

    @QtCore.Slot(bool)
    def _moving_west_action(self, triggered):
        self._uncheck_actions(triggered, "Moving West")
        self._draw_new_animation(64)

    @QtCore.Slot(bool)
    def _moving_east_action(self, triggered):
        self._uncheck_actions(triggered, "Moving East")
        self._draw_new_animation(96)


    @QtCore.Slot(bool)
    def _moving_south_action(self, triggered):
        self._uncheck_actions(triggered, "Moving South")
        self._draw_new_animation(128)


    @QtCore.Slot(bool)
    def _moving_north_action(self, triggered):
        self._uncheck_actions(triggered, "Moving North")
        self._draw_new_animation(160)

    @QtCore.Slot(bool)
    def _moving_southwest_action(self, triggered):
        self._uncheck_actions(triggered, "Moving Southwest")
        self._draw_new_animation(192)

    @QtCore.Slot(bool)
    def _moving_southeast_action(self, triggered):
        self._uncheck_actions(triggered, "Moving Southeast")
        self._draw_new_animation(224)

    @QtCore.Slot(bool)
    def _moving_northwest_action(self, triggered):
        self._uncheck_actions(triggered, "Moving Northwest")
        self._draw_new_animation(256)

    @QtCore.Slot(bool)
    def _moving_northeast_action(self, triggered):
        self._uncheck_actions(triggered, "Moving Northeast")
        self._draw_new_animation(288)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self._context_menu(e)
        if e.button() == Qt.MouseButton.LeftButton:
            self._change_faction()
        else:
            return super(FE13SpriteContainer, self).mousePressEvent(e)

    def _context_menu(self, e: QMouseEvent):
        self._menu.exec_(QCursor().pos())

    def _uncheck_actions(self, triggered: bool, text: str):
        for action in self._menu.actions():
            action: QAction
            if triggered == True:
                if action.text() != text and action.isChecked():
                    action.setChecked(False)
            elif triggered == False:
                if action.text() == text:
                    action.setChecked(True)

    def _draw_new_animation(self, y_pos):
        self.blue._current_frame.setX(0)
        self.green._current_frame.setX(0)
        self.red._current_frame.setX(0)
        
        self.blue._current_frame.setY(y_pos)
        self.green._current_frame.setY(y_pos)
        self.red._current_frame.setY(y_pos)

    def _change_faction(self):
        if self.blue.is_animating():
            self.blue.animation_off()
            self.blue.setVisible(False)

            self.green.animation_on()
            self.green.setVisible(True)

        elif self.green.is_animating():
            self.green.animation_off()
            self.green.setVisible(False)

            self.red.animation_on()
            self.red.setVisible(True)

        elif self.red.is_animating():
            self.red.animation_off()
            self.red.setVisible(False)

            self.blue.animation_on()
            self.blue.setVisible(True)
