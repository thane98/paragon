from PySide2.QtWidgets import QMenu, QAction
from PySide2 import QtCore
from PySide2.QtGui import QPixmap, QPainter, QMouseEvent, QCursor

from paragon.ui.controllers.sprite_item import SpriteItem


class FE15UnitSpriteItem(SpriteItem):
    def __init__(self, sprite_svc, sprite_animation):
        super().__init__(sprite_svc, sprite_animation)
        self._setup_menu()

    def mousePressEvent(self, ev: QMouseEvent):
        super().mousePressEvent(ev)
        if ev.button() == QtCore.Qt.RightButton:
            self._show_context_menu(ev)
        if ev.button() == QtCore.Qt.LeftButton:
            self.left_clicked.emit()

    def _setup_menu(self):
        self._menu = QMenu()
        self._idle_action = QAction("Idle", self)
        self._moving_west_action = QAction("Moving West", self)
        self._moving_east_action = QAction("Moving East", self)
        self._moving_south_action = QAction("Moving South", self)
        self._moving_north_action = QAction("Moving North", self)

        self._idle_action.setCheckable(True)
        self._moving_west_action.setCheckable(True)
        self._moving_east_action.setCheckable(True)
        self._moving_south_action.setCheckable(True)
        self._moving_north_action.setCheckable(True)

        self._idle_action.setChecked(True)
        self._menu.addAction(self._idle_action)
        self._menu.addAction(self._moving_west_action)
        self._menu.addAction(self._moving_east_action)
        self._menu.addAction(self._moving_south_action)
        self._menu.addAction(self._moving_north_action)

        self._idle_action.triggered.connect(self._on_click_idle_action)
        self._moving_west_action.triggered.connect(self._on_click_moving_west_action)
        self._moving_east_action.triggered.connect(self._on_click_moving_east_action)
        self._moving_south_action.triggered.connect(self._on_click_moving_south_action)
        self._moving_north_action.triggered.connect(self._on_click_moving_north_action)

    @QtCore.Slot(bool)
    def _on_click_idle_action(self, triggered):
        self._uncheck_actions(triggered, self._idle_action)
        self._draw_new_animation(0)

    @QtCore.Slot(bool)
    def _on_click_moving_west_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_west_action)
        self._draw_new_animation(1)

    @QtCore.Slot(bool)
    def _on_click_moving_east_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_east_action)
        self._draw_new_animation(2)

    @QtCore.Slot(bool)
    def _on_click_moving_south_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_south_action)
        self._draw_new_animation(3)

    @QtCore.Slot(bool)
    def _on_click_moving_north_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_north_action)
        self._draw_new_animation(4)

    def _show_context_menu(self, e: QMouseEvent):
        self._menu.exec_(QCursor().pos())

    def _uncheck_actions(self, triggered: bool, action_item: QAction):
        for action in self._menu.actions():
            action: QAction
            if triggered:
                if action.text() != action_item.text() and action.isChecked():
                    action.setChecked(False)
            else:
                if action.text() == action_item.text():
                    action.setChecked(True)

    def _reset_actions(self):
        for action in self._menu.actions():
            action: QAction
            if action == self._idle_action:
                action.setChecked(True)
            else:
                action.setChecked(False)

    def _draw_new_animation(self, animation_index):
        self.new_animation.emit(animation_index)

    def paintEvent(self, event):
        painter = QPainter(self)

        if (
            self.sprite
            and self.sprite.animation_data
            and self.animation_index < len(self.sprite.animation_data) - 1
            and self.frame_index
            < len(self.sprite.animation_data[self.animation_index].frame_data) - 1
        ):
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
            draw_pos_x = (
                int((self.width() - frame_width) / 2)
                + self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_offset_x
            )
            draw_pos_y = (
                int((self.height() - frame_height) / 2)
                + self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_offset_y
            )
        else:
            draw_pos_x = int((self.width() - 32) / 2)
            draw_pos_y = int((self.height() - 32) / 2)
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

    def reset_animation(self):
        self.reset_animation_to_idle.emit()

    def next_frame(self):
        if (
            self.sprite
            and self.sprite.animation_data
            and self.animation_index < len(self.sprite.animation_data)
        ):
            if (
                self.frame_index
                < len(self.sprite.animation_data[self.animation_index].frame_data) - 1
            ):
                self.frame_index += 1
            else:
                self.frame_index = 0

            self.current_frame.setX(
                self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_source_x
            )
            self.current_frame.setY(
                self.sprite.animation_data[self.animation_index]
                .frame_data[self.frame_index]
                .body_source_y
            )

            # Redraw new frame
            self.update(0, 0, self.width(), self.height())