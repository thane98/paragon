from typing import Any

from PySide2 import QtCore
from PySide2.QtCore import QAbstractListModel, QModelIndex


class MultiModel(QAbstractListModel):
    def __init__(self, gd):
        super().__init__()
        self.gd = gd
        self.multis = sorted(
            filter(lambda m: not m.hidden, gd.multis()), key=lambda m: m.name
        )

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.multis)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        multi = self.multis[index.row()]
        if role == QtCore.Qt.DisplayRole:
            name = multi.name
            if self.gd.store_is_dirty(multi.id):
                name += "*"
            return name
        elif role == QtCore.Qt.UserRole:
            return multi
        else:
            return None
