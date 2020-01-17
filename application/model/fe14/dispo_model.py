from PySide2 import QtCore
from PySide2.QtGui import QStandardItemModel, QStandardItem

from model.fe14.dispo import Dispo


class DisposModel(QStandardItemModel):
    def __init__(self, dispos: Dispo, parent=None):
        super().__init__(parent)
        self.dispos = dispos
        self._populate_model_from_dispos(dispos)

    def _populate_model_from_dispos(self, dispos):
        self.clear()
        for faction in dispos.factions:
            item = QStandardItem()
            item.setText(faction.name)
            item.setData(faction, QtCore.Qt.UserRole)
            for spawn in faction.spawns:
                spawn_item = QStandardItem()
                spawn_item.setText(spawn["PID"].value)
                spawn_item.setData(spawn, QtCore.Qt.UserRole)
                item.appendRow(spawn_item)
            self.appendRow(item)
