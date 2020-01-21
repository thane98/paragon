import json

from PySide2.QtCore import Signal
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QGridLayout, QShortcut

from ui.map_cell import MapCell


def _load_terrain_colors():
    result = {}
    with open("Modules/ServiceData/FE14TerrainColors.json", "r", encoding="utf-8") as f:
        js = json.load(f)
        for elem in js:
            result[elem] = js[elem]
    return result


TILE_TO_COLOR_STRING = _load_terrain_colors()


class MapGrid(QWidget):
    focused_spawn_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.cells = []
        self.selected_spawns = []
        self.chapter_data = None
        self.selected_tile = None
        self.terrain_mode = False
        self.coordinate_key = "Coordinate (1)"

        layout = QGridLayout()
        for r in range(0, 32):
            row = []
            for c in range(0, 32):
                cell = self._create_cell(r, c)
                layout.addWidget(cell, r, c)
                row.append(cell)
            self.cells.append(row)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        self.setLayout(layout)

        self.delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        self.delete_shortcut.activated.connect(self._delete_selected_spawns)

    def _create_cell(self, r, c):
        cell = MapCell(r, c)
        cell.spawn_selected.connect(self._on_cell_selected)
        cell.spawn_selection_expanded.connect(self._on_cell_selection_expanded)
        cell.selected_for_move.connect(self._on_cell_selected_for_move)
        cell.tile_selected.connect(self._on_tile_selected)
        return cell

    def set_chapter_data(self, chapter_data):
        self.clear()
        if chapter_data:
            self._place_spawns(chapter_data.dispos)
            self._update_terrain(chapter_data.terrain)
        self.chapter_data = chapter_data

    def _refresh_dispos(self):
        dispos = self.chapter_data.dispos
        self.clear()
        self._place_spawns(dispos)

    def clear(self):
        self.selected_spawns.clear()
        for r in range(0, 32):
            for c in range(0, 32):
                cell = self.cells[r][c]
                cell.clear_spawns()

    def _place_spawns(self, dispos):
        for faction in dispos.factions:
            for spawn in faction.spawns:
                coordinate = spawn[self.coordinate_key].value
                if coordinate[0] in range(0, 32) and coordinate[1] in range(0, 32):
                    target_cell = self.cells[coordinate[1]][coordinate[0]]
                    target_cell.place_spawn(spawn)

    def _update_terrain(self, new_terrain):
        for row in range(0, 32):
            for col in range(0, 32):
                tile_id = new_terrain.grid[row][col]
                tile = new_terrain.tiles[tile_id]
                self._update_cell_terrain(row, col, tile)

    def _update_cell_terrain(self, row, col, tile):
        tid = tile["Name"].key
        if tid in TILE_TO_COLOR_STRING:
            color_string = TILE_TO_COLOR_STRING[tid]
        else:
            color_string = "#424242"
        target_cell = self.cells[row][col]
        target_cell.set_color(color_string)
        target_cell.setToolTip(tile["Name"].value)

    def _on_cell_selected(self, selected_cell):
        self._clear_selection()
        self.selected_spawns.append(selected_cell.spawns[-1])
        self.focused_spawn_changed.emit(self.selected_spawns[-1])
        selected_cell.set_selected(True)

    def _clear_selection(self):
        for spawn in self.selected_spawns:
            cell = self._spawn_to_cell(spawn)
            if cell:
                cell.set_selected(False)
        self.selected_spawns.clear()

    def _spawn_to_cell(self, spawn):
        coordinate = spawn[self.coordinate_key].value
        if coordinate[0] in range(0, 32) and coordinate[1] in range(0, 32):
            return self.cells[coordinate[1]][coordinate[0]]
        return None

    def _on_cell_selection_expanded(self, cell):
        spawn = cell.spawns[-1]
        if spawn not in self.selected_spawns:
            self.selected_spawns.append(spawn)
            cell.set_selected(True)
            self.focused_spawn_changed.emit(spawn)

    def _on_cell_selected_for_move(self, cell):
        if not self.selected_spawns:
            return
        origin_spawn = self.selected_spawns[-1]
        (delta_row, delta_col) = self._calculate_move_delta(origin_spawn, cell)
        if self._move_is_valid(delta_row, delta_col):
            self._perform_move(delta_row, delta_col)

    def _calculate_move_delta(self, origin_spawn, target_cell):
        (row, column) = self._get_bounded_position_on_grid(origin_spawn)
        return target_cell.row - row, target_cell.column - column

    def _get_bounded_position_on_grid(self, spawn):
        coordinate = spawn[self.coordinate_key].value
        if coordinate[1] not in range(0, 32):
            row = 0
        else:
            row = coordinate[1]
        if coordinate[0] not in range(0, 32):
            column = 0
        else:
            column = coordinate[0]
        return row, column

    def _move_is_valid(self, delta_row, delta_col):
        for spawn in self.selected_spawns:
            (start_row, start_col) = self._get_bounded_position_on_grid(spawn)
            new_row = start_row + delta_row
            new_col = start_col + delta_col
            if new_row not in range(0, 32) or new_col not in range(0, 32):
                return False
        return True

    def _clear_selected_cells(self):
        for spawn in self.selected_spawns:
            cell = self._spawn_to_cell(spawn)
            if cell:
                cell.set_selected(False)

    def _perform_move(self, delta_row, delta_col):
        self._clear_selected_cells()
        for spawn in self.selected_spawns:
            (start_row, start_col) = self._get_bounded_position_on_grid(spawn)
            new_row = start_row + delta_row
            new_col = start_col + delta_col
            self._move_spawn(spawn, new_row, new_col)

    def _move_spawn(self, spawn, new_row, new_col):
        # Remove the spawn from the old cell if one exists.
        source = self._spawn_to_cell(spawn)
        if source:
            source.pop_spawn()

        # Update the model.
        coordinate = spawn[self.coordinate_key].value
        coordinate[0] = new_col
        coordinate[1] = new_row

        # Add the spawn to the new cell if one exists.
        new_cell = self._spawn_to_cell(spawn)
        if new_cell:
            new_cell.place_spawn(spawn)
            new_cell.set_selected(True)

    def _delete_selected_spawns(self):
        for spawn in self.selected_spawns:
            self.chapter_data.dispos.delete_spawn(spawn)
            cell = self._spawn_to_cell(spawn)
            if cell:
                cell.remove_spawn(spawn)
        self._clear_selection()

    def transition_to_terrain_mode(self):
        self.terrain_mode = True
        self.selected_spawns.clear()
        for r in range(0, 32):
            for c in range(0, 32):
                self.cells[r][c].transition_to_terrain_mode()

    def transition_to_dispos_mode(self):
        self.terrain_mode = False
        for r in range(0, 32):
            for c in range(0, 32):
                self.cells[r][c].transition_to_dispos_mode()

    def toggle_coordinate_key(self):
        if self.coordinate_key == "Coordinate (1)":
            self.coordinate_key = "Coordinate (2)"
        else:
            self.coordinate_key = "Coordinate (1)"
        self.selected_spawns.clear()
        self._refresh_dispos()

    def _on_tile_selected(self, cell):
        if self.selected_tile:
            tile_id = self.selected_tile["ID"].value
            self.chapter_data.terrain.grid[cell.row][cell.column] = tile_id
            self._update_cell_terrain(cell.row, cell.column, self.selected_tile)

    def select_spawn(self, spawn):
        self._clear_selection()
        self.selected_spawns.append(spawn)
        self.focused_spawn_changed.emit(self.selected_spawns[-1])
        cell = self._spawn_to_cell(spawn)
        if cell:
            cell.set_selected(True)

    def add_spawn_to_map(self, spawn):
        cell = self._spawn_to_cell(spawn)
        if cell:
            cell.place_spawn(spawn)

    def update_team_for_focused_spawn(self):
        if self.selected_spawns:
            spawn = self.selected_spawns[-1]
            cell = self._spawn_to_cell(spawn)
            if cell:
                top = cell.pop_spawn()
                cell.place_spawn(top)

    def update_focused_spawn_position(self, new_position, coordinate_key):
        if not self.selected_spawns:
            return
        spawn = self.selected_spawns[-1]
        coordinate = spawn[coordinate_key].value
        if self.coordinate_key == coordinate_key:
            old_cell = self._spawn_to_cell(spawn)
            if old_cell:
                self._remove_spawn_from_cell_and_clear_selection(spawn, old_cell)
        coordinate[0] = new_position[0]
        coordinate[1] = new_position[1]
        if self.coordinate_key == coordinate_key:
            new_cell = self._spawn_to_cell(spawn)
            if new_cell:
                new_cell.place_spawn(spawn)
                new_cell.set_selected(True)

    def _remove_spawn_from_cell_and_clear_selection(self, spawn, cell):
        cell.remove_spawn(spawn)
        for spawn in self.selected_spawns:
            if spawn in cell.spawns:
                return
        cell.set_selected(False)
