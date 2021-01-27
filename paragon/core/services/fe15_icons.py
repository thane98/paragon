import logging

from paragon.core.services import utils
from paragon.model.icons_model import IconsModel
from paragon.core.textures.texture import Texture
from paragon.core.services.icons import Icons


class FE15Icons(Icons):
    def _load(self):
        try:
            uv_file_rid = self.data.multi_open("uvs", "ui/mat/Icon.bin.lz")
            uvs = self.data.items(uv_file_rid, "uvs")
            textures = self.data.read_bch_textures("ui/mat/Icon.bch.lz")
            texture = Texture.from_core_texture(list(textures.values())[0])
            self._load_items(uvs, texture)
            self._load_skills(uvs, texture)
            self._load_belongs(uvs, texture)
        except:
            logging.exception("Failed to load icons.")

    def _load_items(self, uvs, texture):
        item_big_rid = next(
            filter(lambda rid: self.data.key(rid) == "IconItemBig", uvs), None
        )
        if not item_big_rid:
            return
        self._parse_and_register(item_big_rid, 24, 24, "item_big", texture)

    def _load_skills(self, uvs, texture):
        skills_rid = next(
            filter(lambda rid: self.data.key(rid) == "IconSkill", uvs), None
        )
        if not skills_rid:
            return
        self._parse_and_register(skills_rid, 16, 16, "skill", texture)

    def _load_belongs(self, uvs, texture):
        belongs_rid = next(
            filter(lambda rid: self.data.key(rid) == "IconSymbol", uvs), None
        )
        if not belongs_rid:
            return
        self._parse_and_register(belongs_rid, 36, 36, "belong", texture)

    def _parse_and_register(self, uvs_rid, icon_width, icon_height, model_id, texture):
        cropped = utils.parse_texture_with_uvs(self.data, texture, uvs_rid)
        icons = cropped.slice(icon_width, icon_height)
        self.register(model_id, IconsModel(icons))

    def to_row(self, rid, key):
        if key in {"item_big", "skill"}:
            return self.data.int(rid, "icon")
        elif key == "belong":
            value = self.data.int(rid, "icon")
            return value - 1 if value else None
        else:
            return None
