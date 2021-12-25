import dataclasses
from typing import List

from paragon.model.fe15_event_command import FE15EventCommand


@dataclasses.dataclass
class FE15EventSequence:
    name: str
    commands: List[FE15EventCommand]

    def to_paragon_format(self) -> str:
        lines = (
            [f'sequence "{self.name}" {{']
            + ["    " + c.to_paragon_format() for c in self.commands]
            + ["}"]
        )
        return "\n".join(lines)
