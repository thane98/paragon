import logging
import traceback
from typing import Optional, Tuple

from PySide2.QtGui import QPixmap
from paragon.model.sprite import SpriteModel


class Sprites:
    def __init__(self, gd):
        self.gd = gd

        self.defaults = {
            "緑": QPixmap("resources/misc/allied.png"),
            "赤": QPixmap("resources/misc/enemy.png"),
            "青": QPixmap("resources/misc/player.png"),
            "紫": QPixmap("resources/misc/vallite.png"),
        }
        self.team_names = ["青", "赤", "緑", "紫"]

    def from_spawn(self, spawn, person_key=None, animation=0) -> Optional[SpriteModel]:
        team = 0
        try:
            team = self.gd.int(spawn, "team")
            pid = self.gd.string(spawn, "pid")
            if not pid:
                return self.default(team, animation=animation)
            person = self._to_character(pid, person_key)
            if person and self.is_vallite(person):
                team = 3
            job, fallback = self._get_jobs(pid, person_key)
            if not job:
                return self.default(team, animation=animation)
            else:
                char = self.person_to_identifier(person)
                job = job.replace("JID_", "")
                if fallback:
                    fallback = fallback.replace("JID_", "")
                return self.load(
                    char, job, team, fallback_job=fallback, animation=animation
                )
        except:
            logging.exception("Failed to read sprite from spawn.")
            return self.default(team, animation=animation)

    def load(
        self, char, job, team, fallback_job=None, animation=0
    ) -> Optional[SpriteModel]:
        try:
            team_name = self.team_name(team)
            if team_name:
                if sprite := self._load(
                    char, job, team_name, fallback_job=fallback_job, animation=animation
                ):
                    return sprite
                else:
                    return self.default(team, animation=animation)
        except:
            logging.exception(
                f"Failed to load sprite char={char}, job={job}, team={team}"
            )
            return self.default(team, animation=animation)

    def default(self, team: int, animation=0) -> Optional[SpriteModel]:
        team_name = self.team_name(team)
        return (
            self._default(self.defaults[team_name], animation=animation, team=team_name)
            if team_name in self.defaults
            else None
        )

    def _get_jobs(self, pid, person_key=None) -> Tuple[Optional[str], Optional[str]]:
        if person := self._to_character(pid, person_key):
            return self._person_to_jobs(person)
        else:
            return None, None

    def _to_character(self, pid, person_key=None) -> Optional[int]:
        if person_key:
            rid = self.gd.multi_open("person", person_key)
            if rid:
                if char_rid := self.gd.list_key_to_rid(rid, "people", pid):
                    return char_rid
        return self.gd.key_to_rid("characters", pid)

    def person_to_identifier(self, rid) -> Optional[str]:
        raise NotImplementedError

    def _person_to_jobs(self, rid) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError

    def _load(self, char, job, team, fallback_job=None) -> Optional[QPixmap]:
        raise NotImplementedError

    # Need to fix return type
    def _default(self, spritesheet: QPixmap):
        raise NotImplementedError

    def team_name(self, team_number: int) -> Optional[str]:
        if team_number in range(0, len(self.defaults)):
            return self.team_names[team_number]
        else:
            return None

    def is_vallite(self, person):
        return False
