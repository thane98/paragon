import dataclasses
from typing import List, Optional


@dataclasses.dataclass
class Speaker:
    name: str
    position: int
    alias: Optional[str] = None
    fid_alias: Optional[str] = None
    emotions: List[str] = dataclasses.field(default_factory=list)

    @staticmethod
    def anonymous_speaker():
        return Speaker("", -1)

    def is_anonymous(self) -> bool:
        return self.name == "" and self.position == -1

    def is_top(self) -> bool:
        return self.position == 0 or self.position == 2

    def is_bottom(self):
        return not self.is_top()
