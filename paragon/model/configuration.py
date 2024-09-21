import json
import logging
import os
from typing import List, Optional, Literal, Dict

import pydantic
from pydantic import BaseModel

from paragon.model.exalt_script_editor_config import ExaltScriptEditorConfig
from paragon.model.fe13_avatar_config import FE13AvatarConfig
from paragon.model.fe14_avatar_config import FE14AvatarConfig
from paragon.model.project import Project


def default_fe9_job_icons():
    return {
        "JID_RANGER": 1,
        "JID_HERO": 18,
        "JID_HERO_G": 48,
        "JID_SWORDER": 0,
        "JID_SWORDER/F": 0,
        "JID_SWORDMASTER": 11,
        "JID_SWORDMASTER/F": 11,
        "JID_SOLDIER": 20,
        "JID_SOLDIER/F": 20,
        "JID_HALBERDIER": 22,
        "JID_HALBERDIER/F": 22,
        "JID_FIGHTER": 33,
        "JID_WARRIOR": 35,
        "JID_ARCHER": 49,
        "JID_SNIPER": 50,
        "JID_ARMOR": 20,
        "JID_GENERAL": 22,
        "JID_SOCIALKNIGHT_S": 0,
        "JID_SOCIALKNIGHT_L": 20,
        "JID_SOCIALKNIGHT_A": 33,
        "JID_SOCIALKNIGHT_B": 49,
        "JID_SOCIALKNIGHT_S/F": 0,
        "JID_SOCIALKNIGHT_L/F": 20,
        "JID_SOCIALKNIGHT_A/F": 33,
        "JID_SOCIALKNIGHT_B/F": 49,
        "JID_PALADIN_S": 4,
        "JID_PALADIN_L": 23,
        "JID_PALADIN_A": 36,
        "JID_PALADIN_B": 51,
        "JID_PALADIN_S/F": 4,
        "JID_PALADIN_L/F": 23,
        "JID_PALADIN_A/F": 36,
        "JID_PALADIN_B/F": 51,
        "JID_TIAMAT/F": 36,
        "JID_UNUSED0/F": 36,
        "JID_BKNIGHT": 6,
        "JID_CROW_NES": 73,
        "JID_BIRD_C_NES": 73,
        "JID_HAWK_TIB": 71,
        "JID_BIRD_HA_TIB": 71,
        "JID_DUMMY": 186,
        "JID_SAGE_S": 80,
        "JID_PEGASUSKNIGHT/F": 21,
        "JID_FALCONKNIGHT/F": 25,
        "JID_FALCONKNIGHT_E/F": 66,
        "JID_DRAGONKNIGHT": 20,
        "JID_DRAGONKNIGHT/F": 20,
        "JID_DRAGONMASTER": 26,
        "JID_DRAGONMASTER/F": 26,
        "JID_DRAGONMASTER_A": 19,
        "JID_CHILD/F": 186,
        "JID_CHILD": 186,
        "JID_CITIZEN/F": 186,
        "JID_CITIZEN": 186,
        "JID_CROW": 73,
        "JID_HAWK": 71,
        "JID_REDDRAGON/F": 69,
        "JID_REDDRAGON": 69,
        "JID_WHITEDRAGON": 68,
        "JID_BLACKDRAGON": 187,
        "JID_CAT/F": 65,
        "JID_CAT": 65,
        "JID_TIGER": 63,
        "JID_LION": 61,
        "JID_BIRD_C": 73,
        "JID_BIRD_HA": 71,
        "JID_DRAGON_R/F": 69,
        "JID_DRAGON_R": 69,
        "JID_DRAGON_W": 68,
        "JID_DRAGON_B": 68,
        "JID_BEAST_C/F": 65,
        "JID_BEAST_C": 65,
        "JID_BEAST_T": 63,
        "JID_BEAST_L": 61,
        "JID_BERSERKER": 44,
        "JID_BANDIT": 43,
        "JID_ASSASSIN/F": 60,
        "JID_ASSASSIN": 60,
        "JID_THIEF": 58,
        "JID_VALKYRIE/F": 175,
        "JID_CLERIC/F": 100,
        "JID_BISHOP/F": 95,
        "JID_BISHOP": 95,
        "JID_PRIEST": 100,
        "JID_HERON": 133,
        "JID_HERON_W": 133,
        "JID_HERON_W/F": 133,
        "JID_BIRD_HE_W/F": 133,
        "JID_BIRD_HE_W": 133,
        "JID_BIRD_HE": 133,
        "JID_MAGE_F": 78,
        "JID_MAGE_W": 83,
        "JID_MAGE_T": 89,
        "JID_MAGE": 78,
        "JID_MAGE_F/F": 78,
        "JID_MAGE_W/F": 83,
        "JID_MAGE_T/F": 89,
        "JID_MAGE/F": 78,
        "JID_SAGE_F": 79,
        "JID_SAGE_W": 85,
        "JID_SAGE_T": 90,
        "JID_SAGE": 79,
        "JID_SAGE_F/F": 79,
        "JID_SAGE_W/F": 85,
        "JID_SAGE_T/F": 90,
        "JID_SAGE/F": 79,
        "JID_SAGE_R_F": 79,
        "JID_SAGE_R_W": 85,
        "JID_SAGE_R_T": 90,
        "JID_SAGE_S_F": 79,
        "JID_SAGE_S_W": 85,
        "JID_SAGE_S_T": 90
    }

