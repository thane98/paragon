from PySide2.QtWidgets import QLineEdit

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class StringLineEdit(AbstractAutoWidget, QLineEdit):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        QLineEdit.__init__(self)
        self.rid = None
        self.field_id = field_id
        self.textChanged.connect(self._on_edit)

    def set_target(self, rid):
        self.rid = rid
        if rid:
            self.setText(self.data.string(rid, self.field_id))
        else:
            self.clear()
        self.setEnabled(rid is not None)

    def _on_edit(self):
        if self.rid:
            text = self.text() if self.text() else None
            self.data.set_string(self.rid, self.field_id, text)
