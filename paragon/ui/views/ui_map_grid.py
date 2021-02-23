from PySide2.QtWidgets import QScrollArea, QWidget, QGridLayout

from paragon.ui.controllers.map_cell import FE13MapCell
from paragon.ui.controllers.sprites import SpriteItemHandler
from paragon.model.game import Game

class Ui_MapGrid(QScrollArea):
    def __init__(self, sprites, game):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)

        widget = QWidget(parent=self)
        layout = QGridLayout()
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        widget.setLayout(layout)
        self.cells = []
        self.sprite_handler = SpriteItemHandler(self)

        for r in range(0, 32):
            row = []
            for c in range(0, 32):
                # Check on this later
                # This is a test
                if game == Game.FE13:
                    cell = FE13MapCell(r, c, sprites)
                    self.sprite_handler.add_sprite(cell)
                cell.selected.connect(self._on_cell_selected)
                cell.dragged.connect(self._on_cell_dragged)
                cell.hovered.connect(self._on_cell_hovered)
                layout.addWidget(cell, r, c)
                row.append(cell)
            self.cells.append(row)
        self.setWidget(widget)

    def _on_cell_selected(self, cell):
        raise NotImplementedError

    def _on_cell_dragged(self, cell):
        raise NotImplementedError

    def _on_cell_hovered(self, cell):
        raise NotImplementedError
