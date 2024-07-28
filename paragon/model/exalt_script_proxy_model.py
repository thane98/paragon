from typing import Optional

from PySide6 import QtCore
from PySide6.QtCore import QSortFilterProxyModel, QModelIndex
from PySide6.QtWidgets import QStyle

from paragon.model.exalt_script_model import ExaltScriptModel, ExaltScriptItemSummary


class ExaltScriptProxyModel(QSortFilterProxyModel):
    def __init__(self, game_data, style: QStyle):
        super().__init__()

        self.model = ExaltScriptModel(game_data, style)
        self.setSourceModel(self.model)

        self.setFilterCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.setRecursiveFilteringEnabled(True)

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        item_1 = self.model.data_at(left)
        item_2 = self.model.data_at(right)
        if not item_1 or not item_2:
            return True
        elif item_1.path is not None and item_2.path is not None:
            return ExaltScriptProxyModel._less_than(
                item_1.path,
                item_1.node_kind,
                item_2.path,
                item_2.node_kind,
            )
        elif item_1.path is not None:
            return True
        elif item_2.path is not None:
            return False
        else:
            return ExaltScriptProxyModel._less_than(
                item_1.node.path,
                item_1.node.kind(),
                item_2.node.path,
                item_2.node.kind(),
            )

    @staticmethod
    def _less_than(
        path_1: str, node_kind_1: str, path_2: str, node_kind_2: str
    ) -> bool:
        if node_kind_1 != node_kind_2:
            return node_kind_1.lower() < node_kind_2.lower()
        else:
            return path_1.lower() < path_2.lower()

    def data_at(self, index: QModelIndex) -> Optional[ExaltScriptItemSummary]:
        return self.model.data_at(self.mapToSource(index))

    def add_new_script(self, parent_index: QModelIndex, file_name: str):
        self.model.add_new_script(self.mapToSource(parent_index), file_name)
        self.sort(self.sortColumn(), self.sortOrder())

    def add_new_dir(self, parent_index: QModelIndex, file_name: str):
        self.model.add_new_dir(self.mapToSource(parent_index), file_name)
        self.sort(self.sortColumn(), self.sortOrder())

    def index_of(self, path: str, node_kind: str) -> Optional[QModelIndex]:
        index = self.model.index_of(path, node_kind)
        return self.mapFromSource(index) if index else None
