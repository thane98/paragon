import itertools
from pathlib import Path

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import (
    QSyntaxHighlighter,
    QTextDocument,
    QTextCharFormat,
    QColorConstants,
    QFont,
    QColor,
)

from paragon.model.exalt_script_editor_config import (
    ExaltColorTheme,
    ExaltScriptEditorConfig,
)

KEYWORDS = [
    "alias",
    "array",
    "break",
    "event",
    "callback",
    "const",
    "def",
    "func",
    "goto",
    "else",
    "enum",
    "extern",
    "for",
    "if",
    "include",
    "label",
    "let",
    "match",
    "printf",
    "return",
    "static",
    "struct",
    "while",
    "yield",
]


class ExaltSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(
        self,
        document: QTextDocument,
        config: ExaltScriptEditorConfig,
        game_data,
        script_node,
    ):
        super().__init__(document)

        self.config = config
        self.errors = []
        self.warnings = []
        self.blocks_with_errors_or_warnings = []
        self.script_node = script_node
        self.game_data = game_data

        self.error_color: QColor = QColor()
        self.warning_color: QColor = QColor()

        self.keywords = QRegularExpression(
            "|".join(map(lambda w: f"\\b{w}\\b", KEYWORDS))
        )
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColorConstants.Magenta)
        self.keyword_format.setFontWeight(QFont.Weight.Bold.value)

        self.strings = QRegularExpression('"[^"]*"')
        self.strings_format = QTextCharFormat()
        self.strings_format.setForeground(QColorConstants.DarkGreen)

        self.comments = QRegularExpression("(//|#)(.*)")
        self.comments_format = QTextCharFormat()
        self.comments_format.setForeground(QColorConstants.DarkGray)

        self.annotations = QRegularExpression("@\\w+")
        self.annotations_format = QTextCharFormat()
        self.annotations_format.setForeground(QColorConstants.Cyan)

        self.clear_format = QTextCharFormat()

        self.rules = [
            (self.keywords, self.keyword_format),
            (self.annotations, self.annotations_format),
            (self.strings, self.strings_format),
            (self.comments, self.comments_format),
        ]

    def set_color_theme(self, theme: ExaltColorTheme):
        self.error_color = theme.error
        self.warning_color = theme.warning
        self.keyword_format.setForeground(theme.keyword)
        self.strings_format.setForeground(theme.string)
        self.comments_format.setForeground(theme.comment)
        self.annotations_format.setForeground(theme.annotation)

    @staticmethod
    def _make_error_format(message: str):
        error_format = QTextCharFormat()
        error_format.setBackground(QColorConstants.Red)
        error_format.setToolTip(message)
        return error_format

    @staticmethod
    def _make_warning_format(message: str):
        warning_format = QTextCharFormat()
        warning_format.setBackground(QColorConstants.DarkYellow)
        warning_format.setToolTip(message)
        return warning_format

    def _is_same_file(self, diagnostic) -> bool:
        if diagnostic.location:
            diagnostic_node = self.game_data.get_script_node_from_path(
                diagnostic.location.file
            )
            return diagnostic_node == self.script_node
        else:
            return False

    def highlight_errors_and_warnings(self, errors, warnings):
        document = self.document()
        self.errors = [d for d in errors if self._is_same_file(d)]
        self.warnings = [d for d in warnings if self._is_same_file(d)]
        for block in self.blocks_with_errors_or_warnings:
            self.rehighlightBlock(block)

        if self.config.highlight_errors_and_warnings:
            self.blocks_with_errors_or_warnings = []
            for diagnostic in itertools.chain(self.errors, self.warnings):
                if diagnostic.location:
                    block = document.findBlock(diagnostic.location.span[0])
                    if block:
                        self.rehighlightBlock(block)
                        self.blocks_with_errors_or_warnings.append(block)

        # These variables are only used to get the diagnostics into highlightBlock.
        # You might think leaving them populated for rehighlights would be useful,
        # but in practice this leads to incorrectly flagging errors in the wrong
        # block because text positions change.
        self.errors = []
        self.warnings = []

    def highlightBlock(self, text):
        block_position = self.currentBlock().position()
        self.setFormat(0, len(text), self.clear_format)
        for rule, text_format in self.rules:
            matches = rule.globalMatch(text)
            while matches.hasNext():
                current_match = matches.next()
                self.setFormat(
                    current_match.capturedStart(),
                    current_match.capturedLength(),
                    text_format,
                )
        for error in self.errors:
            if error.location and self.currentBlock().contains(error.location.span[0]):
                self.setFormat(
                    error.location.span[0] - block_position,
                    error.location.span[1] - error.location.span[0],
                    self._make_error_format(error.message),
                )
        for warning in self.warnings:
            if warning.location and self.currentBlock().contains(
                warning.location.span[0]
            ):
                self.setFormat(
                    warning.location.span[0] - block_position,
                    warning.location.span[1] - warning.location.span[0],
                    self._make_warning_format(warning.message),
                )
