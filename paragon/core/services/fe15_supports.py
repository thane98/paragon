from random import Random
from typing import Optional, List

from paragon.model.fe15_support_info import FE15SupportInfo


_PLACEHOLDER_SUPPORT = (
    "$t1$Wm%s|3$w0|$Ws%s|$E笑,|This is a placeholder! Add your dialogue here.$k"
)


class FE15Supports:
    def __init__(self, gd):
        self.gd = gd
        self.rand = Random()

        table, field_id = self.gd.table("characters")
        items = self.gd.items(table, field_id)
        self.placeholder_options = []
        for i in range(1, min(35, len(items))):
            fid = self.gd.string(items[i], "fid")
            if fid and fid.startswith("FID_"):
                self.placeholder_options.append(fid[4:])
        if not self.placeholder_options:
            self.placeholder_options.append("ルカ")

    def add_support(self, char1, char2, add_conditions, add_dialogue):
        pid1 = self.gd.key(char1)
        pid2 = self.gd.key(char2)
        effects1 = self._ensure_effects_exists(pid1)
        effects2 = self._ensure_effects_exists(pid2)
        effects1_data = self.gd.list_add(effects1, "items")
        effects2_data = self.gd.list_add(effects2, "items")
        self.gd.set_rid(effects1_data, "character", char2)
        self.gd.set_rid(effects2_data, "character", char1)
        info = FE15SupportInfo(
            pid1,
            pid2,
            effects1_data,
        )
        if add_conditions:
            self.add_conditions_to_support(info)
        if add_dialogue:
            self.add_message_archive_to_support(info)
        return info

    def delete_support(self, info: FE15SupportInfo):
        char1 = self.gd.key_to_rid("characters", info.pid1)
        char2 = self.gd.key_to_rid("characters", info.pid2)
        effects1 = self._get_support_effects_rid_by_pid(info.pid1)
        effects2 = self._get_support_effects_rid_by_pid(info.pid2)
        if effects1:
            self._delete_support_from_effects(effects1, char2)
        if effects2:
            self._delete_support_from_effects(effects2, char1)

    def support_exists(self, char1, char2):
        pid1 = self.gd.key(char1)
        pid2 = self.gd.key(char2)
        for support in self.get_supports(char1):
            if support.pid2 == pid2:
                return True
        for support in self.get_supports(char2):
            if support.pid2 == pid1:
                return True

    def get_supports(self, character_rid) -> List[FE15SupportInfo]:
        pid = self.gd.key(character_rid)
        effects = self._get_supports_effects_by_pid(pid)
        if not effects:
            return []

        supports = []
        for effect in effects:
            other_pid = self.gd.key(effect)
            supports.append(
                FE15SupportInfo(
                    pid1=pid,
                    pid2=other_pid,
                    effects=effect,
                    conditions=self._find_support_conditions(pid, other_pid),
                    archive_path=self._find_message_archive_path(pid, other_pid),
                )
            )
        return supports

    def add_conditions_to_support(self, info: FE15SupportInfo):
        rid = self._ensure_conditions_exists(info.pid1)
        other_character_rid = self.gd.key_to_rid("characters", info.pid2)
        info.conditions = self.gd.list_add(rid, "items")
        self.gd.set_rid(info.conditions, "character", other_character_rid)

    def add_message_archive_to_support(self, info: FE15SupportInfo):
        char1_key = info.pid1[4:]
        char2_key = info.pid2[4:]
        path = f"m/支援会話_{char1_key}_{char2_key}.bin.lz"
        self.gd.new_text_data(path, True)
        self.gd.set_text_archive_title(
            path, True, f"MESS_ARCHIVE_{char1_key}_{char2_key}"
        )
        self.gd.set_message(
            path,
            True,
            f"MID_支援会話_{char1_key}_{char2_key}_C",
            self._generate_placeholder_support(),
        )
        self.gd.set_message(
            path,
            True,
            f"MID_支援会話_{char1_key}_{char2_key}_B",
            self._generate_placeholder_support(),
        )
        self.gd.set_message(
            path,
            True,
            f"MID_支援会話_{char1_key}_{char2_key}_A",
            self._generate_placeholder_support(),
        )
        info.archive_path = path

    def _generate_placeholder_support(self):
        choice = self.rand.choice(self.placeholder_options)
        return _PLACEHOLDER_SUPPORT % (choice, choice)

    def _delete_support_from_effects(self, effects_rid, target: int):
        items = self.gd.items(effects_rid, "items")
        for i, rid in enumerate(items):
            if self.gd.rid(rid, "character") == target:
                self.gd.list_remove(effects_rid, "items", i)
                return

    def _ensure_conditions_exists(self, pid) -> int:
        if rid := self._get_support_conditions_rid_by_pid(pid):
            return rid
        conditions, field_id = self.gd.table("support_conditions")
        new_conditions_table_rid = self.gd.list_add(conditions, field_id)
        self.gd.set_string(new_conditions_table_rid, "rcid", "RCID" + pid[3:])
        conditions_table = self.gd.new_instance("SupportConditionsData")
        self.gd.set_rid(new_conditions_table_rid, "conditions", conditions_table)
        return self._get_support_conditions_rid_by_pid(pid)

    def _find_support_conditions(self, pid1, pid2) -> Optional[int]:
        if not pid1 or not pid2:
            return None
        conditions1 = self._get_support_conditions_rid_by_pid(pid1)
        if conditions1:
            if rid := self.gd.list_key_to_rid(conditions1, "items", pid2):
                return rid
        conditions2 = self._get_support_conditions_rid_by_pid(pid2)
        if conditions2:
            if rid := self.gd.list_key_to_rid(conditions2, "items", pid1):
                return rid
        return None

    def _find_message_archive_path(self, pid1, pid2) -> Optional[str]:
        if not pid1 or not pid2:
            return None
        path1 = f"m/支援会話_{pid1[4:]}_{pid2[4:]}.bin.lz"
        if self.gd.file_exists(path1, True):
            return path1
        path2 = f"m/支援会話_{pid2[4:]}_{pid1[4:]}.bin.lz"
        if self.gd.file_exists(path2, True):
            return path2
        return None

    def _get_support_conditions_rid_by_pid(self, pid) -> Optional[int]:
        if not pid or not pid.startswith("PID_"):
            return None
        else:
            rid = self.gd.key_to_rid("support_conditions", "RCID" + pid[3:])
            if not rid:
                return None
            return self.gd.rid(rid, "conditions")

    def _ensure_effects_exists(self, pid) -> int:
        if rid := self._get_support_effects_rid_by_pid(pid):
            return rid
        table, field_id = self.gd.table("support_effects")
        new_effects_table_rid = self.gd.list_add(table, field_id)
        self.gd.set_string(new_effects_table_rid, "supid", "SU" + pid)
        effects_table = self.gd.new_instance("SupportEffectData")
        self.gd.set_rid(new_effects_table_rid, "conditions", effects_table)
        return self._get_support_effects_rid_by_pid(pid)

    def _get_supports_effects_by_pid(self, pid) -> List[int]:
        rid = self._get_support_effects_rid_by_pid(pid)
        if not rid:
            return []
        return self.gd.items(rid, "items") if rid else []

    def _get_support_effects_rid_by_pid(self, pid) -> Optional[int]:
        if not pid or not pid.startswith("PID_"):
            return None
        else:
            rid = self.gd.key_to_rid("support_effects", "SU" + pid)
            if not rid:
                return None
            return self.gd.rid(rid, "effects")
