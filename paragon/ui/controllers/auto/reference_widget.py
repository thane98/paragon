from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel
from PySide2.QtWidgets import QComboBox, QCompleter

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

        self.proxy = QSortFilterProxyModel()
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setModel(self.proxy)
        self.setEditable(True)

        if not self.table_is_part_of_multi:
            table_rid, table_field_id = self.data.table(fm["table"])
            model = self.gs.models.get(table_rid, table_field_id)
            self.set_model(model)

        self.search_completer = QCompleter()
        self.search_completer.setModel(self.proxy)
        self.search_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.search_completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.search_completer.setCompletionRole(QtCore.Qt.DisplayRole)
        self.setCompleter(self.search_completer)
        self.setInsertPolicy(QComboBox.NoInsert)

        if spec.width:
            self.setMinimumWidth(spec.width)
        else:
            self.setMinimumWidth(150)

        self.currentIndexChanged.connect(self._on_edit)

    def update_model_for_multi(self, multi_id, multi_key):
        table_rid, table_field_id = self.data.multi_table(
            multi_id, multi_key, self.table
        )
        model = self.gs.models.get(table_rid, table_field_id)
        self.set_model(model)

    def set_model(self, model):
        self.rid = None  # Invalidate target when changing out models.
        self.proxy.setSourceModel(model)

    def focusOutEvent(self, e) -> None:
        # TODO: Hack to deal with text getting cleared randomly.
        QComboBox.focusOutEvent(self, e)
        index = self.proxy.index(self.currentIndex(), 0)
        self.setCurrentText(self.proxy.data(index, QtCore.Qt.DisplayRole))

    def set_target(self, rid):
        self.rid = rid
        self.blockSignals(True)
        try:
            if self.rid:
                target_rid = self.data.rid(rid, self.field_id)
                found = False
                for i in range(0, self.proxy.rowCount()):
                    index = self.proxy.index(i, 0)
                    if self.proxy.data(index, QtCore.Qt.UserRole) == target_rid:
                        self.setCurrentIndex(i)
                        self.setCurrentText(self.proxy.data(index, QtCore.Qt.DisplayRole))
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
            index = self.proxy.index(self.currentIndex(), 0)
            self.setCurrentText(self.proxy.data(index, QtCore.Qt.DisplayRole))
