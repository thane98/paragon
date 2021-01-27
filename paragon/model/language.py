from enum import Enum


class Language(str, Enum):
    JAPANESE = "Japanese"
    ENGLISH_NA = "EnglishNA"
    ENGLISH_EU = "EnglishEU"
    SPANISH = "Spanish"
    FRENCH = "French"
    GERMAN = "German"
    ITALIAN = "Italian"
    DUTCH = "Dutch"

    def to_rust_variant(self):
        return self.value
