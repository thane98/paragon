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
    QTransform
)
from PySide2.QtWidgets import QLabel, QMenu, QAction

from paragon.ui.controllers.sprites import FE13UnitSpriteItem, SpriteItem

DEFAULT_BORDER = "1px dashed black"
SELECTED_BORDER = "2px solid black"


class MapCell(SpriteItem):
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
            self.sprite = self.sprite_svc.from_spawn(self.spawns[-1], self.person_key)
            self.animation_index = 0
            self.frame_index = 0
            self.setPixmap(self.sprite.spritesheet)

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

# Do not inherit the spriteItem as Qt Objects do not support multi-inheritance
# This is the prettiest way without a weird abstraction
class FE13MapCell(MapCell):
    def __init__(self, row, column, sprite):
        super().__init__(row, column, sprite)
        self._setup_menu()

    def mousePressEvent(self, ev: QMouseEvent):
        super().mousePressEvent(ev)
        if ev.button() == QtCore.Qt.LeftButton:
            self._reset_actions()
            self.frame_index = 0
            self.animation_index =  0
        if ev.button() == QtCore.Qt.RightButton:
            self._show_context_menu(ev)

    def _setup_menu(self):
        self._menu = QMenu()
        self._idle_1_action = QAction("Idle 1", self)
        self._idle_2_action = QAction("Idle 2", self)
        self._moving_west_action = QAction("Moving West", self)
        self._moving_east_action = QAction("Moving East", self)
        self._moving_south_action = QAction("Moving South", self)
        self._moving_north_action = QAction("Moving North", self)
        self._moving_southwest_action = QAction("Moving Southwest", self)
        self._moving_southeast_action = QAction("Moving Southeast", self)
        self._moving_northwest_action = QAction("Moving Northwest", self)
        self._moving_northeast_action = QAction("Moving Northeast", self)

        self._idle_1_action.setCheckable(True)
        self._idle_2_action.setCheckable(True)
        self._moving_west_action.setCheckable(True)
        self._moving_east_action.setCheckable(True)
        self._moving_south_action.setCheckable(True)
        self._moving_north_action.setCheckable(True)
        self._moving_southwest_action.setCheckable(True)
        self._moving_southeast_action.setCheckable(True)
        self._moving_northwest_action.setCheckable(True)
        self._moving_northeast_action.setCheckable(True)

        self._idle_1_action.setChecked(True)        
        self._menu.addAction(self._idle_1_action)
        self._menu.addAction(self._idle_2_action)
        self._menu.addAction(self._moving_west_action)
        self._menu.addAction(self._moving_east_action)
        self._menu.addAction(self._moving_south_action)
        self._menu.addAction(self._moving_north_action)
        self._menu.addAction(self._moving_southwest_action)
        self._menu.addAction(self._moving_southeast_action)
        self._menu.addAction(self._moving_northwest_action)
        self._menu.addAction(self._moving_northeast_action)

        self._idle_1_action.triggered.connect(self._on_click_idle_1_action)
        self._idle_2_action.triggered.connect(self._on_click_idle_2_action)
        self._moving_west_action.triggered.connect(self._on_click_moving_west_action)
        self._moving_east_action.triggered.connect(self._on_click_moving_east_action)
        self._moving_south_action.triggered.connect(self._on_click_moving_south_action)
        self._moving_north_action.triggered.connect(self._on_click_moving_north_action)
        self._moving_southwest_action.triggered.connect(self._on_click_moving_southwest_action)
        self._moving_southeast_action.triggered.connect(self._on_click_moving_southeast_action)
        self._moving_northwest_action.triggered.connect(self._on_click_moving_northwest_action)
        self._moving_northeast_action.triggered.connect(self._on_click_moving_northeast_action)

    @QtCore.Slot(bool)
    def _on_click_idle_1_action(self, triggered):
        self._uncheck_actions(triggered, self._idle_1_action)
        self._draw_new_animation(0)

    @QtCore.Slot(bool)
    def _on_click_idle_2_action(self, triggered):
        self._uncheck_actions(triggered, self._idle_2_action)
        self._draw_new_animation(1)

    @QtCore.Slot(bool)
    def _on_click_moving_west_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_west_action)
        self._draw_new_animation(2)

    @QtCore.Slot(bool)
    def _on_click_moving_east_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_east_action)
        self._draw_new_animation(3)

    @QtCore.Slot(bool)
    def _on_click_moving_south_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_south_action)
        self._draw_new_animation(4)

    @QtCore.Slot(bool)
    def _on_click_moving_north_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_north_action)
        self._draw_new_animation(5)

    @QtCore.Slot(bool)
    def _on_click_moving_southwest_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_southwest_action)
        self._draw_new_animation(6)

    @QtCore.Slot(bool)
    def _on_click_moving_southeast_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_southeast_action)
        self._draw_new_animation(7)

    @QtCore.Slot(bool)
    def _on_click_moving_northwest_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_northwest_action)
        self._draw_new_animation(8)

    @QtCore.Slot(bool)
    def _on_click_moving_northeast_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_northeast_action)
        self._draw_new_animation(9)

    def _show_context_menu(self, e: QMouseEvent):
        self._menu.exec_(QCursor().pos())

    def _uncheck_actions(self, triggered: bool, action_item: QAction):
        for action in self._menu.actions():
            action: QAction
            if triggered == True:
                if action.text() != action_item.text() and action.isChecked():
                    action.setChecked(False)
            elif triggered == False:
                if action.text() == action_item.text():
                    action.setChecked(True)
    
    def _reset_actions(self):
        for action in self._menu.actions():
            action: QAction
            if action == self._idle_1_action:
                action.setChecked(True)
            else:
                action.setChecked(False)

    def _draw_new_animation(self, animation_index):
        self.frame_index = 0
        self.animation_index = animation_index

    def paintEvent(self, event):
        if self.sprite and self.sprite.animation_data:
            painter = QPainter(self)
            painter.scale(self.zoom, self.zoom)
            if self.sprite.team == "赤" and self.animation_index in [0, 1]:
                painter.setTransform(QTransform().scale(-1, 1))        
                draw_pos_x = int((-self.width()/self.zoom - self.sprite.frame_height)/2)
            else:
                draw_pos_x = int((self.width()/self.zoom - self.sprite.frame_width)/2)

            painter.drawPixmap(
                draw_pos_x,
                int((self.height()/self.zoom - self.sprite.frame_height)/2),
                self.pixmap(), 
                self._current_frame.x(),
                self._current_frame.y(), 
                self.sprite.frame_width, 
                self.sprite.frame_height
            )
            painter.end()
        elif self.sprite and self.sprite.frame_height and self.sprite.frame_width:
            painter = QPainter(self)
            painter.scale(self.zoom, self.zoom)
            painter.drawPixmap(
                int((self.height()/self.zoom - self.sprite.frame_width)/2),
                int((self.height()/self.zoom - self.sprite.frame_height)/2),
                self.pixmap(), 
                self._current_frame.x(),
                self._current_frame.y(), 
                self.sprite.frame_width, 
                self.sprite.frame_height
            )
            painter.end()
        else:
            painter = QPainter(self)
            painter.scale(self.zoom, self.zoom)
            painter.drawPixmap(
                int((self.width()/self.zoom - 32)/2),
                int((self.height()/self.zoom - 32)/2),
                self.pixmap(), 
                self._current_frame.x(),
                self._current_frame.y(), 
                32, 
                32
            )
            painter.end()

    def next_frame(self):
        if self.frame_index < len(self.sprite.animation_data[self.animation_index].frame_data) - 1:
            self.frame_index += 1
        else:
            self.frame_index = 0

        self._current_frame.setX(
            self.sprite.animation_data[self.animation_index].frame_data[self.frame_index].frame_index_x * self.sprite.frame_width
        )
        self._current_frame.setY(
            self.sprite.animation_data[self.animation_index].frame_data[self.frame_index].frame_index_y * self.sprite.frame_height
        )

        # Redraw new frame
        self.update(
            0,
            0,
            self.width(), 
            self.height()
        )