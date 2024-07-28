import dataclasses
from typing import Dict

from PySide6.QtGui import QColor
from pydantic import BaseModel


@dataclasses.dataclass
class ExaltColorTheme:
    background: QColor
    primary_text: QColor
    secondary_text: QColor
    keyword: QColor
    string: QColor
    comment: QColor
    annotation: QColor
    error: QColor
    warning: QColor


EXALT_COLOR_THEMES: Dict[str, ExaltColorTheme] = {
    "Catppuccin (Mocha)": ExaltColorTheme(
        background=QColor.fromString("#1e1e2e"),
        primary_text=QColor.fromString("#cdd6f4"),
        secondary_text=QColor.fromString("#7f849c"),
        keyword=QColor.fromString("#cba6f7"),
        string=QColor.fromString("#a6e3a1"),
        comment=QColor.fromString("#9399b2"),
        annotation=QColor.fromString("#f9e2af"),
        error=QColor.fromString("#f38ba8"),
        warning=QColor.fromString("#f9e2af"),
    ),
    "Dracula": ExaltColorTheme(
        background=QColor.fromString("#282a36"),
        primary_text=QColor.fromString("#f8f8f2"),
        secondary_text=QColor.fromString("#6272a4"),
        keyword=QColor.fromString("#ff79c6"),
        string=QColor.fromString("#f1fa8c"),
        comment=QColor.fromString("#6272a4"),
        annotation=QColor.fromString("#8be9fd"),
        error=QColor.fromString("#ff5555"),
        warning=QColor.fromString("#f1fa8c"),
    ),
    "One Dark": ExaltColorTheme(
        background=QColor.fromString("#282c34"),
        primary_text=QColor.fromString("#abb2bf"),
        secondary_text=QColor.fromString("#4b5263"),
        keyword=QColor.fromString("#c678dd"),
        string=QColor.fromString("#98c379"),
        comment=QColor.fromString("#5c6370"),
        annotation=QColor.fromString("#61afef"),
        error=QColor.fromString("#be5046"),
        warning=QColor.fromString("#d19a66"),
    ),
}


class ExaltScriptEditorConfig(BaseModel):
    auto_complete_parentheses: bool = True
    auto_skip_closing_parentheses: bool = True
    highlight_errors_and_warnings: bool = True
    offer_code_completions: bool = True
    color_theme: str = "One Dark"

    def get_color_theme(self) -> ExaltColorTheme:
        if theme := EXALT_COLOR_THEMES.get(self.color_theme):
            return theme
        return EXALT_COLOR_THEMES["One Dark"]
