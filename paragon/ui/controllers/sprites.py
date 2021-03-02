from PySide2 import QtCore
from PySide2.QtCore import QPoint, Signal
from PySide2.QtWidgets import QLabel, QMenu, QAction
from PySide2.QtGui import QPixmap, QPainter, QMouseEvent, QCursor

class SpriteItem(QLabel):
    def __init__(self, sprite_svc):
        super().__init__()
        self.current_frame = QPoint(0,0)
        self.animation_index = 0
        self.frame_index = 0
        self.sprite_svc = sprite_svc
        self.sprite = None
        self.sprite_svc.add_sprite_to_handler(self)

    def set_sprite(self, sprite):
        self.sprite = sprite
        self.setPixmap(self.sprite.spritesheet) if self.sprite else self.setPixmap(None)
        self.reset_animation()

    def next_frame(self):
        raise NotImplementedError

    def reset_animation(self):
        self.animation_index = 0
        self.frame_index = 0
        self.current_frame.setX(0)
        self.current_frame.setY(0)
        self._reset_actions()

    def _reset_actions(self):
        raise NotImplementedError

    def __del__(self):
        if self.sprite_svc:
            self.sprite_svc.delete_sprite_from_handler(self)
        del self

class FE13UnitSpriteItem(SpriteItem):
    left_clicked = Signal()
    def __init__(self, sprite_svc):
        super().__init__(sprite_svc)
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
        self._idle_hover_action = QAction("Idle Hover", self)
        self._moving_west_action = QAction("Moving West", self)
        self._moving_east_action = QAction("Moving East", self)
        self._moving_south_action = QAction("Moving South", self)
        self._moving_north_action = QAction("Moving North", self)
        self._moving_southwest_action = QAction("Moving Southwest", self)
        self._moving_southeast_action = QAction("Moving Southeast", self)
        self._moving_northwest_action = QAction("Moving Northwest", self)
        self._moving_northeast_action = QAction("Moving Northeast", self)

        self._idle_action.setCheckable(True)
        self._idle_hover_action.setCheckable(True)
        self._moving_west_action.setCheckable(True)
        self._moving_east_action.setCheckable(True)
        self._moving_south_action.setCheckable(True)
        self._moving_north_action.setCheckable(True)
        self._moving_southwest_action.setCheckable(True)
        self._moving_southeast_action.setCheckable(True)
        self._moving_northwest_action.setCheckable(True)
        self._moving_northeast_action.setCheckable(True)

        self._idle_action.setChecked(True)        
        self._menu.addAction(self._idle_action)
        self._menu.addAction(self._idle_hover_action)
        self._menu.addAction(self._moving_west_action)
        self._menu.addAction(self._moving_east_action)
        self._menu.addAction(self._moving_south_action)
        self._menu.addAction(self._moving_north_action)
        self._menu.addAction(self._moving_southwest_action)
        self._menu.addAction(self._moving_southeast_action)
        self._menu.addAction(self._moving_northwest_action)
        self._menu.addAction(self._moving_northeast_action)

        self._idle_action.triggered.connect(self._on_click_idle_action)
        self._idle_hover_action.triggered.connect(self._on_click_idle_hover_action)
        self._moving_west_action.triggered.connect(self._on_click_moving_west_action)
        self._moving_east_action.triggered.connect(self._on_click_moving_east_action)
        self._moving_south_action.triggered.connect(self._on_click_moving_south_action)
        self._moving_north_action.triggered.connect(self._on_click_moving_north_action)
        self._moving_southwest_action.triggered.connect(self._on_click_moving_southwest_action)
        self._moving_southeast_action.triggered.connect(self._on_click_moving_southeast_action)
        self._moving_northwest_action.triggered.connect(self._on_click_moving_northwest_action)
        self._moving_northeast_action.triggered.connect(self._on_click_moving_northeast_action)

    @QtCore.Slot(bool)
    def _on_click_idle_action(self, triggered):
        self._uncheck_actions(triggered, self._idle_action)
        self._draw_new_animation(0)

    @QtCore.Slot(bool)
    def _on_click_idle_hover_action(self, triggered):
        self._uncheck_actions(triggered, self._idle_hover_action)
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
        self.frame_index = 0
        self.animation_index = animation_index
        self.next_frame()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        if self.sprite and self.sprite.frame_height and self.sprite.frame_width and self.sprite.animation_data:
            draw_pos_x = int((self.height() - self.sprite.frame_width)/2)
            draw_pos_y = int((self.width() - self.sprite.frame_width)/2)
            frame_width = self.sprite.frame_width
            frame_height = self.sprite.frame_height
        elif self.sprite and self.sprite.frame_height and self.sprite.frame_width:
            draw_pos_x = int((self.height() - self.sprite.frame_width)/2),
            draw_pos_y = int((self.height() - self.sprite.frame_height)/2),
            frame_width = self.sprite.frame_width
            frame_height = self.sprite.frame_height
        else:
            draw_pos_x = int((self.width() - 32)/2)
            draw_pos_y = int((self.height() - 32)/2)
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

    def next_frame(self):
        if self.sprite and self.sprite.animation_data:
            if self.frame_index < len(self.sprite.animation_data[self.animation_index].frame_data) - 1:
                self.frame_index += 1
            else:
                self.frame_index = 0

            self.current_frame.setX(
                self.sprite.animation_data[self.animation_index].frame_data[self.frame_index].frame_index_x * self.sprite.frame_width
            )
            self.current_frame.setY(
                self.sprite.animation_data[self.animation_index].frame_data[self.frame_index].frame_index_y * self.sprite.frame_height
            )

        # Redraw new frame
        self.update(
            0,
            0,
            self.width(), 
            self.height()
        )

