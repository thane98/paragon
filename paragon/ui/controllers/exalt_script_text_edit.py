import math
from typing import Sequence

from PySide6 import QtGui, QtCore
from PySide6.QtCore import (
    QRect,
    Signal,
    QEvent,
    QMimeData,
    QKeyCombination,
    QRegularExpression,
    QStringListModel,
)
from PySide6.QtGui import (
    QPaintEvent,
    QPainter,
    QResizeEvent,
    QTextCursor,
    QKeyEvent,
    QFont,
    QPalette,
    QTextBlock,
)
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QToolTip, QCompleter

from paragon.model.exalt_script_editor_config import ExaltScriptEditorConfig

PAIR_COMPLETIONS = {
    QtGui.Qt.Key.Key_ParenLeft.value: ")",
    QtGui.Qt.Key.Key_BracketLeft.value: "]",
    QtGui.Qt.Key.Key_BraceLeft.value: "}",
    QtGui.Qt.Key.Key_QuoteDbl.value: '"',
}

CLOSING_CHARACTERS = {
    QtGui.Qt.Key.Key_ParenRight.value: ")",
    QtGui.Qt.Key.Key_BracketRight.value: "]",
    QtGui.Qt.Key.Key_BraceRight.value: "}",
    QtGui.Qt.Key.Key_QuoteDbl.value: '"',
}

NEWLINE_KEYS = {
    QtGui.Qt.Key.Key_Enter.value,
    QtGui.Qt.Key.Key_Return.value,
}

UNINDENT_KEY_COMBO = QKeyCombination(
    QtCore.Qt.KeyboardModifier.ShiftModifier, QtGui.Qt.Key.Key_Backtab
)
COMMENT_KEY_COMBO = QKeyCombination(
    QtCore.Qt.KeyboardModifier.ControlModifier, QtGui.Qt.Key.Key_Slash
)

IDENTIFIER_REGEX = QRegularExpression(r"[^\W0-9](::|\w|・|？)*")


class PlainTextEditWithLostFocusSignal(QPlainTextEdit):
    lostFocus = Signal()

    def focusOutEvent(self, e):
        self.lostFocus.emit()
        super().focusOutEvent(e)


class LineNumberArea(QWidget):
    def __init__(self, editor: "ExaltScriptTextEdit"):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> int:
        return self.editor.line_number_area_width()

    def paintEvent(self, event: QPaintEvent):
        self.editor.line_number_area_paint_event(event)


