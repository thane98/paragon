from enum import Enum

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import Signal, QMimeData
from PySide2.QtGui import QMouseEvent, QPixmap, QDrag, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide2.QtWidgets import QLabel

from services.service_locator import locator


class MapCellOccupationState(Enum):
    UNOCCUPIED = 0
    PLAYER = 1
    ENEMY = 2
    ALLIED = 3


_OCCUPATION_PIXMAPS = {
    MapCellOccupationState.UNOCCUPIED: None,
    MapCellOccupationState.PLAYER: "Assets/player.png",
    MapCellOccupationState.ENEMY: "Assets/enemy.png",
    MapCellOccupationState.ALLIED: "Assets/allied.png"
}

DEFAULT_BORDER = "1px dashed black"
SELECTED_BORDER = "2px solid black"


class FE14MapCell(QLabel):
    selected_for_move = Signal(dict)
    spawn_selected = Signal(dict)
    tile_selected = Signal(dict)
    spawn_dragged_over = Signal(int, int)

    def __init__(self, row, column):
        super().__init__()
        self.setAlignment(QtGui.Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.row = row
        self.column = column
        self.spawns = []
        self.terrain_mode = False
        self._chapter_data = None
        self._current_color = "#424242"
        self._current_border = DEFAULT_BORDER
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setFixedSize(32, 32)
        self._refresh_stylesheet()

    def set_color(self, color_style_string):
        self._current_color = color_style_string
        self._refresh_stylesheet()

    def set_border(self, border):
        self._current_border = border
        self._refresh_stylesheet()

    def _refresh_stylesheet(self):
        params = (self._current_border, self._current_color)
        self.setStyleSheet("QLabel { border: %s; background-color: %s }" % params)

    def place_spawn(self, spawn):
        self.spawns.append(spawn)
        self._set_occupation_from_last_spawn()

    def pop_spawn(self):
        result = self.spawns.pop()
        self._set_occupation_from_last_spawn()
        return result

    def remove_spawn(self, spawn):
        if spawn in self.spawns:
            self.spawns.remove(spawn)
            self._set_occupation_from_last_spawn()

    def clear_spawns(self):
        self.spawns.clear()
        self.clear()
        self.set_border(DEFAULT_BORDER)

    def set_selected(self, is_selected):
        if is_selected:
            self.set_border(SELECTED_BORDER)
        else:
            self.set_border(DEFAULT_BORDER)

    def _set_occupation_from_last_spawn(self):
        if not self.spawns:
            self.clear()
            return
        last_spawn = self.spawns[-1]
        pixmap = self._get_pixmap_from_spawn(last_spawn)
        self.setPixmap(pixmap)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if not self.terrain_mode and event.mimeData().hasFormat("application/fe14-spawn"):
            self.spawn_dragged_over.emit(self.row, self.column)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if not self.terrain_mode and event.mimeData().hasFormat("application/fe14-spawn"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if not self.terrain_mode and event.mimeData().hasFormat("application/fe14-spawn"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def mousePressEvent(self, ev: QMouseEvent):
        if self.terrain_mode:
            self.tile_selected.emit(self)
        else:
            self._handle_mouse_press_event_for_dispos(ev)

    def _handle_mouse_press_event_for_dispos(self, ev: QMouseEvent):
        if ev.button() != QtCore.Qt.LeftButton:
            return
        if self.spawns:
            self.spawn_selected.emit(self)
            mime_data = QMimeData()
            mime_data.setData("application/fe14-spawn", b"")
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(ev.pos())
            drag.exec_(QtCore.Qt.MoveAction)

    def transition_to_terrain_mode(self):
        self.terrain_mode = True
        self.set_border(DEFAULT_BORDER)

    def transition_to_dispos_mode(self):
        self.terrain_mode = False

    def update_chapter_data(self, chapter_data):
        self._chapter_data = chapter_data

    @staticmethod
    def _get_default_pixmap_by_team(team) -> QPixmap:
        if team == 0:
            occupation_state = MapCellOccupationState.PLAYER
        elif team == 1:
            occupation_state = MapCellOccupationState.ENEMY
        else:
            occupation_state = MapCellOccupationState.ALLIED
        return QPixmap(_OCCUPATION_PIXMAPS[occupation_state])

    def _get_pixmap_from_spawn(self, spawn):
        sprite_service = locator.get_scoped("SpriteService")
        pid = spawn["PID"].value
        team = spawn["Team"].value
        sprite = None
        if self._chapter_data and self._chapter_data.person:
            person = self._chapter_data.person
            element = person.get_element_by_key(pid)
            if element:
                sprite = sprite_service.get_sprite_for_character(element, team)
        if not sprite:
            characters = locator.get_scoped("ModuleService").get_module("Characters")
            element = characters.get_element_by_key(pid)
            if element:
                sprite = sprite_service.get_sprite_for_character(element, team)
            if not sprite:
                sprite = self._get_default_pixmap_by_team(team)
        return sprite
