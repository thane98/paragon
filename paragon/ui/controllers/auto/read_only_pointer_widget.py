from PySide2 import QtCore
from PySide2.QtWidgets import QLineEdit

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class ReadOnlyPointerWidget(AbstractAutoWidget, QLineEdit):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        QLineEdit.__init__(self)
        self.field_id = field_id
        self.rid = None

        self.setReadOnly(True)

    def set_target(self, rid):
        self.rid = rid
        if self.rid:
            target_rid = self.data.rid(rid, self.field_id)
            if target_rid:
                self.setText(self.data.display(target_rid))
            else:
                self.setText(None)
        else:
            self.setText(None)

    def _on_edit(self):
        if self.rid:
            self.data.set_rid(self.rid, self.field_id, self.currentData())
