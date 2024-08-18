from PySide6 import QtCore
from PySide6.QtWidgets import QScrollArea, QWidget, QGridLayout

from paragon.ui.controllers.gcn_map_cell import GcnMapCell
from paragon.ui.controllers.map_cell import (
    FE13MapCell,
    FE14MapCell,
    FE15MapCell,
)
from paragon.model.game import Game


class Ui_GcnMapGrid(QScrollArea):
    def __init__(self):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)

        self.main_widget = QWidget(parent=self)
        self.grid_layout = QGridLayout()
        self.grid_layout.setVerticalSpacing(0)
        self.grid_layout.setHorizontalSpacing(0)
        self.main_widget.setLayout(self.grid_layout)
        self.cells = []
        self.setWidget(self.main_widget)
