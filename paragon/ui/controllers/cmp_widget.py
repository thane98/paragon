from pathlib import Path
from typing import Optional

from PySide2.QtWidgets import QFileDialog

from paragon.model.cmp_file_model import CmpFileModel
from paragon.ui.views.ui_cmp_widget import Ui_CmpWidget


class CmpWidget(Ui_CmpWidget):
    def __init__(self, gd):
        super().__init__()
        self.model: Optional[CmpFileModel] = None
        self.gd = gd

        self.new_file_button.clicked.connect(self._on_new_file)
        self.delete_file_button.clicked.connect(self._on_delete_file)
        self.replace_file_button.clicked.connect(self._on_replace_file)
        self.extract_file_button.clicked.connect(self._on_extract_file)

    def set_target(self, archive: Optional[str]):
        self.model = CmpFileModel(self.gd, archive) if archive else None
        self.file_list.setModel(self.model)

    def _refresh(self):
        self.new_file_button.setEnabled(self.model is not None)
        self.delete_file_button.setEnabled(self.file_list.currentIndex().isValid())
        self.replace_file_button.setEnabled(self.file_list.currentIndex().isValid())
        self.extract_file_button.setEnabled(self.file_list.currentIndex().isValid())

    def _on_new_file(self):
        path, ok = QFileDialog.getOpenFileName()
        if ok:
            with open(path, "rb") as f:
                contents = f.read()
            filename = Path(path).name
            print(filename)
            self.model.write_file(filename, contents)

    def _on_delete_file(self):
        self.model.delete_file(self._get_current_file())

    def _on_extract_file(self):
        filename = self._get_current_file()
        ext_filter = "*" + Path(filename).suffix if Path(filename).suffix else None
        destination_path, ok = QFileDialog.getSaveFileName(self, "Save File", filename, ext_filter)
        if ok:
            self.model.extract_file(filename, destination_path)

    def _on_replace_file(self):
        path, ok = QFileDialog.getOpenFileName()
        if ok:
            with open(path, "rb") as f:
                contents = f.read()
            filename = Path(path).name
            print(filename)
            self.model.write_file(self._get_current_file(), contents)

    def _get_current_file(self):
        return self.model.data(self.file_list.currentIndex())
