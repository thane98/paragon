import dataclasses
from typing import List
from PySide2.QtGui import QPixmap

@dataclasses.dataclass
class AnimationData:
    frame_data: list

@dataclasses.dataclass
class FrameData:
    frame_delay: int

class SpriteModel:
    def __init__(self, spritesheet: QPixmap, animation_data: List[AnimationData]):
        self.spritesheet = spritesheet
        self.animation_data = animation_data

class FE13SpriteModel(SpriteModel):
    def __init__(self, spritesheet: QPixmap, name: str, team: str, frame_width: int, frame_height: int, animation_data: List[AnimationData]):
        super().__init__(spritesheet, animation_data)
        self.name = name
        self.team = team
        self.frame_width = frame_width
        self.frame_height = frame_height

class FE14SpriteModel(SpriteModel):
    pass

@dataclasses.dataclass
class FE13FrameData(FrameData):
    frame_index_x: int
    frame_index_y: int

@dataclasses.dataclass
class FE14FrameData(FrameData):
    body_offset_x: int
    body_offset_y: int
    body_width: int
    body_height: int
    body_source_x: int
    body_source_y: int
    head_offset_x: int
    head_offset_y: int
    head_width: int
    head_height: int
    head_source_x: int
    head_source_y: int