
from PySide6.QtGui import (
    QSyntaxHighlighter,
    QTextDocument,
    QTextCharFormat,
    QColorConstants,
    QFont,
    QColor
)
from PySide6.QtCore import (
    QRegularExpression, 
    QStringListModel, 
)

from paragon.core.dialogue.fe10_script_parser import Fe10ScriptParser 


class FE10DialogueHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)


        self.all_format = QTextCharFormat()
        self.all_format.setForeground(QColorConstants.Magenta)

        self.controlcode_format = QTextCharFormat()
        self.controlcode_format.setForeground(QColorConstants.Svg.aquamarine)

        self.args_format = QTextCharFormat()
        self.args_format.setForeground(QColorConstants.Svg.khaki)
        
        self.expression = QRegularExpression(
            r"(\[.*?\])"
        )

        self.test_expression = QRegularExpression(
            fr"\[({'|'.join(Fe10ScriptParser().function_dict.keys())})(.*?)\]"
            )

    def highlightBlock(self, text):
        test_matches = self.test_expression.globalMatch(text)
        while test_matches.hasNext():
            test_match = test_matches.next()
            captured_texts = test_match.capturedTexts()
            
            self.setFormat(
                test_match.capturedStart(0), 
                test_match.capturedLength(0), 
                self.all_format)
            
            self.setFormat(
                test_match.capturedStart(1), 
                test_match.capturedLength(1), 
                self.controlcode_format)

            for i in range(2, len(captured_texts)):
                text = captured_texts[i]
                if text != '':
                    self.setFormat(
                        test_match.capturedStart(i), 
                        test_match.capturedLength(i), 
                        self.args_format)
