from copy import deepcopy
from typing import Optional

from PySide6 import QtCore
from PySide6.QtCore import QItemSelectionModel, QItemSelection
from PySide6.QtWidgets import QInputDialog, QMenu
from PySide6.QtGui import QUndoStack, QStandardItem

from paragon.model.gcn_chapter_data import GcnChapterData
from paragon.model.gcn_dispos_model import GcnDisposModel
from paragon.ui import utils

from paragon.model.game import Game
from paragon.model.coordinate_change_type import CoordinateChangeType
from paragon.ui.commands.add_spawn_undo_command import AddSpawnUndoCommand
from paragon.ui.commands.delete_spawn_undo_command import DeleteSpawnUndoCommand
from paragon.ui.commands.gcn_add_group_undo_command import GcnAddFactionUndoCommand
from paragon.ui.commands.gcn_delete_faction_undo_command import (
    GcnDeleteFactionUndoCommand,
)
from paragon.ui.commands.move_spawn_undo_command import MoveSpawnUndoCommand
from paragon.ui.commands.paste_spawn_undo_command import PasteSpawnUndoCommand
from paragon.ui.commands.paste_tile_undo_command import PasteTileUndoCommand
from paragon.ui.commands.rename_faction_undo_command import RenameFactionUndoCommand
from paragon.ui.commands.reorder_spawn_undo_command import ReorderUndoCommand
from paragon.ui.controllers.fe10_map_editor_side_panel import FE10MapEditorSidePanel
from paragon.ui.controllers.fe9_map_editor_side_panel import FE9MapEditorSidePanel
from paragon.ui.controllers.gcn_map_grid import GcnMapGrid
from paragon.ui.views.ui_gcn_map_editor import Ui_GcnMapEditor


