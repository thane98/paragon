import dataclasses
from typing import Optional


@dataclasses.dataclass
class FE15DungeonInfo:
    name: str
    encount: Optional[int] = None
    dungeon_field: Optional[int] = None
    encount_field: Optional[int] = None
    drop_group: Optional[int] = None
    field_refer: Optional[int] = None
    field_files: Optional[int] = None
    terrain: Optional[int] = None
    terrain_key: Optional[str] = None
    dispos: Optional[int] = None
    dispos_key: Optional[str] = None