def default_fe10_job_icons():
    return {
    "JID_BRAVE": 18,
    "JID_VANGUARD": 18,
    "JID_DARKKNIGHT": 19,
    "JID_SHAMAN": 121,
    "JID_CAESER": 101,
    "JID_CHANCELLOR": 122,
    "JID_QUEEN": 20,
    "JID_LION_GI": 144,
    "JID_KINGLION": 144,
    "JID_LION_CA": 144,
    "JID_BEASTTRIBE_L": 143,
    "JID_LION": 143,
    "JID_KINGLION_GI": 144,
    "JID_QUEENWOLF": 148,
    "JID_KINGHAWK": 150,
    "JID_HAWK_TI": 150,
    "JID_KINGCROW": 152,
    "JID_DRAGONKING": 156,
    "JID_DRAGONPRINCE": 156,
    "JID_GODDESS_AURA": 94,
    "JID_GODDESS": 94,
    "JID_DEBUG": 18,
    "JID_VALKYRIA": 16,
    "JID_SOLDIER": 32,
    "JID_HALBERDIER": 34,
    "JID_HALBERDIER_F": 34,
    "JID_HALBERDIER_SP": 34,
    "JID_HOLYLANCER": 35,
    "JID_HOLYLANCER_F": 35,
    "JID_FIGHTER": 49,
    "JID_WARRIOR": 50,
    "JID_WARRIOR_SP": 50,
    "JID_AXBRAVE": 51,
    "JID_ARCHER": 65,
    "JID_SNIPER": 66,
    "JID_SNIPER_SP": 66,
    "JID_SAGITTARY": 67,
    "JID_BLADE": 1,
    "JID_SWORDMASTER": 9,
    "JID_SWORDMASTER_F": 9,
    "JID_SWORDMASTER_SP": 9,
    "JID_SWORDESCHATOS": 11,
    "JID_SWORDESCHATOS_F": 11,
    "JID_THIEF": 78,
    "JID_ROGUE": 79,
    "JID_ROGUE_F": 79,
    "JID_ESPION": 81,
    "JID_ESPION_F": 81,
    "JID_ASSASSIN": 84,
    "JID_BANDIT": 48,
    "JID_PILGRIM": 253,
    "JID_VENDOR_GOODS": 253,
    "JID_OLDMAN": 253,
    "JID_CITIZEN": 253,
    "JID_CITIZEN_F": 253,
    "JID_CHILD": 253,
    "JID_CHILD_F": 253,
    "JID_HORSE": 253,
    "JID_BLACKDRAGON": 156,
    "JID_WHITEDRAGON": 154,
    "JID_DRAGONTRIBE_W": 154,
    "JID_REDDRAGON_F": 153,
    "JID_DRAGONTRIBE_R/F": 153,
    "JID_REDDRAGON": 153,
    "JID_DRAGONTRIBE_R": 153,
    "JID_EGRET_LE": 164,
    "JID_PRINCESSEGRET": 164,
    "JID_EGRET_RA": 164,
    "JID_PRINCEEGRET_RA": 164,
    "JID_EGRET": 164,
    "JID_PRINCEEGRET": 164,
    "JID_CROW_NA": 151,
    "JID_CROW_F": 151,
    "JID_BIRDTRIBE_C/F": 151,
    "JID_CROW": 151,
    "JID_BIRDTRIBE_C": 151,
    "JID_HAWK": 149,
    "JID_BIRDTRIBE_H": 149,
    "JID_WOLF_F": 149,
    "JID_WOLF": 147,
    "JID_BEASTTRIBE_W": 147,
    "JID_CAT_F": 146,
    "JID_BEASTTRIBE_C/F": 146,
    "JID_CAT": 146,
    "JID_BEASTTRIBE_C": 146,
    "JID_TIGER": 145,
    "JID_BEASTTRIBE_T": 145,
    "JID_RLINDWURM_F": 51,
    "JID_RLINDWURM": 51,
    "JID_DRAGONMASTER_SP": 50,
    "JID_DRAGONMASTER_F": 50,
    "JID_DRAGONMASTER": 50,
    "JID_DRAGONKNIGHT_F": 49,
    "JID_DRAGONKNIGHT": 49,
    "JID_PEGASUSKNIGHT": 32,
    "JID_FALCONKNIGHT": 34,
    "JID_FALCONKNIGHT_SP": 34,
    "JID_ENLILKNIGHT": 35,
    "JID_SILVERKNIGHT_B": 67,
    "JID_SILVERKNIGHT_L_F": 35,
    "JID_SILVERKNIGHT_L": 35,
    "JID_GOLDKNIGHT_A/F": 51,
    "JID_GOLDKNIGHT_A": 51,
    "JID_GOLDKNIGHT_S": 3,
    "JID_ARROWKNIGHT_SP": 66,
    "JID_GREATKNIGHT_SP": 50,
    "JID_GLORYKNIGHT_SP": 34,
    "JID_BLADEKNIGHT_SP": 2,
    "JID_ARROWKNIGHT_F": 66,
    "JID_ARROWKNIGHT": 66,
    "JID_GREATKNIGHT_F": 50,
    "JID_GREATKNIGHT": 50,
    "JID_GLORYKNIGHT_F": 34,
    "JID_GLORYKNIGHT": 34,
    "JID_BLADEKNIGHT": 34,
    "JID_BOWKNIGHT": 65,
    "JID_AXEKNIGHT": 65,
    "JID_LANCEKNIGHT_F": 32,
    "JID_LANCEKNIGHT": 32,
    "JID_SWORDKNIGHT": 1,
    "JID_CLERIC": 16,
    "JID_SUMMONER": 126,
    "JID_DRUID_SP": 123,
    "JID_DRUID": 123,
    "JID_PRIEST": 115,
    "JID_PRIEST_F": 115,
    "JID_BISHOP": 116,
    "JID_BISHOP_F": 116,
    "JID_BISHOP_SP": 116,
    "JID_SAINT": 117,
    "JID_SAINT_F": 117,
    "JID_SAINT_SP": 117,
    "JID_FIREMAGE": 96,
    "JID_FIRESAGE": 97,
    "JID_FIRESAGE_F": 97,
    "JID_FIRESAGE_SP": 97,
    "JID_ARCHSAGE_F": 99,
    "JID_ARCHSAGE_F/F": 98,
    "JID_THUNDERSAGE": 104,
    "JID_THUNDERSAGE_F": 104,
    "JID_THUNDERMAGE": 103,
    "JID_THUNDERMAGE_F": 103,
    "JID_ARCHSAGE_T/F": 105,
    "JID_ARCHSAGE_W": 111,
    "JID_WINDMAGE": 109,
    "JID_WINDSAGE": 110,
    "JID_LIGHTSAGE": 121,
    "JID_LIGHTMAGE": 121,
    "JID_THUNDERSAGE_SP": 104,
    "JID_WINDSAGE_SP": 110,
    "JID_ARCHSAGE_T": 125,
    "JID_DARKSAGE": 124,
    "JID_SPIRIT_F": 98,
    "JID_SPIRIT_S": 105,
    "JID_SPIRIT_W": 111
  }


