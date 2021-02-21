from PySide2.QtCore import QTimer, QDateTime, QPoint
from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QPixmap, QPainter

from paragon.core.services.sprites import Sprites

class SpriteItemHandler():
    def __init__(self):
        super(SpriteItemHandler, self).__init__()

        self.timer = QTimer()
        self.sprites = list()
        self.timeouts = list()
        self.timer.timeout.connect(self._next_frame)


    def add_sprite(self, sprite: Sprites):
        self.sprites.append(sprite)

    def run(self):
        self.activated = [QDateTime().currentMSecsSinceEpoch() for x in range(len(self.timeouts))]
        # Check every 30Hz
        self.timer.start(1000/30)

    def _next_frame(self):
        current_time = QDateTime().currentMSecsSinceEpoch()
        for x in range(len(self.timeouts)):
            if int((current_time - self.activated[x])/self.timeouts[x]):
                self.activated[x] = current_time
                
                # Fire event here
                self.sprites[x]._next_frame()

# Any changes to the child classes of SpriteItem
# Should be changed in MapCell
class SpriteItem(QLabel):
    def __init__(self, spritesheet):
        super().__init__()
        self._current_frame = QPoint(0,0)
        self._loop = True
        self.spritesheet = spritesheet

    def _next_frame(self):
        raise NotImplementedError

class FE13UnitSpriteItem(SpriteItem):
    def __init__(self, spritesheet):
        super().__init__(spritesheet)

        # Might just use spritesheet dimensions instead 
        self._end_frame_pos_x = 96
        self._frame_height = 32
        self._frame_width = 32

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(
            0,
            0, 
            self.pixmap(), 
            self._current_frame.x(), 
            self._current_frame.y(), 
            self._frame_width, 
            self._frame_height
        )
        painter.end()

    def _next_frame(self):
        # Loop frames backwards:
        # `Idle` and `Use` animation
        if self._current_frame.y() in [0, 32]:

            # Start looping back at the end of frame
            if self._current_frame.x() == self._end_frame_pos_x and self._loop == False:
                self._current_frame.setX(
                    self._current_frame.x() - self._frame_width
                )
                self._loop = True
                
            # End loop at the start of frame
            elif self._current_frame.x() == 0 and self._loop == True:
                self._current_frame.setX(
                    self._current_frame.x() + self._frame_width
                )
                self._loop = False

            # If looping back, go back a frame
            elif 0 < self._current_frame.x() < self._end_frame_pos_x and self._loop == True:
                self._current_frame.setX(
                    self._current_frame.x() - self._frame_width
                )

            # If not looping, go forward a frame 
            elif self._current_frame.x() < self._end_frame_pos_x and self._loop == False:
                self._current_frame.setX(
                    self._current_frame.x() + self._frame_width
                )

        # Loop normally
        else:
            if self._current_frame.x() == self._end_frame_pos_x:
                self._current_frame.setX(0)
            elif self._current_frame.x() < self._end_frame_pos_x:
                self._current_frame.setX(
                    self._current_frame.x() + self._frame_width
                )

        # Redraw new frame
        self.update(
            0, 
            0, 
            self._frame_width, 
            self._frame_height
        )
