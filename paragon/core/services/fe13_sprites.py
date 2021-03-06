import functools
from typing import Optional, Tuple, List

from PIL import Image
from PySide2.QtGui import QPixmap

from paragon.core.services.sprites import Sprites
from paragon.model.sprite import FE13SpriteModel, FE13FrameData, AnimationData, SpriteModel
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
            bmap_icon_rid = self.gd.rid(job, "bmap_icon")
            bmap_icon_name = self.gd.string(bmap_icon_rid, "name")
            if not bmap_icon_name:
                return None, None
            else:
                fallback = bmap_icon_name
                bmap_icon_name = bmap_icon_name[:-1]
                return bmap_icon_name, fallback

    def from_spawn(self, spawn, person_key=None, animation=0) -> Optional[SpriteModel]:
        try:
            team = self.gd.int(spawn, "team")
            pid = self.gd.string(spawn, "pid")
            person = self._to_character(pid, person_key)
            if person and self.is_vallite(person):
                team = 3
            job, fallback = self._get_jobs(pid, person_key)
            if not job:
                return self.default(team)
            else:
                char = self._person_to_identifier(person)
                job = job.replace("JID_", "")
                if fallback:
                    fallback = fallback.replace("JID_", "")
                return self.load(char, job, team, fallback_job=fallback)
        except:
            logging.exception("Failed to read sprite from spawn.")
            return self.default(team)

    def _load(self, char, job, team, fallback_job=None, animation=0) -> Optional[FE13SpriteModel]:
        # First, try the character-specific sprite.
        # If that fails, use the fallback job to load a generic sprite.
        # We need this because character-specific sprites don't use the
        # male/female suffix for some reason.
        path1 = f"map/unit/{job}{char}{team}.ctpk.lz"
        path2 = f"map/unit/{fallback_job}{team}.ctpk.lz"
        if self.gd.file_exists(path1, False):
            path = path1
            key = f"{job}{char}"
        elif self.gd.file_exists(path2, False):
            path = path2
            key = f"{fallback_job}"
        else:
            return None
        return self._load_file(key, path, team)

    def _load_file(self, key, path, team):
        raw = self.gd.read_file(path)

        # Parse the texture.
        textures = pgn.read_ctpk(bytes(raw))
        if textures:
            # Need to do some post-processing to get a single frame
            # and remove transparency.
            texture = next(iter(textures))

            animation_data, frame_width, frame_height = self._load_animation_data(key)
            return FE13SpriteModel(
                self.render(Texture.from_core_texture(texture)),
                key,
                team,
                frame_width,
                frame_height,
                animation_data
            )
        else:
            return None

    @staticmethod
    def _default(spritesheet: QPixmap, animation=0, team=None) -> FE13SpriteModel:
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

    def _load_animation_data(self, name) -> Tuple[List[AnimationData], int, int]:
        bmap_icon_index = self.gd.key_to_rid("bmap_icons", name)

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
                    AnimationData(
                        [
                            FE13FrameData(
                                (1000 / 60) * self.gd.int(frame_data_index, "frame_delay"),
                                self.gd.int(frame_data_index, "frame_index_x"),
                                self.gd.int(frame_data_index, "frame_index_y")
                            ) for frame_data_index in frame_data
                        ]
                    )
                )
        return animation_data, frame_width, frame_height