class ExaltScriptTextEdit(PlainTextEditWithLostFocusSignal):
    def __init__(self, game_data, config: ExaltScriptEditorConfig, parent=None):
        super().__init__(parent)

        self.config = config
        self.game_data = game_data

        self.completer = QCompleter()
        self.completer.activated.connect(self._insert_completion)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        self.setMouseTracking(True)
        font = QFont("monospace")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        font.setPointSize(12)
        self.setFont(font)
        self.setWordWrapMode(QtGui.QTextOption.WrapMode.NoWrap)
        self.setTabStopDistance(
            QtGui.QFontMetricsF(self.font()).horizontalAdvance(" ") * 4
        )

        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)

        self._update_line_number_area_width()

    def refresh_settings(self):
        palette = self.palette()
        palette.setColor(
            QPalette.ColorGroup.Active,
            QPalette.ColorRole.Base,
            self.config.get_color_theme().background,
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.Base,
            self.config.get_color_theme().background,
        )
        self.setPalette(palette)

    def keyPressEvent(self, event: QKeyEvent):
        if self.completer.popup().isVisible() and event.key() in [
            QtCore.Qt.Key.Key_Enter,
            QtCore.Qt.Key.Key_Return,
            QtCore.Qt.Key.Key_Up,
            QtCore.Qt.Key.Key_Down,
            QtCore.Qt.Key.Key_Tab,
            QtCore.Qt.Key.Key_Backtab,
        ]:
            event.ignore()
            return

        if self.config.auto_skip_closing_parentheses:
            if closing_character := CLOSING_CHARACTERS.get(event.key()):
                block = self.textCursor().block()
                block_pos = self.textCursor().position() - block.position()
                block_text = block.text()
                if (
                    block
                    and block_pos < len(block_text)
                    and block_text[block_pos] == closing_character
                ):
                    cursor = QTextCursor(self.document())
                    cursor.setPosition(self.textCursor().position() + 1)
                    self.setTextCursor(cursor)
                    event.accept()
                    return

        if event.key() == QtGui.Qt.Key.Key_Backspace:
            block = self.textCursor().block()
            indentation_length = len(block.text()) - len(block.text().lstrip())
            if indentation_length >= self.textCursor().positionInBlock() > 0:
                spaces_to_delete = self.textCursor().positionInBlock() % 4
                if spaces_to_delete == 0:
                    spaces_to_delete = 4
                for _ in range(0, spaces_to_delete):
                    self.textCursor().deletePreviousChar()
                event.accept()
                return

        if event.keyCombination() == COMMENT_KEY_COMBO:
            blocks = self._get_blocks_from_selection_range(
                self.textCursor().selectionStart(), self.textCursor().selectionEnd()
            )
            is_uncomment = ExaltScriptTextEdit._is_uncomment(blocks)
            cursor = QTextCursor(self.document())
            cursor.beginEditBlock()
            for block in blocks:
                if is_uncomment:
                    text = block.text()
                    whitespace = len(text) - len(text.lstrip())
                    whitespace_after_comment = False
                    if text.startswith("#", whitespace):
                        cursor.setPosition(block.position() + whitespace + 1)
                        cursor.deletePreviousChar()
                        whitespace_after_comment = text.startswith(" ", whitespace + 1)
                    if text.startswith("//", whitespace):
                        cursor.setPosition(block.position() + whitespace + 2)
                        cursor.deletePreviousChar()
                        cursor.deletePreviousChar()
                        whitespace_after_comment = text.startswith(" ", whitespace + 2)
                    if whitespace_after_comment:
                        cursor.setPosition(cursor.position() + 1)
                        cursor.deletePreviousChar()
                else:
                    cursor.setPosition(block.position())
                    cursor.insertText("# ")
            cursor.endEditBlock()
            event.accept()
            return

        if event.keyCombination() == UNINDENT_KEY_COMBO:
            blocks = self._get_blocks_from_selection_range(
                self.textCursor().selectionStart(), self.textCursor().selectionEnd()
            )
            cursor = QTextCursor(self.document())
            cursor.beginEditBlock()
            for block in blocks:
                text = block.text()
                i = 0
                while i < min(len(text), 4) and not text[i].strip():
                    i += 1
                cursor.setPosition(block.position(), QTextCursor.MoveMode.MoveAnchor)
                cursor.setPosition(
                    block.position() + i, QTextCursor.MoveMode.KeepAnchor
                )
                cursor.removeSelectedText()
            cursor.endEditBlock()
            event.accept()
            return

        if event.key() == QtGui.Qt.Key.Key_Tab:
            if self.textCursor().hasSelection():
                blocks = self._get_blocks_from_selection_range(
                    self.textCursor().selectionStart(), self.textCursor().selectionEnd()
                )
                cursor = QTextCursor(self.document())
                cursor.beginEditBlock()
                for block in blocks:
                    cursor.setPosition(block.position())
                    cursor.insertText(" " * 4)
                cursor.endEditBlock()
                event.accept()
                return
            else:
                self.insertPlainText(" " * 4)
                event.accept()
                return

        super().keyPressEvent(event)

        if self.config.auto_complete_parentheses:
            if completion := PAIR_COMPLETIONS.get(event.key()):
                self.insertPlainText(completion)
                cursor = QTextCursor(self.document())
                cursor.setPosition(self.textCursor().position() - len(completion))
                self.setTextCursor(cursor)
                return

        if event.key() in NEWLINE_KEYS:
            block_number = self.textCursor().blockNumber() - 1
            block = self.document().findBlockByNumber(block_number)
            if block.isValid():
                indentation_length = len(block.text()) - len(block.text().lstrip())
                self.insertPlainText(block.text()[:indentation_length])
                return

        if not self.config.offer_code_completions or not event.text().strip():
            return
        line = self.textCursor().block().text()[: self.textCursor().positionInBlock()]
        matches = IDENTIFIER_REGEX.globalMatch(line)
        cursor_position = self.textCursor().positionInBlock()
        show_popup = False
        while matches.hasNext():
            regex_match = matches.next()
            if (
                regex_match.capturedStart()
                <= cursor_position
                <= regex_match.capturedEnd()
            ):
                identifier = line[
                    regex_match.capturedStart() : regex_match.capturedEnd()
                ]
                if len(identifier) >= 2:
                    completions = self.game_data.suggest_script_completions(identifier)
                    self.completer.setModel(QStringListModel(completions))
                    self.completer.setCompletionPrefix(identifier)
                    popup = self.completer.popup()
                    popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
                    cr = self.cursorRect()
                    cr.setWidth(
                        max(self.completer.popup().sizeHintForColumn(0), 100)
                        + self.completer.popup().verticalScrollBar().sizeHint().width()
                    )
                    self.completer.complete(cr)
                    show_popup = True
                    break
        if not show_popup:
            self.completer.popup().hide()
            self.completer.setModel(QStringListModel())

    def _get_blocks_from_selection_range(self, start: int, end: int):
        start_block = self.document().findBlock(start)
        end_block = self.document().findBlock(end)
        blocks = [start_block]
        for i in range(start_block.blockNumber() + 1, end_block.blockNumber()):
            blocks.append(self.document().findBlockByNumber(i))
        if start_block.blockNumber() != end_block.blockNumber():
            blocks.append(end_block)
        return blocks

    @staticmethod
    def _is_uncomment(blocks: Sequence[QTextBlock]) -> bool:
        for block in blocks:
            text = block.text().strip()
            if text.startswith("#") or text.startswith("//"):
                return True
        return False

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.ToolTip:
            pos = event.pos()
            pos.setX(pos.x() - self.viewportMargins().left())
            pos.setY(pos.y() - self.viewportMargins().top())
            cursor = self.cursorForPosition(pos)

            # QTextCursor doesn't have a quicker way to get
            # highlighter-applied formats
            for fmt in cursor.block().layout().formats():
                if fmt.start <= cursor.positionInBlock() <= fmt.start + fmt.length:
                    cursor.setPosition(fmt.start)
                    cursor.setPosition(
                        fmt.start + fmt.length, QTextCursor.MoveMode.KeepAnchor
                    )
                    QToolTip.showText(
                        event.globalPos(),
                        fmt.format.toolTip(),
                        self,
                        self.cursorRect(cursor),
                    )
                    return True

        return super().event(event)

    def insertFromMimeData(self, source: QMimeData):
        self.insertPlainText(source.text().replace("\t", "    "))

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_width(self) -> int:
        digits = 1 if self.blockCount() == 0 else int(math.log10(self.blockCount())) + 1
        return max(60, 10 + self.fontMetrics().horizontalAdvance("9") * digits)

    def _update_line_number_area(self, rect: QRect, dy: int):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()

    def line_number_area_paint_event(self, event: QPaintEvent):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), self.palette().base())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            round(
                self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            )
        )
        bottom = top + int(round(self.blockBoundingRect(block).height()))
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(self.config.get_color_theme().secondary_text)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    QtGui.Qt.AlignmentFlag.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(round(self.blockBoundingRect(block).height()))
            block_number += 1

    def _update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _insert_completion(self, completion):
        # TODO: Revisit for ev:: and enum variants
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.MoveOperation.Left)
        tc.movePosition(QTextCursor.MoveOperation.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)
