from PySide2.QtGui import QFont
from PySide2.QtWidgets import (
    QPlainTextEdit,
    QWidget,
    QPushButton,
    QStatusBar,
    QLabel,
    QVBoxLayout,
)

from paragon.ui.controllers.plain_text_edit_with_editing_finished_signal import (
    PlainTextEditWithEditingFinishedSignal,
)


class Ui_FE15EventScriptEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.editor = PlainTextEditWithEditingFinishedSignal()
        editor_font = QFont()
        editor_font.setPointSize(11)  # TODO: Make this configurable
        self.editor.setFont(editor_font)
        self.status_bar = QStatusBar()
        self.cursor_position_label = QLabel()
        self.status_bar.addPermanentWidget(self.cursor_position_label)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.editor)
        main_layout.addWidget(self.status_bar)

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
