from typing import Optional
from PySide6.QtWidgets import QFileDialog
from paragon.ui.views.ui_file_selector import Ui_FileSelector


class FileSelector(Ui_FileSelector):
    def __init__(self, placeholder_text=None, parent=None):
        super().__init__(parent)
        self.line_edit.setPlaceholderText(placeholder_text)
        self.open_dialog_button.clicked.connect(self._on_open_dialog_clicked)

    @property
    def text(self):
        return self.line_edit.text()

    @property
    def selection_changed(self):
        return self.line_edit.textChanged

    def set_text(self, text: Optional[str]):
        self.line_edit.setText(text)

    def _on_open_dialog_clicked(self):
        dialog = QFileDialog()
        f = dialog.getExistingDirectory(parent=self, caption="Select a directory...")
        if f:
            self.set_text(f)
