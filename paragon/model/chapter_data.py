import dataclasses
from typing import Optional

from paragon.model.fe14_chapter_route import FE14ChapterRoute


@dataclasses.dataclass
class ChapterData:
    cid: str
    decl: Optional[int]
    dispos: Optional[int]
    dispos_key: Optional[str]
    person: Optional[int]
    person_key: Optional[str]
    terrain: Optional[int]
    terrain_key: Optional[str]
    config: Optional[int]
    config_key: Optional[str]
    landscape: Optional[int] = None
    landscape_key: Optional[str] = None
    dialogue: Optional[str] = None
    fe14_route: FE14ChapterRoute = FE14ChapterRoute.INVALID
