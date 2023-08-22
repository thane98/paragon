import os

from PySide2 import QtCore
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon


class DisposModel(QStandardItemModel):
    def __init__(self, gd, chapters, rid, cid):
        super().__init__()
        self.gd = gd
        self.rid = rid
        self.cid = cid
        self.chapters = chapters

        for faction_rid in self.gd.items(rid, "factions"):
            item = self._make_faction_item(faction_rid)
            self.appendRow(item)

    def restrict_factions(self, allowed_factions):
        for i in range(0, self.rowCount()):
            faction_item = self.item(i)
            faction = faction_item.data(QtCore.Qt.UserRole)
            faction_name = self.gd.string(faction, "name")
            if faction_name in allowed_factions:
                faction_item.setCheckState(QtCore.Qt.Checked)
                faction_item.setIcon(
                    QIcon(os.path.join("resources", "icons", "check-circle.svg"))
                )
            else:
                faction_item.setCheckState(QtCore.Qt.Unchecked)
                faction_item.setIcon(QIcon())

    def update_spawn_data(self, spawn):
        for i in range(0, self.rowCount()):
            faction_item = self.item(i)
            for j in range(0, faction_item.rowCount()):
                spawn_item = faction_item.child(j, 0)
                if spawn_item.data(QtCore.Qt.UserRole) == spawn:
                    spawn_item.setText(self.chapters.spawn_name(spawn, self.cid))
                    spawn_item.setData(
                        self.chapters.spawn_decoration(spawn, self.cid),
                        QtCore.Qt.DecorationRole,
                    )

    def move_faction_up(self, faction_item):
        # Perform backend changes first so the UI is still synced
        # if something goes wrong.
        row = faction_item.row()
        self.gd.list_swap(self.rid, "factions", row, row - 1)

        # NOW make the change in the ui.
        self.takeRow(row)
        self.insertRow(row - 1, faction_item)

    def move_faction_down(self, faction_item):
        # Perform backend changes first so the UI is still synced
        # if something goes wrong.
        row = faction_item.row()
        self.gd.list_swap(self.rid, "factions", row, row + 1)

        # NOW make the change in the ui.
        self.takeRow(row)
        self.insertRow(row + 1, faction_item)

    def move_spawn_up(self, spawn_item):
        # Perform backend changes first so the UI is still synced
        # if something goes wrong.
        row = spawn_item.row()
        parent = spawn_item.parent()
        faction = parent.data(QtCore.Qt.UserRole)
        table = self._faction_to_spawn_table(faction)
        self.gd.list_swap(table, "spawns", row, row - 1)

        # NOW make the change in the ui.
        parent.takeRow(row)
        parent.insertRow(row - 1, spawn_item)

    def move_spawn_down(self, spawn_item):
        # Perform backend changes first so the UI is still synced
        # if something goes wrong.
        row = spawn_item.row()
        parent = spawn_item.parent()
        faction = parent.data(QtCore.Qt.UserRole)
        table = self._faction_to_spawn_table(faction)
        self.gd.list_swap(table, "spawns", row, row + 1)

        # NOW make the change in the ui.
        parent.takeRow(row)
        parent.insertRow(row + 1, spawn_item)

    def add_faction(self, name=None, rid=None, index=None):
        if not name and not rid:
            raise ValueError("Must provide a name or rid")
        if not rid:
            index = self.rowCount()
            rid = self.gd.list_add(self.rid, "factions")
            self.gd.set_string(rid, "name", name)

            # We don't need the table, but this will generate
            # one for the new faction.
            self._faction_to_spawn_table(rid)
        else:
            # We have an rid and an index.
            # Reinsert the faction at whatever index it was at previously.
            # Perform sanity checks so we don't mess up the file.
            if index is None:
                raise ValueError("Need an index to reinsert the faction at.")
            if self.gd.type_of(rid) != "Faction":
                raise TypeError("Called add_faction with a different type.")
            self.gd.list_insert_existing(self.rid, "factions", rid, index)
        item = self._make_faction_item(rid)
        self.insertRow(index, item)
        return rid, index

    def add_spawn(self, faction, rid=None, index=None):
        # Get the faction.
        faction_item = self._faction_to_item(faction)
        if not faction_item:
            raise ValueError("Faction is not a part of the dispos model.")

        # Get the spawn table.
        table = self._faction_to_spawn_table(faction)
        if not rid:
            # Add a spawn at the end of the table.
            index = faction_item.rowCount()
            rid = self.gd.list_add(table, "spawns")
            self.gd.set_string(rid, "pid", "PID_Placeholder")
        else:
            # We have an rid and an index.
            # Reinsert the spawn at whatever index it was at previously.
            # Perform sanity checks so we don't mess up the file.
            if index is None:
                raise ValueError("Need an index to reinsert the faction at.")
            if self.gd.type_of(rid) != "Spawn":
                raise TypeError("Called add_spawn with a different type.")
            self.gd.list_insert_existing(table, "spawns", rid, index)

        # Update the UI.
        if faction_item:
            item = self._make_spawn_item(rid)
            faction_item.insertRow(index, item)
            faction_item.child(index)
        return rid, index

    def delete_faction(self, faction):
        if item := self._faction_to_item(faction):
            self.gd.list_remove(self.rid, "factions", item.row())
            self.removeRow(item.row())

    def delete_spawn(self, spawn):
        # First, locate the faction + spawn items.
        for i in range(0, self.rowCount()):
            faction_item = self.item(i)
            for j in range(0, faction_item.rowCount()):
                spawn_item = faction_item.child(j, 0)
                if spawn_item.data(QtCore.Qt.UserRole) == spawn:
                    # Found them. Next, delete in the backend.
                    faction = faction_item.data(QtCore.Qt.UserRole)
                    table = self._faction_to_spawn_table(faction)
                    self.gd.list_remove(table, "spawns", j)

                    # Delete in the UI and exit.
                    faction_item.removeRow(j)
                    return

    def enumerate_spawns(self):
        spawns = []
        for r in range(0, self.rowCount()):
            faction_item = self.item(r)
            if faction_item.checkState() == QtCore.Qt.Checked:
                faction = faction_item.data(QtCore.Qt.UserRole)
                table = self._faction_to_spawn_table(faction)
                spawns.extend(self.gd.items(table, "spawns"))
        return spawns

    def spawn_to_index(self, spawn):
        for r in range(0, self.rowCount()):
            faction_item = self.item(r)
            for c in range(0, faction_item.rowCount()):
                spawn_item = faction_item.child(c, 0)
                if spawn_item.data(QtCore.Qt.UserRole) == spawn:
                    return self.index(c, 0, faction_item.index())
        return QModelIndex()

    def spawn_to_faction(self, spawn):
        index = self.spawn_to_index(spawn)
        if index.isValid():
            item = self.itemFromIndex(index)
            return item.parent().data(QtCore.Qt.UserRole)
        else:
            return None

    def rename_faction(self, faction, name):
        item = self._faction_to_item(faction)
        if item:
            self.gd.set_string(faction, "name", name)
            item.setText(name)

    def _faction_to_item(self, faction):
        for r in range(0, self.rowCount()):
            item = self.item(r)
            if item.data(QtCore.Qt.UserRole) == faction:
                return item
        return None

    def _make_faction_item(self, rid) -> QStandardItem:
        item = QStandardItem()
        item.setText(self.gd.key(rid))
        item.setData(rid, QtCore.Qt.UserRole)
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.Checked)
        table = self.gd.rid(rid, "table")
        if not table:
            # Corrupted spawn table.
            # Not going to fix it here...
            return item
        for spawn in self.gd.items(table, "spawns"):
            spawn_item = self._make_spawn_item(spawn)
            item.appendRow(spawn_item)
        return item

    def _make_spawn_item(self, spawn_rid):
        item = QStandardItem()
        item.setText(self.chapters.spawn_name(spawn_rid, self.cid))
        item.setData(
            self.chapters.spawn_decoration(spawn_rid, self.cid),
            QtCore.Qt.DecorationRole,
        )
        item.setData(spawn_rid, QtCore.Qt.UserRole)
        return item

    def _faction_to_spawn_table(self, faction_rid):
        table = self.gd.rid(faction_rid, "table")
        if not table:
            # Corrupted faction, missing a spawn table.
            # We need a table, so let's make one here.
            table = self.gd.new_instance("SpawnTable", self.gd.store_number_of(faction_rid))
            self.gd.set_rid(faction_rid, "table", table)
        return table