class FE14UnitSpriteItem(SpriteItem):
    def __init__(self, sprite_svc):
        super().__init__(sprite_svc)
        self._setup_menu()

    def mousePressEvent(self, ev: QMouseEvent):
        super().mousePressEvent(ev)
        if ev.button() == QtCore.Qt.RightButton:
            self._show_context_menu(ev)

    def _setup_menu(self):
        self._menu = QMenu()
        self._idle_action = QAction("Idle", self)
        self._moving_west_action = QAction("Moving West", self)
        self._moving_east_action = QAction("Moving East", self)
        self._moving_south_action = QAction("Moving South", self)
        self._moving_north_action = QAction("Moving North", self)
        self._moving_southwest_action = QAction("Moving Southwest", self)
        self._moving_southeast_action = QAction("Moving Southeast", self)
        self._moving_northwest_action = QAction("Moving Northwest", self)
        self._moving_northeast_action = QAction("Moving Northeast", self)

        self._idle_action.setCheckable(True)
        self._moving_west_action.setCheckable(True)
        self._moving_east_action.setCheckable(True)
        self._moving_south_action.setCheckable(True)
        self._moving_north_action.setCheckable(True)
        self._moving_southwest_action.setCheckable(True)
        self._moving_southeast_action.setCheckable(True)
        self._moving_northwest_action.setCheckable(True)
        self._moving_northeast_action.setCheckable(True)

        self._idle_action.setChecked(True)        
        self._menu.addAction(self._idle_action)
        self._menu.addAction(self._moving_west_action)
        self._menu.addAction(self._moving_east_action)
        self._menu.addAction(self._moving_south_action)
        self._menu.addAction(self._moving_north_action)
        self._menu.addAction(self._moving_southwest_action)
        self._menu.addAction(self._moving_southeast_action)
        self._menu.addAction(self._moving_northwest_action)
        self._menu.addAction(self._moving_northeast_action)

        self._idle_action.triggered.connect(self._on_click_idle_action)
        self._moving_west_action.triggered.connect(self._on_click_moving_west_action)
        self._moving_east_action.triggered.connect(self._on_click_moving_east_action)
        self._moving_south_action.triggered.connect(self._on_click_moving_south_action)
        self._moving_north_action.triggered.connect(self._on_click_moving_north_action)
        self._moving_southwest_action.triggered.connect(self._on_click_moving_southwest_action)
        self._moving_southeast_action.triggered.connect(self._on_click_moving_southeast_action)
        self._moving_northwest_action.triggered.connect(self._on_click_moving_northwest_action)
        self._moving_northeast_action.triggered.connect(self._on_click_moving_northeast_action)

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

    @QtCore.Slot(bool)
    def _on_click_moving_southwest_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_southwest_action)
        self._draw_new_animation(5)

    @QtCore.Slot(bool)
    def _on_click_moving_southeast_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_southeast_action)
        self._draw_new_animation(6)

    @QtCore.Slot(bool)
    def _on_click_moving_northwest_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_northwest_action)
        self._draw_new_animation(7)

    @QtCore.Slot(bool)
    def _on_click_moving_northeast_action(self, triggered):
        self._uncheck_actions(triggered, self._moving_northeast_action)
        self._draw_new_animation(8)

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
        self.frame_index = 0
        self.animation_index = animation_index
        self.next_frame()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        if self.sprite and self.sprite.frame_height and self.sprite.frame_width and self.sprite.animation_data:
            draw_pos_x = int((self.height() - self.sprite.frame_width)/2)
            draw_pos_y = int((self.width() - self.sprite.frame_width)/2)
            frame_width = self.sprite.frame_width
            frame_height = self.sprite.frame_height
        elif self.sprite and self.sprite.frame_height and self.sprite.frame_width:
            draw_pos_x = int((self.height() - self.sprite.frame_width)/2),
            draw_pos_y = int((self.height() - self.sprite.frame_height)/2),
            frame_width = self.sprite.frame_width
            frame_height = self.sprite.frame_height
        else:
            draw_pos_x = int((self.width() - 32)/2)
            draw_pos_y = int((self.height() - 32)/2)
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

    def next_frame(self):
        if self.sprite and self.sprite.animation_data:
            if self.frame_index < len(self.sprite.animation_data[self.animation_index].frame_data) - 1:
                self.frame_index += 1
            else:
                self.frame_index = 0

            self.current_frame.setX(
                self.sprite.animation_data[self.animation_index].frame_data[self.frame_index].frame_index_x * self.sprite.frame_width
            )
            self.current_frame.setY(
                self.sprite.animation_data[self.animation_index].frame_data[self.frame_index].frame_index_y * self.sprite.frame_height
            )

        # Redraw new frame
        self.update(
            0,
            0,
            self.width(), 
            self.height()
        )