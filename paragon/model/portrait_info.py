import dataclasses


# There isn't much here yet, but we'll need this if
# we start generating player portraits, adjusting based
# on portrait positions, etc.
from typing import Tuple, Dict


@dataclasses.dataclass
class PortraitInfo:
    body_arc: str
    blush_coords: Dict[str, Tuple[int, int]]
    sweat_coords: Dict[str, Tuple[int, int]]
