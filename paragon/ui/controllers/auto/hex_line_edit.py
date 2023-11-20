from PySide6.QtWidgets import QLineEdit

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class HexLineEdit(AbstractAutoWidget, QLineEdit):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        QLineEdit.__init__(self)
        self.rid = None
        self.field_id = field_id
        self.textChanged.connect(self._on_edit)
        fm = state.field_metadata[field_id]
        self.length = fm["length"]
        self.setInputMask(" ".join(["HH"] * self.length) + ";0")

    def set_target(self, rid):
        self.rid = rid
        if self.rid:
            value = self.data.bytes(rid, self.field_id)
            self.setText(" ".join(map(lambda x: "%02X" % x, value)))
        else:
            self.setText("")
        self.setEnabled(self.rid is not None)

    def _on_edit(self):
        if self.rid:
            split_text = self.displayText().split()
            value = bytearray(map(lambda x: int(x, 16), split_text))
            self.data.set_bytes(self.rid, self.field_id, value)
