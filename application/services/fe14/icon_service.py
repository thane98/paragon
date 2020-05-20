from typing import Optional, Dict, List

from PySide2.QtGui import QIcon, QPixmap

from model.texture import Texture
from module.properties.property_container import PropertyContainer
from services.service_locator import locator

_SKILL_ICON_ID_KEY = "Icon ID"
_SKILL_ICON_DIMENSIONS = (24, 24)
_SKILL_TEXTURE_KEY = "skill"
_ITEM_ICON_ID_KEY = "Item Icon"
_ITEM_ICON_DIMENSIONS = (16, 16)
_ITEM_TEXTURE_KEY = "item"


class FE14IconService:
    def __init__(self):
        self._loaded = False
        self._skill_icons: List[QIcon] = []
        self._item_icons: List[QIcon] = []

    def _load_icons(self):
        if self._loaded:
            return
        self._loaded = True
        assets_service = locator.get_scoped("AssetsService")
        icons: Optional[Dict[str, Texture]] = assets_service.load_bch("/icon/Icon.bch.lz")
        if not icons:
            return

        if _SKILL_TEXTURE_KEY in icons:
            skill_icons_texture = icons[_SKILL_TEXTURE_KEY]
            icon_width, icon_height = _SKILL_ICON_DIMENSIONS
            self._skill_icons = self._slice(skill_icons_texture, icon_width, icon_height)
        if _ITEM_TEXTURE_KEY in icons:
            item_icons_texture = icons[_ITEM_TEXTURE_KEY]
            icon_width, icon_height = _ITEM_ICON_DIMENSIONS
            self._item_icons = self._slice(item_icons_texture, icon_width, icon_height)
            print("Loaded items!")

    @staticmethod
    def _slice(texture: Texture, cell_width, cell_height) -> List[QIcon]:
        pixmap = QPixmap.fromImage(texture.image())
        cells_per_row = texture.width() // cell_width
        cells_per_column = texture.height() // cell_height
        result = []
        for r in range(0, cells_per_column):
            for c in range(0, cells_per_row):
                x = c * cell_width
                y = r * cell_height
                if x + cell_width > texture.width() or y + cell_height > texture.height():
                    continue
                section = pixmap.copy(x, y, cell_width, cell_height)
                result.append(QIcon(section))
        return result

    def get_icon_by_type(self, entry: PropertyContainer, entry_type: str):
        if entry_type == "skill":
            return self.get_icon_for_skill(entry)
        elif entry_type == "item":
            return self.get_icon_for_item(entry)
        return None

    def get_icon_for_skill(self, skill: PropertyContainer) -> Optional[QIcon]:
        self._load_icons()
        skill_id = skill[_SKILL_ICON_ID_KEY].value
        if not skill_id or skill_id not in range(0, len(self._skill_icons)):
            return None
        return self._skill_icons[skill_id]

    def get_icon_for_item(self, item: PropertyContainer) -> Optional[QIcon]:
        self._load_icons()
        item_id = item[_ITEM_ICON_ID_KEY].value
        if not item_id or item_id not in range(0, len(self._item_icons)):
            return None
        return self._item_icons[item_id]
