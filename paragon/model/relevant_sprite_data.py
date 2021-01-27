import dataclasses


@dataclasses.dataclass
class RelevantSpriteData:
    head_x: int
    head_y: int
    is_half_size: bool
