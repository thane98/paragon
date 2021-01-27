from PySide2 import QtCore
from PySide2.QtGui import QStandardItemModel, QStandardItem
from paragon.ui import utils


class AdvancedCopyModel(QStandardItemModel):
    def __init__(self, data, typename):
        super().__init__()

        fm = data.field_metadata(typename)
        for field_id in fm:
            name = fm[field_id]["name"]
            display = utils.capitalize(field_id, name)
            item = QStandardItem()
            item.setText(display)
            item.setData(field_id, QtCore.Qt.UserRole)
            self.appendRow(item)
