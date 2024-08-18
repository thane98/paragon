from typing import Dict, List, Tuple

from PySide6.QtGui import QPixmap

from paragon.core.services.dialogue import Dialogue


class FE9Dialogue(Dialogue):
    def _translate_asset(self, alias: str):
        return alias

    def _base_asset_translations(self) -> Dict[str, str]:
        return {}

    def _load_backgrounds(self) -> List[Tuple[str, QPixmap]]:
        pass

    def _load_windows(self) -> Dict[str, Dict[str, QPixmap]]:
        pass

    def _get_avatar_config(self):
        return None
