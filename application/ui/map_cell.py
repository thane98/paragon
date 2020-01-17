from enum import Enum

from PySide2 import QtGui, QtCore
from PySide2.QtCore import Signal
from PySide2.QtGui import QPixmap, QMouseEvent
from PySide2.QtWidgets import QLabel


class MapCellOccupationState(Enum):
    SELECTED = 0
    UNOCCUPIED = 1
    PLAYER = 2
    ENEMY = 3
    ALLIED = 4


_OCCUPATION_PIXMAPS = {
    MapCellOccupationState.SELECTED: "selected.png",
    MapCellOccupationState.UNOCCUPIED: None,
    MapCellOccupationState.PLAYER: "player.png",
    MapCellOccupationState.ENEMY: "enemy.png",
    MapCellOccupationState.ALLIED: "allied.png"
}


class MapCell(QLabel):
    selected = Signal(dict)
    selection_expanded = Signal(dict)

    def __init__(self, row, column):
        super().__init__()
        self.setStyleSheet("border: 1px dashed black")
        self.setAlignment(QtGui.Qt.AlignCenter)
        self.row = row
        self.column = column
        self.spawns = []

    def set_color(self, color_style_string):
        new_style = "QLabel { border: 1px dashed black; background-color: %s }" % color_style_string
        self.setStyleSheet(new_style)

    def place_spawn(self, spawn):
        self.spawns.append(spawn)
        self._set_occupation_from_last_spawn()

    def remove_spawn(self, spawn):
        self.spawns.remove(spawn)
        if not self.spawns:
            self.clear()
        else:
            self._set_occupation_from_last_spawn()

    def clear_spawns(self):
        self.spawns.clear()
        self.clear()

    def _set_occupation_from_last_spawn(self):
        if not self.spawns:
            raise IndexError
        last_spawn = self.spawns[-1]
        team = last_spawn["Team"].value
        if team == 0:
            occupation_state = MapCellOccupationState.PLAYER
        elif team == 1:
            occupation_state = MapCellOccupationState.ENEMY
        else:
            occupation_state = MapCellOccupationState.ALLIED
        self.setPixmap(QPixmap(_OCCUPATION_PIXMAPS[occupation_state]))

    def mousePressEvent(self, ev: QMouseEvent):
        if ev.button() != QtCore.Qt.LeftButton or not self.spawns:
            return
        if ev.modifiers() & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
            self.selection_expanded.emit(self.spawns[-1])
        else:
            self.selected.emit(self.spawns[-1])
