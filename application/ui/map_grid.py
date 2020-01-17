from PySide2.QtWidgets import QWidget, QGridLayout

from ui.map_cell import MapCell

TILE_TO_COLOR_STRING = {
    "TID_平地": "#8BC34A",
    "TID_橋": "#795548",
    "TID_河／平地": "#1565C0",
    "TID_無し": "#424242",
    "TID_林": "#1B5E20"
}


class MapGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.cells = []
        self.selected_cells = []
        layout = QGridLayout()
        for r in range(0, 32):
            row = []
            for c in range(0, 32):
                cell = MapCell(r, c)
                layout.addWidget(cell, r, c)
                row.append(cell)
            self.cells.append(row)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        self.setLayout(layout)

    def set_chapter_data(self, chapter_data):
        self.clear()
        if chapter_data:
            self._place_spawns(chapter_data.dispos)
            self._update_terrain(chapter_data.terrain)

    def clear(self):
        for r in range(0, 32):
            for c in range(0, 32):
                cell = self.cells[r][c]
                cell.clear_spawns()

    def _place_spawns(self, dispos):
        for faction in dispos.factions:
            for spawn in faction.spawns:
                coordinate = spawn["Coordinate (1)"].value
                target_cell = self.cells[coordinate[1]][coordinate[0]]
                target_cell.place_spawn(spawn)

    def _update_terrain(self, new_terrain):
        for row in range(0, 32):
            for col in range(0, 32):
                tile_id = new_terrain.grid[row][col]
                tile = new_terrain.tiles[tile_id]
                self._update_cell_terrain(row, col, tile)

    def _update_cell_terrain(self, row, col, tile):
        tid = tile["TID"].value
        if tid in TILE_TO_COLOR_STRING:
            color_string = TILE_TO_COLOR_STRING[tid]
        else:
            color_string = "#424242"
        target_cell = self.cells[row][col]
        target_cell.set_color(color_string)

    def _on_cell_selected(self, spawn):
        pass

    def _on_cell_selection_expanded(self, spawn):
        pass
