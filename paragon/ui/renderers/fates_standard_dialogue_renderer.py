from typing import Dict

from PySide2.QtGui import QPixmap, QColor
from PySide2.QtWidgets import QGraphicsScene

from paragon.model.dialogue_snapshot import DialogueSnapshot
from paragon.ui.controllers.sprite_item import SceneSpriteItem
from paragon.ui.renderers.standard_dialogue_renderer import StandardDialogueRenderer


class FatesStandardDialogueRenderer(StandardDialogueRenderer):
    def _render_text_box(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service,
        sprite_animation_svc,
        snapshot: DialogueSnapshot,
    ):
        if snapshot.panicked:
            text_box = scene.addPixmap(textures["talk_window_panicked"])
            text_box.setPos(-4, 180)
        else:
            text_box = scene.addPixmap(textures["talk_window"])
            text_box.setPos(9, 187)
        self.arrow = SceneSpriteItem(
            textures["arrow"], "arrow", service, sprite_animation_svc
        )
        scene.addItem(self.arrow)
        self.arrow.setPos(367, 215)

    def text_x(self):
        return 38

    def text_y(self):
        return 194

    def text_color(self):
        return QColor.fromRgba(0xFF440400)

    def name_box_text_color(self):
        return QColor.fromRgba(0xFFFFFFB3)

    def standard_portrait_mode(self):
        return "ST"

    def name_box_texture(self):
        return "name_plate"

    def name_box_width(self):
        return 112

    def left_name_box_x(self):
        return 7

    def left_name_box_y(self):
        return 170

    def right_name_box_x(self):
        return 281

    def right_name_box_y(self):
        return 170
