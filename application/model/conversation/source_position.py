from dataclasses import dataclass


@dataclass
class SourcePosition:
    line_number: int
    character: int
