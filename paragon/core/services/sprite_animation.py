from PySide2.QtCore import QTimer, QDateTime
from paragon.ui.controllers.sprite_item import SpriteItem


class SpriteAnimation:
    def __init__(self):
        self.timer = QTimer()
        self.sprite_items = []
        self.activated = []
        self.timer.timeout.connect(self._next_frame)

    def add_sprite(self, sprite_item: SpriteItem):
        if self.timer.isActive():
            self.activated.append(QDateTime().currentMSecsSinceEpoch())
        self.sprite_items.append(sprite_item)

    def delete_sprite(self, sprite_item: SpriteItem):
        if self.activated and self.sprite_items:
            for index in range(len(self.sprite_items)):
                if self.sprite_items[index] == sprite_item:
                    self.sprite_items.pop(index)
                    self.activated.pop(index)
                    break

    def start(self):
        time = QDateTime().currentMSecsSinceEpoch()
        self.activated = [time for _ in range(len(self.sprite_items))]
        # Check every 60Hz or 60FPS for layman's terms
        self.timer.start(1000 / 60)

    def stop(self):
        self.timer.stop()

    def _next_frame(self):
        current_time = QDateTime().currentMSecsSinceEpoch()
        for x in range(len(self.sprite_items)):
            # If non-zero
            if frame_delay := self.sprite_items[x].get_current_frame_delay():
                if (current_time - self.activated[x]) / frame_delay > 1:
                    self.activated[x] = current_time
                    # Fire signal here
                    try:
                        self.sprite_items[x].next_frame()
                    except:
                        pass
            # If zero
            else:
                # Fire signal here
                try:
                    self.sprite_items[x].next_frame()
                except:
                    pass
