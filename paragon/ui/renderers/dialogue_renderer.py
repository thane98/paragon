from typing import Dict

from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QGraphicsScene

from paragon.model.dialogue_snapshot import DialogueSnapshot


class DialogueRenderer:
    def render(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service,
        sprite_animation_svc,
        snapshot: DialogueSnapshot,
    ):
        raise NotImplementedError
