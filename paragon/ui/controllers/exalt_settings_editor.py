from paragon.model.exalt_script_editor_config import (
    ExaltScriptEditorConfig,
    EXALT_COLOR_THEMES,
)
from paragon.ui.views.ui_exalt_settings_editor import (
    Ui_ExaltSettingsEditor,
)


class ExaltSettingsEditor(Ui_ExaltSettingsEditor):
    def __init__(self, config: ExaltScriptEditorConfig, parent=None):
        super().__init__(parent)

        self.config = config

        for i, color_theme in enumerate(EXALT_COLOR_THEMES):
            if color_theme == self.config.color_theme:
                self.color_theme_combobox.setCurrentIndex(i)
                break
        self.highlight_errors_and_warnings_checkbox.setChecked(
            config.highlight_errors_and_warnings
        )
        self.auto_complete_parentheses_checkbox.setChecked(
            config.auto_complete_parentheses
        )
        self.auto_skip_closing_parentheses_checkbox.setChecked(
            config.auto_skip_closing_parentheses
        )

        self.color_theme_combobox.currentTextChanged.connect(
            self._on_color_theme_changed
        )
        self.offer_code_completions_checkbox.checkStateChanged.connect(
            self._on_offer_code_completions_changed
        )
        self.highlight_errors_and_warnings_checkbox.checkStateChanged.connect(
            self._on_highlight_errors_and_warnings_changed
        )
        self.auto_complete_parentheses_checkbox.checkStateChanged.connect(
            self._on_auto_complete_parentheses_changed
        )
        self.auto_skip_closing_parentheses_checkbox.checkStateChanged.connect(
            self._on_auto_skip_closing_parentheses_changed
        )

    def _on_color_theme_changed(self, color_theme: str):
        self.config.color_theme = color_theme

    def _on_offer_code_completions_changed(self):
        self.config.offer_code_completions = (
            self.offer_code_completions_checkbox.isChecked()
        )

    def _on_highlight_errors_and_warnings_changed(self):
        self.config.highlight_errors_and_warnings = (
            self.highlight_errors_and_warnings_checkbox.isChecked()
        )

    def _on_auto_complete_parentheses_changed(self):
        self.config.auto_complete_parentheses = (
            self.auto_complete_parentheses_checkbox.isChecked()
        )

    def _on_auto_skip_closing_parentheses_changed(self):
        self.config.auto_skip_closing_parentheses = (
            self.auto_skip_closing_parentheses_checkbox.isChecked()
        )
