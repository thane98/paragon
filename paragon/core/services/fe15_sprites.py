import logging
import os
from typing import Optional, Tuple, List

from PIL import Image
from PySide6.QtGui import QPixmap
from paragon import paragon as pgn
from paragon.core.services.sprites import Sprites
from paragon.core.textures.texture import Texture
from paragon.model.sprite import FE15SpriteModel, FE15FrameData, AnimationData


class FE15Sprites(Sprites):
    def person_to_identifier(self, rid) -> Optional[str]:
        aid = self.gd.string(rid, "aid")
        if aid:
            return aid[4:]
        else:
            job, _ = self._person_to_jobs(rid)
            return job[4:] if job else None

    def _person_to_jobs(self, rid) -> Tuple[Optional[str], Optional[str]]:
        job = self.gd.rid(rid, "job")
        if not job:
            return None, None
        else:
            jid = self.gd.key(job)
            if not jid:
                return None, None
            else:
                return jid, jid

    def _load(
        self, char, job, team, fallback_job=None, animation=0
    ) -> Optional[FE15SpriteModel]:
        # Try to load the unique sprite
        try:
            sprite_filename = team + "1.bch.lz" if animation else team + "0.bch.lz"

            if job == "不明":
                return self._load_dummy_sprite(animation=animation, team=team)

            job_rid = self.gd.key_to_rid("jobs", "JID_" + job)
            job_aid = self.gd.string(job_rid, "aid") if job_rid else None
            aid = job_aid[4:] if job_aid else job

            # Check for a unique sprite.
            path = os.path.join("unit", "Unique", f"{aid}_{char}")
            path_2 = os.path.join("unit", "Unique", f"{aid}_{aid}")
            anime_path = os.path.join(path, "anime.bin")
            anime_path_2 = os.path.join(path_2, "anime.bin")
            if self.gd.file_exists(anime_path, False):
                # Found a unique sprite. Load it!
                image_path = os.path.join(path, sprite_filename)
                rid = self.gd.multi_open("sprite_data", anime_path)
                return FE15SpriteModel(
                    self._load_unique_sprite(image_path),
                    self._load_animation_data(rid, animation=animation),
                    team,
                )
            elif self.gd.file_exists(anime_path_2, False):
                # Found a unique sprite. Load it!
                image_path = os.path.join(path_2, sprite_filename)
                rid = self.gd.multi_open("sprite_data", anime_path_2)
                return FE15SpriteModel(
                    self._load_unique_sprite(image_path),
                    self._load_animation_data(rid, animation=animation),
                    team,
                )

            # Extract data for building the sprite from its components.
            body_path = os.path.join("unit", "Body", aid)
            anime_path = os.path.join(body_path, "anime.bin")
            rid = self.gd.multi_open("sprite_data", anime_path)
            sprite_data = self._load_animation_data(rid, animation=animation)

            # Load by stitching together body and head sprites.
            body_filename = os.path.join(body_path, sprite_filename)
            if char:
                head_path = os.path.join("unit", "Head", char)
                head_filename = os.path.join(head_path, sprite_filename)

                if not self.gd.file_exists(head_filename, False):
                    head_path = os.path.join("unit", "Head", aid)
                    head_filename = os.path.join(head_path, sprite_filename)
            else:
                head_path = os.path.join("unit", "Head", aid)
                head_filename = os.path.join(head_path, sprite_filename)

            return FE15SpriteModel(
                self._load_standard_sprite(sprite_data, body_filename, head_filename),
                sprite_data,
                team,
            )
        except:
            logging.exception("Failed to load sprite.")
            raise

    def _load_animation_data(self, rid, animation=0) -> List[AnimationData]:
        animations = self.gd.items(rid, "animations")
        animation_data = []
        for rid in animations:
            if self.gd.bool(rid, "is_used"):
                frame_count = self.gd.int(rid, "frame_count")

                animation_data.append(
                    AnimationData(
                        [
                            self._load_frame_data(self.gd.list_get(rid, "frames", i))
                            for i in range(0, frame_count)
                            if self.gd.int(
                                self.gd.list_get(rid, "frames", i), "frame_delay"
                            )
                        ]
                    )
                )
                if not animation:
                    break
        return animation_data

    def _load_frame_data(self, rid) -> FE15FrameData:
        return FE15FrameData(
            body_offset_x=self.gd.int(rid, "body_draw_offset_x"),
            body_offset_y=self.gd.int(rid, "body_draw_offset_y"),
            body_width=self.gd.int(rid, "body_width"),
            body_height=self.gd.int(rid, "body_height"),
            body_source_x=self.gd.int(rid, "body_source_position_x"),
            body_source_y=self.gd.int(rid, "body_source_position_y"),
            head_offset_x=self.gd.int(rid, "head_draw_offset_x"),
            head_offset_y=self.gd.int(rid, "head_draw_offset_y"),
            head_width=self.gd.int(rid, "head_width"),
            head_height=self.gd.int(rid, "head_height"),
            head_source_x=self.gd.int(rid, "head_source_position_x"),
            head_source_y=self.gd.int(rid, "head_source_position_y"),
            frame_delay=self.gd.int(rid, "frame_delay") * 1000 / 60,
        )

    def _load_dummy_sprite(self, animation=0, team=None) -> Optional[FE15SpriteModel]:
        sprite_filename = team + "1.bch.lz" if animation else team + "0.bch.lz"
        # Dummy sprite
        dummy_path = os.path.join("unit", "Unique", "ダミー_ダミー")
        dummy_anime_path = os.path.join(dummy_path, "anime.bin")

        if self.gd.file_exists(dummy_anime_path, False):
            image_path = os.path.join(dummy_path, sprite_filename)
            rid = self.gd.multi_open("sprite_data", dummy_anime_path)
            return FE15SpriteModel(
                self._load_unique_sprite(image_path),
                self._load_animation_data(rid, animation=animation),
                team,
            )
        else:
            return None

    def _default(self, spritesheet: QPixmap, animation=0, team=None) -> FE15SpriteModel:
        # Load Dummy
        if sprite := self._load_dummy_sprite(animation=animation, team=team):
            return sprite
        else:
            return FE15SpriteModel(spritesheet, None, team)

    def _load_unique_sprite(self, path: str) -> Optional[QPixmap]:
        image = self.gd.read_bch_textures(path)
        image = Texture.from_core_texture(list(image.values())[0])
        frame = image.to_pillow_image().rotate(90, expand=True)
        raw = pgn.increase_alpha(frame.tobytes())
        return Image.frombytes(
            "RGBA", (frame.width, frame.height), raw, "raw", "RGBA"
        ).toqpixmap()

    def _load_standard_sprite(
        self, data: List[AnimationData], body_path: str, head_path: str
    ) -> Optional[QPixmap]:
        body_image = self.gd.read_bch_textures(body_path)
        body_image = Texture.from_core_texture(list(body_image.values())[0])
        body_image = body_image.to_pillow_image().rotate(90, expand=True)
        head_image = self.gd.read_bch_textures(head_path)
        head_image = Texture.from_core_texture(list(head_image.values())[0])
        head_image = head_image.to_pillow_image().rotate(90, expand=True)

        head_tmp = Image.new(
            "RGBA", (body_image.width, body_image.height), (0, 0, 0, 0)
        )

        for animation_data in data:
            for frame_data in animation_data.frame_data:
                head_paste_x = frame_data.body_source_x + frame_data.head_offset_x
                head_paste_y = frame_data.body_source_y + frame_data.head_offset_y
                left = frame_data.head_source_x
                upper = frame_data.head_source_y
                right = left + frame_data.head_width
                lower = upper + frame_data.head_height
                section = head_image.crop((left, upper, right, lower))
                head_tmp.paste(section, (head_paste_x, head_paste_y))
        raw = pgn.merge_images_and_increase_alpha(
            head_tmp.tobytes(), body_image.tobytes()
        )
        image = Image.frombytes(
            "RGBA", (body_image.width, body_image.height), raw, "raw", "RGBA"
        )
        return image.toqpixmap()
