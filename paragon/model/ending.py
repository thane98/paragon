import dataclasses
from typing import Optional


@dataclasses.dataclass
class Ending:
    key: str
    value: str
    char1: Optional[int] = None
    char1_name: Optional[str] = None
    char2: Optional[int] = None
    char2_name: Optional[str] = None

    def is_single(self):
        return self.char2 is None

    def is_empty(self):
        return bool(not self.char1 and not self.char2)

    def display(self):
        if self.is_single():
            ending_type = "Single"
            char_text = self.char1_name if self.char1_name else "???"
        elif self.is_empty():
            return "???"
        else:
            ending_type = "Paired"
            char1_text = self.char1_name if self.char1_name else "???"
            char2_text = self.char2_name if self.char2_name else "???"
            char_text = f"{char1_text} x {char2_text}"
        return f"{char_text} ({ending_type})"
