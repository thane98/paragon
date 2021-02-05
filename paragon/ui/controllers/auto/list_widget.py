from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel
from PySide2.QtWidgets import QInputDialog

from paragon.ui.controllers.advanced_copy_dialog import AdvancedCopyDialog
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.views.ui_list_widget import Ui_ListWidget


class ListWidget(AbstractAutoWidget, Ui_ListWidget):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        Ui_ListWidget.__init__(self)
        self.models = self.gs.models
        self.field_id = field_id
        self.rid = None
        self.dialog = None
        self.proxy_model = None

        fm = state.field_metadata[field_id]
        self.stored_type = fm["stored_type"]
        self.inner = state.generator.generate_for_type(fm["stored_type"])
        self.splitter.addWidget(self.inner)
        self.splitter.setStretchFactor(1, 1)

        self.add_action.triggered.connect(self._on_add)
        self.delete_action.triggered.connect(self._on_delete)
        self.copy_to_action.triggered.connect(self._on_copy_to)
        self.advanced_copy_action.triggered.connect(self._on_advanced_copy)
        self.search.textChanged.connect(self._on_search)

        self._update_buttons()

    def set_target(self, rid):
        self.rid = rid
        if rid:
            model = self.models.get(rid, self.field_id)
            self.proxy_model = QSortFilterProxyModel()
            self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
            self.proxy_model.setSourceModel(model)
            self.list.setModel(self.proxy_model)
            self.list.selectionModel().currentChanged.connect(self._on_select)
        else:
            self.list.setModel(None)
            self.proxy_model = None
        self._update_buttons()

    def _update_buttons(self):
        self.delete_action.setEnabled(self.list.currentIndex().isValid())
        self.copy_to_action.setEnabled(self.list.currentIndex().isValid())
        self.advanced_copy_action.setEnabled(self.list.currentIndex().isValid())
        self.add_action.setEnabled(self.list.model() is not None)

    def _on_search(self):
        if self.proxy_model:
            self.proxy_model.setFilterRegExp(self.search.text())

    def _on_select(self):
        if model := self.list.model():
            rid = model.data(self.list.currentIndex(), QtCore.Qt.UserRole)
            self.inner.set_target(rid)
        self._update_buttons()

    def _on_add(self):
        if self.rid:
            self.list.model().add_item()
            self._update_buttons()

    def _on_delete(self):
        if self.list.currentIndex().isValid():
            self.list.model().delete_item(self.list.currentIndex())
            self._update_buttons()

    def _on_copy_to(self):
        if not self.list.currentIndex().isValid():
            return
        choices = self._get_copy_choices()
        choice, ok = QInputDialog.getItem(
            self, "Select Destination", "Destination", choices, 0
        )
        if ok:
            model = self.list.model()
            index = choices.index(choice)
            source_rid = model.data(self.list.currentIndex(), QtCore.Qt.UserRole)
            dest_rid = model.data(model.index(index, 0), QtCore.Qt.UserRole)
            self.data.copy(source_rid, dest_rid, [])

    def _get_copy_choices(self):
        choices = []
        model = self.list.model()
        for i in range(0, model.rowCount()):
            choices.append(
                str(i + 1) + ". " + model.data(model.index(i, 0), QtCore.Qt.DisplayRole)
            )
        return choices

    def _on_advanced_copy(self):
        if not self.list.currentIndex().isValid():
            return
        model = self.list.model()
        source_rid = model.data(self.list.currentIndex(), QtCore.Qt.UserRole)
        self.dialog = AdvancedCopyDialog(
            self.data, self.list.model(), self.stored_type, source_rid
        )
        self.dialog.show()
