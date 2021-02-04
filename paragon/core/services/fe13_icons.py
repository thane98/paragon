import logging

from paragon.model.icons_model import IconsModel

from paragon.core.services.icons import Icons
from paragon.core.textures.texture import Texture


class FE13Icons(Icons):
    def _try_load_texture(self):
        # Assuming this is localized, we need the texture with
        # the correct prefix.
        # Don't really *need* these to be localized though since
        # we aren't using icons with noticeable text differences.
        paths = {
            "systems/icon.ctpk.lz",
            "systems/icon_E.ctpk.lz",
            "systems/icon_U.ctpk.lz",
            "systems/icon_S.ctpk.lz",
            "systems/icon_F.ctpk.lz",
            "systems/icon_G.ctpk.lz",
            "systems/icon_i.ctpk.lz",
        }
        for path in paths:
            try:
                return self.data.read_ctpk_textures(path)
            except:
                pass
        return None

    def _load(self):
        try:
            textures = self._try_load_texture()
            item_texture = Texture.from_core_texture(textures["item.tga"])
            skill_texture = Texture.from_core_texture(textures["skill.tga"])

            item_icons = item_texture.slice(16, 16)
            self.register("item", IconsModel(item_icons))

            skill_icons = skill_texture.slice(24, 24)
            self.register("skill", IconsModel(skill_icons))
        except:
            logging.exception("Failed to load icons.")

    def to_row(self, rid, key):
        if key in {"item", "skill"}:
            return self.data.int(rid, "icon")
        else:
            return None
