from PySide2.QtCore import QTimer, QDateTime, QPoint
from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QPixmap, QPainter

from paragon.core.services.sprites import Sprites

class SpriteItemHandler:
    def __init__(self, parent):
        self.timer = QTimer(parent)
        self.sprite_items = list()
        self.timer.timeout.connect(self._next_frame)

    def add_sprite(self, sprite_item: Sprites):
        self.sprite_items.append(sprite_item)

    def run(self):
        time = QDateTime().currentMSecsSinceEpoch()
        self.activated = [time for _ in range(len(self.sprite_items))]
        # Check every 30Hz
        self.timer.start(1000/30)
    
    def stop(self):
        self.timer.stop()

    def _next_frame(self):
        current_time = QDateTime().currentMSecsSinceEpoch()
        for x in range(len(self.sprite_items)):
            # If sprite is loaded
            if sprite := self.sprite_items[x].sprite:
                # If the sprite has animation data
                if animation_data := sprite.animation_data:
                    if (current_time - self.activated[x])/sprite.animation_data[self.sprite_items[x].animation_index].frame_data[self.sprite_items[x].frame_index].frame_delay > 1:
                        self.activated[x] = current_time
                        
                        # Fire signal here
                        self.sprite_items[x].next_frame()

# Any changes to the child classes of SpriteItem
# Should be changed in MapCell
class SpriteItem(QLabel):
    def __init__(self, sprite_svc):
        super().__init__()
        self.current_frame = QPoint(0,0)
        self.animation_index = 0
        self.frame_index = 0
        self.sprite_svc = sprite_svc
        self.sprite = None

    def next_frame(self):
        raise NotImplementedError

    def reset_animation(self):
        self.animation_index = 0
        self.frame_index = 0
        self.current_frame.setX(0)
        self.current_frame.setY(0)


class FE13UnitSpriteItem(SpriteItem):
    pass
    # def __init__(self, sprite_svc, is_sprite_item):
    #     if not is_sprite_item:
    #         super().__init__(sprite_svc)
    #         print("yes")

        # self._frame_height = 32
        # self._frame_width = 32

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.drawPixmap(
    #         32,
    #         32, 
    #         self.pixmap(), 
    #         self._current_frame.x(), 
    #         self._current_frame.y(), 
    #         self._frame_width, 
    #         self._frame_height
    #     )
    #     painter.end()

    # def _next_frame(self):
    #     # Loop frames backwards:
    #     # `Idle` and `Use` animation
    #     if self.frame_index < len(self.sprite.animation_data[self.animation_index]) - 1:
    #         self.frame_index += 1
    #     else:
    #         self.frame_index = 0

    #     self._current_frame.setX(self.sprite.animation_data[self.animation_index][self.frame_index].x() * self._frame_width)
    #     self._current_frame.setY(self.sprite.animation_data[self.animation_index][self.frame_index].y() * self._frame_height)

    #     # Redraw new frame
    #     self.update(
    #         0, 
    #         0, 
    #         self._frame_width, 
    #         self._frame_height
    #     )
