from copy import deepcopy

from PySide2 import QtCore
from PySide2.QtCore import QItemSelectionModel, QItemSelection
from PySide2.QtWidgets import QUndoStack, QInputDialog

from paragon.model.dispos_model import DisposModel
from paragon.model.game import Game
from paragon.ui.commands.add_faction_undo_command import AddFactionUndoCommand
from paragon.ui.commands.add_spawn_undo_command import AddSpawnUndoCommand
from paragon.ui.commands.delete_faction_undo_command import DeleteFactionUndoCommand
from paragon.ui.commands.delete_spawn_undo_command import DeleteSpawnUndoCommand
from paragon.ui.commands.move_spawn_undo_command import MoveSpawnUndoCommand
from paragon.ui.commands.reorder_spawn_undo_command import ReorderSpawnUndoCommand
from paragon.ui.controllers.fe13_map_editor_side_panel import FE13MapEditorSidePanel
from paragon.ui.controllers.map_grid import MapGrid
from paragon.ui.views.ui_map_editor import Ui_MapEditor


class MapEditor(Ui_MapEditor):
    def __init__(self, ms, gs):
        super().__init__()
        self.dispos_model = None
        self.tiles_model = None
        self.terrain = None
        self.cid = None
        self.gd = gs.data
        self.chapters = gs.chapters
        self.undo_stack = QUndoStack()

        self.grid = MapGrid(
            gs.chapters, gs.sprites, self._is_terrain_mode, self._is_coordinate_2
        )
        self.splitter.addWidget(self.grid)
        self.splitter.setStretchFactor(1, 1)

        if gs.project.game == Game.FE13:
            self.side_panel = FE13MapEditorSidePanel(ms, gs)
            self.splitter.addWidget(self.side_panel)
        else:
            raise NotImplementedError

        self.grid.dragged.connect(self._on_drag)
        self.grid.hovered.connect(self._on_hover)
        self.add_faction_action.triggered.connect(self._on_add_faction)
        self.add_spawn_action.triggered.connect(self._on_add_spawn)
        self.delete_action.triggered.connect(self._on_delete)
        self.move_up_action.triggered.connect(self._on_move_up)
        self.move_down_action.triggered.connect(self._on_move_down)
        self.terrain_mode_action.toggled.connect(self._on_terrain_mode)
        self.terrain_mode_action.toggled.connect(self.grid.toggle_mode)
        self.terrain_mode_action.toggled.connect(self.side_panel.toggle_mode)
        self.coordinate_mode_action.toggled.connect(self.grid.refresh)
        self.undo_action.triggered.connect(self._on_undo)
        self.redo_action.triggered.connect(self._on_redo)
        self.zoom_slider.valueChanged.connect(self._on_zoom)

        self.refresh_actions()

    def refresh_actions(self):
        dispos_actions_enabled = not self._is_terrain_mode()
        faction_actions_enabled = self._selection_is_faction()
        spawn_actions_enabled = self._selection_is_spawn()
        terrain_actions_enabled = self._is_terrain_mode()
        self.add_faction_action.setEnabled(dispos_actions_enabled)
        self.add_spawn_action.setEnabled(faction_actions_enabled)
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

        # Update the UI based on the new data.
        self._update_tree_model()
        self.grid.set_dispos(self.dispos_model, person_key)
        self.grid.set_selection_model(self.tree.selectionModel())
        self.refresh_actions()

    def set_selection(self, selection):
        if not selection:
            self.tree.clearSelection()
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
        self.refresh_actions()

    def add_faction(self, name=None, faction=None, index=None):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        faction, index = self.dispos_model.add_faction(name, faction, index)
        self.grid.refresh()
        self.refresh_actions()
        return faction, index

    def delete_faction(self, faction):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        self.dispos_model.delete_faction(faction)
        self.grid.refresh()
        self.refresh_actions()

    def add_spawn(self, faction, spawn=None, index=None):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        spawn, index = self.dispos_model.add_spawn(faction, rid=spawn, index=index)
        self.grid.refresh()
        self.refresh_actions()
        return spawn, index

    def delete_spawn(self, spawn):
        if self._is_terrain_mode():
            self.toggle_terrain_mode()
        self.dispos_model.delete_spawn(spawn)
        self.grid.refresh()
        self.refresh_actions()

    def reorder_spawn(self, index, new_index):
        item = self.dispos_model.itemFromIndex(index)
        if index.row() < new_index.row():
            self.dispos_model.move_spawn_down(item)
        else:
            self.dispos_model.move_spawn_up(item)
        self.tree.selectionModel().setCurrentIndex(
            new_index, QItemSelectionModel.ClearAndSelect
        )

    def toggle_terrain_mode(self):
        self.terrain_mode_action.setChecked(not self.terrain_mode_action.isChecked())
        self._update_tree_model()

    def _on_current_changed(self, current: QItemSelection):
        if current.count():
            index = current.indexes()[0]
            model = self.tiles_model if self._is_terrain_mode() else self.dispos_model
            if model:
                self.set_selection(model.data(index, QtCore.Qt.UserRole))

    def _on_drag(self, row, col):
        if not self._is_terrain_mode():
            coord_2 = self._is_coordinate_2()
            spawn = self._get_selection()
            old = deepcopy(self.chapters.coord(spawn, coord_2))
            new = [col, row]
            if old != new:
                self.undo_stack.push(
                    MoveSpawnUndoCommand(old, new, spawn, coord_2, self)
                )

    def _on_hover(self, row, col):
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

    def _on_tile_clicked(self):
        pass

    def _on_add_faction(self):
        choice, ok = QInputDialog.getText(self, "Enter Name", "Name")
        if ok:
            self.undo_stack.push(AddFactionUndoCommand(choice, self))
            self.refresh_actions()

    def _on_add_spawn(self):
        faction_item = self.dispos_model.itemFromIndex(
            self.tree.selectionModel().currentIndex()
        )
        if faction_item:
            faction = faction_item.data(QtCore.Qt.UserRole)
            self.undo_stack.push(AddSpawnUndoCommand(faction, self))
            self.refresh_actions()

    def _on_add_tile(self):
        pass

    def _on_delete(self):
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

    def _on_move_up(self):
        index = self.tree.selectionModel().currentIndex()
        item = self.dispos_model.itemFromIndex(index)
        new_index = self.dispos_model.index(item.row() - 1, 0, item.parent().index())
        self.undo_stack.push(ReorderSpawnUndoCommand(index, new_index, self))
        self.refresh_actions()

    def _on_move_down(self):
        index = self.tree.selectionModel().currentIndex()
        item = self.dispos_model.itemFromIndex(index)
        new_index = self.dispos_model.index(item.row() + 1, 0, item.parent().index())
        self.undo_stack.push(ReorderSpawnUndoCommand(index, new_index, self))
        self.refresh_actions()

    def _on_copy(self):
        pass

    def _on_paste(self):
        pass

    def _on_undo(self):
        if self.undo_stack.canUndo():
            self.undo_stack.undo()
            self.refresh_actions()

    def _on_redo(self):
        if self.undo_stack.canRedo():
            self.undo_stack.redo()
            self.refresh_actions()

    def _on_terrain_mode(self):
        self._update_tree_model()
        self.refresh_actions()

    def _on_zoom(self):
        self.grid.set_zoom(self.zoom_slider.value())

    def _update_tree_model(self):
        if self.tree.selectionModel():
            self.tree.selectionModel().disconnect(self)
        if self._is_terrain_mode():
            self.tree.setModel(self.tiles_model)
        else:
            self.tree.setModel(self.dispos_model)
            self.grid.set_selection_model(self.tree.selectionModel())
        if self.tree.selectionModel():
            self.tree.selectionModel().selectionChanged.connect(
                self._on_current_changed
            )

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
