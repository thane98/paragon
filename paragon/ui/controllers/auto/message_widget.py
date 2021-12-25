from PySide2 import QtCore

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.views.ui_message_widget import Ui_MessageWidget


class MessageWidget(AbstractAutoWidget, Ui_MessageWidget):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        Ui_MessageWidget.__init__(self)
        self.field_id = field_id
        self.rid = None
        self.current_path = None
        self.no_write_back = False

        fm = state.field_metadata[field_id]
        self.paths = fm["paths"]
        self.localized = fm["localized"]

        self.key.textChanged.connect(self.refresh_value, QtCore.Qt.UniqueConnection)
        self.key.editingFinished.connect(self._save_key, QtCore.Qt.UniqueConnection)
        self.value.textChanged.connect(
            self._on_value_changed, QtCore.Qt.UniqueConnection
        )

    def _find_path(self, key):
        self.current_path = None
        if key:
            for path in self.paths:
                if self.data.has_message(path, self.localized, key):
                    self.current_path = path
                    break
            if not self.current_path:
                self.current_path = self.paths[0]

    def _on_value_changed(self, text: str):
        if self.rid and self.current_path:
            key = self.key.text()
            if not self.no_write_back:
                self.data.set_message(self.current_path, self.localized, key, text)

    def _save_key(self):
        if self.rid:
            key = self.key.text() if self.key.text() else None
            self.data.set_string(self.rid, self.field_id, key)

    def set_target(self, rid):
        self.rid = rid
        self.no_write_back = True
        try:
            if self.rid:
                self.key.setText(self.data.string(rid, self.field_id))
                self.refresh_value()
            else:
                self.key.clear()
                self.value.clear()
            self.setEnabled(rid is not None)
        finally:
            self.no_write_back = False

    def refresh_value(self):
        key = self.key.text()
        self._find_path(key)
        if not self.current_path or not self.rid or not key:
            self.value.clear()
            return
        self.value.setText(self.data.message(self.current_path, self.localized, key))
