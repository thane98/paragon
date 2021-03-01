import logging
import os
from typing import Optional, Tuple, List

from PIL import Image
from PySide2.QtGui import QPixmap
from paragon import paragon as pgn
from paragon.core.services.sprites import Sprites
from paragon.core.textures.texture import Texture
from paragon.model.sprite import FE14SpriteModel, FE14FrameData, AnimationData


class FE14Sprites(Sprites):
    def _person_to_identifier(self, rid) -> Optional[str]:
        # TODO: Customize avatar?
        pid = self.gd.key(rid)
        if pid == "PID_プレイヤー男":
            return "プレイヤー男1_01"
        elif pid == "PID_プレイヤー女":
            return "プレイヤー女1_01"

        aid = self.gd.string(rid, "aid")
        if aid:
            return aid[4:]
        else:
            job, _ = self._person_to_jobs(rid)
            return job[4:] if job else None

    def _person_to_jobs(self, rid) -> Tuple[Optional[str], Optional[str]]:
        job = self.gd.rid(rid, "class_1")
        if not job:
            return None, None
        else:
            jid = self.gd.key(job)
            if not jid:
                return None, None
            else:
                return jid, jid

    def _load(self, char, job, team, fallback_job=None) -> Optional[QPixmap]:
        # Try to load the unique sprite
        try:
            sprite_filename = team + "0.bch.lz"

            # Check for a unique sprite.
            path = os.path.join("unit", "Unique", f"{job}_{char}")
            path_2 = os.path.join("unit", "Unique", f"{job}_{job}")
            anime_path = os.path.join(path, "anime.bin")
            anime_path_2 = os.path.join(path_2, "anime.bin")
            if self.gd.file_exists(anime_path, False):
                # Found a unique sprite. Load it!
                image_path = os.path.join(path, sprite_filename)
                return self._load_unique_sprite(image_path)
            elif self.gd.file_exists(anime_path_2, False):
                # Found a unique sprite. Load it!
                image_path = os.path.join(path_2, sprite_filename)
                return self._load_unique_sprite(image_path)

            # Extract data for building the sprite from its components.
            body_path = os.path.join("unit", "Body", job)
            anime_path = os.path.join(body_path, "anime.bin")
            rid = self.gd.multi_open("sprite_data", anime_path)
            sprite_data = self.get_all_sprite_data(rid)

            # Load by stitching together body and head sprites.
            body_filename = os.path.join(body_path, sprite_filename)
            head_path = os.path.join("unit", "Head", char)
            head_filename = os.path.join(head_path, sprite_filename)
            return self._load_standard_sprite(sprite_data, body_filename, head_filename)
        except:
            logging.exception("Failed to load sprite.")
            raise

    def is_vallite(self, person):
        army = self.gd.rid(person, "army")
        if not army:
            return None
        else:
            key = self.gd.key(army)
            return key == "BID_謎の軍" or key == "BID_透魔王国軍"

    def get_all_sprite_data(self, rid) -> List[List[AnimationData]]:
        animations = self.gd.items(rid, "animations")
        res = []
        for rid in animations:
            if not self.gd.bool(rid, "is_used"):
                continue
            else:
                frames = []
                frame_count = self.gd.int(rid, "frame_count")
                for i in range(0, frame_count):
                    frame = self.gd.list_get(rid, "frames", i)
                    frames.append(self._load_animation_data(frame))
                res.append(frames)
        return res

    def _load_animation_data(self, rid) -> FE14FrameData:
        return FE14FrameData(
            body_draw_x=self.gd.int(rid, "body_draw_offset_x"),
            body_draw_y=self.gd.int(rid, "body_draw_offset_y"),
            body_width=self.gd.int(rid, "body_width"),
            body_height=self.gd.int(rid, "body_height"),
            body_source_x=self.gd.int(rid, "body_source_position_x"),
            body_source_y=self.gd.int(rid, "body_source_position_y"),
            head_draw_x=self.gd.int(rid, "head_draw_offset_x"),
            head_draw_y=self.gd.int(rid, "head_draw_offset_y"),
            head_width=self.gd.int(rid, "head_width"),
            head_height=self.gd.int(rid, "head_height"),
            head_source_x=self.gd.int(rid, "head_source_position_x"),
            head_source_y=self.gd.int(rid, "head_source_position_y"),
            frame_delay=self.gd.int(rid, "frame_delay")
        )

    def _load_unique_sprite(self, path: str) -> Optional[QPixmap]:
        image = self.gd.read_bch_textures(path)
        image = Texture.from_core_texture(list(image.values())[0])
        frame = image.to_pillow_image().rotate(90, expand=True).crop((32, 0, 64, 32))
        raw = pgn.increase_alpha(frame.tobytes())
        return Image.frombytes("RGBA", (32, 32), raw, "raw", "RGBA").toqpixmap()

    def _load_standard_sprite(
        self,
        data: List[List[AnimationData]],
        body_path: str,
        head_path: str
    ) -> Optional[QPixmap]:
        body_image = self.gd.read_bch_textures(body_path)
        body_image = Texture.from_core_texture(list(body_image.values())[0])
        body_image = body_image.to_pillow_image().rotate(90, expand=True)
        head_image = self.gd.read_bch_textures(head_path)
        head_image = Texture.from_core_texture(list(head_image.values())[0])
        head_image = head_image.to_pillow_image().rotate(90, expand=True)

        head_tmp = Image.new("RGBA", (body_image.width, body_image.height), (0, 0, 0, 0))

        for frame in data[0]:
            head_paste_x = frame.body_source_x + frame.head_offset_x
            head_paste_y = frame.body_source_y + frame.head_offset_y
            left = frame.head_source_x
            upper = frame.head_source_y
            right = left + frame.head_width
            lower = upper + frame.head_height
            section = head_image.crop((left, upper, right, lower))
            head_tmp.paste(section, (head_paste_x, head_paste_y))
        raw = pgn.merge_images_and_increase_alpha(head_tmp.tobytes(), body_image.tobytes())
        image = Image.frombytes("RGBA", (body_image.width, body_image.height), raw, "raw", "RGBA")
        return image.crop((32, 0, 64, 32)).toqpixmap()
