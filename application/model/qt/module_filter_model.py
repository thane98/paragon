from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel


class ModuleFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_model = None

    # Normally we'd just use self.sourceModel() to get the source_model.
    # However, doing this in filterAcceptsRow causes memory leaks!
    def setSourceModel(self, source_model: QtCore.QAbstractItemModel):
        self.source_model = source_model
        super().setSourceModel(source_model)

    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        if source_parent.isValid() and self.filterRegExp().pattern() in self._get_text_for_index(source_parent):
            return True
        self._get_text_for_index(source_parent)

        text_to_search = self._get_text_for_index(self.source_model.index(source_row, 0, source_parent))
        result = self.filterRegExp().pattern() in text_to_search
        sub_index = self.source_model.index(source_row, 0, source_parent)
        if sub_index.isValid():
            for i in range(0, self.source_model.rowCount(sub_index)):
                result = result or self.filterAcceptsRow(i, sub_index)
        return result

    def _get_text_for_index(self, index: QtCore.QModelIndex):
        if not index.isValid():
            return None
        text = self.source_model.data(index, QtCore.Qt.DisplayRole)
        return text.lower()
