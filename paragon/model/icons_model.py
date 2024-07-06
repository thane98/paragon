from typing import Any

from PySide6 import QtCore
from PySide6.QtCore import QAbstractListModel, QModelIndex


class IconsModel(QAbstractListModel):
    def __init__(self, icons):
        super().__init__()
        self.icons = icons

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.icons)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return str(index.row())
        elif role == QtCore.Qt.DecorationRole:
            return self.icons[index.row()]
        return None
