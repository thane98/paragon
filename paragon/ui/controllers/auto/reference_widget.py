from PySide2 import QtCore
from PySide2.QtWidgets import QComboBox

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class ReferenceWidget(AbstractAutoWidget, QComboBox):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        QComboBox.__init__(self)
        self.setStyleSheet("combobox-popup: 0;")
        self.field_id = field_id
        self.rid = None

        fm = state.field_metadata[field_id]
        table_rid, table_field_id = self.data.table(fm["table"])
        self.model = self.gs.models.get(table_rid, table_field_id)
        self.setModel(self.model)

        if self.model:
            pixmap = self.itemData(0, QtCore.Qt.DecorationRole)
            if pixmap:
                self.setIconSize(pixmap.size())

        self.currentIndexChanged.connect(self._on_edit)

    def set_target(self, rid):
        self.rid = rid
        if self.rid:
            target_rid = self.data.rid(rid, self.field_id)
            found = False
            for i in range(0, self.model.rowCount()):
                index = self.model.index(i, 0)
                if self.model.data(index, QtCore.Qt.UserRole) == target_rid:
                    self.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.setCurrentIndex(-1)
        else:
            self.setCurrentIndex(-1)
        self.setEnabled(self.rid is not None)

    def _on_edit(self):
        if self.rid:
            self.data.set_rid(self.rid, self.field_id, self.currentData())