class GcnMapEditor(Ui_GcnMapEditor):
    def __init__(self, ms, gs):
        super().__init__(ms.config)
        self.config = ms.config
        self.gd = gs.data
        self.dispos_model = None
        self.chapter_data: Optional[GcnChapterData] = None
        self.gd = gs.data
        self.maps = gs.maps
        self.undo_stack = QUndoStack()

        self.grid = GcnMapGrid(
            self,
            gs.maps,
            gs.sprites,
            gs.sprite_animation,
            lambda: False,
            self._is_coordinate_2,
        )
        self.splitter.addWidget(self.grid)
        self.splitter.setStretchFactor(1, 1)

        if gs.project.game == Game.FE9:
            self.side_panel = FE9MapEditorSidePanel(ms, gs)
            self.splitter.addWidget(self.side_panel)
        elif gs.project.game == Game.FE10:
            self.side_panel = FE10MapEditorSidePanel(ms, gs)
            self.splitter.addWidget(self.side_panel)
        else:
            raise NotImplementedError
        self.spawn_widgets = self.side_panel.get_spawn_widgets()

        self.grid.hovered.connect(
            self._on_hover, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.grid.dragged.connect(
            self._on_drag, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.deselect_shortcut.activated.connect(
            self._on_deselect, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.status_bar_action.toggled.connect(
            self._on_status_bar_toggled, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.left_panel_action.toggled.connect(
            self._on_left_panel_toggled, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.right_panel_action.toggled.connect(
            self._on_right_panel_toggled, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.add_shortcut.activated.connect(
            self._on_add_shortcut, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.rename_group_action.triggered.connect(
            self._on_rename_group, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.add_group_action.triggered.connect(
            self._on_add_group, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.add_spawn_action.triggered.connect(
            self._on_add_spawn, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.delete_action.triggered.connect(
            self._on_delete, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.move_up_action.triggered.connect(
            self._on_move_up, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.move_down_action.triggered.connect(
            self._on_move_down, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.coordinate_mode_action.toggled.connect(
            self.grid.refresh, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.update_both_coordinates_action.toggled.connect(
            self._on_update_both_coordinates_checked,
            QtCore.Qt.ConnectionType.UniqueConnection,
        )
        self.copy_action.triggered.connect(
            self._on_copy, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.paste_action.triggered.connect(
            self._on_paste, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.undo_action.triggered.connect(
            self._on_undo, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.redo_action.triggered.connect(
            self._on_redo, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.zoom_slider.valueChanged.connect(
            self._on_zoom, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.reload_action.triggered.connect(
            self._on_reload, QtCore.Qt.ConnectionType.UniqueConnection
        )

        self.refresh_actions()
        self.tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(
            self._on_tree_view_context_menu, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self._on_zoom()

    def _on_tree_view_context_menu(self, point):
        menu = QMenu()
        index = self.tree.indexAt(point)
        rid = self.tree.model().data(index, QtCore.Qt.ItemDataRole.UserRole)
        if not rid:
            return
        type_of_rid = self.gd.type_of(rid)
        if type_of_rid == "Spawn":
            menu.addAction(self.move_up_action)
            menu.addAction(self.move_down_action)
            menu.addAction(self.delete_action)
            menu.exec_(self.tree.viewport().mapToGlobal(point))
        elif type_of_rid == "DispoGroup":
            menu.addAction(self.add_spawn_action)
            menu.addAction(self.delete_action)
            menu.exec_(self.tree.viewport().mapToGlobal(point))

    def refresh_actions(self):
        dispos_actions_enabled = bool(self.dispos_model)
        difficulty_actions_enabled = self._selection_is_difficulty()
        group_actions_enabled = self._selection_is_group()
        spawn_actions_enabled = self._selection_is_spawn()
        self.add_shortcut.setEnabled(
            difficulty_actions_enabled or group_actions_enabled
        )
        self.add_group_action.setEnabled(
            difficulty_actions_enabled or group_actions_enabled
        )
        self.add_spawn_action.setEnabled(group_actions_enabled)
        self.rename_group_action.setEnabled(group_actions_enabled)
        self.delete_action.setEnabled(group_actions_enabled or spawn_actions_enabled)
        self.move_up_action.setEnabled(self._can_move_up())
        self.move_down_action.setEnabled(self._can_move_down())
        self.copy_action.setEnabled(spawn_actions_enabled)
        self.paste_action.setEnabled(spawn_actions_enabled)
        self.coordinate_mode_action.setEnabled(dispos_actions_enabled)
        self.undo_action.setEnabled(self.undo_stack.canUndo())
        self.redo_action.setEnabled(self.undo_stack.canRedo())
        self.spawn_widgets["team"].currentIndexChanged.connect(self._on_team_changed)
        if "pid" in self.spawn_widgets:
            self.spawn_widgets["pid"].editingFinished.connect(
                self._on_character_changed
            )
        else:
            self.spawn_widgets["character"].currentIndexChanged.connect(
                self._on_character_changed
            )

        coord_1 = self.spawn_widgets["coord_1"]
        coord_2 = self.spawn_widgets["coord_2"]
        coord_1.disconnect_boxes()
        coord_2.disconnect_boxes()
        coord_1.editors[0].valueChanged.connect(
            self._on_coord_1_widget_changed, QtCore.Qt.ConnectionType.UniqueConnection
        )
        coord_1.editors[1].valueChanged.connect(
            self._on_coord_1_widget_changed, QtCore.Qt.ConnectionType.UniqueConnection
        )
        coord_2.editors[0].valueChanged.connect(
            self._on_coord_2_widget_changed, QtCore.Qt.ConnectionType.UniqueConnection
        )
        coord_2.editors[1].valueChanged.connect(
            self._on_coord_2_widget_changed, QtCore.Qt.ConnectionType.UniqueConnection
        )

    def set_target(self, chapter_data: GcnChapterData):
        # Clear everything.
        self.dispos_model = None
        self.chapter_data = chapter_data
        self.side_panel.clear_forms()
        self.grid.clear()
        self.undo_stack.clear()

        # Update the UI based on the new data.
        self.dispos_model = GcnDisposModel(self.gd, self.maps, chapter_data.dispos)
        self._update_tree_model()
        self.grid.set_target(chapter_data, self.dispos_model)
        self.grid.set_selection_model(self.tree.selectionModel())
        self.grid.set_tile_colors(self.maps.get_terrain_colors(chapter_data))
        self.refresh_actions()

    def set_selection(self, selection):
        if not selection:
            self.side_panel.set_spawn_target(None)
            self.tree.clearSelection()
            if self.tree.selectionModel():
                self.tree.selectionModel().clearCurrentIndex()
        if self.maps.is_spawn(selection):
            self.side_panel.set_spawn_target(selection)
        self.refresh_actions()

    def move_spawn(self, row, col, spawn, coordinate_change_type):
        # Get back to the state the editor was in
        # when the change was made.
        current_change_type = (
            CoordinateChangeType.COORD_2
            if self._is_coordinate_2()
            else CoordinateChangeType.COORD_1
        )
        if (
            current_change_type != coordinate_change_type
            and coordinate_change_type != CoordinateChangeType.BOTH
        ):
            self.coordinate_mode_action.setChecked(
                current_change_type == CoordinateChangeType.COORD_2
            )

        # Move the spawn in the frontend.
        self.grid.move_spawn(spawn, row, col)
        index = self.dispos_model.spawn_to_index(spawn)

        # Move the spawn in the backend.
        self.maps.move_spawn(spawn, row, col, coordinate_change_type)

        # Update the selected spawn.
        if index.isValid():
            self.tree.selectionModel().setCurrentIndex(
                index, QItemSelectionModel.SelectionFlag.ClearAndSelect
            )

            # Update widgets.
            self.spawn_widgets["coord_1"].set_target(spawn)
            self.spawn_widgets["coord_2"].set_target(spawn)
        self.status_bar.showMessage(f"Moved spawn to ({col}, {row})", 5000)
        self.refresh_actions()

    def add_faction(
        self, difficulty_item: QStandardItem, name=None, faction=None, index=None
    ):
        group, index = self.dispos_model.add_group(
            difficulty_item, name, faction, index
        )
        self.grid.refresh()
        self.refresh_actions()
        self.status_bar.showMessage("Added group.", 5000)
        return group, index

    def delete_faction(self, group):
        self.dispos_model.delete_group(group)
        self.grid.refresh()
        self.refresh_actions()
        self.status_bar.showMessage("Deleted group.", 5000)

    def add_spawn(self, group, spawn=None, index=None):
        spawn, index = self.dispos_model.add_spawn(group, rid=spawn, index=index)
        self.grid.refresh()
        self.refresh_actions()
        self.status_bar.showMessage("Added spawn.", 5000)
        return spawn, index

    def delete_spawn(self, spawn):
        self.dispos_model.delete_spawn(spawn)
        self.grid.refresh()
        self.refresh_actions()
        self.status_bar.showMessage("Deleted spawn.", 5000)

    def reorder_spawn(self, index, new_index):
        item = self.dispos_model.itemFromIndex(index)
        if index.row() < new_index.row():
            self.dispos_model.move_spawn_down(item)
        else:
            self.dispos_model.move_spawn_up(item)
        self.tree.selectionModel().setCurrentIndex(
            new_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        self.status_bar.showMessage("Reordered spawn.", 5000)

    def reorder_faction(self, index, new_index):
        item = self.dispos_model.itemFromIndex(index)
        if index.row() < new_index.row():
            self.dispos_model.move_group_down(item)
        else:
            self.dispos_model.move_group_up(item)
        self.tree.selectionModel().setCurrentIndex(
            new_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        self.status_bar.showMessage("Reordered group.", 5000)

    def paste_spawn(self, source, dest):
        self.gd.copy(source, dest, [])
        self.grid.refresh()
        self.dispos_model.update_spawn_data(dest)
        self.set_selection(dest)
        self.refresh_actions()
        self.status_bar.showMessage("Pasted spawn.", 5000)

    def paste_tile(self, source, dest):
        self.gd.copy(source, dest, [])
        self.grid.refresh()
        self.set_selection(dest)
        self.refresh_actions()
        self.status_bar.showMessage("Pasted tile.", 5000)

    def rename_group(self, group, name):
        self.dispos_model.rename_group(group, name)
        self.refresh_actions()
        self.status_bar.showMessage(f"Renamed group to {name}.", 5000)

    def _on_deselect(self):
        try:
            self.set_selection(None)
        except:
            utils.error(self)

    def _on_current_changed(self, current: QItemSelection):
        try:
            if current.count():
                index = current.indexes()[0]
                if self.dispos_model:
                    self.set_selection(
                        self.dispos_model.data(index, QtCore.Qt.ItemDataRole.UserRole)
                    )
        except:
            utils.error(self)

    def _on_team_changed(self):
        if self._selection_is_spawn():
            try:
                spawn = self._get_selection()
                self.grid.update_spawn(spawn)
            except:
                utils.error(self)

    def _on_character_changed(self):
        if self._selection_is_spawn():
            try:
                spawn = self._get_selection()
                self.grid.update_spawn(spawn)
                self.dispos_model.update_spawn_data(spawn)
            except:
                utils.error(self)

    def _on_coord_1_widget_changed(self):
        if self._selection_is_spawn():
            try:
                spawn = self._get_selection()
                old = deepcopy(self.maps.coord(spawn, False))
                new = self.spawn_widgets["coord_1"].value()
                if old != new:
                    change_type = (
                        CoordinateChangeType.BOTH
                        if self._is_sync_coordinate_changes()
                        else CoordinateChangeType.COORD_1
                    )
                    self.undo_stack.push(
                        MoveSpawnUndoCommand(old, new, spawn, change_type, self)
                    )
            except:
                utils.error(self)

    def _on_coord_2_widget_changed(self):
        if self._selection_is_spawn():
            try:
                spawn = self._get_selection()
                old = deepcopy(self.maps.coord(spawn, True))
                new = self.spawn_widgets["coord_2"].value()
                if old != new:
                    change_type = (
                        CoordinateChangeType.BOTH
                        if self._is_sync_coordinate_changes()
                        else CoordinateChangeType.COORD_2
                    )
                    self.undo_stack.push(
                        MoveSpawnUndoCommand(old, new, spawn, change_type, self)
                    )
            except:
                utils.error(self)

    def _on_hover(self, row, col):
        try:
            if not self.dispos_model:
                self.spawn_label.setText("Spawn: None")
            else:
                spawn = self.grid.spawn_at(row, col)
                spawn_name = self.maps.spawn_name(spawn)
                self.spawn_label.setText(f"Spawn: {spawn_name}")
            if self.chapter_data:
                tile_name = self.maps.tile_name(self.chapter_data, row, col)
                self.tile_label.setText(f"Tile: {tile_name}")
            self.x_label.setText(f"X: {col}")
            self.y_label.setText(f"Y: {row}")
        except:
            utils.error(self)

    def _on_drag(self, row, col):
        try:
            coord_2 = self._is_coordinate_2()
            spawn = self._get_selection()
            old = deepcopy(self.maps.coord(spawn, coord_2))
            new = [col, row]
            if old != new:
                change_type = (
                    CoordinateChangeType.BOTH
                    if self._is_sync_coordinate_changes()
                    else (
                        CoordinateChangeType.COORD_2
                        if coord_2
                        else CoordinateChangeType.COORD_1
                    )
                )
                self.undo_stack.push(
                    MoveSpawnUndoCommand(old, new, spawn, change_type, self)
                )
        except:
            utils.error(self)

    def _on_dispos_item_changed(self, item):
        try:
            data = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if self.dispos_model and (
                self.maps.is_group(data) or self.maps.is_difficulty(data)
            ):
                self.grid.refresh()
                self.set_selection(None)
        except:
            utils.error(self)

    def _on_rename_group(self):
        try:
            new_name, ok = QInputDialog.getText(self, "Enter New Name", "Name")
            if ok:
                group = self._get_selection()
                old_name = self.gd.string(group, "name")
                self.undo_stack.push(
                    RenameFactionUndoCommand(group, old_name, new_name, self)
                )
        except:
            utils.error(self)

    def _on_add_group(self):
        try:
            difficulty_item = self.dispos_model.itemFromIndex(
                self.tree.selectionModel().currentIndex()
            )
            if difficulty_item:
                choice, ok = QInputDialog.getText(self, "Enter Name", "Name")
                if ok:
                    self.undo_stack.push(
                        GcnAddFactionUndoCommand(difficulty_item, choice, self)
                    )
                    self.refresh_actions()
        except:
            utils.error(self)

    def _on_add_spawn(self):
        try:
            group_item = self.dispos_model.itemFromIndex(
                self.tree.selectionModel().currentIndex()
            )
            if group_item:
                group = group_item.data(QtCore.Qt.ItemDataRole.UserRole)
                self.undo_stack.push(AddSpawnUndoCommand(group, self))
                self.refresh_actions()
        except:
            utils.error(self)

    def _on_add_shortcut(self):
        try:
            if self._selection_is_group():
                self._on_add_spawn()
            elif self.dispos_model:
                self._on_add_group()
        except:
            utils.error(self)

    def _on_reload(self):
        try:
            self.set_target(self.chapter_data)
        except:
            utils.error(self)

    def _on_delete(self):
        try:
            selection = self._get_selection()
            index = self.tree.currentIndex().row()
            if self._selection_is_group():
                difficulty = self.dispos_model.itemFromIndex(
                    self.tree.currentIndex()
                ).parent()
                self.undo_stack.push(
                    GcnDeleteFactionUndoCommand(difficulty, selection, self, index)
                )
            else:
                group = self.dispos_model.spawn_to_group(selection)
                self.undo_stack.push(
                    DeleteSpawnUndoCommand(group, selection, self, index)
                )
            self.set_selection(None)
        except:
            utils.error(self)

    def _on_move_up(self):
        try:
            index = self.tree.selectionModel().currentIndex()
            item = self.dispos_model.itemFromIndex(index)
            new_index = self.dispos_model.index(
                item.row() - 1, 0, item.parent().index()
            )
            self.undo_stack.push(
                ReorderUndoCommand(index, new_index, self, self._selection_is_group())
            )
            self.refresh_actions()
        except:
            utils.error(self)

    def _on_move_down(self):
        try:
            index = self.tree.selectionModel().currentIndex()
            item = self.dispos_model.itemFromIndex(index)
            if item.parent():
                new_index = self.dispos_model.index(
                    item.row() + 1, 0, item.parent().index()
                )
            else:
                new_index = self.dispos_model.index(item.row() + 1, 0)
            self.undo_stack.push(
                ReorderUndoCommand(index, new_index, self, self._selection_is_group())
            )
            self.refresh_actions()
        except:
            utils.error(self)

    def _on_copy(self):
        try:
            selection = self._get_selection()
            if self.maps.is_spawn(selection) or self.maps.is_tile(selection):
                utils.put_rid_on_clipboard(selection)
        except:
            utils.error(self)

    def _on_paste(self):
        try:
            # Verify that a spawn is currently selected.
            selection = self._get_selection()
            if self.maps.is_spawn(selection):
                # Check if we have an RID on the clipboard.
                rid = utils.get_rid_from_clipboard()
                if not rid:
                    return
                # Perform the paste.
                self.undo_stack.push(
                    PasteSpawnUndoCommand(self.gd, rid, selection, self)
                )
            elif self.maps.is_tile(selection):
                # Check if we have an RID on the clipboard.
                rid = utils.get_rid_from_clipboard()
                if not rid:
                    return
                # Perform the paste.
                self.undo_stack.push(
                    PasteTileUndoCommand(self.gd, rid, selection, self)
                )
        except:
            utils.error(self)

    def _on_undo(self):
        try:
            if self.undo_stack.canUndo():
                self.undo_stack.undo()
                self.refresh_actions()
        except:
            utils.error(self)

    def _on_redo(self):
        try:
            if self.undo_stack.canRedo():
                self.undo_stack.redo()
                self.refresh_actions()
        except:
            utils.error(self)

    def _on_zoom(self):
        try:
            self.grid.set_zoom(self.zoom_slider.value())
            self.config.map_editor_zoom = self.zoom_slider.value()
        except:
            utils.error(self)

    def _on_update_both_coordinates_checked(self):
        self.config.sync_coordinate_changes = self._is_sync_coordinate_changes()

    def _update_tree_model(self):
        if self.tree.model():
            self.tree.model().disconnect(self)
        if self.tree.selectionModel():
            self.tree.selectionModel().disconnect(self)
        self.tree.setModel(self.dispos_model)
        self.grid.set_selection_model(self.tree.selectionModel())
        if self.dispos_model:
            self.dispos_model.itemChanged.connect(
                self._on_dispos_item_changed, QtCore.Qt.ConnectionType.UniqueConnection
            )
        if self.tree.selectionModel():
            self.tree.selectionModel().selectionChanged.connect(
                self._on_current_changed, QtCore.Qt.ConnectionType.UniqueConnection
            )

    def _on_status_bar_toggled(self):
        self.status_bar.setVisible(self.status_bar_action.isChecked())

    def _on_left_panel_toggled(self):
        self.tree.setVisible(self.left_panel_action.isChecked())

    def _on_right_panel_toggled(self):
        self.side_panel.setVisible(self.right_panel_action.isChecked())

    def _get_selection(self):
        index = self.tree.currentIndex()
        if index.isValid():
            return self.tree.model().data(index, QtCore.Qt.ItemDataRole.UserRole)
        else:
            return None

    def _selection_is_spawn(self):
        if not self.dispos_model:
            return False
        index = self.tree.currentIndex()
        data = self.dispos_model.data(index, QtCore.Qt.ItemDataRole.UserRole)
        return self.maps.is_spawn(data)

    def _selection_is_group(self):
        if not self.dispos_model:
            return False
        index = self.tree.currentIndex()
        data = self.dispos_model.data(index, QtCore.Qt.ItemDataRole.UserRole)
        return self.maps.is_group(data)

    def _selection_is_difficulty(self):
        if not self.dispos_model:
            return False
        index = self.tree.currentIndex()
        data = self.dispos_model.data(index, QtCore.Qt.ItemDataRole.UserRole)
        return self.maps.is_difficulty(data)

    def _can_move_up(self):
        if not self._selection_is_spawn() and not self._selection_is_group():
            return False
        return self.tree.currentIndex().row() > 0

    def _can_move_down(self):
        if not self._selection_is_spawn() and not self._selection_is_group():
            return False
        item = self.dispos_model.itemFromIndex(self.tree.currentIndex())
        row_count = (
            item.parent().rowCount() if item.parent() else self.dispos_model.rowCount()
        )
        return self.tree.currentIndex().row() < row_count - 1

    def _is_coordinate_2(self):
        return self.coordinate_mode_action.isChecked()

    def _is_sync_coordinate_changes(self):
        return self.update_both_coordinates_action.isChecked()
