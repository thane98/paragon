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
