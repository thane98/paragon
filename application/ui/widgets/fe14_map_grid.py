import json
from typing import Tuple, List

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QGridLayout, QScrollArea

from ui.widgets.fe14_map_cell import FE14MapCell


def _load_terrain_colors():
    result = {}
    with open("Modules/ServiceData/FE14TerrainColors.json", "r", encoding="utf-8") as f:
        js = json.load(f)
        for elem in js:
            result[elem] = js[elem]
    return result


TILE_TO_COLOR_STRING = _load_terrain_colors()


class FE14MapGrid(QScrollArea):
    focused_spawn_changed = Signal(dict)
    spawn_location_changed = Signal(list, list)
    coordinate_type_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.selected_spawn = None
        self.chapter_data = None
        self.selected_tile = None
        self.terrain_mode = False
        self.coordinate_key = "Coordinate (1)"
        cells_widget, self.cells = self._create_cells()
        self.setWidget(cells_widget)

    def _create_cells(self) -> Tuple[QWidget, List[List[FE14MapCell]]]:
        widget = QWidget(parent=self)
        layout = QGridLayout()
        cells = []
        for r in range(0, 32):
            row = []
            for c in range(0, 32):
                cell = self._create_cell(r, c)
                layout.addWidget(cell, r, c)
                row.append(cell)
            cells.append(row)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        widget.setLayout(layout)
        return widget, cells

    def _create_cell(self, r, c):
        cell = FE14MapCell(r, c)
        cell.spawn_selected.connect(self._on_cell_selected)
        cell.spawn_dragged_over.connect(self.move_for_drag)
        cell.tile_selected.connect(self._on_tile_selected)
        return cell

    def set_chapter_data(self, chapter_data):
        self.clear()
        if chapter_data:
            self._update_cell_data(chapter_data)
            if chapter_data.dispos:
                self._place_spawns(chapter_data.dispos)
        self.chapter_data = chapter_data

    def _refresh_dispos(self):
        dispos = self.chapter_data.dispos
        self.clear()
        self._place_spawns(dispos)

    def clear(self):
        self.selected_spawn = None
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

    def _update_cell_data(self, chapter_data):
        new_terrain = chapter_data.terrain if chapter_data else None
        for row in range(0, 32):
            for col in range(0, 32):
                self.cells[row][col].update_chapter_data(chapter_data)
                if new_terrain:
                    tile_id = new_terrain.grid[row][col]
                    tile = new_terrain.tiles[tile_id]
                    self._update_cell_terrain(row, col, tile)
                else:
                    self.cells[row][col].set_color("#424242")
                    self.cells[row][col].setToolTip("")

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
        self.clear_selection()
        self.selected_spawn = selected_cell.spawns[-1]
        self.focused_spawn_changed.emit(self.selected_spawn)
        selected_cell.set_selected(True)

    def clear_selection(self):
        cell = self._spawn_to_cell(self.selected_spawn)
        if cell:
            cell.set_selected(False)
        self.selected_spawn = None

    def _spawn_to_cell(self, spawn):
        if spawn:
            coordinate = spawn[self.coordinate_key].value
            if coordinate[0] in range(0, 32) and coordinate[1] in range(0, 32):
                return self.cells[coordinate[1]][coordinate[0]]
        return None

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
        (start_row, start_col) = self._get_bounded_position_on_grid(self.selected_spawn)
        new_row = start_row + delta_row
        new_col = start_col + delta_col
        if new_row not in range(0, 32) or new_col not in range(0, 32):
            return False
        return True

    def _clear_selected_cells(self):
        cell = self._spawn_to_cell(self.selected_spawn)
        if cell:
            cell.set_selected(False)

    def _perform_move(self, delta_row, delta_col):
        self._clear_selected_cells()
        (start_row, start_col) = self._get_bounded_position_on_grid(self.selected_spawn)
        new_row = start_row + delta_row
        new_col = start_col + delta_col
        self._move_spawn(self.selected_spawn, new_row, new_col)

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

    def delete_spawn(self, spawn):
        cell = self._spawn_to_cell(spawn)
        if cell:
            cell.remove_spawn(spawn)
        self.clear_selection()

    def delete_selected_spawn(self):
        cell = self._spawn_to_cell(self.selected_spawn)
        if cell:
            cell.remove_spawn(self.selected_spawn)
        self.clear_selection()

    def transition_to_terrain_mode(self):
        self.terrain_mode = True
        self.selected_spawn = None
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
        self.selected_spawn = None
        self._refresh_dispos()
        self.coordinate_type_changed.emit()

    def _on_tile_selected(self, cell):
        if self.selected_tile:
            tile_id = self.selected_tile["ID"].value
            self.chapter_data.terrain.grid[cell.row][cell.column] = tile_id
            self._update_cell_terrain(cell.row, cell.column, self.selected_tile)

    def select_spawn(self, spawn):
        self.clear_selection()
        self.selected_spawn = spawn
        self.focused_spawn_changed.emit(self.selected_spawn)
        cell = self._spawn_to_cell(spawn)
        if cell:
            cell.set_selected(True)

    def add_spawn_to_map(self, spawn):
        cell = self._spawn_to_cell(spawn)
        if cell:
            cell.place_spawn(spawn)

    def update_team_for_focused_spawn(self):
        cell = self._spawn_to_cell(self.selected_spawn)
        if cell:
            top = cell.pop_spawn()
            cell.place_spawn(top)

    def update_focused_spawn_position(self, new_position, coordinate_key):
        if not self.selected_spawn:
            return
        spawn = self.selected_spawn
        coordinate = spawn[coordinate_key].value
        if self.coordinate_key == coordinate_key:
            old_cell = self._spawn_to_cell(spawn)
            if old_cell:
                self._remove_spawn_from_cell_and_clear_selection(spawn, old_cell)
        old_coordinate = [coordinate[0], coordinate[1]]
        coordinate[0] = new_position[0]
        coordinate[1] = new_position[1]
        if self.coordinate_key == coordinate_key:
            new_cell = self._spawn_to_cell(spawn)
            if new_cell:
                new_cell.place_spawn(spawn)
                new_cell.set_selected(True)
            self.spawn_location_changed.emit(old_coordinate, coordinate)

    def _remove_spawn_from_cell_and_clear_selection(self, spawn, cell):
        cell.remove_spawn(spawn)
        if self.selected_spawn in cell.spawns:
            return
        cell.set_selected(False)

    def move_for_drag(self, row: int, col: int):
        self.update_focused_spawn_position([col, row], self.coordinate_key)

    def refresh_cell_from_spawn(self, spawn):
        cell = self._spawn_to_cell(spawn)
        if cell:
            top = cell.pop_spawn()
            cell.place_spawn(top)
