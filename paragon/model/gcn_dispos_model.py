from typing import Generator, Optional

from PySide6 import QtCore
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem

from paragon.model.gcn_chapter_data import GcnDisposData


GROUP_TYPE = "DispoGroup"


class GcnDisposModel(QStandardItemModel):
    def __init__(self, gd, map_service, data: GcnDisposData):
        super().__init__()
        self.gd = gd
        self.dispos_data = data
        self.map_service = map_service

        if data.common:
            self.appendRow(self._make_difficulty_item("Common", data.common))
        if data.normal:
            self.appendRow(self._make_difficulty_item("Normal", data.normal))
        if data.hard:
            self.appendRow(self._make_difficulty_item("Hard", data.hard))
        if data.maniac:
            self.appendRow(self._make_difficulty_item("Maniac", data.maniac))

    def update_spawn_data(self, spawn):
        if spawn_item := self.spawn_to_item(spawn):
            spawn_item.setText(self.map_service.spawn_name(spawn))
            spawn_item.setData(
                self.map_service.spawn_decoration(spawn),
                QtCore.Qt.ItemDataRole.DecorationRole,
            )

    def move_group_up(self, group_item: QStandardItem):
        difficulty_item = group_item.parent()
        difficulty_rid = difficulty_item.data(QtCore.Qt.ItemDataRole.UserRole)
        row = group_item.row()
        self.gd.list_swap(difficulty_rid, "groups", row, row - 1)
        difficulty_item.takeRow(row)
        difficulty_item.insertRow(row - 1, group_item)

    def move_group_down(self, group_item):
        difficulty_item = group_item.parent()
        difficulty_rid = difficulty_item.data(QtCore.Qt.ItemDataRole.UserRole)
        row = group_item.row()
        self.gd.list_swap(difficulty_rid, "groups", row, row + 1)
        difficulty_item.takeRow(row)
        difficulty_item.insertRow(row + 1, group_item)

    def move_spawn_up(self, spawn_item: QStandardItem):
        row = spawn_item.row()
        parent = spawn_item.parent()
        group = parent.data(QtCore.Qt.ItemDataRole.UserRole)
        self.gd.list_swap(group, "spawns", row, row - 1)
        parent.takeRow(row)
        parent.insertRow(row - 1, spawn_item)

    def move_spawn_down(self, spawn_item: QStandardItem):
        row = spawn_item.row()
        parent = spawn_item.parent()
        group = parent.data(QtCore.Qt.ItemDataRole.UserRole)
        self.gd.list_swap(group, "spawns", row, row + 1)
        parent.takeRow(row)
        parent.insertRow(row + 1, spawn_item)

    def add_group(
        self, difficulty_item: QStandardItem, name=None, rid=None, index=None
    ):
        parent_rid = difficulty_item.data(QtCore.Qt.ItemDataRole.UserRole)
        if not name and not rid:
            raise ValueError("Must provide a name or rid")
        if not rid:
            index = difficulty_item.rowCount()
            rid = self.gd.list_add(parent_rid, "groups")
            self.gd.set_string(rid, "label", name)
        else:
            # We have an rid and an index.
            # Reinsert the group at whatever index it was at previously.
            # Perform sanity checks so we don't mess up the file.
            if index is None:
                raise ValueError("Need an index to reinsert the group at.")
            if self.gd.type_of(rid) != GROUP_TYPE:
                raise TypeError("Called add_group with a different type.")
            self.gd.list_insert_existing(parent_rid, "groups", rid, index)
        item = self._make_group_item(rid)
        difficulty_item.insertRow(index, [item])
        return rid, index

    def add_spawn(self, group, rid=None, index=None):
        # Get the group.
        group_item = self._group_to_item(group)
        if not group_item:
            raise ValueError("group is not a part of the dispos model.")

        # Get the spawn table.
        if not rid:
            # Add a spawn at the end of the table.
            index = group_item.rowCount()
            rid = self.gd.list_add(group, "spawns")
            self.gd.set_string(rid, "pid", "PID_Placeholder")
        else:
            # We have an rid and an index.
            # Reinsert the spawn at whatever index it was at previously.
            # Perform sanity checks so we don't mess up the file.
            if index is None:
                raise ValueError("Need an index to reinsert the group at.")
            if self.gd.type_of(rid) != "Spawn":
                raise TypeError("Called add_spawn with a different type.")
            self.gd.list_insert_existing(group, "spawns", rid, index)

        # Update the UI.
        item = self._make_spawn_item(rid)
        group_item.insertRow(index, [item])
        return rid, index

    def delete_group(self, group):
        if item := self._group_to_item(group):
            parent = item.parent()
            self.gd.list_remove(
                parent.data(QtCore.Qt.ItemDataRole.UserRole), "groups", item.row()
            )
            parent.removeRow(item.row())

    def delete_spawn(self, spawn):
        # First, locate the group + spawn items.
        if spawn_item := self.spawn_to_item(spawn):
            group_item: QStandardItem = spawn_item.parent()
            group = group_item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.gd.list_remove(group, "spawns", spawn_item.row())
            group_item.removeRow(spawn_item.row())
            return

    def enumerate_spawns(self):
        spawns = []
        for difficulty_item in self._difficulties():
            if difficulty_item.checkState() == QtCore.Qt.CheckState.Checked:
                for group_index in range(0, difficulty_item.rowCount()):
                    group_item = difficulty_item.child(group_index)
                    if group_item.checkState() == QtCore.Qt.CheckState.Checked:
                        for spawn_index in range(0, group_item.rowCount()):
                            spawn_item = group_item.child(spawn_index)
                            if spawn_item:
                                spawns.append(
                                    spawn_item.data(QtCore.Qt.ItemDataRole.UserRole)
                                )
                            else:
                                print(
                                    group_item.rowCount(),
                                    spawn_index,
                                    group_item.child(spawn_index),
                                )
        return spawns

    def _spawns_from_dispos(self, dispos_rid) -> Generator[int, None, None]:
        for group in self.gd.items(dispos_rid, "groups"):
            for spawn in self.gd.items(group, "spawns"):
                yield spawn

    def spawn_to_item(self, spawn) -> Optional[QStandardItem]:
        for spawn_item in self._spawns():
            if spawn_item.data(QtCore.Qt.ItemDataRole.UserRole) == spawn:
                return spawn_item

    def spawn_to_index(self, spawn) -> Optional[QModelIndex]:
        if item := self.spawn_to_item(spawn):
            return item.index()

    def spawn_to_group(self, spawn) -> Optional[int]:
        if item := self.spawn_to_item(spawn):
            return item.parent().data(QtCore.Qt.ItemDataRole.UserRole)

    def group_to_dispos_item(self, group) -> QStandardItem:
        if item := self._group_to_item(group):
            return item.parent()

    def rename_group(self, group, name):
        item = self._group_to_item(group)
        if item:
            self.gd.set_string(group, "label", name)
            item.setText(name)

    def _group_to_item(self, group) -> QStandardItem:
        return next(
            item
            for item in self._groups()
            if item.data(QtCore.Qt.ItemDataRole.UserRole) == group
        )

    def _make_difficulty_item(self, difficulty: str, rid: int) -> QStandardItem:
        item = QStandardItem()
        item.setText(difficulty)
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.CheckState.Checked)
        item.setData(rid, QtCore.Qt.ItemDataRole.UserRole)
        for group_rid in self.gd.items(rid, "groups"):
            item.appendRow(self._make_group_item(group_rid))
        return item

    def _make_group_item(self, rid) -> QStandardItem:
        item = QStandardItem()
        item.setText(self.gd.key(rid))
        item.setData(rid, QtCore.Qt.ItemDataRole.UserRole)
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.CheckState.Checked)
        for spawn in self._group_to_spawn_table(rid):
            spawn_item = self._make_spawn_item(spawn)
            item.appendRow(spawn_item)
        return item

    def _make_spawn_item(self, spawn_rid):
        item = QStandardItem()
        item.setText(self.map_service.spawn_name(spawn_rid))
        item.setData(
            self.map_service.spawn_decoration(spawn_rid),
            QtCore.Qt.ItemDataRole.DecorationRole,
        )
        item.setData(spawn_rid, QtCore.Qt.ItemDataRole.UserRole)
        return item

    def _group_to_spawn_table(self, group):
        return self.gd.items(group, "spawns")

    def _difficulties(self) -> Generator[QStandardItem, None, None]:
        for difficulty_index in range(0, self.rowCount()):
            yield self.item(difficulty_index)

    def _groups(self) -> Generator[QStandardItem, None, None]:
        for difficulty_index in range(0, self.rowCount()):
            difficulty_item = self.item(difficulty_index)
            for group_index in range(0, difficulty_item.rowCount()):
                yield difficulty_item.child(group_index)

    def _spawns(self) -> Generator[QStandardItem, None, None]:
        for group_item in self._groups():
            for spawn_index in range(0, group_item.rowCount()):
                yield group_item.child(spawn_index)
