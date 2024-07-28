from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QCheckBox, QDialog

from paragon.model.exalt_script_editor_config import EXALT_COLOR_THEMES
from paragon.ui.views import layouts


class Ui_ExaltSettingsEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Paragon - Script Editor Settings")
        self.setWindowIcon(QIcon("paragon.ico"))

        self.color_theme_combobox = QComboBox()
        self.color_theme_combobox.addItems(list(EXALT_COLOR_THEMES.keys()))

        self.offer_code_completions_checkbox = QCheckBox()
        self.auto_complete_parentheses_checkbox = QCheckBox()
        self.auto_skip_closing_parentheses_checkbox = QCheckBox()
        self.highlight_errors_and_warnings_checkbox = QCheckBox()

        self.setLayout(
            layouts.make_form(
                [
                    ("Color Theme", self.color_theme_combobox),
                    ("Offer Code Completions", self.offer_code_completions_checkbox),
                    (
                        "Highlight Errors and Warnings",
                        self.highlight_errors_and_warnings_checkbox,
                    ),
                    (
                        "Auto Complete Parentheses",
                        self.auto_complete_parentheses_checkbox,
                    ),
                    (
                        "Auto Skip Closing Parentheses",
                        self.auto_skip_closing_parentheses_checkbox,
                    ),
                ]
            )
        )
