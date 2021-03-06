from PySide2 import QtCore
from PySide2.QtCore import QItemSelectionModel, Signal

from paragon.ui.views.ui_map_grid import Ui_MapGrid


def coord_in_bounds(coord):
    return coord[0] in range(0, 32) and coord[1] in range(0, 32)


class MapGrid(Ui_MapGrid):
    tile_clicked = Signal(int, int)
    hovered = Signal(int, int)
    dragged = Signal(int, int)

    def __init__(
        self, chapters, sprites, sprite_animation_svc, mode_fn, coord_fn, game
    ):
        super().__init__(sprites, sprite_animation_svc, game)

        self.chapters = chapters
        self.dispos_model = None
        self.person_key = None
        self.selection_model = None
        self.is_terrain_mode = mode_fn
        self.is_coord_2 = coord_fn

    def move_spawn(self, spawn, row, col):
        if cell := self._spawn_to_cell(spawn):
            cell.remove_spawn(spawn)
            cell.set_selected(False)
        self.cells[row][col].place_spawn(spawn)
        self.cells[row][col].set_selected(True)

    def set_tile_color(self, row, col, color):
        self.cells[row][col].set_color(color)

    def clear(self):
        self._for_each_cell(lambda cell: cell.clear_spawns())

    def refresh(self):
        self.set_dispos(self.dispos_model, self.person_key)

    def toggle_mode(self):
        self._for_each_cell(lambda c: c.toggle_mode())

    def set_dispos(self, dispos_model, person_key):
        self.person_key = person_key
        self._for_each_cell(lambda c, k=person_key: self._update_cell_for_dispos(c, k))
        self.dispos_model = dispos_model
        if dispos_model:
            for spawn in dispos_model.enumerate_spawns():
                self.place_spawn(spawn)

    @staticmethod
    def _update_cell_for_dispos(c, person_key):
        c.clear_spawns()
        c.person_key = person_key

    def set_zoom(self, zoom):
        self._for_each_cell(lambda c: c.set_zoom(zoom))
        self.widget().resize(zoom * 32 * 40, zoom * 32 * 40)

    def set_tile_colors(self, colors):
        if not colors:
            self._for_each_cell(lambda c: c.set_color("#424242"))
        else:
            self._for_each_cell(lambda c: c.set_color(colors[c.row][c.column]))

    def set_selection_model(self, selection_model: QItemSelectionModel):
        self.selection_model = selection_model
        selection_model.currentChanged.connect(self._on_selection)

    def place_spawn(self, spawn):
        if cell := self._spawn_to_cell(spawn):
            cell.place_spawn(spawn)

    def spawn_at(self, row, col):
        if not coord_in_bounds([row, col]):
            return None
        else:
            return self.cells[row][col].top_spawn()

    def _spawn_to_cell(self, spawn):
        if spawn:
            coord = self.chapters.coord(spawn, self.is_coord_2())
            if coord_in_bounds(coord):
                return self.cells[coord[1]][coord[0]]
        return None

    def _on_cell_selected(self, cell):
        if not self.is_terrain_mode() and cell.spawns:
            index = self.dispos_model.spawn_to_index(cell.spawns[-1])
            self.selection_model.setCurrentIndex(
                index, QItemSelectionModel.ClearAndSelect
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
        spawn = self.dispos_model.data(current, QtCore.Qt.UserRole)
        previous_spawn = self.dispos_model.data(previous, QtCore.Qt.UserRole)
        if self.chapters.is_spawn(previous_spawn):
            if cell := self._spawn_to_cell(previous_spawn):
                cell.set_selected(False)
        if self.chapters.is_spawn(spawn):
            if cell := self._spawn_to_cell(spawn):
                cell.set_selected(True)
                cell.move_spawn_to_top(spawn)

    def _for_each_cell(self, fn):
        for row in self.cells:
            for cell in row:
                fn(cell)
