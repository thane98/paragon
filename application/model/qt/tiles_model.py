from copy import deepcopy
from typing import Any, List

from PySide2 import QtCore
from PySide2.QtCore import QAbstractListModel, QModelIndex

from model.fe14 import terrain


class TilesModel(QAbstractListModel):
    def __init__(self, tiles: List, parent=None):
        super().__init__(parent)
        self.tiles = tiles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.tiles)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None

        tile = self.tiles[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return self._get_display_name(tile)
        if role == QtCore.Qt.UserRole:
            return tile
        return None

    @staticmethod
    def _get_display_name(tile):
        if tile["Name"].value:
            return tile["Name"].value
        return tile["TID"].value

    def add_tile(self):
        tile = deepcopy(terrain.TILE_TEMPLATE)
        if self.tiles:
            source = self.tiles[0]
            for prop in source.values():
                prop.copy_to(tile)
        self.tiles.append(tile)

        self.beginResetModel()
        self.endResetModel()
