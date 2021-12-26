import dataclasses
from typing import Optional


@dataclasses.dataclass
class FE15SupportInfo:
    pid1: str
    pid2: str
    effects: int
    archive_path: Optional[str] = None
    conditions: Optional[int] = None
