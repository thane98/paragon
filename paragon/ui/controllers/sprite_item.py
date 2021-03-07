from PySide2.QtCore import QPoint, Signal, QRectF
from PySide2.QtWidgets import QLabel, QGraphicsItem
from PySide2.QtGui import QPixmap, QPainter

from paragon.core.services.dialogue import Dialogue

class AbstractSpriteItem:
    left_clicked = Signal()
    new_animation = Signal(int)
    reset_animation_to_idle = Signal()
    
    def __init__(self, sprite_svc, sprite_animation_svc):
        self.current_frame = QPoint(0,0)
        self.animation_index = 0
        self.frame_index = 0
        self.sprite_svc = sprite_svc
        self.sprite_animation_svc = sprite_animation_svc
        self.sprite = None
        self.sprite_animation_svc.add_sprite(self)

    def set_sprite(self, sprite):
        self.sprite = sprite
        self.setPixmap(self.sprite.spritesheet) if self.sprite else self.setPixmap(None)
        self.reset_animation()
                            
    def next_frame(self):
        raise NotImplementedError

    def reset_animation(self):
        raise NotImplementedError

    def _reset_actions(self):
        raise NotImplementedError

class SpriteItem(AbstractSpriteItem, QLabel):
    def __init__(self, sprite_svc, sprite_animation):
        AbstractSpriteItem.__init__(self, sprite_svc, sprite_animation)
        QLabel.__init__(self)

    def get_current_frame_delay(self) -> int:
        # If sprite is loaded
        if self.sprite:
            # If the sprite has animation data
            if animation_data := self.sprite.animation_data:
                # Is it possible to index the animation data
                if self.animation_index < len(animation_data) and self.frame_index < len(animation_data[self.animation_index].frame_data):
                    if frame_delay := animation_data[self.animation_index].frame_data[self.frame_index].frame_delay:
                        return frame_delay
                    else:
                        return 0

    def __del__(self):
        if self.sprite_animation_svc:
            self.sprite_animation_svc.delete_sprite(self)
        del self

class SceneSpriteItem(AbstractSpriteItem, QGraphicsItem):
    def __init__(self, sprite: QPixmap, texture_name: str, dialogue_svc: Dialogue, sprite_animation_svc):
        AbstractSpriteItem.__init__(self, dialogue_svc, sprite_animation_svc)
        QGraphicsItem.__init__(self)        

        self.animation_data = None
        self.sprite = sprite
        for obj in dialogue_svc.dialogue_animations:
            if obj["texture"] == texture_name:
                self.animation_data = obj
                break

    def get_current_frame_delay(self) -> int:
        return 1000/60 * self.animation_data["animation_data"][self.frame_index]["frame_delay"]

    def next_frame(self):
        if self.frame_index < len(self.animation_data["animation_data"]) - 1:
            self.frame_index += 1
        else:
            self.frame_index = 0

        self.current_frame.setX(
            self.animation_data["animation_data"][self.frame_index]["draw_position_x"]
        )
        self.current_frame.setY(
            self.animation_data["animation_data"][self.frame_index]["draw_position_y"]
        )
        self.update(
            0,
            0,
            self.sprite.width(),
            self.sprite.height()
        )

    def boundingRect(self) -> QRectF:
        return QRectF(
            0, 
            0, 
            self.sprite.width(), 
            self.sprite.height()
        )

    def paint(self, painter: QPainter, option, widget):
        painter.drawPixmap(
            self.current_frame.x(),
            self.current_frame.y(), 
            self.sprite, 
            0, 
            0, 
            self.sprite.width(), 
            self.sprite.height()
        )

    def __del__(self):
        if self.sprite_animation_svc:
            self.sprite_animation_svc.delete_scene_sprite(self)
        del self
