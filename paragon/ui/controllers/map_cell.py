from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import Signal, QMimeData, QEvent, Qt
from PySide2.QtGui import (
    QMouseEvent,
    QDrag,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QPainter,
    QCursor,
)
from PySide2.QtWidgets import QLabel, QMenu, QAction

from paragon.ui.controllers.sprites import FE13UnitSpriteItem, SpriteItem

DEFAULT_BORDER = "1px dashed black"
SELECTED_BORDER = "2px solid black"

# This should be subclassed by a class that inherits or is a QLabel
# The reason for this weird design choice is b/c Qt Objects do not
# Support the inheritance of two Qt Objects at the same time
class MapCell:
    selected = Signal(object)
    hovered = Signal(object)
    dragged = Signal(object)

    def __init__(self, row, column, sprite_svc):
        super().__init__(sprite_svc)
        self.setAlignment(QtGui.Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.person_key = None
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
        self.setFixedSize(zoom * 40, zoom * 40)
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
            self.set_sprite(self.sprite_svc.from_spawn(self.spawns[-1], self.person_key))

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

class FE13MapCell(MapCell, FE13UnitSpriteItem):
    def __init__(self, row, column, sprite):
        super().__init__(row, column, sprite)

    def mousePressEvent(self, ev: QMouseEvent):
        super().mousePressEvent(ev)
        if ev.button() == QtCore.Qt.LeftButton:
            self.reset_animation()
        if ev.button() == QtCore.Qt.RightButton:
            self._show_context_menu(ev)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.sprite and self.sprite.frame_height and self.sprite.frame_width and self.sprite.animation_data:
            if self.sprite.team == "赤" and self.animation_index in [0, 1]:
                painter.scale(-self.zoom, self.zoom)
                draw_pos_x = int((-self.width()/self.zoom - self.sprite.frame_height)/2)
            else:
                painter.scale(self.zoom, self.zoom)
                draw_pos_x = int((self.height()/self.zoom - self.sprite.frame_width)/2)
            draw_pos_y = int((self.width()/self.zoom - self.sprite.frame_width)/2)
            frame_width = self.sprite.frame_width
            frame_height = self.sprite.frame_height
        elif self.sprite and self.sprite.frame_height and self.sprite.frame_width:
            painter.scale(self.zoom, self.zoom)
            draw_pos_x = int((self.height()/self.zoom - self.sprite.frame_width)/2),
            draw_pos_y = int((self.height()/self.zoom - self.sprite.frame_height)/2),
            frame_width = self.sprite.frame_width
            frame_height = self.sprite.frame_height
        else:
            painter.scale(self.zoom, self.zoom)
            draw_pos_x = int((self.width()/self.zoom - 32)/2)
            draw_pos_y = int((self.height()/self.zoom - 32)/2)
            frame_width = 32
            frame_height = 32

        painter.drawPixmap(
            draw_pos_x,
            draw_pos_y,
            self.pixmap(), 
            self.current_frame.x(),
            self.current_frame.y(), 
            frame_width, 
            frame_height
        )
        painter.end()