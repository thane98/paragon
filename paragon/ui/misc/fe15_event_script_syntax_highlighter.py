from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor


class FE15EventScriptHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text) -> None:
        keyword_format = QTextCharFormat()
        keyword_format.setFontWeight(QFont.Bold)
        keyword_format.setForeground(QColor.fromRgb(0xC6, 0x78, 0xDD))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor.fromRgb(0xE5, 0xC0, 0x7B))

        sequence_reg_exp = QRegularExpression(
            "(\\bsequence\\b)|(\\bif\\b)|(\\bif\\()|null"
        )
        index = sequence_reg_exp.indexIn(text)
        while index >= 0:
            length = sequence_reg_exp.matchedLength()
            # Hack to deal with matching if(
            if length == 3:
                length -= 1
            self.setFormat(index, length, keyword_format)
            index = sequence_reg_exp.indexIn(text, index + length)

        string_reg_exp = QRegularExpression('"[^"]*"')
        index = string_reg_exp.indexIn(text)
        while index >= 0:
            length = string_reg_exp.matchedLength()
            self.setFormat(index, length, string_format)
            index = string_reg_exp.indexIn(text, index + length)
