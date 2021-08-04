import dataclasses
from enum import Enum
from typing import Optional


class DialogueType(str, Enum):
    STANDARD = "Standard"
    PARENT_CHILD = "Parent / Child"
    SIBLINGS = "Siblings"
    BIRTHRIGHT_ONLY = "Birthright Only"
    CONQUEST_ONLY = "Conquest Only"
    REVELATION_ONLY = "Revelation Only"


@dataclasses.dataclass
class SupportInfo:
    char1: int
    char2: int
    dialogue_path: str
    dialogue_type: DialogueType
    support: Optional[int] = None
    already_localized: bool = False
