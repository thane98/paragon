from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel


class ModuleFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        source_model = self.sourceModel()
        if source_parent.isValid() and self.filterRegExp().pattern() in source_model.data(source_parent).lower():
            return True

        text_to_search = source_model.data(source_model.index(source_row, 0, source_parent)).lower()
        result = self.filterRegExp().pattern() in text_to_search
        sub_index = source_model.index(source_row, 0, source_parent)
        if sub_index.isValid():
            for i in range(0, source_model.rowCount(sub_index)):
                result = result or self.filterAcceptsRow(i, sub_index)
        return result
