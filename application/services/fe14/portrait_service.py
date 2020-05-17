from functools import lru_cache
from typing import Dict, Optional

from model.texture import Texture
from module.properties.property_container import PropertyContainer
from services.service_locator import locator

_FID_KEY = "FID"
_PORTRAIT_MODULE_KEY = "Portraits / FaceData"
_PORTRAIT_FILE_KEY = "Portrait File"
_ST_TEMPLATE = "FSID_ST_%s"
_BU_TEMPLATE = "FSID_BU_%s"


class FE14PortraitService:
    def get_portraits_for_character(self, character: PropertyContainer, mode: str) -> Optional[Dict[str, Texture]]:
        portraits_module = locator.get_scoped("ModuleService").get_module(_PORTRAIT_MODULE_KEY)
        fid = character[_FID_KEY].value
        if not fid or len(fid) < 4:
            return None

        if mode == "st":
            key = _ST_TEMPLATE % fid[4:]
        else:
            key = _BU_TEMPLATE % fid[4:]
        entry = portraits_module.get_element_by_key(key)
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

    def get_hair_from_arc(self):
        pass

    def get_accessory_from_arc(self):
        pass

    @staticmethod
    def _prune_file_extensions_from_keys(texture_map: Dict[str, Texture]):
        result = {}
        for key, texture in texture_map.items():
            if key.endswith(".bch.lz"):
                result[key[:-7]] = texture
        return result
