import logging
from typing import Optional, List

from paragon.core.display import display_rid
from paragon.model.support_info import SupportInfo, DialogueType

_ROMANTIC_SUPPORT_TYPE = 336464132
_PLACEHOLDER_SUPPORT = (
    "$t1$Wmアンナ|3$w0|$Wsアンナ|$E通常,|This message was generated\\nby Paragon.$k"
)


class FE14Supports:
    def __init__(self, gd):
        self.gd = gd
        self.support_table_rid, self.support_table_field_id = self.gd.table("supports")
        self.char_table_rid, self.char_table_field_id = self.gd.table("characters")
        self.dialogue_types = [
            (DialogueType.PARENT_CHILD, "m/%s_%s_親子.bin.lz"),
            (DialogueType.SIBLINGS, "m/%s_%s_兄弟.bin.lz"),
            (DialogueType.BIRTHRIGHT_ONLY, "m/%s白_%s.bin.lz"),
            (DialogueType.CONQUEST_ONLY, "m/%s黒_%s.bin.lz"),
            (DialogueType.REVELATION_ONLY, "m/%s透_%s.bin.lz"),
        ]

    def add_support(self, char1, char2, support_type=_ROMANTIC_SUPPORT_TYPE):
        table1 = self._ensure_table_exists(char1)
        table2 = self._ensure_table_exists(char2)
        self._add_support(table2, char1, support_type)
        return self._add_support(table1, char2, support_type)

    def _add_support(self, table, char, support_type):
        support = self.gd.list_add(table, "supports")
        self.gd.set_rid(support, "character", char)
        self.gd.set_int(support, "type", support_type)
        return support

    def _ensure_table_exists(self, char):
        if table := self.get_table(char):
            return table
        main_entry = self.gd.list_add(
            self.support_table_rid, self.support_table_field_id
        )
        table = self.gd.new_instance("SupportTable")
        self.gd.set_rid(table, "owner", char)
        self.gd.set_rid(main_entry, "table", table)
        return table

    def create_dialogue_archive(
        self, char1, char2, dialogue_type=DialogueType.STANDARD
    ) -> str:
        char1_key = self.gd.key(char1)[4:]
        char2_key = self.gd.key(char2)[4:]
        if dialogue_type == DialogueType.PARENT_CHILD:
            path = f"m/{char1_key}_{char2_key}_親子.bin.lz"
            template = f"MID_支援_{char1_key}_{char2_key}_親子"
        elif dialogue_type == DialogueType.SIBLINGS:
            path = f"m/{char1_key}_{char2_key}_兄弟.bin.lz"
            template = f"MID_支援_{char1_key}_{char2_key}_兄弟"
        elif dialogue_type == DialogueType.BIRTHRIGHT_ONLY:
            path = f"m/{char1_key}白_{char2_key}.bin.lz"
            template = f"MID_支援_{char1_key}白_{char2_key}"
        elif dialogue_type == DialogueType.CONQUEST_ONLY:
            path = f"m/{char1_key}黒_{char2_key}.bin.lz"
            template = f"MID_支援_{char1_key}黒_{char2_key}"
        elif dialogue_type == DialogueType.REVELATION_ONLY:
            path = f"m/{char1_key}透_{char2_key}.bin.lz"
            template = f"MID_支援_{char1_key}透_{char2_key}"
        else:
            path = f"m/{char1_key}_{char2_key}.bin.lz"
            template = f"MID_支援_{char1_key}_{char2_key}"
        self.gd.new_text_data(path, True)
        self._populate_archive(path, template, dialogue_type)
        return path

    def _populate_archive(self, path, template, dt):
        c_support = template + "_Ｃ"
        b_support = template + "_Ｂ"
        a_support = template + "_Ａ"
        self.gd.set_message(path, True, c_support, _PLACEHOLDER_SUPPORT)
        self.gd.set_message(path, True, b_support, _PLACEHOLDER_SUPPORT)
        self.gd.set_message(path, True, a_support, _PLACEHOLDER_SUPPORT)
        if dt != DialogueType.PARENT_CHILD and dt != DialogueType.SIBLINGS:
            s_support = template + "_Ｓ"
            self.gd.set_message(path, True, s_support, _PLACEHOLDER_SUPPORT)

    # TODO: Can we make this support other dialogue types as well?
    def delete_support(self, char1, char2):
        if table := self.get_table(char1):
            self._remove_support(table, char2)
        if table := self.get_table(char2):
            self._remove_support(table, char2)

    def _remove_support(self, table, target):
        for i, support in enumerate(self.gd.items(table, "supports")):
            character = self.gd.rid(support, "character")
            if target == character:
                self.gd.list_remove(table, "supports", i)
                return

    # Determine if the char/type combo exists in the given support list.
    @staticmethod
    def support_exists(char, dialogue_type, support_infos) -> bool:
        for info in support_infos:
            if info.char2 == char and info.dialogue_type == dialogue_type:
                return True
        return False

    def get_table(self, char) -> Optional[int]:
        for table in self.gd.items(self.support_table_rid, self.support_table_field_id):
            table = self.gd.rid(table, "table")  # Dereference pointer.
            if table:
                owner = self.gd.rid(table, "owner")
                if owner == char:
                    return table
        return None

    # Partition characters based on whether or not they have
    # a support with the given character.
    def get_supports(self, char) -> List[SupportInfo]:
        # Enumerate characters and get the support table.
        characters = self.gd.items(self.char_table_rid, self.char_table_field_id)
        table = self.get_table(char)
        if not table:
            return []

        # Start partitioning. Couple of situations we need to check for:
        # - Standard supports which are actually listed in the support table.
        # - Remaining types are only stored as dialogue in the rom.
        #   to get these, we check if the files exist.
        supports = []
        char1_key = self.gd.key(char)
        if char1_key and char1_key.startswith("PID_"):
            char1_key = char1_key[4:]
        else:
            return []

        # Start with the easy case: the support is in the table.
        for support in self.gd.items(table, "supports"):
            # Lots of ways that this can go wrong...
            char2 = self.gd.rid(support, "character")
            try:
                char2_key = self.gd.key(char2)[4:]
                path = self._get_support_path("m/%s_%s.bin.lz", char1_key, char2_key)
                if not path:
                    path = f"m/{char1_key}_{char2_key}.bin.lz"
                supports.append(
                    SupportInfo(char, char2, path, DialogueType.STANDARD, support)
                )
            except:
                logging.exception("Error due to bad support or PID.")

        # Now search for the special support types.
        for other in characters:
            try:
                char2_key = self.gd.key(other)[4:]
                for dialogue_type, template in self.dialogue_types:
                    path = self._get_support_path(template, char1_key, char2_key)
                    if path:
                        supports.append(SupportInfo(char, other, path, dialogue_type))
            except:
                logging.exception("Error searching for special support dialogue.")

        return sorted(
            supports, key=lambda s: display_rid(self.gd, s.char2, "fe14_character")
        )

    def _get_support_path(self, path_base, key1, key2) -> Optional[str]:
        path1 = path_base % (key1, key2)
        path2 = path_base % (key2, key1)
        if self.gd.file_exists(path1, True) or self.gd.has_text_data(path1, True):
            return path1
        elif self.gd.file_exists(path2, True) or self.gd.has_text_data(path2, True):
            return path2
        return None
