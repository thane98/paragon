import logging
from typing import List, Dict

from paragon.model.icons_model import IconsModel

from paragon.core.services.icons import Icons
from paragon.core.textures.texture import Texture


class FE14Icons(Icons):
    def __init__(self, data):
        super().__init__(data)
        self.belong_teams = []

    def _load(self):
        try:
            textures = self.data.read_bch_textures("icon/Icon.bch.lz")
            textures = {k: Texture.from_core_texture(v) for k, v in textures.items()}
            self._load_items(textures)
            self._load_skills(textures)
            self._load_belongs(textures)
        except:
            logging.exception("Failed to load icons.")

    def _load_items(self, textures: Dict[str, Texture]):
        try:
            icons = textures["item"].slice(16, 16)
            self.register("item", IconsModel(icons))
        except:
            logging.exception("Failed to load item icons")

    def _load_skills(self, textures: Dict[str, Texture]):
        try:
            skill_icons = textures["skill"].slice(24, 24)
            skill_icons.extend(textures["skill2"].slice(24, 24))
            self.register("skill", IconsModel(skill_icons))
        except:
            logging.exception("Failed to load item icons")

    def _load_belongs(self, textures: Dict[str, Texture]):
        try:
            belong_texture = textures["belong"].crop(0, 0, 200, 120)
            icons = belong_texture.slice(40, 40)
            self.register("belong", IconsModel(icons))
        except:
            logging.exception("Failed to load belong icons")

    def to_row(self, rid, key):
        if key in {"item", "skill", "belong"}:
            return self.data.int(rid, "icon")
        else:
            return None
