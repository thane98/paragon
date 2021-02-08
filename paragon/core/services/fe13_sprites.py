from typing import Optional

from PIL import Image
from PySide2.QtGui import QPixmap

from paragon.core.services.sprites import Sprites
from paragon import paragon as pgn
from paragon.core.textures.texture import Texture


class FE13Sprites(Sprites):
    def _load(self, char, job, team, fallback_job=None) -> Optional[QPixmap]:
        # First, try the character-specific sprite.
        # If that fails, use the fallback job to load a generic sprite.
        # We need this because character-specific sprites don't use the
        # male/female suffix for some reason.
        try:
            raw = self.gd.read_file(f"map/unit/{job}{char}{team}.ctpk.lz")
        except:
            raw = self.gd.read_file(f"map/unit/{fallback_job}.ctpk.lz")

        # Parse the texture.
        textures = pgn.read_ctpk(bytes(raw))
        if textures:
            # Need to do some post-processing to get a single frame
            # and remove transparency.
            texture = next(iter(textures))
            return self.render(Texture.from_core_texture(texture))
        else:
            return None

    @staticmethod
    def render(texture: Texture):
        frame = texture.crop(0, 0, 32, 32)
        raw = pgn.increase_alpha(frame.pixel_data)
        return Image.frombytes("RGBA", (32, 32), raw, "raw", "RGBA").toqpixmap()
