from typing import Dict

from PySide2.QtGui import QPixmap, QColor
from PySide2.QtWidgets import QGraphicsScene

from paragon.model.dialogue_snapshot import DialogueSnapshot
from paragon.ui.renderers.standard_dialogue_renderer import StandardDialogueRenderer


class AwakeningStandardDialogueRenderer(StandardDialogueRenderer):
    def _render_text_box(self, scene: QGraphicsScene, textures: Dict[str, QPixmap], service, sprite_animation_svc,
                         snapshot: DialogueSnapshot):
        text_box = scene.addPixmap(textures["TextBox"])
        text_box.setPos(10, 176)

    def text_x(self):
        return 30

    def text_y(self):
        return 185

    def text_color(self):
        return QColor.fromRgba(0xFF440400)

    def name_box_text_color(self):
        return QColor.fromRgba(0xFFFFFFB3)

    def standard_portrait_mode(self):
        return "BU"

    def name_box_texture(self):
        return "NameBox"

    def name_box_width(self):
        return 112

    def left_name_box_x(self):
        return 24

    def left_name_box_y(self):
        return 160

    def right_name_box_x(self):
        return 264

    def right_name_box_y(self):
        return 160
