from typing import Optional

from PySide6.QtGui import QPixmap, QTransform

from paragon.core.services.icons import Icons


class GcnSprites:
    def __init__(self, gd, icons: Icons):
        self.gd = gd
        self.icons = icons

        self.defaults = [
            QPixmap("resources/misc/player.png"),
            QPixmap("resources/misc/enemy.png"),
            QPixmap("resources/misc/allied.png"),
        ]

    def from_spawn(self, spawn) -> Optional[QPixmap]:
        team = self.gd.int(spawn, "team")
        job = self.gd.rid(spawn, "class")
        if job:
            icon = self.icons.icon(job)
            if icon:
                if team == 1:
                    return icon.transformed(QTransform().scale(-1, 1))
                return icon
        team = self.gd.int(spawn, "team")
        if team < len(self.defaults):
            return self.defaults[team]
