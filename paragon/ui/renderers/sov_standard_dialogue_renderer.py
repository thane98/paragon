from typing import Dict

from PySide2 import QtGui
from PySide2.QtGui import QPixmap, QColor, QTextBlockFormat, QTextCursor, QPainter
from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PySide2.QtCore import QPoint, QTimer, QRectF, QDateTime

from paragon.model.dialogue_snapshot import DialogueSnapshot
from paragon.ui.renderers.dialogue_renderer import DialogueRenderer

import json

class SOVStandardDialogueRenderer(DialogueRenderer):
    def render(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service,
        snapshot: DialogueSnapshot,
    ):
        # Render portraits first so the window and text paint on top of them.
        for speaker in snapshot.speakers:
            # This position shows on the bottom screen.
            # Not supported in the previewer currently.
            if speaker.position == "h" or speaker.is_anonymous():
                continue

            # Render the portrait.
            active = speaker.name == snapshot.active
            pixmap = service.render(speaker, "BU", active)
            bust = scene.addPixmap(pixmap)

            # Translate the portrait to the appropriate position.
            if speaker.position == 3:
                bust.setX(-30)
            elif speaker.position == 5:
                bust.setX(72)
            elif speaker.position == 7:
                bust.setX(174)
            else:
                raise NotImplementedError(
                    f"Position {speaker.position} is not supported by this renderer."
                )

        # Draw the window and decorations.
        u0 = scene.addPixmap(textures["u0"])
        u0.setY(151)
        arrow = AnimationSpriteItem(textures["arrow"])
        scene.addItem(arrow)
        arrow.setPos(367, 211)

        # Draw the actual text.
        font = service.font()
        display_text = snapshot.bottom_text()
        text = scene.addText(display_text, font)
        text.setDefaultTextColor(QColor.fromRgba(0xFFF2F1CE))
        text.setPos(30, 185)

        # Draw the nameplate.
        # This works by centering the text within a rectangle.
        speaker_name = service.speaker_names(snapshot)[1]
        name = scene.addText(speaker_name, font)
        name.setDefaultTextColor(QColor.fromRgba(0xFFF2F1CE))
        name.setTextWidth(110)
        name.setPos(14, 157)
        block_format = QTextBlockFormat()
        block_format.setAlignment(QtGui.Qt.AlignCenter)
        cursor = name.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_format)
        cursor.clearSelection()
        name.setTextCursor(cursor)


class AnimationSpriteItem(QGraphicsItem):
    """Spritesheet widget"""
    def __init__(self, sprite: QPixmap):
        super(AnimationSpriteItem, self).__init__()

        # TODO: Call from svc
        dialogue_animations_path = "resources/shadows_of_valentia/DialogueAnimations.json"
        # try:
        with open(dialogue_animations_path, "r", encoding="utf-8") as f:
            self.dialogue_animations = json.load(f)
        # except:
        #     logging.exception("Failed to load dialogue animations.")
        #     self.dialogue_animations = {}

        self._timer = QTimer()
        self.current_frame = QPoint(0, 0)
        self._timer.timeout.connect(self.next_frame)
        self._is_looping = False
        self.frame_index = 0
        self.sprite = sprite
        self._timer.start(1000/30)

        for obj in self.dialogue_animations:
            if obj["texture"] == "arrow":
                self.sprite_data = obj
                break

        self.activated = QDateTime().currentMSecsSinceEpoch()

    def boundingRect(self) -> QRectF:
        return QRectF(
            0, 
            0, 
            self.sprite.width(), 
            self.sprite.height()
        )

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        painter.drawPixmap(
            self.current_frame.x(),
            self.current_frame.y(), 
            self.sprite, 
            0, 
            0, 
            self.sprite.width(), 
            self.sprite.height()
        )

    def next_frame(self):
        current_time = QDateTime().currentMSecsSinceEpoch()
        if (current_time - self.activated)/(1000/60 * self.sprite_data["animation_data"][self.frame_index]["frame_delay"]) > 1:
            self.activated = current_time
            
            if self.frame_index < len(self.sprite_data["animation_data"]) - 1:
                self.frame_index += 1
            else:
                self.frame_index = 0

            self.current_frame.setX(
                self.sprite_data["animation_data"][self.frame_index]["draw_position_x"]
            )
            self.current_frame.setY(
                self.sprite_data["animation_data"][self.frame_index]["draw_position_y"]
            )

        self.update(
            0,
            0,
            self.sprite.width(),
            self.sprite.height()
        )
