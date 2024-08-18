from PySide6.QtWidgets import QPlainTextEdit

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class StringMultiLineEdit(AbstractAutoWidget, QPlainTextEdit):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        QPlainTextEdit.__init__(self)
        self.rid = None
        self.field_id = field_id
        self.textChanged.connect(self._on_edit)

    def set_target(self, rid):
        self.rid = rid
        if rid:
            text = self.data.string(rid, self.field_id)
            if text:
                text = text.replace("\\n", "\n")
            self.setPlainText(text)
        else:
            self.clear()
        self.setEnabled(rid is not None)

    def _on_edit(self):
        if self.rid:
            text = self.toPlainText()
            text = text.replace("\n", "\\n") if text else None
            self.data.set_string(self.rid, self.field_id, text)
