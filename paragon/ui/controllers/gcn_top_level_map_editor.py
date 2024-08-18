import logging
import traceback
from pathlib import Path

from PySide6 import QtCore
from PySide6.QtCore import QSortFilterProxyModel, QStringListModel

from paragon.ui.controllers.error_dialog import ErrorDialog
from paragon.ui.views.ui_gcn_top_level_map_editor import Ui_GcnTopLevelMapEditor


class GcnTopLevelMapEditor(Ui_GcnTopLevelMapEditor):
    def __init__(self, ms, gs):
        super().__init__(ms, gs)
        self.project = gs.project
        self.models = gs.models
        self.gd = gs.data
        self.maps = gs.maps

        self.model = QStringListModel(
            [Path(p).name for p in self.gd.subdirectories("zmap", False)]
        )
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterCaseSensitivity(
            QtCore.Qt.CaseSensitivity.CaseInsensitive
        )
        self.proxy_model.setSourceModel(self.model)
        self.list.setModel(self.proxy_model)

        self.list.selectionModel().currentChanged.connect(
            self._on_select, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.search.textChanged.connect(
            self._on_search, QtCore.Qt.ConnectionType.UniqueConnection
        )

    def _on_search(self):
        self.proxy_model.setFilterRegularExpression(self.search.text())

    def _on_select(self):
        index = self.list.currentIndex()
        if not index:
            self.map_editor.set_target(None)
            return
        zmap = self.list.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        if not zmap:
            self.map_editor.set_target(None)
            return
        try:
            data = self.maps.load(zmap)
            self.map_editor.set_target(data)
        except:
            logging.exception(f"Failed to load map {zmap}")
            self.error_dialog = ErrorDialog(traceback.format_exc())
            self.error_dialog.show()
