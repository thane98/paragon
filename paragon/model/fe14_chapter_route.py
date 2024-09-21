from enum import Enum


class FE14ChapterRoute(Enum):
    BIRTHRIGHT = 0
    CONQUEST = 1
    REVELATION = 2
    ALL = 3
    INVALID = 4

    def subdir(self) -> str:
        if self == FE14ChapterRoute.BIRTHRIGHT:
            return "A"
        elif self == FE14ChapterRoute.CONQUEST:
            return "B"
        elif self == FE14ChapterRoute.REVELATION:
            return "C"
        elif self == FE14ChapterRoute.ALL:
            return ""
        else:
            raise ValueError("Cannot compute subdir for an invalid chapter.")

    def byte_value(self):
        if self == FE14ChapterRoute.BIRTHRIGHT:
            return 0b001
        elif self == FE14ChapterRoute.CONQUEST:
            return 0b010
        elif self == FE14ChapterRoute.REVELATION:
            return 0b100
        elif self == FE14ChapterRoute.ALL:
            return 0b111
        else:
            raise ValueError("Cannot compute byte value for an invalid chapter.")
