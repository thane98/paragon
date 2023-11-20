from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtCore import Signal, QMimeData, QEvent, Qt
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import (
    QMouseEvent,
    QDrag,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QPainter,
)
from paragon.ui.controllers.fe15_unit_sprite_item import FE15UnitSpriteItem

from paragon.ui.controllers.fe13_unit_sprite_item import FE13UnitSpriteItem
from paragon.ui.controllers.fe14_unit_sprite_item import FE14UnitSpriteItem

DEFAULT_BORDER = "1px dashed black"
SELECTED_BORDER = "2px solid black"


# This should be subclassed by a class that inherits SpriteItem
# The reason for this weird design choice is b/c Qt Objects do not
# Support the inheritance of two Qt Objects at the same time
class MapCell:
    selected = Signal(object)
    hovered = Signal(object)
    dragged = Signal(object)

    def __init__(self, row, column, sprite_svc, sprite_animation_svc):
        super().__init__(sprite_svc, sprite_animation_svc)
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
        self.zoom = zoom if zoom != 0 else 1
        if zoom == 0:
            self.setFixedSize(32, 32)
        else:
            self.setFixedSize(self.zoom * 40, self.zoom * 40)
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
            DEFAULT_BORDER if self.terrain_mode else SELECTED_BORDER,
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
            self.set_sprite(
                self.sprite_svc.from_spawn(self.spawns[-1], self.person_key)
            )

    def enterEvent(self, event: QEvent) -> None:
        super().enterEvent(event)
        self.hovered.emit(self)

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime = event.mimeData()
        if mime.hasFormat("application/paragon-spawn") or mime.hasFormat(
            "application/paragon-tile"
        ):
            self.dragged.emit(self)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        mime = event.mimeData()
        if mime.hasFormat("application/paragon-spawn") or mime.hasFormat(
            "application/paragon-tile"
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        mime = event.mimeData()
        if mime.hasFormat("application/paragon-spawn") or mime.hasFormat(
            "application/paragon-tile"
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
        elif self.terrain_mode:
            mime_data = QMimeData()
            mime_data.setData("application/paragon-tile", b"")
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(ev.pos())
            drag.exec_(QtCore.Qt.ActionMask)

    def toggle_mode(self):
        self.terrain_mode = not self.terrain_mode
        if self.terrain_mode:
            self.set_border(DEFAULT_BORDER)


class FE13MapCell(MapCell, FE13UnitSpriteItem):
    def __init__(self, editor, row, column, sprite_svc, sprite_animation_svc):
        super().__init__(row, column, sprite_svc, sprite_animation_svc)
        self._menu = QMenu()
        animations_menu = self._menu.addMenu("Animations")
        animations_menu.addAction(self._idle_action)
        animations_menu.addAction(self._idle_hover_action)
        animations_menu.addAction(self._moving_west_action)
        animations_menu.addAction(self._moving_east_action)
        animations_menu.addAction(self._moving_south_action)
        animations_menu.addAction(self._moving_north_action)
        animations_menu.addAction(self._moving_southwest_action)
        animations_menu.addAction(self._moving_southeast_action)
        animations_menu.addAction(self._moving_northwest_action)
        animations_menu.addAction(self._moving_northeast_action)
        self._menu.addAction(editor.delete_action)

    def mousePressEvent(self, ev: QMouseEvent):
        super().mousePressEvent(ev)
        if ev.button() == QtCore.Qt.LeftButton:
            self.reset_animation()
        if ev.button() == QtCore.Qt.RightButton:
            self._show_context_menu(ev)

    def paintEvent(self, event):
        painter = QPainter(self)
        if (
            self.sprite
            and self.sprite.frame_height
            and self.sprite.frame_width
            and self.sprite.animation_data
        ):
            if self.sprite.is_enemy() and self.animation_index in [0, 1]:
                painter.scale(-self.zoom, self.zoom)
                draw_pos_x = int(
                    (-self.width() / self.zoom - self.sprite.frame_width) / 2
                )
            else:
                painter.scale(self.zoom, self.zoom)
                draw_pos_x = int(
                    (self.height() / self.zoom - self.sprite.frame_width) / 2
                )
            draw_pos_y = int((self.width() / self.zoom - self.sprite.frame_height) / 2)
            frame_width = self.sprite.frame_width
            frame_height = self.sprite.frame_height
        elif self.sprite and self.sprite.frame_height and self.sprite.frame_width:
            painter.scale(self.zoom, self.zoom)
            draw_pos_x = (
                int((self.height() / self.zoom - self.sprite.frame_width) / 2),
            )
            draw_pos_y = (
                int((self.height() / self.zoom - self.sprite.frame_height) / 2),
            )
            frame_width = self.sprite.frame_width
            frame_height = self.sprite.frame_height
        else:
            painter.scale(self.zoom, self.zoom)
            draw_pos_x = int((self.width() / self.zoom - 32) / 2)
            draw_pos_y = int((self.height() / self.zoom - 32) / 2)
            frame_width = 32
            frame_height = 32

        painter.drawPixmap(
            draw_pos_x,
            draw_pos_y,
            self.pixmap(),
            self.current_frame.x(),
            self.current_frame.y(),
            frame_width,
            frame_height,
        )
        painter.end()


class FE14MapCell(MapCell, FE14UnitSpriteItem):
    def __init__(self, editor, row, column, sprite_svc, sprite_animation_svc):
        super().__init__(row, column, sprite_svc, sprite_animation_svc)
        self._menu = QMenu()
        animations_menu = self._menu.addMenu("Animations")
        animations_menu.addAction(self._idle_action)
        animations_menu.addAction(self._moving_west_action)
        animations_menu.addAction(self._moving_east_action)
        animations_menu.addAction(self._moving_south_action)
        animations_menu.addAction(self._moving_north_action)
        animations_menu.addAction(self._moving_southwest_action)
        animations_menu.addAction(self._moving_southeast_action)
        animations_menu.addAction(self._moving_northwest_action)
        animations_menu.addAction(self._moving_northeast_action)
        self._menu.addAction(editor.delete_action)

        self.new_animation.connect(self.draw_new_animation)
        self.reset_animation_to_idle.connect(self.idle_animation)

    def mousePressEvent(self, ev: QMouseEvent):
        super().mousePressEvent(ev)
        if ev.button() == QtCore.Qt.LeftButton:
            self.reset_animation()
        if ev.button() == QtCore.Qt.RightButton:
            self._show_context_menu(ev)

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.sprite and self.sprite.animation_data:
            frame_width = (
                self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_width
            )
            frame_height = (
                self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_height
            )
            draw_pos_y = (
                int((self.height() / self.zoom - frame_height) / 2)
                + self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_offset_y
            )

            if self.sprite.is_enemy() and self.animation_index == 0:
                painter.scale(-self.zoom, self.zoom)
                draw_pos_x = (
                    int((-self.width() / self.zoom - frame_width) / 2)
                    - self.sprite.animation_data[self.animation_index]
                    .frame_data[self.frame_index]
                    .body_offset_x
                )
            else:
                painter.scale(self.zoom, self.zoom)
                draw_pos_x = (
                    int((self.width() / self.zoom - frame_width) / 2)
                    + self.sprite.animation_data[self.animation_index]
                    .frame_data[self.frame_index]
                    .body_offset_x
                )
        else:
            painter.scale(self.zoom, self.zoom)
            draw_pos_x = int((self.width() / self.zoom - 32) / 2)
            draw_pos_y = int((self.height() / self.zoom - 32) / 2)
            frame_width = 32
            frame_height = 32

        painter.drawPixmap(
            draw_pos_x,
            draw_pos_y,
            self.pixmap(),
            self.current_frame.x(),
            self.current_frame.y(),
            frame_width,
            frame_height,
        )
        painter.end()

    def idle_animation(self):
        if self.spawns:
            self.sprite = self.sprite_svc.from_spawn(
                self.spawns[-1], self.person_key, animation=0
            )
            self.setPixmap(self.sprite.spritesheet) if self.sprite else self.setPixmap(
                None
            )
            self.animation_index = 0
            self.frame_index = 0
            self.current_frame.setX(0)
            self.current_frame.setY(0)
            self._reset_actions()

    def draw_new_animation(self, animation_index):
        self.sprite = self.sprite_svc.from_spawn(
            self.spawns[-1], self.person_key, animation=animation_index
        )
        self.setPixmap(self.sprite.spritesheet) if self.sprite else self.setPixmap(None)
        self.current_frame.setX(0)
        self.current_frame.setY(0)
        self.frame_index = 0
        self.animation_index = animation_index
        self.next_frame()


class FE15MapCell(MapCell, FE15UnitSpriteItem):
    def __init__(self, editor, row, column, sprite_svc, sprite_animation_svc):
        super().__init__(row, column, sprite_svc, sprite_animation_svc)
        self._menu = QMenu()
        animations_menu = self._menu.addMenu("Animations")
        animations_menu.addAction(self._idle_action)
        animations_menu.addAction(self._moving_west_action)
        animations_menu.addAction(self._moving_east_action)
        animations_menu.addAction(self._moving_south_action)
        animations_menu.addAction(self._moving_north_action)
        self._menu.addAction(editor.delete_action)

        self.new_animation.connect(self.draw_new_animation)
        self.reset_animation_to_idle.connect(self.idle_animation)

    def mousePressEvent(self, ev: QMouseEvent):
        super().mousePressEvent(ev)
        if ev.button() == QtCore.Qt.LeftButton:
            self.reset_animation()
        if ev.button() == QtCore.Qt.RightButton:
            self._show_context_menu(ev)

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.sprite and self.sprite.animation_data:
            frame_width = (
                self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_width
            )
            frame_height = (
                self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_height
            )
            draw_pos_y = (
                int((self.height() / self.zoom - frame_height) / 2)
                + self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_offset_y
            )

            if self.sprite.is_enemy() and self.animation_index == 0:
                painter.scale(-self.zoom, self.zoom)
                draw_pos_x = (
                    int((-self.width() / self.zoom - frame_width) / 2)
                    - self.sprite.animation_data[self.animation_index]
                    .frame_data[self.frame_index]
                    .body_offset_x
                )
            else:
                painter.scale(self.zoom, self.zoom)
                draw_pos_x = (
                    int((self.width() / self.zoom - frame_width) / 2)
                    + self.sprite.animation_data[self.animation_index]
                    .frame_data[self.frame_index]
                    .body_offset_x
                )
        else:
            painter.scale(self.zoom, self.zoom)
            draw_pos_x = int((self.width() / self.zoom - 32) / 2)
            draw_pos_y = int((self.height() / self.zoom - 32) / 2)
            frame_width = 32
            frame_height = 32

        painter.drawPixmap(
            draw_pos_x,
            draw_pos_y,
            self.pixmap(),
            self.current_frame.x(),
            self.current_frame.y(),
            frame_width,
            frame_height,
        )
        painter.end()

    def idle_animation(self):
        if self.spawns:
            self.sprite = self.sprite_svc.from_spawn(
                self.spawns[-1], self.person_key, animation=0
            )
            self.setPixmap(self.sprite.spritesheet) if self.sprite else self.setPixmap(
                None
            )
            self.animation_index = 0
            self.frame_index = 0
            self.current_frame.setX(0)
            self.current_frame.setY(0)
            self._reset_actions()

    def draw_new_animation(self, animation_index):
        self.sprite = self.sprite_svc.from_spawn(
            self.spawns[-1], self.person_key, animation=animation_index
        )
        self.setPixmap(self.sprite.spritesheet) if self.sprite else self.setPixmap(None)
        self.current_frame.setX(0)
        self.current_frame.setY(0)
        self.frame_index = 0
        self.animation_index = animation_index
        self.next_frame()
