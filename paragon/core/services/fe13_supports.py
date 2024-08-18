import dataclasses
import os
from typing import Dict, List, Optional


@dataclasses.dataclass
class FE13FamilySupport:
    path: str
    char1: int
    char2: int


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
                if len(parts) == 3 and parts[-1] == "親子":
                    char1_stem, char2_stem = parts[0], parts[1]
                    char1, char2 = key_to_rid.get(char1_stem), key_to_rid.get(
                        char2_stem
                    )
                    if char1 and char2 and (char1 == character or char2 == character):
                        family_supports.append(FE13FamilySupport(f, char1, char2))
            self.supports_by_character[character] = family_supports

    def get_supports(self, character: int) -> Optional[List[FE13FamilySupport]]:
        return self.supports_by_character.get(character)

    def _build_key_to_rid_dict(self, characters):
        key_to_rid = {}
        for rid in characters:
            key = self.gd.key(rid)
            if key and key.startswith("PID_"):
                key_to_rid[key[4:]] = rid
        return key_to_rid
