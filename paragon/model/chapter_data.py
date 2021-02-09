import dataclasses
from typing import Optional


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
