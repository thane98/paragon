from enum import Enum


class Game(str, Enum):
    FE13 = "FE13"
    FE14 = "FE14"
    FE15 = "FE15"

    def to_rust_variant(self):
        return self.value
