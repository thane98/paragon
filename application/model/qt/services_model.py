from typing import Dict, Any
from PySide2 import QtCore
from PySide2.QtCore import QAbstractListModel, QModelIndex


class ServicesModel(QAbstractListModel):
    def __init__(self, services: Dict, parent=None):
        super().__init__(parent)
        self.services = []
        for service in services.items():
            self.services.append(service)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.services)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None

        _, value = self.services[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return value.get_display_name()
        if role == QtCore.Qt.UserRole:
            return value
        return None
