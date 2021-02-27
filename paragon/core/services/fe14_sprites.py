from typing import Optional, Tuple

from PySide2.QtGui import QPixmap

from paragon.core.services.sprites import Sprites
from paragon.model.relevant_sprite_data import RelevantSpriteData


class FE14Sprites(Sprites):
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
        job = self.gd.rid(char_rid, "class_1")
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
            pass
        except:
            pass

    def _load_unique_sprite(self, data: RelevantSpriteData, raw_sprite: bytes) -> Optional[QPixmap]:
        pass

    def _load_standard_sprite(self, data: RelevantSpriteData, raw_body: bytes, raw_head: bytes) -> Optional[QPixmap]:
        pass
