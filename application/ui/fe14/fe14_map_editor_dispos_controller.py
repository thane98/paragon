from typing import Optional

from PySide2 import QtCore
from PySide2.QtCore import QModelIndex, QItemSelectionModel
from PySide2.QtWidgets import QInputDialog

from model.fe14.chapter_data import ChapterData
from model.fe14.dispo import Faction
from model.qt.dispo_model import DisposModel
from module.properties.property_container import PropertyContainer
from ui.error_dialog import ErrorDialog
from ui.fe14.actions.add_group_action import AddGroupAction
from ui.fe14.actions.add_spawn_action import AddSpawnAction
from ui.fe14.actions.delete_group_action import DeleteGroupAction
from ui.fe14.actions.delete_spawn_action import DeleteSpawnAction
from ui.fe14.actions.move_spawn_action import MoveSpawnAction
from ui.fe14.actions.paste_spawn_action import PasteSpawnAction
from ui.fe14.fe14_map_editor import FE14MapEditor


class FE14MapEditorDisposController:
    def __init__(self, map_editor: FE14MapEditor):
        self.view = map_editor
        self.error_dialog = None
        self.copied_spawn = None
        self.chapter_data: Optional[ChapterData] = None
        self.dispos_model: Optional[DisposModel] = None
        self.current_faction: Optional[Faction] = None
        self.active = True
        self.selection_change_in_progress = False
        self.set_active(self.active)
        self.view.coordinate_type_label.setText("Coordinate Type: " + self.view.grid.coordinate_key)

        self.view.add_group_action.triggered.connect(self._add_group)
        self.view.delete_group_action.triggered.connect(self._delete_group)
        self.view.delete_spawn_action.triggered.connect(self._delete_spawn)
        self.view.add_spawn_action.triggered.connect(self._add_spawn_to_group)
        self.view.grid.focused_spawn_changed.connect(self._update_spawn_selection)
        self.view.grid.spawn_location_changed.connect(self.update_active_spawn_position_from_grid_change)
        self.view.toggle_coordinate_type_action.triggered.connect(self._toggle_coordinate_type)
        self.view.copy_spawn_action.triggered.connect(self._copy_spawn)
        self.view.paste_spawn_action.triggered.connect(self._paste_spawn)
        self.view.undo_action.triggered.connect(self._undo)
        self.view.redo_action.triggered.connect(self._redo)
        self.view.add_item_shortcut.activated.connect(self._on_add_shortcut_pressed)
        self.view.delete_shortcut.activated.connect(self._on_delete_shortcut_pressed)
        self.view.deselect_shortcut.activated.connect(self._deselect)
        self.view.refresh_action.triggered.connect(self._refresh)

        spawn_form = self.view.spawn_pane.form
        spawn_form.editors["PID"].editingFinished.connect(self._on_important_spawn_field_changed)
        spawn_form.editors["Team"].currentIndexChanged.connect(self._on_important_spawn_field_changed)
        spawn_form.editors["Coordinate (1)"].set_disable_write_back(True)
        spawn_form.editors["Coordinate (1)"].position_changed.connect(self._on_coordinate_1_field_changed)
        spawn_form.editors["Coordinate (2)"].set_disable_write_back(True)
        spawn_form.editors["Coordinate (2)"].position_changed.connect(self._on_coordinate_2_field_changed)

    def update_chapter_data(self, chapter_data: Optional[ChapterData]):
        self.chapter_data = chapter_data
        if self.dispos_model:
            self.dispos_model.undo_stack.stack_state_changed.disconnect()
        self.dispos_model = chapter_data.dispos_model if chapter_data else None
        if self.dispos_model:
            self.dispos_model.undo_stack.stack_state_changed.connect(self._update_undo_redo_actions)
        self.update_selection(QModelIndex())
        self.set_active(self.dispos_model is not None)
        self._update_undo_redo_actions()

    def update_selection(self, index: QModelIndex):
        if self.dispos_model and index.isValid():
            data = self.dispos_model.data(index, QtCore.Qt.UserRole)
            if isinstance(data, Faction):
                self._toggle_spawn_actions(False)
                self._toggle_faction_actions(True)
                self.view.grid.clear_selection()
                self.view.spawn_pane.form.update_target(None)
                self.current_faction = data
            else:
                self._update_spawn_selection(data)
                if data:
                    self.view.grid.select_spawn(data)
        else:
            self.view.spawn_pane.update_target(None)
            self.view.grid.clear_selection()
            self.current_faction = None

    def _update_spawn_selection(self, spawn: Optional[PropertyContainer]):
        self.selection_change_in_progress = True
        self.current_faction = self.dispos_model.get_faction_from_spawn(spawn) if spawn else None
        self._toggle_faction_actions(spawn is not None)
        self._toggle_spawn_actions(spawn is not None)
        self.view.spawn_pane.update_target(spawn)
        self.view.model_view.selectionModel().select(
            self.dispos_model.get_index_from_spawn(spawn),
            QItemSelectionModel.SelectCurrent
        )
        faction_index = self.dispos_model.get_index_from_faction(self.current_faction)
        if faction_index and faction_index.isValid():
            self.view.model_view.expand(faction_index)
        self.selection_change_in_progress = False

    def set_active(self, active: bool):
        self.active = active and self.dispos_model
        if active:
            self.enable_actions_post_switch()
            self.view.show_spawn_pane(self.dispos_model)
        else:
            self.disable_all_actions()
            self.current_faction = None

    def enable_actions_post_switch(self):
        self.disable_all_actions()
        self.view.toggle_coordinate_type_action.setEnabled(True)
        self.view.add_group_action.setEnabled(True)
        self._update_undo_redo_actions()

    def disable_all_actions(self):
        self.view.add_group_action.setEnabled(False)
        self.view.delete_group_action.setEnabled(False)
        self.view.add_spawn_action.setEnabled(False)
        self.view.delete_spawn_action.setEnabled(False)
        self.view.toggle_coordinate_type_action.setEnabled(False)
        self.view.undo_action.setEnabled(False)
        self.view.redo_action.setEnabled(False)
        self.view.copy_spawn_action.setEnabled(False)
        self.view.paste_spawn_action.setEnabled(False)

    def _toggle_faction_actions(self, on: bool):
        self.view.add_spawn_action.setEnabled(on)
        self.view.delete_group_action.setEnabled(on)
        self.view.paste_spawn_action.setEnabled(on and self.copied_spawn is not None)

    def _toggle_spawn_actions(self, on: bool):
        self.view.delete_spawn_action.setEnabled(on)
        self.view.copy_spawn_action.setEnabled(on)

    def _add_group(self):
        if self.active and self.dispos_model:
            (faction_name, ok) = QInputDialog.getText(self.view, "Enter a group name.", "Name:")
            if ok:
                if self.dispos_model.is_faction_name_in_use(faction_name):
                    self.error_dialog = ErrorDialog("Faction name is already in use.")
                    self.error_dialog.show()
                    return
                else:
                    self.dispos_model.add_faction(faction_name)
                    faction = self.dispos_model.dispos.factions[-1]
                    self.dispos_model.undo_stack.push_action(AddGroupAction(self, faction))

    def _delete_group(self):
        if self.active and self.dispos_model and self.current_faction:
            self.dispos_model.undo_stack.push_action(DeleteGroupAction(self, self.current_faction))
            self.dispos_model.delete_faction(self.current_faction)
            self.view.grid.set_chapter_data(self.chapter_data)  # Force a refresh.
            self.view.spawn_pane.update_target(None)

    def _add_spawn_to_group(self):
        if self.active and self.dispos_model and self.current_faction:
            self.dispos_model.add_spawn_to_faction(self.current_faction)
            spawn = self.current_faction.spawns[-1]
            self.dispos_model.undo_stack.push_action(AddSpawnAction(self, self.current_faction, spawn))
            self.view.grid.add_spawn_to_map(spawn)

    def _delete_spawn(self):
        if self.active and self.dispos_model and self.current_faction:
            spawn = self.view.grid.selected_spawn
            self.dispos_model.undo_stack.push_action(DeleteSpawnAction(self, self.current_faction, spawn))
            self.dispos_model.delete_spawn(spawn)
            self.view.grid.delete_selected_spawn()
            self._deselect()

    def _toggle_coordinate_type(self):
        if self.dispos_model:
            self.view.grid.toggle_coordinate_key()
            self.update_selection(QModelIndex())

    def update_active_spawn_position_from_grid_change(self, old_position, new_position):
        if not self.view.grid.selected_spawn:
            return
        if old_position[0] == new_position[0] and old_position[1] == new_position[1]:
            return
        spawn = self.view.grid.selected_spawn
        coordinate_key = self.view.grid.coordinate_key
        action = MoveSpawnAction(spawn, old_position, new_position, coordinate_key, self)
        self.dispos_model.undo_stack.push_action(action)
        spawn[coordinate_key].value = new_position
        self.view.spawn_pane.update_coordinate_of_target(coordinate_key, spawn)

    def _undo(self):
        if not self.active or not self.dispos_model or not self.dispos_model.undo_stack.can_undo():
            return
        undo_stack = self.dispos_model.undo_stack
        undo_stack.undo()
        self._update_undo_redo_actions()

    def _redo(self):
        if not self.active or not self.dispos_model or not self.dispos_model.undo_stack.can_redo():
            return
        undo_stack = self.dispos_model.undo_stack
        undo_stack.redo()
        self._update_undo_redo_actions()

    def _copy_spawn(self):
        if self.active and self.current_faction:
            spawn = self.view.grid.selected_spawn
            if spawn:
                self.copied_spawn = spawn.duplicate()
                self.view.paste_spawn_action.setEnabled(True)

    def _paste_spawn(self):
        if not self.dispos_model or not self.copied_spawn:
            return
        elif self.view.grid.selected_spawn:
            target_spawn = self.view.grid.selected_spawn
            self.dispos_model.undo_stack.push_action(PasteSpawnAction(self, target_spawn, self.copied_spawn))
            self.dispos_model.copy_spawn_and_ignore_coordinates(self.copied_spawn, target_spawn)
            self.view.grid.refresh_cell_from_spawn(target_spawn)
            self.view.spawn_pane.update_target(target_spawn)
        elif self.current_faction:
            self.dispos_model.add_spawn_to_faction(self.current_faction, self.copied_spawn.duplicate())
            spawn = self.current_faction.spawns[-1]
            self.dispos_model.undo_stack.push_action(AddSpawnAction(self, self.current_faction, spawn))
            self.view.grid.add_spawn_to_map(spawn)

    def _on_important_spawn_field_changed(self):
        spawn = self.view.grid.selected_spawn
        if spawn:
            self.dispos_model.refresh_spawn(spawn)
            self.view.grid.refresh_cell_from_spawn(spawn)

    def _on_coordinate_1_field_changed(self, row, col):
        grid = self.view.grid
        if grid.selected_spawn and not self.selection_change_in_progress:
            grid.update_focused_spawn_position([row, col], "Coordinate (1)")

    def _on_coordinate_2_field_changed(self, row, col):
        grid = self.view.grid
        if grid.selected_spawn and not self.selection_change_in_progress:
            grid.update_focused_spawn_position([row, col], "Coordinate (2)")

    def _on_add_shortcut_pressed(self):
        if not self.active:
            return
        if self.current_faction:
            self._add_spawn_to_group()
        else:
            self._add_group()

    def _on_delete_shortcut_pressed(self):
        if not self.active:
            return
        if self.view.grid.selected_spawn:
            self._delete_spawn()
        else:
            self._delete_group()

    def _deselect(self):
        if self.active:
            self.view.model_view.setCurrentIndex(QModelIndex())
            self.update_selection(QModelIndex())
            self.view.grid.clear_selection()

    def _update_undo_redo_actions(self):
        if self.dispos_model:
            self.view.undo_action.setEnabled(self.active and self.dispos_model.undo_stack.can_undo())
            self.view.redo_action.setEnabled(self.active and self.dispos_model.undo_stack.can_redo())

    def _refresh(self):
        if self.chapter_data:
            self._deselect()
            self.selection_change_in_progress = False
            self.view.grid.set_chapter_data(self.chapter_data)
            self.view.status_bar.showMessage("Refreshed map editor.", 5000)
