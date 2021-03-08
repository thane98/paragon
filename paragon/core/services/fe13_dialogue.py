import logging
from typing import Dict, List, Tuple

from PySide2.QtGui import QPixmap

from paragon.core.services.dialogue import Dialogue


class FE13Dialogue(Dialogue):
    def _translate_asset(self, alias: str):
        if "マイユニ" in alias or "プレイヤー" in alias:
            return self._get_avatar_config().name
        return self.data.message("m/GameData.bin.lz", True, alias)

    def _base_asset_translations(self) -> Dict[str, str]:
        try:
            table_rid, field_id = self.data.table("portraits")
            all_portraits = self.data.items(table_rid, field_id)
            avatar_asset = (
                ""
                if not self._get_avatar_config().portraits
                else self._get_avatar_config().portraits.replace("FID_", "")
            )
            translations = {"username": avatar_asset}
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
        return [("Default", QPixmap("resources/awakening/SupportBG.png"))]

    def _load_windows(self) -> Dict[str, Dict[str, QPixmap]]:
        # Awakening textures aren't stored in a convenient format.
        # Easier to use the resources from Fire Emblem Conversation Editor.
        # All credit to SecretiveCactus for these.
        return {
            "Standard": {
                "NameBox": QPixmap("resources/awakening/NameBox.png"),
                "TextBox": QPixmap("resources/awakening/TextBox.png"),
            }
        }

    def _get_avatar_config(self):
        return self.config.fe13_avatar
