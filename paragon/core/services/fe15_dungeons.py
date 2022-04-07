import logging
import os
from typing import Optional, Set, Tuple

import yaml
from PySide2.QtCore import QStringListModel
from yaml import Loader

from paragon.core.services import utils
from paragon.model.dungeons_model import DungeonsModel
from paragon.model.fe15_dungeon_info import FE15DungeonInfo


_DEFAULT_FACTIONS = [
    "Player",
    "Player_Good",
    "EnemyU",
    "EnemyL",
    "EnemyR",
    "EnemyUL",
    "EnemyUR",
]


class FE15Dungeons:
    def __init__(self, gd):
        self.gd = gd

        try:
            with open(
                os.path.join("resources", "FE15", "Dungeons.yml"), "r", encoding="utf-8"
            ) as f:
                self.dungeon_list = sorted(yaml.load(f, Loader=Loader))
        except:
            logging.exception("Failed to load dungeon list.")
            self.dungeon_list = set()

        self.dungeons_model = DungeonsModel(self.gd, self.dungeon_list)

    def get_drop_list_from_drop_group(
        self, selected_drop_group: Optional[int]
    ) -> Optional[int]:
        if not selected_drop_group:
            return None
        drop_list = self.gd.rid(selected_drop_group, "drop_list")
        return self.gd.rid(drop_list, "item_list") if drop_list else None

    def get_encounter_factions(self, info: FE15DungeonInfo) -> Set[str]:
        if not info.encount or not info.dispos:
            return set()
        else:
            factions = set()
            encounters = self.gd.items(info.encount, "encounters")
            for encounter in encounters:
                faction = self.gd.string(encounter, "dispo_faction")
                if faction:
                    factions.add(faction)
            return factions.union(_DEFAULT_FACTIONS)

    def get_dungeons_model(self) -> QStringListModel:
        return self.dungeons_model

    def mark_dirty(self, dungeon_info: FE15DungeonInfo):
        self.gd.set_store_dirty("field", True)
        self.gd.set_store_dirty("dungeon", True)
        if dungeon_info.encount:
            self.gd.multi_set_dirty("encounters", dungeon_info.encount_key, True)
        if dungeon_info.dispos:
            self.gd.multi_set_dirty("dispos", dungeon_info.dispos_key, True)
        if dungeon_info.terrain_key:
            self.gd.multi_set_dirty("grids", dungeon_info.terrain_key, True)

    def load_dungeon(self, dungeon_name: str) -> FE15DungeonInfo:
        dungeon_drop_group = self._get_dungeon_drop_group(dungeon_name)
        dungeon_field = self.gd.key_to_rid("field", dungeon_name)
        encount_field = self._get_encount_field(dungeon_field)
        encount_key = f"Data/Encount/{dungeon_name}.bin.lz"
        encount = utils.try_multi_open(
            self.gd, "encounters", encount_key
        )
        if encount:
            dispos, dispos_key = self._get_battlefield_dispos(encount_field)
            terrain_key, terrain_rid = self._get_battlefield_terrain(encount_field)
        else:
            dispos, dispos_key, terrain_key, terrain_rid = None, None, None, None
        return FE15DungeonInfo(
            dungeon_name,
            drop_group=dungeon_drop_group,
            dungeon_field=dungeon_field,
            encount_field=encount_field,
            encount=encount,
            encount_key=encount_key,
            dispos=dispos,
            dispos_key=dispos_key,
            terrain_key=terrain_key,
            terrain=terrain_rid,
        )

    def _get_dungeon_drop_group(self, dungeon_name) -> Optional[int]:
        dungeon_drop_group = self.gd.key_to_rid(
            "dungeon_drop_groups", "DG_" + dungeon_name
        )
        if not dungeon_drop_group:
            return None
        else:
            return self.gd.rid(dungeon_drop_group, "data")

    def _get_encount_field(self, dungeon_field: Optional[int]) -> Optional[int]:
        if not dungeon_field:
            return None
        encounter_field = self.gd.string(dungeon_field, "encounter_field")
        if not encounter_field:
            return None
        return self.gd.key_to_rid("field", encounter_field)

    def _get_battlefield_dispos(self, encount_field: Optional[int]) -> Tuple[Optional[str], Optional[int]]:
        if not encount_field:
            return None, None
        encounter_dispos = self.gd.string(encount_field, "encounter_dispos")
        if not encounter_dispos:
            return None, None
        key = f"Data/Dispos/{encounter_dispos}.bin.lz"
        rid = utils.try_multi_open(self.gd, "dispos", key)
        return (rid, key) if rid else (None, None)

    def _get_battlefield_terrain(
        self, encount_field: Optional[int]
    ) -> Tuple[Optional[str], Optional[int]]:
        if not encount_field:
            return None, None
        encounter_terrain = self.gd.string(encount_field, "encounter_terrain")
        if not encounter_terrain:
            return None, None
        key = f"Data/Terrain/{encounter_terrain}.bin.lz"
        rid = utils.try_multi_open(self.gd, "grids", key)
        return (key, rid) if rid else (None, None)