class Configuration(BaseModel):
    projects: List[Project] = []
    remember_project: bool = True
    current_project: Optional[str] = None
    theme: Optional[str] = "Fusion Dark"
    backup: Literal["Smart", "Full", "None"] = "Smart"
    show_animations: bool = False
    log_level: int = logging.INFO
    font: Optional[str] = None
    map_editor_zoom: int = 1
    sync_coordinate_changes: bool = True
    quick_dialogue_auto_line_break: bool = True
    quick_dialogue_line_width_chars: int = 30
    store_manager_auto_refresh: bool = True
    exalt_script_editor_config: ExaltScriptEditorConfig = pydantic.Field(
        default_factory=ExaltScriptEditorConfig
    )
    fe13_avatar: FE13AvatarConfig = pydantic.Field(default_factory=FE13AvatarConfig)
    fe14_avatar: FE14AvatarConfig = pydantic.Field(default_factory=FE14AvatarConfig)
    fe9_job_icons: Dict[str, int] = pydantic.Field(default_factory=default_fe9_job_icons)
    fe10_job_icons: Dict[str, int] = pydantic.Field(default_factory=default_fe10_job_icons)

    def set_current_project(self, project: Project):
        self.current_project = project.get_id()

    @staticmethod
    def load(path) -> "Configuration":
        logging.info("Loading configuration...")
        path = os.path.abspath(path)
        if not os.path.exists(path):
            logging.warn(
                f'paragon.json was not found at path "{path}". Using default configuration...'
            )
            return Configuration()
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_config = json.load(f)
                return Configuration(**raw_config)
        except:
            logging.exception(f"Failed to load config {path}.")
            return Configuration()

    def save(self, path):
        logging.info("Saving configuration...")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.dict(), f, indent=2, ensure_ascii=False)
        except:
            logging.exception(f"Failed to save config {path}.")
            raise

    @staticmethod
    def available_themes() -> List[str]:
        return ["Native", "Fusion", "Fusion Dark"]
