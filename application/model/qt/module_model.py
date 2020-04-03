from typing import List, Any

from PySide2 import QtCore
from PySide2.QtCore import QAbstractListModel, QModelIndex
from module.module import Module


class ModuleModel(QAbstractListModel):
    def __init__(self, modules: List[Module], parent=None):
        super().__init__(parent)
        self.modules: List[Module] = modules

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.modules)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.modules[index.row()].name
        if role == QtCore.Qt.UserRole:
            return self.modules[index.row()]
        return None
