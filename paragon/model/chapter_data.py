import dataclasses
from typing import Optional

from paragon.model.fe14_chapter_route import FE14ChapterRoute


@dataclasses.dataclass
class ChapterData:
    cid: str
    decl: Optional[int]
    dispos: Optional[int] = None
    dispos_key: Optional[str] = None
    person: Optional[int] = None
    person_key: Optional[str] = None
    terrain: Optional[int] = None
    terrain_key: Optional[str] = None
    config: Optional[int] = None
    config_key: Optional[str] = None
    landscape: Optional[int] = None
    landscape_key: Optional[str] = None
    event: Optional[int] = None
    event_key: Optional[str] = None
    dialogue: Optional[str] = None
    fe14_route: FE14ChapterRoute = FE14ChapterRoute.INVALID
