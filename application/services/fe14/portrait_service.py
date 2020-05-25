from functools import lru_cache
from typing import Dict, Optional, List, Tuple

from model.texture import Texture
from module.properties.property_container import PropertyContainer
from services.service_locator import locator

_FID_KEY = "FID"
_PORTRAIT_MODULE_KEY = "Portraits / FaceData"
_PORTRAIT_FILE_KEY = "Portrait File"
_ST_TEMPLATE = "FSID_ST_%s"
_BU_TEMPLATE = "FSID_BU_%s"
_MALE_AVATAR_PORTRAIT_FILE = "aマイユニ男1_st"
_MALE_AVATAR_HAIR_FILE = "/face/hair/マイユニ男1_st/髪0.bch.lz"
_FEMALE_AVATAR_PORTRAIT_FILE = "aマイユニ女2_st"
_FEMALE_AVATAR_HAIR_FILE = "/face/hair/マイユニ女2_st/髪0.bch.lz"

_EMOTION_VALUES = {
    "通常": 0,
    "びっくり": 1,
    "怒": 3,
    "苦": 4,
    "笑": 5,
    "キメ": 6,
    "やけくそ": 7,
    "汗": 100,
    "照": 101
}


def _get_portrait_key_value(element):
    key, _ = element
    if key in _EMOTION_VALUES:
        return _EMOTION_VALUES[key]
    return 8  # An arbitrary value between normal portraits and blush / sweat.


class FE14PortraitService:
    def __init__(self):
        self._cached_avatar = None
        self._cached_avatar_is_female = None

    def get_sorted_portraits_for_character(self, character: PropertyContainer, mode: str) \
            -> Optional[List[Tuple[str, Texture]]]:
        portraits = self.get_portraits_for_character(character, mode)
        if not portraits:
            return None
        portraits_list = [(k, v) for k, v in portraits.items()]
        return sorted(portraits_list, key=_get_portrait_key_value)

    def get_portraits_for_character(self, character: PropertyContainer, mode: str) -> Optional[Dict[str, Texture]]:
        if not character:
            return None
        fid = character[_FID_KEY].value
        if not fid or len(fid) < 4:
            return None
        return self.get_portraits_for_fid(fid, mode)

    def get_portraits_for_fid(self, fid: str, mode: str):
        entry = self.get_portrait_entry_for_fid(fid, mode)
        if not entry:
            return None
        portrait_file = entry[_PORTRAIT_FILE_KEY].value
        return self.get_portraits_from_arc(portrait_file)

    @lru_cache(maxsize=32)
    def get_portraits_from_arc(self, portrait_file_name) -> Optional[Dict[str, Texture]]:
        if not portrait_file_name:
            return None
        assets_service = locator.get_scoped("AssetsService")
        texture_map = assets_service.load_arc("/face/face/%s.arc" % portrait_file_name)
        pruned_texture_map = self._prune_file_extensions_from_keys(texture_map)
        return pruned_texture_map

    def get_blush_and_sweat_coordinates(self, fid: str, mode: str) -> Optional[List[Tuple[int, int]]]:
        entry = self.get_portrait_entry_for_fid(fid, mode)
        if not entry:
            return None
        if mode == "bu":
            return [(0, 0), (0, 0)]
        else:
            return [
                (entry["Blush Position X"].value, entry["Blush Position Y"].value),
                (entry["Sweat Position X"].value, entry["Sweat Position Y"].value)
            ]

    @staticmethod
    def get_portrait_entry_for_fid(fid: str, mode: str) -> Optional[PropertyContainer]:
        if mode == "st":
            key = _ST_TEMPLATE % fid[4:]
        else:
            key = _BU_TEMPLATE % fid[4:]
        portraits_module = locator.get_scoped("ModuleService").get_module(_PORTRAIT_MODULE_KEY)
        return portraits_module.get_element_by_key(key)

    def get_avatar_portraits(self, is_female: bool, mode: str = "st"):
        if self._cached_avatar and self._cached_avatar_is_female == is_female:
            return self._cached_avatar

        assets_service = locator.get_scoped("AssetsService")
        if is_female:
            portraits = self.get_portraits_from_arc(_FEMALE_AVATAR_PORTRAIT_FILE)
            hair = assets_service.load_bch(_FEMALE_AVATAR_HAIR_FILE)
        else:
            portraits = self.get_portraits_from_arc(_MALE_AVATAR_PORTRAIT_FILE)
            hair = assets_service.load_bch(_MALE_AVATAR_HAIR_FILE)
        if not portraits or not hair:
            portraits = self.get_portraits_for_fid("FID_フードマン", mode)
        else:
            hair_texture: Texture = hair["tmp"]
            for portrait in portraits.values():
                if portrait != "汗" and portrait != "照":
                    portrait.raw_image().paste(hair_texture.raw_image(), (0, 0), hair_texture.raw_image())
        self._cached_avatar = portraits
        self._cached_avatar_is_female = is_female
        return portraits

    @staticmethod
    def _prune_file_extensions_from_keys(texture_map: Dict[str, Texture]):
        result = {}
        for key, texture in texture_map.items():
            if key.endswith(".bch.lz"):
                result[key[:-7]] = texture
        return result
