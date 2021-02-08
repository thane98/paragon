import logging
from typing import Optional

from PySide2.QtGui import QPixmap


class Sprites:
    def __init__(self, gd):
        self.gd = gd

        self.defaults = {
            "緑": QPixmap("resources/misc/allied.png"),
            "赤": QPixmap("resources/misc/enemy.png"),
            "青": QPixmap("resources/misc/player.png"),
        }
        self.team_names = ["青", "赤", "緑"]

    def load(self, char, job, team, fallback_job=None) -> Optional[QPixmap]:
        try:
            team_name = self.team_name(team)
            if team_name:
                if sprite := self._load(char, job, team_name, fallback_job=fallback_job):
                    return sprite
                else:
                    return self.default(team)
        except:
            logging.exception(f"Failed to load sprite char={char}, job={job}, team={team}")
            return self.default(team)

    def _load(self, char, job, team, fallback_job=None) -> Optional[QPixmap]:
        raise NotImplementedError

    def default(self, team: int) -> Optional[QPixmap]:
        name = self.team_name(team)
        return self.defaults[name] if name in self.defaults else None

    def team_name(self, team_number: int) -> Optional[str]:
        if team_number in range(0, len(self.defaults)):
            return self.team_names[team_number]
        else:
            return None

