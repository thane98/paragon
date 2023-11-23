from PySide6 import QtCore
from PySide6.QtWidgets import QListWidgetItem

from paragon.ui import utils
from paragon.ui.views.ui_layered_dir_editor import Ui_LayeredDirEditor


class LayeredDirEditor(Ui_LayeredDirEditor):
    def __init__(self, ms, gs, has_sub_entries=False):
        super().__init__(has_sub_entries)
        self.ms = ms
        self.gs = gs
        self.gd = self.gs.data
        self.has_sub_entries = has_sub_entries

        self.setWindowTitle(self._get_window_title())
        for path in self._get_initial_model_items():
            item = QListWidgetItem()
            item.setText(path)
            item.setData(QtCore.Qt.UserRole, path)
            self.list_widget.addItem(item)

        self.list_widget.currentItemChanged.connect(self._on_file_selection_changed)
        self.entries_box.currentIndexChanged.connect(self._on_entry_selection_changed)
        self.editor.lostFocus.connect(self._on_save)

    def _get_initial_model_items(self):
        raise NotImplementedError

    def _get_window_title(self):
        raise NotImplementedError

    def _load_file(self, path):
        raise NotImplementedError

    def _load_entry(self, path, entry):
        raise NotImplementedError

    def _save(self, path, entry, text):
        raise NotImplementedError

    def _on_file_selection_changed(self):
        item = self.list_widget.currentItem()
        if item:
            try:
                path = item.data(QtCore.Qt.UserRole)
                data = self._load_file(path)
                self.entries_box.clear()
                self.entries_box.addItems(data)
            except:
                utils.error(self)
        enabled = self.entries_box.count() > 0
        self.entries_box.setEnabled(enabled)
        self.editor.setEnabled(enabled)
        if not enabled:
            self.editor.clear()

    def _on_entry_selection_changed(self):
        file_item = self.list_widget.currentItem()
        path = file_item.data(QtCore.Qt.UserRole) if file_item else None
        entry = self.entries_box.currentText()
        if path and entry:
            try:
                data = self._load_entry(path, entry)
                self.editor.setPlainText(data if data else "")
            except:
                utils.error(self)

    def _on_save(self):
        file_item = self.list_widget.currentItem()
        path = file_item.data(QtCore.Qt.UserRole) if file_item else None
        entry = self.entries_box.currentText()
        if path and entry:
            try:
                self._save(path, entry, self.editor.toPlainText())
                if entry == "PLACEHOLDER":
                    self.status_bar.showMessage(f"Saved path={path}", 5000)
                else:
                    self.status_bar.showMessage(
                        f"Saved path={path} entry={entry}", 5000
                    )
            except:
                utils.error(self)
                self.status_bar.showMessage("Encountered error during saving.", 10000)
