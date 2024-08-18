from PySide6.QtWidgets import QMenu
from PySide6 import QtCore
from PySide6.QtGui import QMouseEvent, QCursor, QAction

from paragon.ui.controllers.sprite_item import SpriteItem


class GcnUnitSpriteItem(SpriteItem):
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

    def _show_context_menu(self, e: QMouseEvent):
        self._menu.exec_(QCursor().pos())

    def _uncheck_actions(self, triggered: bool, action_item: QAction):
        pass

    def _reset_actions(self):
        pass

    def _draw_new_animation(self, animation_index):
        self.frame_index = 0
        self.animation_index = animation_index
        self.next_frame()

    def reset_animation(self):
        self.animation_index = 0
        self.frame_index = 0
        self.current_frame.setX(0)
        self.current_frame.setY(0)
        self._reset_actions()

    def next_frame(self):
        pass
