import dataclasses
from typing import Tuple, Optional, List


class GcnMapData:
    width: int
    height: int
    margin: int

    def get_tile(self, index: int) -> int:
        raise NotImplementedError

    def len(self) -> int:
        raise NotImplementedError


@dataclasses.dataclass
class GcnDisposData:
    common: Optional[int]
    normal: Optional[int]
    hard: Optional[int]
    maniac: Optional[int]

    def get_dispos_options(self) -> List[str]:
        options = []
        if self.common:
            options.append("Common")
        if self.normal:
            options.append("Normal")
        if self.hard:
            options.append("Hard")
        if self.maniac:
            options.append("Maniac")
        return options


@dataclasses.dataclass
class GcnChapterData:
    zmap: str
    map_data: GcnMapData
    dispos: GcnDisposData
