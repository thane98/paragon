from typing import Any
from PySide2 import QtCore
from PySide2.QtCore import QModelIndex, QAbstractListModel

from services.service_locator import locator


class ModuleEntryModel(QAbstractListModel):
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.entries = module.entries

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.entries)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None

        elem = self.entries[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return elem.get_display_name()
        if role == QtCore.Qt.DecorationRole:
            return locator.get_scoped("IconService").get_icon_by_type(elem, self.module.entry_icon_type)
        if role == QtCore.Qt.UserRole:
            return elem
        return None

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginInsertRows(parent, row, row + count)
        for _ in range(0, count):
            self.module.add_elem()
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if row not in range(0, len(self.entries)) or row + count not in range(0, len(self.entries) + 1):
            return False

        self.beginRemoveRows(parent, row, row + count)
        self.module.remove_range(row, row + count)
        self.endRemoveRows()
        return True
