from typing import Optional, Tuple

from PIL import Image
from PySide2.QtGui import QPixmap

from paragon.core.services.sprites import Sprites
from paragon.model.sprite_model import FE13SpriteModel, FE13FrameData, FE13AnimationData
from paragon import paragon as pgn
from paragon.core.textures.texture import Texture


class FE13Sprites(Sprites):
    def _person_to_identifier(self, rid) -> Optional[str]:
        return self.gd.key(rid)[4:]

    def _person_to_jobs(self, rid) -> Tuple[Optional[str], Optional[str]]:
        job = self.gd.rid(rid, "job")
        if not job:
            return None, None
        else:
            jid = self.gd.string(job, "jid")
            if not jid:
                return None, None
            else:
                fallback = jid
                jid = jid.replace("男", "")
                jid = jid.replace("女", "")
                return jid, fallback

    def _load(self, char, job, team, fallback_job=None) -> Optional[QPixmap]:
        # First, try the character-specific sprite.
        # If that fails, use the fallback job to load a generic sprite.
        # We need this because character-specific sprites don't use the
        # male/female suffix for some reason.
        try:
            raw = self.gd.read_file(f"map/unit/{job}{char}{team}.ctpk.lz")
            name = f"{job}{char}"
        except:
            raw = self.gd.read_file(f"map/unit/{fallback_job}{team}.ctpk.lz")
            name = f"{fallback_job}"

        # Parse the texture.
        textures = pgn.read_ctpk(bytes(raw))
        if textures:
            # Need to do some post-processing to get a single frame
            # and remove transparency.
            texture = next(iter(textures))

            animation_data, frame_width, frame_height = self._animation_data(name)
            return FE13SpriteModel(
                self.render(Texture.from_core_texture(texture)),
                name,
                team,
                frame_width,
                frame_height,
                animation_data
            )
        else:
            return None

    @staticmethod
    def _default(spritesheet: QPixmap, team: str) -> FE13SpriteModel:
        return FE13SpriteModel(
            spritesheet,
            None,
            team,
            None,
            None,
            None
        )

    @staticmethod
    def render(texture: Texture):
        raw = pgn.increase_alpha(texture.pixel_data)
        return Image.frombytes("RGBA", (texture.width, texture.height), raw, "raw", "RGBA").toqpixmap()

    def _animation_data(self, name) -> Tuple[list, int, int]:
        rid, bmap_icons = self.gd.table("bmap_icons")
        bmap_icon = self.gd.items(rid, bmap_icons)

        for bmap_icon_index in bmap_icon:
            if self.gd.string(bmap_icon_index, "name") == name:
                if frame_width := self.gd.int(bmap_icon_index, "frame_width"):
                    pass
                else:
                    frame_width = 32
                if frame_height := self.gd.int(bmap_icon_index, "frame_height"):
                    pass
                else:
                    frame_height = 32

                bmap_icon_data = self.gd.rid(bmap_icon_index, "pointer")
                animation_data = list()
                for bmap_icon_animation_data_index in range(1, 14):
                    bmap_icon_animation_data = self.gd.rid(bmap_icon_data, f"animation_data_{bmap_icon_animation_data_index}")
                    # Not all animation entries are used
                    if bmap_icon_animation_data:
                        frame_data = self.gd.items(bmap_icon_animation_data, "frame_data")

                        animation_data.append(
                            FE13AnimationData(
                                [
                                    FE13FrameData(
                                        (1000/60) * self.gd.int(frame_data_index, "frame_delay"),
                                        self.gd.int(frame_data_index, "frame_index_x"),
                                        self.gd.int(frame_data_index, "frame_index_y")
                                    ) for frame_data_index in frame_data
                                ]
                            )
                        )
                return animation_data, frame_width, frame_height