from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QComboBox, QAction, QMenu

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class ReferenceWidget(AbstractAutoWidget, QComboBox):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QComboBox.__init__(self)
        self.setStyleSheet("combobox-popup: 0;")
        self.field_id = field_id
        self.rid = None
        self.table_is_part_of_multi = spec.multi

        fm = state.field_metadata[field_id]
        self.table = fm["table"]

        if not self.table_is_part_of_multi:
            table_rid, table_field_id = self.data.table(fm["table"])
            model = self.gs.models.get(table_rid, table_field_id)
            self.set_model(model)

        if spec.width:
            self.setMinimumWidth(spec.width)
        else:
            self.setMinimumWidth(150)

        self.setContextMenuPolicy(QtGui.Qt.CustomContextMenu)

        self.customContextMenuRequested.connect(self._on_context_menu_requested)
        self.currentIndexChanged.connect(self._on_edit)

    def _on_context_menu_requested(self, pos):
        menu = QMenu()
        clear_action = QAction("Clear Selection")
        menu.addAction(clear_action)
        action = menu.exec_(self.mapToGlobal(pos))
        if action == clear_action:
            self.setCurrentIndex(-1)

    def update_model_for_multi(self, multi_id, multi_key):
        table_rid, table_field_id = self.data.multi_table(
            multi_id, multi_key, self.table
        )
        model = self.gs.models.get(table_rid, table_field_id)
        self.set_model(model)

    def set_model(self, model):
        self.rid = None  # Invalidate target when changing out models.
        self.setModel(model)

    def set_target(self, rid):
        self.rid = rid
        self.blockSignals(True)
        try:
            if self.rid:
                target_rid = self.data.rid(rid, self.field_id)
                found = False
                for i in range(0, self.model().rowCount()):
                    index = self.model().index(i, 0)
                    if self.model().data(index, QtCore.Qt.UserRole) == target_rid:
                        self.setCurrentIndex(i)
                        self.setCurrentText(self.model().data(index, QtCore.Qt.DisplayRole))
                        found = True
                        break
                if not found:
                    self.setCurrentIndex(-1)
            else:
                self.setCurrentIndex(-1)
        finally:
            self.blockSignals(False)
        self.setEnabled(self.rid is not None)

    def _on_edit(self):
        if self.rid:
            self.data.set_rid(self.rid, self.field_id, self.currentData())
            print("Check?")
