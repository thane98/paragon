import logging

from PySide2 import QtCore

from paragon.model.advanced_copy_model import AdvancedCopyModel
from paragon.ui.views.ui_advanced_copy_dialog import Ui_AdvancedCopyDialog


class AdvancedCopyDialog(Ui_AdvancedCopyDialog):
    def __init__(self, data, dest_model, typename, source_rid):
        super().__init__()
        self.data = data
        self.field_model = AdvancedCopyModel(data, typename)
        self.source_rid = source_rid
        self.list.setModel(self.field_model)
        self.combo_box.setModel(dest_model)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def accept(self) -> None:
        try:
            fields = self.selected_fields()
            dest_rid = self.combo_box.currentData()
            self.data.copy(self.source_rid, dest_rid, fields)
        except:
            logging.exception("Advanced Copy failed.")
        super().accept()

    def selected_fields(self):
        ls = []
        indices = self.list.selectedIndexes()
        for index in indices:
            ls.append(self.field_model.data(index, QtCore.Qt.UserRole))
        return ls
