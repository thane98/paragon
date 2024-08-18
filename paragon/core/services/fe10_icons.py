import logging
from typing import Dict

from paragon.model.icons_model import IconsModel

from paragon.core.textures.texture import Texture

from paragon.core.services.icons import Icons


_AFFINITY_ICON_INDICES = {
    "heaven": 0,
    "telius": 1,
    "water": 2,
    "light": 3,
    "dark": 4,
    "fire": 5,
    "wind": 6,
    "thunder": 7,
}


class FE10Icons(Icons):
    def __init__(self, data, icon_mapping: Dict[str, int]):
        super().__init__(data)

        self.job_icon_mapping = icon_mapping

    def _load(self):
        try:
            textures = self.data.read_tpl_textures("window/icon.cms")
            main_icons, skill_icons = (
                Texture.from_core_texture(textures[0]),
                Texture.from_core_texture(textures[1]),
            )

            affinity_icons = main_icons.crop(0, 0, 192, 24).slice(24, 24)
            self.register("affinity", IconsModel(affinity_icons))

            item_icons = main_icons.crop(
                0, 96, main_icons.width, main_icons.height - 96
            ).slice(24, 24)
            self.register("item", IconsModel(item_icons))

            skill_icons = skill_icons.slice(32, 32)
            self.register("skill", IconsModel(skill_icons))
        except:
            logging.exception("Failed to load icons.")

    def to_row(self, rid, key):
        if key == "skill":
            return self.data.int(rid, "icon") - 1
        elif self.data.type_of(rid) == "Job":
            return self.job_icon_mapping.get(self.data.key(rid), 0)
        elif key == "item":
            return self.data.int(rid, "icon")
        elif key == "affinity":
            affinity_name = self.data.key(rid)
            return _AFFINITY_ICON_INDICES.get(affinity_name)
        else:
            return None
