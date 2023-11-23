import struct
from typing import Any, List

from PySide6 import QtCore
from PySide6.QtCore import QAbstractListModel


class DungeonsModel(QAbstractListModel):
    def __init__(self, gd, dungeons):
        super().__init__()
        self.gd = gd
        self.dungeons = dungeons

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.dungeons)

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        dungeon = self.dungeons[index.row()]
        if role == QtCore.Qt.DisplayRole:
            field_rid = self.gd.key_to_rid("field", dungeon)
            if field_rid:
                title = self.gd.string(field_rid, "title")
                if title:
                    message = self.gd.message("m/Name.bin.lz", True, title)
                    if message:
                        return f"{message} ({dungeon})"
            if "テーベ" in dungeon:
                return f"Thabes ({dungeon})"
            return dungeon
        elif role == QtCore.Qt.UserRole:
            return dungeon
        return None
