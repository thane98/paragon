from typing import Optional, Tuple

from PIL import Image
from PySide2.QtGui import QPixmap

from paragon.core.services.sprites import Sprites
from paragon import paragon as pgn
from paragon.core.textures.texture import Texture


class FE13Sprites(Sprites):
    def _person_to_jobs(self, pid, person_key) -> Tuple[Optional[str], Optional[str]]:
        rid = self.gd.multi_open("person", person_key)
        if rid:
            return self._parse_jobs(rid, "people", pid)
        else:
            return None, None

    def _static_character_to_jobs(self, pid) -> Tuple[Optional[str], Optional[str]]:
        rid, field_id = self.gd.table("characters")
        return self._parse_jobs(rid, field_id, pid)

    def _parse_jobs(self, rid, field_id, pid) -> Tuple[Optional[str], Optional[str]]:
        # Get the character.
        char_rid = self.gd.list_key_to_rid(rid, field_id, pid)
        if not char_rid:
            return None, None

        # Get the job.
        job = self.gd.rid(char_rid, "job")
        if not job:
            return None, None
        else:
            jid = self.gd.key(job)
            if not jid:
                return None, None
            else:
                jid = jid.replace("JID_", "")
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
