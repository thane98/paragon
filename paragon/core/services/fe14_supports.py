import logging
import os
from typing import Optional, List

from paragon.model.support_info import SupportInfo, DialogueType

_ROMANTIC_SUPPORT_TYPE = 336464132
_DEFAULT_MUSIC = "STRM_EVT_DAILY_E1"
_PLACEHOLDER_SUPPORT = (
    "$t1$Wmアンナ|3$w0|$Wsアンナ|$E通常,|This message was generated\\nby Paragon.$k"
)


class FE14Supports:
    def __init__(self, gd):
        self.gd = gd
        self.support_table_rid, self.support_table_field_id = self.gd.table("supports")
        self.char_table_rid, self.char_table_field_id = self.gd.table("characters")
        self.dialogue_types = [
            (DialogueType.PARENT_CHILD, "*_*_親子.bin.lz", False),
            (DialogueType.SIBLINGS, "*_*_兄弟.bin.lz", False),
            (DialogueType.BIRTHRIGHT_ONLY, "*白_*.bin.lz", True),
            (DialogueType.CONQUEST_ONLY, "*黒_*.bin.lz", True),
            (DialogueType.REVELATION_ONLY, "*透_*.bin.lz", True),
        ]
        self.supports = self._load_all_supports()

    @staticmethod
    def _is_male_corrin(char_key):
        return char_key == "プレイヤー男"

    @staticmethod
    def _is_female_corrin(char_key):
        return char_key == "プレイヤー女"

    def _get_support_suffix(self, char1_key, char2_key):
        if self._is_male_corrin(char1_key) or self._is_male_corrin(char2_key):
            return "_PCM1"
        elif self._is_female_corrin(char1_key) or self._is_female_corrin(char2_key):
            return "_PCF1"
        else:
            return ""

    def create_s_support(self, info):
        _, template, suffix = self._get_template(
            info.char1, info.char2, DialogueType.STANDARD
        )
        key = template + "_Ｓ" + suffix
        self.gd.set_message(
            info.dialogue_path,
            not info.already_localized,
            key,
            "This is a placeholder message.\\nSee the guide for info on formatting.",
        )

        table, field_id = self.gd.table("support_music")
        s_support = template[7:] + "_Ｓ"
        self._add_support_music(table, field_id, s_support, _DEFAULT_MUSIC)
        return key

    def add_support(
        self,
        char1,
        char2,
        support_type=_ROMANTIC_SUPPORT_TYPE,
        dialogue_type=DialogueType.STANDARD,
    ):
        char1_key = self.gd.key(char1)[4:]
        char2_key = self.gd.key(char2)[4:]
        if dialogue_type == DialogueType.STANDARD:
            table1 = self._ensure_table_exists(char1)
            table2 = self._ensure_table_exists(char2)
            support1 = self._add_support(table1, char2, support_type)
            support2 = self._add_support(table2, char1, support_type)
        else:
            support1, support2 = None, None
        path = self._create_dialogue_archive(char1, char2, dialogue_type)
        support_info_1 = SupportInfo(
            char1, char2, path, dialogue_type, support=support1
        )
        support_info_2 = SupportInfo(
            char2, char1, path, dialogue_type, support=support2
        )
        insert_row = self._add_support_to_cache(char1_key, support_info_1)
        self._add_support_to_cache(char2_key, support_info_2)
        return insert_row, support_info_1

    def set_type_for_inverse_support(self, info: SupportInfo, raw_support_type):
        if table := self.get_table(info.char2):
            for support in self.gd.items(table, "supports"):
                character = self.gd.rid(support, "character")
                if info.char1 == character:
                    self.gd.set_int(support, "type", raw_support_type)
                    return

    def _add_support(self, table, char, support_type):
        support = self.gd.list_add(table, "supports")
        self.gd.set_rid(support, "character", char)
        self.gd.set_int(support, "type", support_type)
        return support

    def _add_support_to_cache(self, key, support) -> int:
        if key in self.supports:
            if support.dialogue_type == DialogueType.STANDARD:
                insert_index = next(
                    filter(
                        lambda s: s[1].dialogue_type != DialogueType.STANDARD,
                        enumerate(self.supports[key]),
                    ),
                    (len(self.supports[key]), None),
                )[0]
                self.supports[key].insert(insert_index, support)
                return insert_index
            else:
                self.supports[key].append(support)
                return len(self.supports[key]) - 1
        else:
            self.supports[key] = [support]
            return 0

    def _ensure_table_exists(self, char):
        if table := self.get_table(char):
            return table
        main_entry = self.gd.list_add(
            self.support_table_rid, self.support_table_field_id
        )
        table = self.gd.new_instance("SupportTable", self.gd.store_number_of(self.support_table_rid))
        self.gd.set_rid(table, "owner", char)
        self.gd.set_rid(main_entry, "table", table)
        return table

    def _create_dialogue_archive(
        self, char1, char2, dialogue_type=DialogueType.STANDARD
    ) -> str:
        if dialogue_type == DialogueType.PARENT_CHILD:
            # Ensure that the child goes before the parent.
            if self.gd.int(char1, "child_id") == 0xFFFF:
                char1, char2 = char2, char1
        char1_key = self.gd.key(char1)[4:]
        char2_key = self.gd.key(char2)[4:]
        path, template, suffix = self._get_template(char1, char2, dialogue_type)
        self.gd.new_text_data(path, True)
        self.gd.set_text_archive_title(
            path, True, f"MESS_ARCHIVE_{char1_key}_{char2_key}"
        )
        self._populate_archive(path, template, suffix, dialogue_type)
        self._create_music_entries(template[7:], dialogue_type)
        return path

    def _get_template(self, char1, char2, dialogue_type):
        char1_key = self.gd.key(char1)[4:]
        char2_key = self.gd.key(char2)[4:]
        suffix = self._get_support_suffix(char1_key, char2_key)
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
        return path, template, suffix

    def _populate_archive(self, path, template, suffix, dt):
        c_support = template + "_Ｃ" + suffix
        b_support = template + "_Ｂ" + suffix
        a_support = template + "_Ａ" + suffix
        self.gd.set_message(path, True, c_support, _PLACEHOLDER_SUPPORT)
        self.gd.set_message(path, True, b_support, _PLACEHOLDER_SUPPORT)
        self.gd.set_message(path, True, a_support, _PLACEHOLDER_SUPPORT)
        if dt != DialogueType.PARENT_CHILD and dt != DialogueType.SIBLINGS:
            s_support = template + "_Ｓ" + suffix
            self.gd.set_message(path, True, s_support, _PLACEHOLDER_SUPPORT)

    def _create_music_entries(self, template, dt):
        table, field_id = self.gd.table("support_music")
        c_support = template + "_Ｃ"
        b_support = template + "_Ｂ"
        a_support = template + "_Ａ"
        self._add_support_music(table, field_id, c_support, _DEFAULT_MUSIC)
        self._add_support_music(table, field_id, b_support, _DEFAULT_MUSIC)
        self._add_support_music(table, field_id, a_support, _DEFAULT_MUSIC)
        if dt != DialogueType.PARENT_CHILD and dt != DialogueType.SIBLINGS:
            s_support = template + "_Ｓ"
            self._add_support_music(table, field_id, s_support, _DEFAULT_MUSIC)

    def _add_support_music(self, table, field_id, key, music):
        # Only create the entry if it doesn't exist yet.
        if _rid := self.gd.list_key_to_rid(table, field_id, key):
            return
        rid = self.gd.list_add(table, field_id)
        self.gd.set_string(rid, "support", key)
        self.gd.set_string(rid, "music", music)

    # TODO: Can we make this support other dialogue types as well?
    def delete_support(self, char1, char2):
        if table := self.get_table(char1):
            self._remove_support_from_table(table, char2)
        if table := self.get_table(char2):
            self._remove_support_from_table(table, char2)
        self._remove_support_from_cache(char1, char2)
        self._remove_support_from_cache(char2, char1)

    def _remove_support_from_table(self, table, target):
        for i, support in enumerate(self.gd.items(table, "supports")):
            character = self.gd.rid(support, "character")
            if target == character:
                self.gd.list_remove(table, "supports", i)
                return

    def _remove_support_from_cache(
        self, char1, char2, dialogue_type=DialogueType.STANDARD
    ):
        key = self.gd.key(char1)[4:]
        if key in self.supports:
            for i, support in enumerate(self.supports[key]):
                if support.char2 == char2 and support.dialogue_type == dialogue_type:
                    del self.supports[key][i]
                    break

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

    def shift_supports(self, char, support1, support2):
        table = self.get_table(char)
        if not table:
            return
        index1 = None
        index2 = None
        for i, support in enumerate(self.gd.items(table, "supports")):
            if support == support1:
                index1 = i
            if support == support2:
                index2 = i
        if index1 is None or index1 == index2:
            return
        if index2 is None:
            index2 = self.gd.list_size(table, "supports")
        self.gd.list_remove(table, "supports", index1)
        if index1 < index2:
            self.gd.list_insert_existing(table, "supports", support1, index2 - 1)
        else:
            self.gd.list_insert_existing(table, "supports", support1, index2)

    # Partition characters based on whether or not they have
    # a support with the given character.
    def get_supports(self, char) -> List[SupportInfo]:
        key = self.gd.key(char)
        if key and key.startswith("PID_"):
            return self.supports.get(key[4:], [])
        else:
            return []

    def _load_all_supports(self):
        characters = self.gd.items(self.char_table_rid, self.char_table_field_id)
        key_to_rid = self._build_key_to_rid_dict(characters)
        supports = {}
        for rid in characters:
            key_and_supports = self._load_normal_supports_for_character(rid)
            if key_and_supports:
                key, char_supports = key_and_supports
                supports[key] = char_supports
        for t, glob, extra_char in self.dialogue_types:
            self._load_special_supports(key_to_rid, supports, t, glob, extra_char)
        return supports

    def _build_key_to_rid_dict(self, characters):
        key_to_rid = {}
        for rid in characters:
            key = self.gd.key(rid)
            if key and key.startswith("PID_"):
                key_to_rid[key[4:]] = rid
        return key_to_rid

    def _load_special_supports(
        self, key_to_rid, supports, dialogue_type, glob, extra_char=None
    ):
        for f in self.gd.list_files("m", glob, True):
            parts = os.path.basename(f).replace(".bin.lz", "").split("_")
            char1, char2 = parts[0], parts[1]
            if extra_char:
                char1 = char1[:-1]
            if char1 in key_to_rid and char2 in key_to_rid:
                char1_rid, char2_rid = key_to_rid[char1], key_to_rid[char2]
                support1 = SupportInfo(
                    char1_rid, char2_rid, f, dialogue_type, already_localized=True
                )
                support2 = SupportInfo(
                    char2_rid, char1_rid, f, dialogue_type, already_localized=True
                )
                if char1 in supports:
                    supports[char1].append(support1)
                else:
                    supports[char1] = [support1]
                if char2 in supports:
                    supports[char2].append(support2)
                else:
                    supports[char2] = [support2]
            else:
                logging.info(
                    f"Discarding support chars={char1},{char2}, path={f}"
                    " because character data cannot be found."
                )

    def _load_normal_supports_for_character(self, char):
        table = self.get_table(char)
        if not table:
            return None
        supports = []
        char1_key = self.gd.key(char)
        if char1_key and char1_key.startswith("PID_"):
            char1_key = char1_key[4:]
        else:
            return None
        for support in self.gd.items(table, "supports"):
            char2 = self.gd.rid(support, "character")
            if char2 and self.gd.key(char2).startswith("PID_"):
                char2_key = self.gd.key(char2)[4:]
                path = self._get_support_path("m/%s_%s.bin.lz", char1_key, char2_key)
                if not path:
                    path = f"m/{char1_key}_{char2_key}.bin.lz"
                supports.append(
                    SupportInfo(char, char2, path, DialogueType.STANDARD, support)
                )
        return char1_key, supports

    def _get_support_path(self, path_base, key1, key2) -> Optional[str]:
        path1 = path_base % (key1, key2)
        path2 = path_base % (key2, key1)
        if self.gd.file_exists(path1, True) or self.gd.has_text_data(path1, True):
            return path1
        elif self.gd.file_exists(path2, True) or self.gd.has_text_data(path2, True):
            return path2
        return None
