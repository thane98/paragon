from copy import deepcopy

from PySide2 import QtCore
from PySide2.QtCore import QItemSelectionModel, QItemSelection, QMimeData
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QUndoStack, QInputDialog
from paragon.ui import utils

from paragon.model.dispos_model import DisposModel
from paragon.model.game import Game
from paragon.ui.commands.add_faction_undo_command import AddFactionUndoCommand
from paragon.ui.commands.add_spawn_undo_command import AddSpawnUndoCommand
from paragon.ui.commands.delete_faction_undo_command import DeleteFactionUndoCommand
from paragon.ui.commands.delete_spawn_undo_command import DeleteSpawnUndoCommand
from paragon.ui.commands.move_spawn_undo_command import MoveSpawnUndoCommand
from paragon.ui.commands.paste_spawn_undo_command import PasteSpawnUndoCommand
from paragon.ui.commands.rename_faction_undo_command import RenameFactionUndoCommand
from paragon.ui.commands.reorder_spawn_undo_command import ReorderSpawnUndoCommand
from paragon.ui.controllers.fe13_map_editor_side_panel import FE13MapEditorSidePanel
from paragon.ui.controllers.fe14_map_editor_side_panel import FE14MapEditorSidePanel
from paragon.ui.controllers.map_grid import MapGrid
from paragon.ui.views.ui_map_editor import Ui_MapEditor


