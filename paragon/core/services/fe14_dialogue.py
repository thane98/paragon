import logging
import json
from typing import Dict, List, Tuple

from PySide2.QtGui import QPixmap

from paragon.core.services.dialogue import Dialogue
from paragon import paragon as pgn
from paragon.core.textures.texture import Texture
from paragon.core.services.portraits import Portraits


class FE14Dialogue(Dialogue):
    def __init__(self, game, config, data, portraits: Portraits, config_root: str):
        super().__init__(game, config, data, portraits, config_root)
        dialogue_animations_path = "resources/FE14/DialogueAnimations.json"
        try:
            with open(dialogue_animations_path, "r", encoding="utf-8") as f:
                self.dialogue_animations = json.load(f)
        except:
            logging.exception("Failed to load dialogue animations.")
            self.dialogue_animations = {}

    def _translate_asset(self, alias: str):
        if alias.startswith("MPID_マイユニ"):
            return self.config.fe14_avatar.name
        return self.data.message("m/GameData.bin.lz", True, alias)

    def _base_asset_translations(self) -> Dict[str, str]:
        try:
            table_rid, field_id = self.data.table("portraits")
            all_portraits = self.data.items(table_rid, field_id)
            translations = {"username": "username"}
            for rid in all_portraits:
                name_key = self.data.string(rid, "name")
                if name_key and name_key.startswith("MPID_"):
                    value = self.data.message("m/GameData.bin.lz", True, name_key)
                    if value:
                        value = value.replace(" ", "")
                    if value and value not in translations:
                        translations[value] = name_key[5:]
            return translations
        except:
            logging.exception("Failed to parse portrait name translations.")
            return {}

    def _load_backgrounds(self) -> List[Tuple[str, QPixmap]]:
        try:
            arc = self.data.read_arc("effect/Tlp_Ev_t001.arc.lz")
            if not arc or "model.bch" not in arc:
                return []
            else:
                res = []
                raw_texture = bytes(arc["model.bch"])
                bch_textures = pgn.read_bch(raw_texture)
                bg = Texture.from_core_texture(bch_textures[0])
                res.append(("Default", bg.to_qpixmap()))
                return res
        except:
            logging.exception("Failed to load dialogue backgrounds.")
            return []

    @staticmethod
    def _slice_window_texture(texture) -> Dict[str, QPixmap]:
        texture = Texture.from_core_texture(texture)
        talk_window = texture.crop(0, 0, 384, 56).to_qpixmap()
        talk_window_panicked = texture.crop(0, 56, 408, 72).to_qpixmap()
        talk_window_mini = texture.crop(0, 128, 200, 56).to_qpixmap()
        return {
            "talk_window": talk_window,
            "talk_window_panicked": talk_window_panicked,
            "talk_window_mini": talk_window_mini,
        }

    def _load_windows(self) -> Dict[str, Dict[str, QPixmap]]:
        core1 = self.data.read_bch_textures("ui/TalkWindow.bch.lz")["TalkWindow"]
        core2 = self.data.read_bch_textures("ui/TalkWindow2.bch.lz")["TalkWindow2"]
        core2 = Texture.from_core_texture(core2)
        name_plate = core2.crop(0, 0, 112, 24).to_qpixmap()
        arrow = core2.crop(112, 0, 16, 16).to_qpixmap()
        common_textures = {"name_plate": name_plate, "arrow": arrow}
        core1 = self._slice_window_texture(core1)
        core1.update(common_textures)
        res = {"Default / Revelation": core1}
        try:
            birthright = self.data.read_bch_textures("ui/TalkWindowW.bch.lz")[
                "TalkWindow"
            ]
            birthright = self._slice_window_texture(birthright)
            birthright.update(common_textures)
            res["Birthright"] = birthright
        except:
            logging.exception("Failed to load Birthright window textures.")
        try:
            conquest = self.data.read_bch_textures("ui/TalkWindowB.bch.lz")[
                "TalkWindow"
            ]
            conquest = self._slice_window_texture(conquest)
            conquest.update(common_textures)
            res["Conquest"] = conquest
        except:
            logging.exception("Failed to load Conquest window textures.")
        return res

    def _get_avatar_config(self):
        return self.config.fe14_avatar
