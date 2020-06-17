from copy import deepcopy
from typing import Optional

from PySide2 import QtCore
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QStandardItemModel, QStandardItem

from core.simple_undo_redo_stack import SimpleUndoRedoStack
from model.fe14 import dispo
from model.fe14.dispo import Dispo, Faction
from module.properties.property_container import PropertyContainer
from services.service_locator import locator


class DisposModel(QStandardItemModel):
    def __init__(self, dispos: Dispo, chapter_data, parent=None):
        super().__init__(parent)
        self.dispos = dispos
        self.chapter_data = chapter_data
        self.undo_stack = SimpleUndoRedoStack()
        self.undo_position = -1
        self._populate_model_from_dispos(dispos)

    def _populate_model_from_dispos(self, dispos):
        self.clear()
        for faction in dispos.factions:
            item = QStandardItem()
            item.setText(faction.name)
            item.setData(faction, QtCore.Qt.UserRole)
            for spawn in faction.spawns:
                spawn_item = QStandardItem()
                self._set_item_name_and_decoration(spawn_item, spawn)
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

    def add_existing_faction(self, faction):
        self.dispos.factions.append(faction)
        item = QStandardItem()
        item.setText(faction.name)
        item.setData(faction, QtCore.Qt.UserRole)
        for spawn in faction.spawns:
            spawn_item = QStandardItem()
            self._set_item_name_and_decoration(spawn_item, spawn)
            item.appendRow(spawn_item)
        self.appendRow(item)

    def add_spawn_to_faction(self, faction, spawn=None):
        if not spawn:
            spawn = dispo.SPAWN_TEMPLATE.duplicate()
            spawn["PID"].value = "PID_Placeholder"
            spawn["Coordinate (1)"].value = [0, 0]
            spawn["Coordinate (2)"].value = [0, 0]
        item = self._find_item_for_faction(faction)
        faction.spawns.append(spawn)
        spawn_item = QStandardItem()
        self._set_item_name_and_decoration(spawn_item, spawn)
        item.appendRow(spawn_item)

    def delete_faction(self, faction):
        for i in range(0, len(self.dispos.factions)):
            item = self.item(i, 0)
            if item.data(QtCore.Qt.UserRole) == faction:
                del self.dispos.factions[i]
                self.removeRow(i)
                return
        raise ValueError

    def _find_item_for_faction(self, faction):
        for i in range(0, len(self.dispos.factions)):
            item = self.item(i, 0)
            if item.data(QtCore.Qt.UserRole) == faction:
                return item
        raise ValueError

    def refresh_spawn(self, spawn):
        for i in range(0, len(self.dispos.factions)):
            faction_item = self.item(i, 0)
            for j in range(0, faction_item.rowCount()):
                spawn_item = faction_item.child(j, 0)
                if spawn_item.data(QtCore.Qt.UserRole) == spawn:
                    self._set_item_name_and_decoration(spawn_item, spawn)
                    return
        raise ValueError

    def is_faction_name_in_use(self, faction_name: str):
        for faction in self.dispos.factions:
            if faction.name == faction_name:
                return True
        return False

    def get_faction_from_spawn(self, spawn: PropertyContainer):
        return self.dispos.find_faction_from_spawn(spawn)

    def delete_spawn(self, spawn: PropertyContainer):
        removed = False
        for i in range(0, len(self.dispos.factions)):
            faction_item = self.item(i, 0)
            for j in range(0, faction_item.rowCount()):
                spawn_item = faction_item.child(j, 0)
                if spawn_item.data(QtCore.Qt.UserRole) == spawn:
                    faction_item.removeRow(j)
                    removed = True
                    break
        if not removed:
            raise ValueError
        self.dispos.delete_spawn(spawn)

    def get_character_from_spawn(self, spawn: PropertyContainer) -> Optional[PropertyContainer]:
        person = self.chapter_data.person
        result = None
        if person:
            result = person.get_element_by_key(spawn.get_key())
        if not result:
            characters_module = locator.get_scoped("ModuleService").get_module("Characters")
            result = characters_module.get_element_by_key(spawn.get_key())
        return result

    def _get_display_name_from_spawn(self, spawn: PropertyContainer):
        person = self.chapter_data.person
        result = None
        if person:
            elem = person.get_element_by_key(spawn.get_key())
            if elem:
                result = person.get_display_name_for_entry(elem)
        if not result:
            characters_module = locator.get_scoped("ModuleService").get_module("Characters")
            elem = characters_module.get_element_by_key(spawn.get_key())
            result = characters_module.get_display_name_for_entry(elem)
        return result

    def _set_item_name_and_decoration(self, item: QStandardItem, spawn: PropertyContainer):
        character = self.get_character_from_spawn(spawn)
        if not character:
            item.setText("[Broken PID]")
            item.setData(None, QtCore.Qt.DecorationRole)
        else:
            item.setText(self._get_display_name_from_spawn(spawn))
            army_id = character["Army ID"].value
            decoration = locator.get_scoped("IconService").get_icon_for_army(army_id)
            item.setData(decoration, QtCore.Qt.DecorationRole)
        item.setData(spawn, QtCore.Qt.UserRole)

    def get_index_from_spawn(self, spawn: Optional[PropertyContainer]):
        for i in range(0, len(self.dispos.factions)):
            faction_item = self.item(i, 0)
            for j in range(0, faction_item.rowCount()):
                spawn_item = faction_item.child(j, 0)
                if spawn_item.data(QtCore.Qt.UserRole) == spawn:
                    parent = self.index(i, 0)
                    return self.index(j, 0, parent)
        return QModelIndex()

    def get_index_from_faction(self, faction):
        for i in range(0, len(self.dispos.factions)):
            faction_item = self.item(i, 0)
            if faction_item.data(QtCore.Qt.UserRole) == faction:
                return self.index(i, 0)
        return QModelIndex()

    def copy_spawn_and_ignore_coordinates(self, source_spawn, target_spawn):
        coordinate_one = deepcopy(target_spawn["Coordinate (1)"].value)
        coordinate_two = deepcopy(target_spawn["Coordinate (2)"].value)
        source_spawn.copy_to(target_spawn)
        target_spawn["Coordinate (1)"].value = coordinate_one
        target_spawn["Coordinate (2)"].value = coordinate_two
        for i in range(0, len(self.dispos.factions)):
            faction_item = self.item(i, 0)
            for j in range(0, faction_item.rowCount()):
                spawn_item = faction_item.child(j, 0)
                if spawn_item.data(QtCore.Qt.UserRole) == target_spawn:
                    self._set_item_name_and_decoration(spawn_item, target_spawn)