class MapEditor(Ui_MapEditor):
    def __init__(self, ms, gs):
        super().__init__()
        self.gd = gs.data
        self.dispos_model = None
        self.tiles_model = None
        self.person_key = None
        self.dispos = None
        self.terrain = None
        self.cid = None
        self.gd = gs.data
        self.chapters = gs.chapters
        self.undo_stack = QUndoStack()

        self.grid = MapGrid(
            gs.chapters,
            gs.sprites,
            gs.sprite_animation,
            self._is_terrain_mode,
            self._is_coordinate_2,
            gs.project.game,
        )
        self.splitter.addWidget(self.grid)
        self.splitter.setStretchFactor(1, 1)

        if gs.project.game == Game.FE13:
            self.side_panel = FE13MapEditorSidePanel(ms, gs)
            self.splitter.addWidget(self.side_panel)
        elif gs.project.game == Game.FE14:
            self.side_panel = FE14MapEditorSidePanel(ms, gs)
            self.splitter.addWidget(self.side_panel)
        else:
            raise NotImplementedError

        self.grid.dragged.connect(self._on_drag)
        self.grid.hovered.connect(self._on_hover)
        self.grid.tile_clicked.connect(self._on_tile_clicked)
        self.deselect_shortcut.activated.connect(self._on_deselect)
        self.status_bar_action.toggled.connect(self._on_status_bar_toggled)
        self.left_panel_action.toggled.connect(self._on_left_panel_toggled)
        self.right_panel_action.toggled.connect(self._on_right_panel_toggled)
        self.add_shortcut.activated.connect(self._on_add_shortcut)
        self.rename_faction_action.triggered.connect(self._on_rename_faction)
        self.add_faction_action.triggered.connect(self._on_add_faction)
        self.add_spawn_action.triggered.connect(self._on_add_spawn)
        self.add_tile_action.triggered.connect(self._on_add_tile)
        self.delete_action.triggered.connect(self._on_delete)
        self.move_up_action.triggered.connect(self._on_move_up)
        self.move_down_action.triggered.connect(self._on_move_down)
        self.terrain_mode_action.toggled.connect(self._on_terrain_mode)
        self.terrain_mode_action.toggled.connect(self.grid.toggle_mode)
        self.terrain_mode_action.toggled.connect(self.side_panel.toggle_mode)
        self.coordinate_mode_action.toggled.connect(self.grid.refresh)
        self.copy_action.triggered.connect(self._on_copy)
        self.paste_action.triggered.connect(self._on_paste)
        self.undo_action.triggered.connect(self._on_undo)
        self.redo_action.triggered.connect(self._on_redo)
        self.zoom_slider.valueChanged.connect(self._on_zoom)
        self.reload_action.triggered.connect(self._on_reload)

        self.refresh_actions()

    def refresh_actions(self):
        dispos_actions_enabled = bool(not self._is_terrain_mode() and self.dispos_model)
        faction_actions_enabled = self._selection_is_faction()
        spawn_actions_enabled = self._selection_is_spawn()
        terrain_actions_enabled = bool(
            self._is_terrain_mode() and self.terrain and self.tiles_model
        )
        self.add_shortcut.setEnabled(dispos_actions_enabled or terrain_actions_enabled)
        self.add_faction_action.setEnabled(dispos_actions_enabled)
        self.add_spawn_action.setEnabled(faction_actions_enabled)
        self.rename_faction_action.setEnabled(faction_actions_enabled)
        self.delete_action.setEnabled(faction_actions_enabled or spawn_actions_enabled)
        self.move_up_action.setEnabled(self._can_move_up())
        self.move_down_action.setEnabled(self._can_move_down())
        self.copy_action.setEnabled(spawn_actions_enabled)
        self.paste_action.setEnabled(spawn_actions_enabled)
        self.add_tile_action.setEnabled(terrain_actions_enabled)
        self.coordinate_mode_action.setEnabled(dispos_actions_enabled)
        self.undo_action.setEnabled(self.undo_stack.canUndo())
        self.redo_action.setEnabled(self.undo_stack.canRedo())

    def set_target(self, cid, person_key, dispos, terrain):
        # Clear everything.
        self.dispos_model = None
        self.tiles_model = None
        self.cid = cid
        self.person_key = person_key
        self.dispos = dispos
        self.terrain = terrain
        self.side_panel.clear_forms()
        self.grid.clear()
        self.undo_stack.clear()

        # Get models if we have data to work with.
        if dispos:
            self.dispos_model = DisposModel(self.gd, self.chapters, dispos, cid)
        if terrain:
            self.tiles_model = self.chapters.tiles_model(cid)
            self.grid.set_tile_colors(self.chapters.terrain_to_colors(terrain))
            self.side_panel.set_terrain_target(terrain)
        else:
            self.grid.set_tile_colors(None)

        # Update the UI based on the new data.
        self._update_tree_model()
        self.grid.set_dispos(self.dispos_model, person_key)
        self.grid.set_selection_model(self.tree.selectionModel())
        self.refresh_actions()

    def set_selection(self, selection):
        if not selection:
            self.side_panel.set_spawn_target(None)
            self.side_panel.set_tile_target(None)
            self.tree.clearSelection()
            if self.tree.selectionModel():
                self.tree.selectionModel().clearCurrentIndex()
        if self.chapters.is_spawn(selection):
            self.side_panel.set_spawn_target(selection)
        if self.chapters.is_tile(selection):
            self.side_panel.set_tile_target(selection)
        self.refresh_actions()

    def move_spawn(self, row, col, spawn, coord_2):
        # Get back to the state the editor was in
        # when the change was made.
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        if self._is_coordinate_2() != coord_2:
            self.coordinate_mode_action.setChecked(coord_2)

        # Move the spawn in the frontend.
        self.grid.move_spawn(spawn, row, col)
        index = self.dispos_model.spawn_to_index(spawn)

        # Move the spawn in the backend.
        self.chapters.move_spawn(spawn, row, col, self._is_coordinate_2())

        # Update the selected spawn.
        if index.isValid():
            self.tree.selectionModel().setCurrentIndex(
                index, QItemSelectionModel.ClearAndSelect
            )
        self.status_bar.showMessage(f"Moved spawn to ({col}, {row})", 5000)
        self.refresh_actions()

    def add_faction(self, name=None, faction=None, index=None):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        faction, index = self.dispos_model.add_faction(name, faction, index)
        self.grid.refresh()
        self.refresh_actions()
        self.status_bar.showMessage("Added faction.", 5000)
        return faction, index

    def delete_faction(self, faction):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        self.dispos_model.delete_faction(faction)
        self.grid.refresh()
        self.refresh_actions()
        self.status_bar.showMessage("Deleted faction.", 5000)

    def add_spawn(self, faction, spawn=None, index=None):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        spawn, index = self.dispos_model.add_spawn(faction, rid=spawn, index=index)
        self.grid.refresh()
        self.refresh_actions()
        self.status_bar.showMessage("Added spawn.", 5000)
        return spawn, index

    def delete_spawn(self, spawn):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
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
            new_index, QItemSelectionModel.ClearAndSelect
        )
        self.status_bar.showMessage("Reordered spawn.", 5000)

    def paste_spawn(self, source, dest):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        self.gd.copy(source, dest, [])
        self.grid.refresh()
        self.set_selection(self._get_selection())
        self.refresh_actions()
        self.status_bar.showMessage("Pasted spawn.", 5000)

    def rename_faction(self, faction, name):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        self.dispos_model.rename_faction(faction, name)
        self.refresh_actions()
        self.status_bar.showMessage(f"Renamed faction to {name}.", 5000)

    def toggle_terrain_mode(self):
        self.terrain_mode_action.setChecked(not self.terrain_mode_action.isChecked())
        self._update_tree_model()

    def _on_deselect(self):
        try:
            self.set_selection(None)
        except:
            utils.error(self)

    def _on_current_changed(self, current: QItemSelection):
        try:
            if current.count():
                index = current.indexes()[0]
                model = (
                    self.tiles_model if self._is_terrain_mode() else self.dispos_model
                )
                if model:
                    self.set_selection(model.data(index, QtCore.Qt.UserRole))
        except:
            utils.error(self)

    def _on_drag(self, row, col):
        try:
            if not self._is_terrain_mode():
                coord_2 = self._is_coordinate_2()
                spawn = self._get_selection()
                old = deepcopy(self.chapters.coord(spawn, coord_2))
                new = [col, row]
                if old != new:
                    self.undo_stack.push(
                        MoveSpawnUndoCommand(old, new, spawn, coord_2, self)
                    )
        except:
            utils.error(self)

    def _on_hover(self, row, col):
        try:
            if not self.dispos_model:
                self.spawn_label.setText("Spawn: None")
            else:
                spawn = self.grid.spawn_at(row, col)
                spawn_name = self.chapters.spawn_name(spawn, self.cid)
                self.spawn_label.setText(f"Spawn: {spawn_name}")
            if not self.terrain:
                self.tile_label.setText("Tile: None")
            else:
                tile_name = self.chapters.tile_name(self.terrain, self.cid, row, col)
                self.tile_label.setText(f"Tile: {tile_name}")
        except:
            utils.error(self)

    def _on_dispos_item_changed(self, item):
        try:
            data = item.data(QtCore.Qt.UserRole)
            if self.dispos_model and self.chapters.is_faction(data):
                self.grid.refresh()
                self.set_selection(None)
        except:
            utils.error(self)

    def _on_tile_clicked(self, row, col):
        try:
            # TODO: Undo/redo
            selection = self._get_selection()
            if self._is_terrain_mode() and self.chapters.is_tile(selection):
                self.chapters.set_tile(self.terrain, selection, row, col)
                color = self.chapters.tile_to_color(selection)
                self.grid.set_tile_color(row, col, color)
        except:
            utils.error(self)

    def _on_rename_faction(self):
        try:
            new_name, ok = QInputDialog.getText(self, "Enter New Name", "Name")
            if ok:
                faction = self._get_selection()
                old_name = self.gd.string(faction, "name")
                self.undo_stack.push(
                    RenameFactionUndoCommand(faction, old_name, new_name, self)
                )
        except:
            utils.error(self)

    def _on_add_faction(self):
        try:
            choice, ok = QInputDialog.getText(self, "Enter Name", "Name")
            if ok:
                self.undo_stack.push(AddFactionUndoCommand(choice, self))
                self.refresh_actions()
        except:
            utils.error(self)

    def _on_add_spawn(self):
        try:
            faction_item = self.dispos_model.itemFromIndex(
                self.tree.selectionModel().currentIndex()
            )
            if faction_item:
                faction = faction_item.data(QtCore.Qt.UserRole)
                self.undo_stack.push(AddSpawnUndoCommand(faction, self))
                self.refresh_actions()
        except:
            utils.error(self)

    def _on_add_shortcut(self):
        try:
            if self._selection_is_faction():
                self._on_add_spawn()
            elif self._is_terrain_mode():
                self._on_add_tile()
            elif self.dispos_model:
                self._on_add_faction()
        except:
            utils.error(self)

    def _on_reload(self):
        try:
            self.set_target(self.cid, self.person_key, self.dispos, self.terrain)
        except:
            utils.error(self)

    def _on_add_tile(self):
        try:
            # TODO: Undo/Redo?
            if self.tiles_model:
                self.tiles_model.add_item()
        except:
            utils.error(self)

    def _on_delete(self):
        try:
            selection = self._get_selection()
            index = self.tree.currentIndex().row()
            if self._selection_is_faction():
                self.undo_stack.push(DeleteFactionUndoCommand(selection, self, index))
            else:
                faction = self.dispos_model.spawn_to_faction(selection)
                self.undo_stack.push(
                    DeleteSpawnUndoCommand(faction, selection, self, index)
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
            self.undo_stack.push(ReorderSpawnUndoCommand(index, new_index, self))
            self.refresh_actions()
        except:
            utils.error(self)

    def _on_move_down(self):
        try:
            index = self.tree.selectionModel().currentIndex()
            item = self.dispos_model.itemFromIndex(index)
            new_index = self.dispos_model.index(
                item.row() + 1, 0, item.parent().index()
            )
            self.undo_stack.push(ReorderSpawnUndoCommand(index, new_index, self))
            self.refresh_actions()
        except:
            utils.error(self)

    def _on_copy(self):
        try:
            selection = self._get_selection()
            if self.chapters.is_spawn(selection):
                utils.put_rid_on_clipboard(selection)
        except:
            utils.error(self)

    def _on_paste(self):
        try:
            # Verify that a spawn is currently selected.
            selection = self._get_selection()
            if not self.chapters.is_spawn(selection):
                return

            # Check if we have an RID on the clipboard.
            rid = utils.get_rid_from_clipboard()
            if not rid:
                return

            # Perform the paste.
            self.undo_stack.push(PasteSpawnUndoCommand(self.gd, rid, selection, self))
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

    def _on_terrain_mode(self):
        try:
            self._update_tree_model()
            self.refresh_actions()
        except:
            utils.error(self)

    def _on_zoom(self):
        try:
            self.grid.set_zoom(self.zoom_slider.value())
        except:
            utils.error(self)

    def _update_tree_model(self):
        if self.tree.model():
            self.tree.model().disconnect(self)
        if self.tree.selectionModel():
            self.tree.selectionModel().disconnect(self)
        if self._is_terrain_mode():
            self.tree.setModel(self.tiles_model)
        else:
            self.tree.setModel(self.dispos_model)
            self.grid.set_selection_model(self.tree.selectionModel())
            if self.dispos_model:
                self.dispos_model.itemChanged.connect(self._on_dispos_item_changed)
        if self.tree.selectionModel():
            self.tree.selectionModel().selectionChanged.connect(
                self._on_current_changed
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
            return self.tree.model().data(index, QtCore.Qt.UserRole)
        else:
            return None

    def _selection_is_spawn(self):
        if self._is_terrain_mode() or not self.dispos_model:
            return False
        index = self.tree.currentIndex()
        data = self.dispos_model.data(index, QtCore.Qt.UserRole)
        return self.chapters.is_spawn(data)

    def _selection_is_faction(self):
        if self._is_terrain_mode() or not self.dispos_model:
            return False
        index = self.tree.currentIndex()
        data = self.dispos_model.data(index, QtCore.Qt.UserRole)
        return self.chapters.is_faction(data)

    def _can_move_up(self):
        if not self._selection_is_spawn():
            return False
        return self.tree.currentIndex().row() > 0

    def _can_move_down(self):
        if not self._selection_is_spawn():
            return False
        item = self.dispos_model.itemFromIndex(self.tree.currentIndex())
        return self.tree.currentIndex().row() < item.parent().rowCount() - 1

    def _is_terrain_mode(self):
        return self.terrain_mode_action.isChecked()

    def _is_coordinate_2(self):
        return self.coordinate_mode_action.isChecked()
