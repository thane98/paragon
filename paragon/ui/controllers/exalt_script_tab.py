import dataclasses
from typing import List, Optional

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QKeyEvent, QTextCursor, QTextDocument, QColor

from paragon.model.exalt_script_editor_config import (
    ExaltScriptEditorConfig,
)
from paragon.ui.misc.exalt_syntax_highlighter import ExaltSyntaxHighlighter
from paragon.ui.views.ui_exalt_script_tab import Ui_ExaltScriptTab


@dataclasses.dataclass
class ExaltScriptAnalysisResult:
    errors: List
    warnings: List


@dataclasses.dataclass
class PrettyDiagnosticLocation:
    file: Optional[str]
    line: int
    index: int


class ExaltScriptTab(Ui_ExaltScriptTab):
    analysis_complete = Signal(ExaltScriptAnalysisResult)

    def __init__(
        self, game_data, config: ExaltScriptEditorConfig, script_node, parent=None
    ):
        super().__init__(game_data, config, parent)

        # if script_node.kind() == "standard_library":
        #     self.editor.setReadOnly(True)

        self.script_node = script_node
        self.game_data = game_data
        self.config = config
        self.script_path: str = script_node.path
        self.highlighter = ExaltSyntaxHighlighter(
            self.editor.document(), config, game_data, script_node
        )

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(250)

        self.timer.timeout.connect(self.analyze)
        self.find_shortcut.activated.connect(self._on_find_shortcut_pressed)
        self.find_line_edit.returnPressed.connect(self._on_find_next)
        self.find_next_button.clicked.connect(self._on_find_next)
        self.find_prev_button.clicked.connect(self._on_find_prev)
        self.replace_line_edit.returnPressed.connect(self._on_replace_next_activated)
        self.replace_button.clicked.connect(self._on_replace_next_activated)
        self.replace_all_button.clicked.connect(self._on_replace_all_clicked)
        self.editor.textChanged.connect(self._on_find_data_changed)
        self.find_line_edit.textChanged.connect(self._on_find_data_changed)
        self.editor.lostFocus.connect(self.save)

        self.refresh_settings()
        self.editor.setPlainText(self.game_data.open_script(script_node))

    def refresh_settings(self):
        theme = self.config.get_color_theme()
        text_color = theme.primary_text.name(QColor.NameFormat.HexRgb)
        self.highlighter.set_color_theme(theme)
        self.highlighter.rehighlight()
        self.editor.refresh_settings()
        self.editor.setStyleSheet(f"QPlainTextEdit {{color: {text_color}}}")

    def keyReleaseEvent(self, event: QKeyEvent):
        if self.editor.hasFocus():
            self.timer.start()

    def analyze(self):
        if analysis := self.game_data.analyze_script(
            self.script_node, self.editor.toPlainText()
        ):
            errors = analysis.get_errors()
            warnings = analysis.get_warnings()
            self.highlighter.highlight_errors_and_warnings(errors, warnings)
            self.analysis_complete.emit(ExaltScriptAnalysisResult(errors, warnings))

    def cancel_analysis(self):
        self.timer.stop()

    def jump_to_diagnostic(self, diagnostic):
        if diagnostic.location:
            self.jump_to_location(diagnostic.location)

    def jump_to_location(self, location):
        cursor = QTextCursor(self.editor.document())
        cursor.setPosition(location.span[0])
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()
        self.editor.setFocus()

    def get_diagnostic_position(self, diagnostic) -> Optional[PrettyDiagnosticLocation]:
        if diagnostic.location:
            block = self.editor.document().findBlock(diagnostic.location.span[0])
            if block:
                return PrettyDiagnosticLocation(
                    diagnostic.location.file,
                    block.firstLineNumber() + 1,
                    diagnostic.location.span[1] - diagnostic.location.span[0],
                )
        return None

    def _on_find_shortcut_pressed(self):
        if self.find_replace_panel.isVisible():
            self.find_replace_panel.hide()
        else:
            self.find_replace_panel.show()
            self.find_line_edit.setFocus()

    def _on_find_data_changed(self):
        search = self.find_line_edit.text()
        if search:
            count = 0
            text = self.editor.toPlainText()
            start = text.find(search)
            while start != -1:
                count += 1
                start = text.find(search, start + len(search))
            self.find_label.setText(f"{count} results")
        else:
            self.find_label.setText("")

    def _on_find_prev(self):
        search = self.find_line_edit.text()
        if search:
            if not self._find_prev_from_cursor(search, self.editor.textCursor()):
                cursor = QTextCursor(self.editor.document())
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self._find_prev_from_cursor(search, cursor)

    def _find_prev_from_cursor(self, search: str, start_cursor: QTextCursor) -> bool:
        flags = (
            QTextDocument.FindFlag.FindCaseSensitively
            | QTextDocument.FindFlag.FindBackward
        )
        cursor = self.editor.document().find(search, start_cursor, flags)
        if not cursor.isNull():
            self.editor.setTextCursor(cursor)
            self.editor.centerCursor()
        return not cursor.isNull()

    def _on_find_next(self):
        search = self.find_line_edit.text()
        if search:
            if not self._find_next_from_cursor(search, self.editor.textCursor()):
                cursor = QTextCursor(self.editor.document())
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                self._find_next_from_cursor(search, cursor)

    def _find_next_from_cursor(self, search: str, start_cursor: QTextCursor) -> bool:
        cursor = self.editor.document().find(
            search,
            start_cursor,
            QTextDocument.FindFlag.FindCaseSensitively,
        )
        if not cursor.isNull():
            self.editor.setTextCursor(cursor)
            self.editor.centerCursor()
        return not cursor.isNull()

    def _on_replace_next_activated(self):
        search = self.find_line_edit.text()
        if search:
            replacement = self.replace_line_edit.text()
            cursor = self.editor.textCursor()
            if cursor.selectedText() == search:
                cursor.insertText(replacement)
            else:
                cursor = self.editor.document().find(
                    search,
                    self.editor.textCursor(),
                    QTextDocument.FindFlag.FindCaseSensitively,
                )
                if not cursor.isNull():
                    self.editor.setTextCursor(cursor)
                    self.editor.centerCursor()
                    cursor.insertText(replacement)
                    self.analyze()

    def _on_replace_all_clicked(self):
        if self.find_line_edit.text():
            text = self.editor.toPlainText()
            cursor = QTextCursor(self.editor.document())
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.insertText(
                text.replace(self.find_line_edit.text(), self.replace_line_edit.text())
            )
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.analyze()

    def save(self):
        self.game_data.update_script(self.script_node, self.editor.toPlainText())
