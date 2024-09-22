import dataclasses
import os
from enum import Enum
from typing import Dict, List, Optional


_PLACEHOLDER_SUPPORT = (
    "$t1$Wmアンナ|3$w0|$Wsアンナ|$E通常,|This message was generated\\nby Paragon.$k"
)


class FE13FamilySupportType(str, Enum):
    PARENT_CHILD = "Parent / Child"
    SIBLINGS = "Siblings"

    def get_stem(self) -> str:
        if self == FE13FamilySupportType.PARENT_CHILD:
            return "親子"
        else:
            return "兄弟"


@dataclasses.dataclass
class FE13FamilySupport:
    path: str
    char1: int
    char2: int
    support_type: FE13FamilySupportType
    localized: bool


class FE13Supports:
    def __init__(self, gd):
        self.gd = gd

        self.supports_by_character: Dict[int, List[FE13FamilySupport]] = {}

        char_table_rid, char_table_field_id = self.gd.table("characters")
        characters = self.gd.items(char_table_rid, char_table_field_id)
        key_to_rid = self._build_key_to_rid_dict(characters)
        support_files = self.gd.list_files("m", "**/*.bin.lz", True)
        for character in characters:
            pid = self.gd.key(character)
            if pid and pid.startswith("PID_"):
                stem = pid[4:]
            else:
                continue
            supports = [s for s in support_files if stem in s]
            family_supports = []
            for f in supports:
                parts = os.path.basename(f).replace(".bin.lz", "").split("_")
                if len(parts) == 3 and (parts[-1] == "親子" or parts[-1] == "兄弟"):
                    char1_stem, char2_stem = parts[0], parts[1]
                    char1, char2 = key_to_rid.get(char1_stem), key_to_rid.get(
                        char2_stem
                    )
                    support_type = (
                        FE13FamilySupportType.PARENT_CHILD
                        if parts[-1] == "親子"
                        else FE13FamilySupportType.SIBLINGS
                    )
                    if char1 and char2 and (char1 == character or char2 == character):
                        family_supports.append(
                            FE13FamilySupport(f, char1, char2, support_type, False)
                        )
            self.supports_by_character[character] = family_supports

    def get_supports(self, character: int) -> Optional[List[FE13FamilySupport]]:
        return self.supports_by_character.get(character)

    def family_support_exists(
        self, char1: int, char2: int, support_type: FE13FamilySupportType
    ) -> bool:
        if supports := self.get_supports(char1):
            for support in supports:
                if (
                    support.char1 == char2 or support.char2 == char2
                ) and support.support_type == support_type:
                    return True
        return False

    def add_support(
        self, char1: int, char2: int, support_type: FE13FamilySupportType
    ) -> FE13FamilySupport:
        char1_stem = self.gd.key(char1)[4:]
        char2_stem = self.gd.key(char2)[4:]
        archive_path = f"m/{char1_stem}_{char2_stem}_{support_type.get_stem()}.bin.lz"
        support1 = FE13FamilySupport(archive_path, char1, char2, support_type, True)
        support2 = FE13FamilySupport(archive_path, char2, char1, support_type, True)

        char1_supports = self.supports_by_character.get(char1, [])
        char1_supports.append(support1)
        self.supports_by_character[char1] = char1_supports
        char2_supports = self.supports_by_character.get(char2, [])
        char2_supports.append(support2)
        self.supports_by_character[char2] = char2_supports

        self.gd.new_text_data(archive_path, True)
        self.gd.set_text_archive_title(
            archive_path,
            True,
            f"MESS_ARCHIVE_{char1_stem}_{char2_stem}_{support_type.get_stem()}",
        )

        self.gd.set_message(
            archive_path,
            True,
            f"MID_支援_{char1_stem}_{char2_stem}_{support_type.get_stem()}_Ｃ",
            _PLACEHOLDER_SUPPORT,
        )
        self.gd.set_message(
            archive_path,
            True,
            f"MID_支援_{char1_stem}_{char2_stem}_{support_type.get_stem()}_Ｂ",
            _PLACEHOLDER_SUPPORT,
        )
        self.gd.set_message(
            archive_path,
            True,
            f"MID_支援_{char1_stem}_{char2_stem}_{support_type.get_stem()}_Ａ",
            _PLACEHOLDER_SUPPORT,
        )

        return support1

    def _build_key_to_rid_dict(self, characters):
        key_to_rid = {}
        for rid in characters:
            key = self.gd.key(rid)
            if key and key.startswith("PID_"):
                key_to_rid[key[4:]] = rid
        return key_to_rid
