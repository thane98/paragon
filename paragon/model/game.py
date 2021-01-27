from enum import Enum


class Game(str, Enum):
    FE9 = "FE9"
    FE10 = "FE10"
    FE11 = "FE11"
    FE12 = "FE12"
    FE13 = "FE13"
    FE14 = "FE14"
    FE15 = "FE15"

    def to_rust_variant(self):
        return self.value
