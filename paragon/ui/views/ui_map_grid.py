from PySide6 import QtCore
from PySide6.QtWidgets import QScrollArea, QWidget, QGridLayout

from paragon.ui.controllers.map_cell import FE13MapCell, FE14MapCell, FE15MapCell
from paragon.model.game import Game


class Ui_MapGrid(QScrollArea):
    def __init__(self, editor, sprites, sprite_animation_svc, game):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)

        widget = QWidget(parent=self)
        layout = QGridLayout()
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        widget.setLayout(layout)
        self.cells = []

        for r in range(0, 32):
            row = []
            for c in range(0, 32):
                cell = (
                    FE13MapCell(editor, r, c, sprites, sprite_animation_svc)
                    if game == Game.FE13
                    else FE14MapCell(editor, r, c, sprites, sprite_animation_svc)
                    if game == Game.FE14
                    else FE15MapCell(editor, r, c, sprites, sprite_animation_svc)
                    if game == Game.FE15
                    else None
                )
                cell.selected.connect(
                    self._on_cell_selected, QtCore.Qt.UniqueConnection
                )
                cell.dragged.connect(self._on_cell_dragged, QtCore.Qt.UniqueConnection)
                cell.hovered.connect(self._on_cell_hovered, QtCore.Qt.UniqueConnection)
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
