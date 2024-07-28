from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QGridLayout,
    QStyle,
)

from paragon.model.exalt_script_editor_config import ExaltScriptEditorConfig
from paragon.ui.controllers.exalt_script_text_edit import ExaltScriptTextEdit
from paragon.ui.views import layouts


class Ui_ExaltScriptTab(QWidget):
    def __init__(self, game_data, config: ExaltScriptEditorConfig, parent=None):
        super().__init__(parent)

        self.find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)

        self.find_line_edit = QLineEdit()
        self.find_line_edit.setPlaceholderText("Search...")
        self.find_label = QLabel()
        self.find_label.setMinimumWidth(100)

        self.find_prev_button = QPushButton()
        self.find_prev_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        )
        self.find_next_button = QPushButton()
        self.find_next_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        )

        find_layout = layouts.make_hbox(
            [self.find_prev_button, self.find_next_button, self.find_label],
            margins=False,
        )

        self.replace_line_edit = QLineEdit()
        self.replace_line_edit.setPlaceholderText("Replace with...")
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")

        replace_layout = layouts.make_hbox(
            [self.replace_button, self.replace_all_button], margins=False
        )

        self.find_replace_grid = QGridLayout()
        self.find_replace_grid.setContentsMargins(0, 0, 0, 0)
        self.find_replace_grid.addWidget(self.find_line_edit, 0, 0)
        self.find_replace_grid.addWidget(layouts.wrap_layout(find_layout), 0, 1)
        self.find_replace_grid.addWidget(self.replace_line_edit, 1, 0)
        self.find_replace_grid.addWidget(layouts.wrap_layout(replace_layout), 1, 1)
        self.find_replace_grid.setColumnStretch(0, 1)
        self.find_replace_grid.setColumnStretch(1, 0)

        self.editor = ExaltScriptTextEdit(game_data, config)

        self.find_replace_panel = QWidget()
        self.find_replace_panel.setContentsMargins(0, 0, 0, 0)
        self.find_replace_panel.setLayout(self.find_replace_grid)
        self.find_replace_panel.hide()

        self.setLayout(
            layouts.make_vbox([self.find_replace_panel, self.editor], margins=False)
        )
