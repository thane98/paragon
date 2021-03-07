from PySide2.QtCore import QTimer, QDateTime
from paragon.ui.controllers.sprite_item import SpriteItem, SceneSpriteItem


class SpriteAnimation:
    def __init__(self):
        self.timer = QTimer()
        self.sprite_items = []
        self.activated = []

        self.scene_sprite_timer = QTimer()
        self.scene_sprite_items = []
        self.scene_sprite_activated = []

        self.timer.timeout.connect(self._next_frame)
        self.scene_sprite_timer.timeout.connect(self._next_scene_item_frame)

    def add_sprite(self, sprite_item: SpriteItem):
        if isinstance(sprite_item, SceneSpriteItem):
            if self.timer.isActive():
                self.scene_sprite_activated.append(QDateTime().currentMSecsSinceEpoch())
            self.scene_sprite_items.append(sprite_item)
        else:
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
    
    def delete_scene_sprite(self, sprite_item: SceneSpriteItem):
        if self.activated and self.scene_sprite_items:
            for index in range(len(self.scene_sprite_items)):
                if self.scene_sprite_items[index] == sprite_item:
                    self.scene_sprite_items.pop(index)
                    self.scene_sprite_activated.pop(index)
                    break

    def start(self):
        time = QDateTime().currentMSecsSinceEpoch()
        self.activated = [time for _ in range(len(self.sprite_items))]
        # Check every 30Hz or 30FPS for layman's terms
        self.timer.start(1000 / 30)
        # Check every 60Hz or 60FPS for layman's terms
        self.scene_sprite_timer.start(1000 / 60)

    def stop(self):
        self.timer.stop()

    def _next_frame(self):
        current_time = QDateTime().currentMSecsSinceEpoch()
        for x in range(len(self.sprite_items)):
            # If non-zero
            if (current_time - self.activated[x]) / self.sprite_items[x].get_current_frame_delay() > 1:
                self.activated[x] = current_time
                # Fire signal here
                try:
                    self.sprite_items[x].next_frame()
                except:
                    pass

    def _next_scene_item_frame(self):
        current_time = QDateTime().currentMSecsSinceEpoch()
        for x in range(len(self.scene_sprite_items)):
            # All entries with frame delay of 0 are skipped
            if (current_time - self.scene_sprite_activated[x]) / self.scene_sprite_items[x].get_current_frame_delay() > 1:
                self.scene_sprite_activated[x] = current_time
                # Fire signal here
                try:
                    self.scene_sprite_items[x].next_frame()
                except:
                    pass