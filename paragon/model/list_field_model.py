import struct
from typing import Any, List

from PySide2 import QtCore
from PySide2.QtCore import QAbstractListModel, QModelIndex, QMimeData, QByteArray

from paragon.core.display import display_rid


_REORDERING_MIMETYPE = "application/paragon-model-row"


class ListFieldModel(QAbstractListModel):
    def __init__(self, gd, icons, rid, field_id, display_function=None):
        super().__init__()
        self.gd = gd
        self.icons = icons
        self.rid = rid
        self.field_id = field_id
        self.display_function = display_function

    def refresh(self):
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return self.gd.list_size(self.rid, self.field_id)

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        rid = self.gd.list_get(self.rid, self.field_id, index.row())
        if role == QtCore.Qt.DisplayRole:
            if self.display_function:
                display = display_rid(self.gd, rid, self.display_function, index.row())
            else:
                display = None
            display = display if display else self.gd.display(rid)
            display = display if display else self.gd.key(rid)
            return display if display else f"Item {index.row()}"
        elif role == QtCore.Qt.DecorationRole:
            return self.icons.icon(rid)
        elif role == QtCore.Qt.UserRole:
            return rid
        return None

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if row > self.rowCount():
            return False
        else:
            self.beginInsertRows(parent, row, row + count - 1)
            for i in range(0, count):
                self.gd.list_insert(self.rid, self.field_id, row)
            self.endInsertRows()
            return True

    def _insert_row_for_move(self, row: int, rid: int):
        parent = QModelIndex()
        self.beginInsertRows(parent, row, row)
        self.gd.list_insert_existing(self.rid, self.field_id, rid, row)
        self.refresh()
        self.endInsertRows()

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if row >= self.rowCount() or row + count > self.rowCount():
            return False
        else:
            self.beginRemoveRows(parent, row, row + count - 1)
            for _ in range(0, count):
                self.gd.list_remove(self.rid, self.field_id, row)
            self.endRemoveRows()
            return True

    def add_item(self):
        self.insertRow(self.rowCount())

    def supportedDropActions(self) -> QtCore.Qt.DropActions:
        return QtCore.Qt.MoveAction

    def flags(self, index: QModelIndex) -> QtCore.Qt.ItemFlags:
        flags = super().flags(index)
        if index.isValid():
            return QtCore.Qt.ItemIsDragEnabled | flags
        else:
            return QtCore.Qt.ItemIsDropEnabled | flags

    def mimeTypes(self) -> List:
        return [_REORDERING_MIMETYPE]

    def mimeData(self, indexes: List) -> QMimeData:
        if not indexes:
            return QMimeData()
        raw_data = bytearray()
        for index in indexes:
            raw_data.extend(index.row().to_bytes(8, byteorder="little"))
        mime_data = QMimeData()
        mime_data.setData(_REORDERING_MIMETYPE, QByteArray(raw_data))
        return mime_data

    def dropMimeData(
        self,
        data: QMimeData,
        action: QtCore.Qt.DropAction,
        row: int,
        column: int,
        parent: QModelIndex,
    ) -> bool:
        raw_indices = bytearray(data.data(_REORDERING_MIMETYPE))
        source_row = struct.unpack_from("<L", raw_indices, 0)[0]
        if source_row not in range(0, self.rowCount()):
            return False
        source_data = self.gd.list_get(self.rid, self.field_id, source_row)
        if source_row < row:
            self.removeRow(source_row)
            self._insert_row_for_move(row - 1, source_data)
            self.beginResetModel()
            self.endResetModel()
        elif source_row != row:
            self.removeRow(source_row)
            self._insert_row_for_move(row, source_data)
            self.beginResetModel()
            self.endResetModel()
        return source_row != row
