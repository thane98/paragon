from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.views.ui_message_widget import Ui_MessageWidget


class MessageWidget(AbstractAutoWidget, Ui_MessageWidget):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        Ui_MessageWidget.__init__(self)
        self.field_id = field_id
        self.rid = None
        self.current_path = None

        fm = state.field_metadata[field_id]
        self.paths = fm["paths"]
        self.localized = fm["localized"]

        self.key.textChanged.connect(self.refresh_value)
        self.key.editingFinished.connect(self._save_key)
        self.value.textChanged.connect(self._on_value_changed)

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
            self.data.set_message(self.current_path, self.localized, key, text)

    def _save_key(self):
        if self.rid:
            key = self.key.text() if self.key.text() else None
            self.data.set_string(self.rid, self.field_id, key)

    def set_target(self, rid):
        self.rid = rid
        if self.rid:
            self.key.setText(self.data.string(rid, self.field_id))
            self.refresh_value()
        else:
            self.key.clear()
            self.value.clear()
        self.setEnabled(rid is not None)

    def refresh_value(self):
        key = self.key.text()
        self._find_path(key)
        if not self.current_path or not self.rid or not key:
            self.value.clear()
            return
        self.value.setText(self.data.message(self.current_path, self.localized, key))
