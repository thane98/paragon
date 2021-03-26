from PySide2 import QtCore
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QStandardItemModel, QStandardItem
from paragon.core.display import display_rid

from paragon.core.services.fe14_supports import FE14Supports
from paragon.model.support_info import DialogueType, SupportInfo


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
        if dialogue_type == DialogueType.STANDARD:
            support = self.service.add_support(char1, char2)
            path = self.service.create_dialogue_archive(char1, char2, dialogue_type)
            info = SupportInfo(char1, char2, path, dialogue_type, support)
        else:
            path = self.service.create_dialogue_archive(char1, char2, dialogue_type)
            info = SupportInfo(char1, char2, path, dialogue_type)
        item = self._create_item(info, self.rowCount())
        self.appendRow(item)

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
