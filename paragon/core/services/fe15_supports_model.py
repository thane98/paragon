from PySide6 import QtCore
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem

from paragon.core.display import display_rid
from paragon.model.fe15_support_info import FE15SupportInfo


class FE15SupportsModel(QStandardItemModel):
    def __init__(self, gd, service):
        super().__init__()

        self.gd = gd
        self.service = service
        self.character = None

    def set_character(self, character):
        self.character = character
        self._populate()

    def delete_support(self, index: QModelIndex):
        info = self.data(index, QtCore.Qt.UserRole)
        if info:
            self.service.delete_support(info)
            self.removeRow(index.row())

    def add_support(self, char1, char2, add_conditions, add_dialogue):
        info = self.service.add_support(char1, char2, add_conditions, add_dialogue)
        item = self._create_item(info)
        self.appendRow(item)

    def _populate(self):
        self.clear()
        if self.character:
            supports = self.service.get_supports(self.character)
            for support in supports:
                self.appendRow(self._create_item(support))

    def _create_item(self, info: FE15SupportInfo) -> QStandardItem:
        item = QStandardItem()
        item.setText(self._display_pid(info.pid2))
        item.setData(info, QtCore.Qt.UserRole)
        return item

    def _display_pid(self, pid):
        rid = self.gd.key_to_rid("characters", pid)
        return (
            display_rid(self.gd, rid, "fe15_character", None)
            if rid
            else "{unknown pid}"
        )
