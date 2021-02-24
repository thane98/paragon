import logging
from typing import Optional, Tuple

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

    # Need to fix return type
    def from_spawn(self, spawn, person_key=None) -> Optional[QPixmap]:
        team = 0
        try:
            team = self.gd.int(spawn, "team")
            pid = self.gd.string(spawn, "pid")
            job, fallback = self._get_jobs(pid, person_key)
            if not job:
                return self.default(team)
            else:
                pid = pid[4:] if pid and pid.startswith("PID_") else pid
                job = job[4:] if job.startswith("JID_") else job
                fallback = (
                    fallback[4:]
                    if fallback and fallback.startswith("JID_")
                    else fallback
                )
                return self.load(pid, job, team, fallback_job=fallback)
        except:
            logging.exception("Failed to read sprite from spawn.")
            return self.default(team)

    # Need to fix return type
    def load(self, char, job, team, fallback_job=None) -> Optional[QPixmap]:
        try:
            team_name = self.team_name(team)
            if team_name:
                if sprite := self._load(
                    char, job, team_name, fallback_job=fallback_job
                ):
                    return sprite
                else:
                    return self.default(team)
        except:
            logging.exception(
                f"Failed to load sprite char={char}, job={job}, team={team}"
            )
            return self.default(team)

        # Need to fix return type
    def default(self, team: int) -> Optional[QPixmap]:
        team_name = self.team_name(team)
        return self._default(self.defaults[team_name], team_name) if team_name in self.defaults else None

    def _get_jobs(self, pid, person_key=None) -> Tuple[Optional[str], Optional[str]]:
        job = None
        fallback = None
        if person_key:
            job, fallback = self._person_to_jobs(pid, person_key)
        if not job:
            job, fallback = self._static_character_to_jobs(pid)
        return job, fallback

    def _person_to_jobs(self, pid, person_key) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError

    def _static_character_to_jobs(self, pid) -> Tuple[Optional[str], Optional[str]]:
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