from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import Signal, QMimeData, QEvent
from PySide2.QtGui import (
    QMouseEvent,
    QDrag,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
)
from PySide2.QtWidgets import QLabel

DEFAULT_BORDER = "1px dashed black"
SELECTED_BORDER = "2px solid black"


class MapCell(QLabel):
    selected = Signal(object)
    hovered = Signal(object)
    dragged = Signal(object)

    def __init__(self, row, column, sprites):
        super().__init__()
        self.setAlignment(QtGui.Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.person_key = None
        self.sprites = sprites
        self.row = row
        self.column = column
        self.spawns = []
        self.terrain_mode = False
        self._current_color = "#424242"
        self._current_border = DEFAULT_BORDER
        self.zoom = 1
        self.set_zoom(self.zoom)

    def top_spawn(self):
        if self.spawns:
            return self.spawns[-1]
        else:
            return None

    def set_zoom(self, zoom):
        self.zoom = zoom
        self.setFixedSize(zoom * 32, zoom * 32)
        self._set_occupation_from_last_spawn()
        self._refresh_stylesheet()

    def set_color(self, color_style_string):
        self._current_color = color_style_string
        self._refresh_stylesheet()

    def set_border(self, border):
        self._current_border = border
        self._refresh_stylesheet()

    def _refresh_stylesheet(self):
        params = (
            self._current_border,
            self._current_color,
            SELECTED_BORDER,
            self._current_color,
        )
        self.setStyleSheet(
            (
                "QLabel { border: %s; background-color: %s } "
                + "QLabel:hover { border: %s; background-color: %s }"
            )
            % params
        )

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

    def move_spawn_to_top(self, spawn):
        if spawn in self.spawns:
            self.remove_spawn(spawn)
            self.place_spawn(spawn)

    def clear_spawns(self):
        self.spawns.clear()
        self.clear()
        self.set_border(DEFAULT_BORDER)

    def set_selected(self, is_selected):
        self.set_border(SELECTED_BORDER if is_selected else DEFAULT_BORDER)

    def _set_occupation_from_last_spawn(self):
        if not self.spawns:
            self.clear()
        else:
            dim = self.zoom * 32
            pixmap = self.sprites.from_spawn(self.spawns[-1], self.person_key).scaled(
                dim, dim
            )
            self.setPixmap(pixmap)

    def enterEvent(self, event: QEvent) -> None:
        self.hovered.emit(self)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if not self.terrain_mode and event.mimeData().hasFormat(
            "application/paragon-spawn"
        ):
            self.dragged.emit(self)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if not self.terrain_mode and event.mimeData().hasFormat(
            "application/paragon-spawn"
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if not self.terrain_mode and event.mimeData().hasFormat(
            "application/paragon-spawn"
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def mousePressEvent(self, ev: QMouseEvent):
        self.selected.emit(self)
        if (
            not self.terrain_mode
            and ev.button() == QtCore.Qt.LeftButton
            and self.spawns
        ):
            mime_data = QMimeData()
            mime_data.setData("application/paragon-spawn", b"")
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(ev.pos())
            drag.exec_(QtCore.Qt.MoveAction)

    def toggle_mode(self):
        self.terrain_mode = not self.terrain_mode
        if self.terrain_mode:
            self.set_border(DEFAULT_BORDER)
