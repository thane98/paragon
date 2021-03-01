import dataclasses
from PySide2.QtGui import QPixmap

class SpriteModel:
    def __init__(self, spritesheet: QPixmap):
        self.animation_data = list()
        self.spritesheet = spritesheet

class FE13SpriteModel(SpriteModel):
    def __init__(self, spritesheet: QPixmap, name: str, team: str, frame_width: int, frame_height: int, animation_data: list):
        super().__init__(spritesheet)
        self.name = name
        self.team = team
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.animation_data = animation_data

class FE14SpriteModel(SpriteModel):
    def __init__(self, spritesheet: QPixmap, animation_data: list):
        super().__init__(spritesheet)
        self.animation_data = animation_data

@dataclasses.dataclass
class AnimationData:
    frame_data: list

@dataclasses.dataclass
class FE13FrameData:
    frame_delay: int
    frame_index_x: int
    frame_index_y: int

@dataclasses.dataclass
class FE14FrameData:
    body_draw_x: int
    body_draw_y: int
    body_width: int
    body_height: int
    body_source_x: int
    body_source_y: int
    head_draw_x: int
    head_draw_y: int
    head_width: int
    head_height: int
    head_source_x: int
    head_source_y: int
    frame_delay: int
