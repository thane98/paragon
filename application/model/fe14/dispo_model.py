from copy import deepcopy

from PySide2 import QtCore
from PySide2.QtGui import QStandardItemModel, QStandardItem

from model.fe14 import dispo
from model.fe14.dispo import Dispo, Faction


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

    def add_faction(self, faction_name):
        faction = Faction()
        faction.name = faction_name
        faction.spawns = []
        self.dispos.factions.append(faction)

        item = QStandardItem()
        item.setText(faction.name)
        item.setData(faction, QtCore.Qt.UserRole)
        self.appendRow(item)

    def add_spawn_to_faction(self, faction):
        item = self._find_item_for_faction(faction)
        spawn = deepcopy(dispo.SPAWN_TEMPLATE)
        if faction.spawns:
            source = faction.spawns[0]
            for prop in source.values():
                prop.copy_to(spawn)
        else:
            spawn["PID"].value = "PID_Placeholder"
            spawn["Coordinate (1)"].value = [-1, -1]
            spawn["Coordinate (2)"].value = [-1, -1]
        spawn_item = QStandardItem()
        spawn_item.setText(spawn["PID"].value)
        spawn_item.setData(spawn, QtCore.Qt.UserRole)
        faction.spawns.append(spawn)
        item.appendRow(spawn_item)

    def _find_item_for_faction(self, faction):
        for i in range(0, len(self.dispos.factions)):
            item = self.item(i, 0)
            if item.data(QtCore.Qt.UserRole) == faction:
                return item
        raise ValueError
