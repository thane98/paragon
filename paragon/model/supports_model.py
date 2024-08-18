import struct
from typing import List

from PySide6 import QtCore
from PySide6.QtCore import QModelIndex, QAbstractItemModel, QMimeData, QByteArray
from PySide6.QtGui import QStandardItemModel, QStandardItem

from paragon.core.display import display_rid
from paragon.core.services.fe14_supports import FE14Supports
from paragon.model.support_info import DialogueType, SupportInfo

_REORDERING_MIMETYPE = "application/paragon-support-model-row"


class SupportsModel(QStandardItemModel):
    SORT_BY_ID_ROLE = QtCore.Qt.UserRole + 1

    def __init__(self, gd, service: FE14Supports):
        super().__init__()
        self.gd = gd
        self.service = service
        self.character = None

    def set_character(self, rid):
        self.character = rid
        self._populate()

    def add_support(self, char1, char2, dialogue_type):
        row, info = self.service.add_support(char1, char2, dialogue_type=dialogue_type)
        item = self._create_item(info, row)
        self.insertRow(row, [item])

    def delete_support(self, index: QModelIndex):
        info = self.data(index, QtCore.Qt.UserRole)
        if info:
            self.service.delete_support(info.char1, info.char2)
            self.removeRow(index.row())

    def enumerate(self):
        res = []
        for i in range(0, self.rowCount()):
            index = self.index(i, 0)
            data = self.data(index, QtCore.Qt.UserRole)
            res.append(data)
        return res

    def _populate(self):
        self.clear()
        if self.character:
            supports = self.service.get_supports(self.character)
            for i, info in enumerate(supports):
                item = self._create_item(info, i)
                self.appendRow(item)

    def _create_item(self, info, index):
        name = display_rid(self.gd, info.char2, "fe14_character", None)
        if not name:
            name = "{Undefined}"
        if info.dialogue_type != DialogueType.STANDARD:
            name = f"{name} ({info.dialogue_type})"
        item = QStandardItem()
        item.setText(name)
        item.setData(name, QtCore.Qt.DisplayRole)
        item.setData(info, QtCore.Qt.UserRole)
        item.setData(index, self.SORT_BY_ID_ROLE)
        return item

    def supportedDropActions(self) -> QtCore.Qt.DropActions:
        return QtCore.Qt.MoveAction

    def flags(self, index: QModelIndex) -> QtCore.Qt.ItemFlags:
        flags = QAbstractItemModel.flags(self, index)
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
        source_data = self.data(self.index(source_row, 0), QtCore.Qt.UserRole)
        if source_data.dialogue_type != DialogueType.STANDARD:
            return False
        if source_row == row:
            return False
        dest_data = self.data(self.index(row, 0), QtCore.Qt.UserRole)
        dest_support = dest_data.support if dest_data else None
        self.service.shift_supports(
            source_data.char1, source_data.support, dest_support
        )
        self._populate()
        return True
