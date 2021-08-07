import logging

from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel, QModelIndex
from PySide2.QtWidgets import QInputDialog

from paragon.ui import utils
from paragon.ui.controllers.advanced_copy_dialog import AdvancedCopyDialog
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.views.ui_list_widget import Ui_ListWidget


class ListWidget(AbstractAutoWidget, Ui_ListWidget):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        Ui_ListWidget.__init__(self, spec.static_items, spec.orientation, spec.no_ids, spec.no_copies, spec.no_search)
        self.models = self.gs.models
        self.field_id = field_id
        self.rid = None
        self.dialog = None
        self.proxy_model = None

        fm = state.field_metadata[field_id]
        self.fixed_size = fm.get("fixed_size")
        self.stored_type = fm["stored_type"]
        self.inner = state.generator.generate_for_type(fm["stored_type"], state)
        self.inner.set_target(None)
        self.splitter.addWidget(self.inner)
        self.splitter.setStretchFactor(spec.stretch_index, 1)

        if spec.no_margins:
            self.setContentsMargins(0, 0, 0, 0)
            self.layout().setContentsMargins(0, 0, 0, 0)
        if self.fixed_size:
            self.tool_bar.setVisible(False)
            self.list.setDragEnabled(False)
            self.list.setAcceptDrops(False)
            self.list.setDropIndicatorShown(False)

        self.add_action.triggered.connect(self._on_add)
        self.delete_action.triggered.connect(self._on_delete)
        self.copy_to_action.triggered.connect(self._on_copy_to)
        self.advanced_copy_action.triggered.connect(self._on_advanced_copy)
        self.deselect_shortcut.activated.connect(self._on_deselect)
        self.deselect_shortcut.activatedAmbiguously.connect(self._on_deselect)
        self.copy_shortcut.activated.connect(self._on_copy)
        self.paste_shortcut.activated.connect(self._on_paste)
        self.search.textChanged.connect(self._on_search)
        self.regenerate_ids_action.triggered.connect(self._on_regenerate_ids)

    def set_target(self, rid):
        self.rid = rid
        if rid:
            model = self.models.get(rid, self.field_id)
            if self.fixed_size and model.rowCount() < self.fixed_size:
                for _ in range(model.rowCount(), self.fixed_size):
                    model.add_item()
            self.proxy_model = self._wrap_in_proxy_model(model)
            self.list.setModel(self.proxy_model)
            self.list.selectionModel().currentChanged.connect(self._on_select)
        else:
            self.list.setModel(None)
            self.proxy_model = None
        self.inner.set_target(None)
        self._update_buttons()

    @staticmethod
    def _wrap_in_proxy_model(model):
        proxy_model = QSortFilterProxyModel()
        proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        proxy_model.setSourceModel(model)
        return proxy_model

    def _update_buttons(self):
        self.delete_action.setEnabled(self.list.currentIndex().isValid())
        self.copy_to_action.setEnabled(self.list.currentIndex().isValid())
        self.advanced_copy_action.setEnabled(self.list.currentIndex().isValid())
        self.add_action.setEnabled(self.list.model() is not None)
        self.regenerate_ids_action.setEnabled(self.rid is not None)

    def _on_deselect(self):
        if self.list.selectionModel():
            self.list.setCurrentIndex(QModelIndex())

    def _on_copy(self):
        if model := self.list.model():
            rid = model.data(self.list.currentIndex(), QtCore.Qt.UserRole)
            if rid:
                utils.put_rid_on_clipboard(rid)

    def _on_regenerate_ids(self):
        if self.rid:
            base_id, ok = QInputDialog.getInt(self, "Enter Start ID", "Start ID")
            if ok:
                self.data.list_regenerate_ids(self.rid, self.field_id, base_id)

    def _on_paste(self):
        try:
            if model := self.list.model():
                rid = model.data(self.list.currentIndex(), QtCore.Qt.UserRole)
                if rid:
                    other_rid = utils.get_rid_from_clipboard()
                    if other_rid and rid != other_rid:
                        self.data.copy(other_rid, rid, [])

                        # Refresh the view.
                        self.inner.set_target(rid)
                        self.list.model().dataChanged.emit(
                            self.list.currentIndex(),
                            self.list.currentIndex(),
                            [QtCore.Qt.DisplayRole, QtCore.Qt.DecorationRole],
                        )
        except:
            logging.exception("Paste failed in ListWidget.")
            utils.error(self)

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
            self._get_model().add_item()
            self._update_buttons()

    def _on_delete(self):
        if self.list.currentIndex().isValid():
            self.list.model().removeRow(self.list.currentIndex().row())
            self._update_buttons()

    def _on_copy_to(self):
        if not self.list.currentIndex().isValid():
            return
        try:
            choices = self._get_copy_choices()
            choice, ok = QInputDialog.getItem(
                self, "Select Destination", "Destination", choices, 0
            )
            if ok:
                model = self.list.model()
                index = choices.index(choice)
                source_rid = model.data(self.list.currentIndex(), QtCore.Qt.UserRole)
                dest_rid = self.proxy_model.sourceModel().data(model.index(index, 0), QtCore.Qt.UserRole)
                self.data.copy(source_rid, dest_rid, [])
        except:
            logging.exception("Copy to failed")
            utils.error(self)

    def _get_copy_choices(self):
        choices = []
        model = self._get_model()
        for i in range(0, model.rowCount()):
            choices.append(
                model.data(model.index(i, 0), QtCore.Qt.DisplayRole)
            )
        return choices

    def _on_advanced_copy(self):
        if not self.list.currentIndex().isValid():
            return
        model = self.list.model()
        source_rid = model.data(self.list.currentIndex(), QtCore.Qt.UserRole)
        self.dialog = AdvancedCopyDialog(
            self.data, self._get_model(), self.stored_type, source_rid
        )
        self.dialog.show()

    def _get_model(self):
        return self.list.model().sourceModel()
