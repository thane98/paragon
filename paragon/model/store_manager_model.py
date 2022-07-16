import os.path
from typing import List

from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel, QModelIndex
from PySide2.QtGui import QStandardItemModel, QStandardItem


class StoreManagerModel(QStandardItemModel):
    def __init__(self, gd):
        super().__init__()
        self.gd = gd
        self.setHorizontalHeaderLabels(["Store ID", "Path", "Type", "Dirty?"])
        self.refresh()

        self.itemChanged.connect(self._on_dirty_state_changed)

    def refresh(self):
        self.removeRows(0, self.rowCount())
        for store in self.gd.describe_stores():
            self.appendRow(self.create_row(store))

    @staticmethod
    def create_row(store) -> List[QStandardItem]:
        item = QStandardItem()
        item.setText(str(store.store_number))
        item.setData(store.store_number)
        if store.store_type != "Cmp":
            path_item = QStandardItem(os.path.normpath(store.path))
        else:
            path_item = QStandardItem(store.path)
        type_item = QStandardItem(store.store_type)
        dirty_item = QStandardItem()
        dirty_item.setCheckable(True)
        dirty_item.setCheckState(QtCore.Qt.Checked if store.dirty else QtCore.Qt.Unchecked)
        dirty_item.setEnabled(store.store_type != "Multi")
        return [item, path_item, type_item, dirty_item]

    def _on_dirty_state_changed(self, item: QStandardItem):
        store_number = self.item(item.row(), 0).data()
        dirty_item = self.item(item.row(), 3)
        self.gd.set_forced_dirty(store_number, dirty_item.checkState() == QtCore.Qt.Checked)


class StoreManagerProxyModel(QSortFilterProxyModel):
    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex) -> bool:
        if source_left.isValid() and source_right.isValid() and source_left.column() == 0 and source_right.column() == 0:
            return int(source_left.data()) < int(source_right.data())
        return QSortFilterProxyModel.lessThan(self, source_left, source_right)
