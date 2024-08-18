from typing import Optional

from PySide6 import QtCore
from PySide6.QtCore import QItemSelectionModel, Signal
from PySide6.QtWidgets import QGridLayout, QWidget

from paragon.model.gcn_chapter_data import GcnChapterData
from paragon.ui.controllers.gcn_map_cell import GcnMapCell
from paragon.ui.views.ui_gcn_map_grid import Ui_GcnMapGrid


class GcnMapGrid(Ui_GcnMapGrid):
    tile_clicked = Signal(int, int)
    hovered = Signal(int, int)
    dragged = Signal(int, int)

    def __init__(self, editor, maps, sprites, sprite_animation_svc, mode_fn, coord_fn):
        super().__init__()

        self.editor = editor
        self.sprites = sprites
        self.sprite_animation_svc = sprite_animation_svc

        self.zoom = 1
        self.maps = maps
        self.data: Optional[GcnChapterData] = None
        self.dispos_model = None
        self.selection_model = None
        self.is_terrain_mode = mode_fn
        self.is_coord_2 = coord_fn

    def coord_in_bounds(self, coord):
        if not self.data:
            return False
        else:
            return coord[0] in range(0, self.data.map_data.width) and coord[1] in range(
                0, self.data.map_data.height
            )

    def move_spawn(self, spawn, row, col):
        if cell := self._spawn_to_cell(spawn):
            cell.remove_spawn(spawn)
            cell.set_selected(False)
        if self.coord_in_bounds([row, col]):
            self.cells[row][col].place_spawn(spawn)
            self.cells[row][col].set_selected(True)

    def set_tile_color(self, row, col, color):
        self.cells[row][col].set_color(color)

    def clear(self):
        self._for_each_cell(lambda cell: cell.clear_spawns())

    def refresh(self):
        self.set_dispos(self.dispos_model)

    def toggle_mode(self):
        self._for_each_cell(lambda c: c.toggle_mode())

    def set_target(self, data: Optional[GcnChapterData], dispos_model):
        self.set_terrain(data)
        self.set_dispos(dispos_model)

    def set_terrain(self, data: GcnChapterData):
        QWidget().setLayout(self.grid_layout)
        self.data = data

        layout = QGridLayout()
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        self.cells = []
        for r in range(0, data.map_data.height):
            row = []
            for c in range(0, data.map_data.width):
                cell = GcnMapCell(r, c, self.sprites)
                cell.selected.connect(
                    self._on_cell_selected, QtCore.Qt.ConnectionType.UniqueConnection
                )
                cell.dragged.connect(
                    self._on_cell_dragged, QtCore.Qt.ConnectionType.UniqueConnection
                )
                cell.hovered.connect(
                    self._on_cell_hovered, QtCore.Qt.ConnectionType.UniqueConnection
                )
                layout.addWidget(cell, r, c)
                row.append(cell)
            self.cells.append(row)
        self.grid_layout = layout
        self.main_widget.setLayout(layout)
        self.set_zoom(self.zoom)

    def set_dispos(self, dispos_model):
        self._for_each_cell(lambda c: self._update_cell_for_dispos(c))
        self.dispos_model = dispos_model
        if dispos_model:
            for spawn in dispos_model.enumerate_spawns():
                self.place_spawn(spawn)

    @staticmethod
    def _update_cell_for_dispos(c):
        c.clear_spawns()

    def set_zoom(self, zoom):
        self.zoom = zoom if zoom != 0 else 1
        self._for_each_cell(lambda c: c.set_zoom(zoom))
        width = self.data.map_data.width if self.data else 32
        height = self.data.map_data.height if self.data else 32
        self.widget().resize(self.zoom * width * 32, self.zoom * height * 32)

    def set_tile_colors(self, colors):
        if not colors:
            self._for_each_cell(lambda c: c.set_color("#424242"))
        else:
            self._for_each_cell(lambda c: c.set_color(colors[c.row][c.column]))

    def set_selection_model(self, selection_model: QItemSelectionModel):
        self.selection_model = selection_model
        selection_model.currentChanged.connect(
            self._on_selection, QtCore.Qt.ConnectionType.UniqueConnection
        )

    def place_spawn(self, spawn):
        if cell := self._spawn_to_cell(spawn):
            cell.place_spawn(spawn)

    def spawn_at(self, row, col):
        if not self.coord_in_bounds([row, col]):
            return None
        else:
            return self.cells[row][col].top_spawn()

    def update_spawn(self, spawn):
        cell = self._spawn_to_cell(spawn)
        if cell:
            cell.move_spawn_to_top(spawn)

    def _spawn_to_cell(self, spawn):
        if spawn:
            coord = self.maps.coord(spawn, self.is_coord_2())
            if self.coord_in_bounds(coord):
                return self.cells[coord[1]][coord[0]]
        return None

    def _on_cell_selected(self, cell):
        if not self.is_terrain_mode() and cell.spawns:
            index = self.dispos_model.spawn_to_index(cell.spawns[-1])
            self.selection_model.setCurrentIndex(
                index, QItemSelectionModel.SelectionFlag.ClearAndSelect
            )
        elif self.is_terrain_mode():
            self.tile_clicked.emit(cell.row, cell.column)

    def _on_cell_dragged(self, cell):
        self.dragged.emit(cell.row, cell.column)

    def _on_cell_hovered(self, cell):
        self.hovered.emit(cell.row, cell.column)

    def _on_selection(self, current, previous):
        if not self.is_terrain_mode():
            self._highlight_selection(current, previous)

    def _highlight_selection(self, current, previous):
        spawn = self.dispos_model.data(current, QtCore.Qt.ItemDataRole.UserRole)
        previous_spawn = self.dispos_model.data(
            previous, QtCore.Qt.ItemDataRole.UserRole
        )
        if self.maps.is_spawn(previous_spawn):
            if cell := self._spawn_to_cell(previous_spawn):
                cell.set_selected(False)
        if self.maps.is_spawn(spawn):
            if cell := self._spawn_to_cell(spawn):
                cell.set_selected(True)
                cell.move_spawn_to_top(spawn)

    def _for_each_cell(self, fn):
        for row in self.cells:
            for cell in row:
                fn(cell)
