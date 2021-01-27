from typing import Dict

from PySide2.QtGui import QFont, QPixmap
from PySide2.QtWidgets import QGraphicsScene

from paragon.core.services.portraits import Portraits
from paragon.model.dialogue_snapshot import DialogueSnapshot


class DialogueRenderer:
    def render(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service,
        snapshot: DialogueSnapshot,
    ):
        raise NotImplementedError
