import dataclasses


@dataclasses.dataclass
class RelevantSpriteData:
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
