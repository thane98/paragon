import logging
import json
from typing import List, Tuple, Dict

from PySide6.QtGui import QPixmap, QFont
from paragon.core.textures.texture import Texture

from paragon.core.services import utils
from paragon.core.services.dialogue import Dialogue
from paragon.core.services.portraits import Portraits
from paragon.model.fe15_avatar_config import FE15AvatarConfig

_BACKGROUNDS = [
    "ui/mat/photo/迷路_盗賊のほこら１.bch.lz",
    "ui/mat/photo/迷路_ドルクの砦１.bch.lz",
    "ui/mat/photo/迷路_お花畑.bch.lz",
    "ui/mat/photo/要塞.bch.lz",
    "ui/mat/photo/竜の火口.bch.lz",
    "ui/mat/photo/砂漠の南.bch.lz",
    "ui/mat/photo/砂漠の北.bch.lz",
    "ui/mat/photo/盗賊の森.bch.lz",
    "ui/mat/photo/海賊の砦.bch.lz",
    "ui/mat/photo/海のほこら.bch.lz",
    "ui/mat/photo/海５.bch.lz",
    "ui/mat/photo/沼の墓地.bch.lz",
    "ui/mat/photo/水門.bch.lz",
    "ui/mat/photo/死人の沼.bch.lz",
    "ui/mat/photo/森の村.bch.lz",
]


class FE15Dialogue(Dialogue):
    def __init__(self, game, config, data, portraits: Portraits, config_root: str):
        super().__init__(game, config, data, portraits, config_root)
        dialogue_animations_path = "resources/FE15/DialogueAnimations.json"
        try:
            with open(dialogue_animations_path, "r", encoding="utf-8") as f:
                self.dialogue_animations = json.load(f)
        except:
            logging.exception("Failed to load dialogue animations.")
            self.dialogue_animations = {}

    def _base_asset_translations(self) -> Dict[str, str]:
        try:
            table_rid, field_id = self.data.table("portraits")
            all_portraits = self.data.items(table_rid, field_id)
            translations = {}
            for rid in all_portraits:
                name_key = self.data.string(rid, "name")
                if name_key and name_key.startswith("MPID_"):
                    value = self.data.message("m/Name.bin.lz", True, name_key)
                    if value:
                        value = value.replace(" ", "")
                    if value and value not in translations:
                        translations[value] = name_key[5:]
            return translations
        except:
            logging.exception("Failed to parse portrait name translations.")
            return {}

    def _load_backgrounds(self) -> List[Tuple[str, QPixmap]]:
        textures = []
        for path in _BACKGROUNDS:
            res = utils.safe_texture_load(lambda: self.data.read_bch_textures(path))
            for key in res:
                pixmap = Texture.from_core_texture(res[key]).to_qpixmap()
                textures.append((path[7:], pixmap))
        return textures

    def _load_windows(self) -> Dict[str, Dict[str, QPixmap]]:
        core = self.data.read_bch_textures("ui/mat/Talk.bch.lz")["IntermediateCtex1"]
        texture = Texture.from_core_texture(core)
        uvs_rid = self.data.multi_open("uvs", "ui/mat/Talk.bin.lz")
        all_uvs = self.data.items(uvs_rid, "uvs")
        u0_texture = utils.parse_texture_with_uvs(self.data, texture, all_uvs[2])
        u1_texture = utils.parse_texture_with_uvs(self.data, texture, all_uvs[3])
        d_texture = utils.parse_texture_with_uvs(self.data, texture, all_uvs[4])
        arrow_texture = utils.parse_texture_with_uvs(self.data, texture, all_uvs[6])
        return {
            "Standard": {
                "u0": u0_texture.to_qpixmap(),
                "u1": u1_texture.to_qpixmap(),
                "d": d_texture.to_qpixmap(),
                "arrow": arrow_texture.to_qpixmap(),
            }
        }

    def _translate_asset(self, alias: str):
        return self.data.message("m/Name.bin.lz", True, alias)

    def _get_avatar_config(self):
        return FE15AvatarConfig()
