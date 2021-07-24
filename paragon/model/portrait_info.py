import dataclasses


# There isn't much here yet, but we'll need this if
# we start generating player portraits, adjusting based
# on portrait positions, etc.
from typing import Tuple, Dict, Optional


@dataclasses.dataclass
class PortraitInfo:
    body_arc: str
    blush_coords: Dict[str, Tuple[int, int]] = dataclasses.field(default_factory=dict)
    sweat_coords: Dict[str, Tuple[int, int]] = dataclasses.field(default_factory=dict)
    draw_coords: Dict[str, Tuple[int, int]] = dataclasses.field(default_factory=dict)
    component_indices: Dict[str, int] = dataclasses.field(default_factory=dict)
    file_index: Optional[int] = None
    hair_file: Optional[str] = None
    accessory_file: Optional[str] = None
    hair_color: Optional[bytes] = None
