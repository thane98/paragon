from typing import Any

from PySide2 import QtCore
from PySide2.QtCore import QAbstractListModel, QModelIndex


class NodeModel(QAbstractListModel):
    def __init__(self, gd):
        super().__init__()
        self.gd = gd
        self.nodes = sorted(gd.nodes(), key=lambda n: n.name)

    def get_by_id(self, node_id):
        return next(filter(lambda n: n.id == node_id, self.nodes), None)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.nodes)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        node = self.nodes[index.row()]
        if role == QtCore.Qt.DisplayRole:
            name = node.name
            if self.gd.store_is_dirty(node.store):
                name += "*"
            return name
        elif role == QtCore.Qt.UserRole:
            return node
        else:
            return None
