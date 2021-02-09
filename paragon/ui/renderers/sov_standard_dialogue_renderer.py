from typing import Dict

from PySide2 import QtGui
from PySide2.QtGui import QPixmap, QColor, QTextBlockFormat, QTextCursor, QPainter
from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PySide2.QtCore import QPoint, QTimer, QRectF

from paragon.model.dialogue_snapshot import DialogueSnapshot
from paragon.ui.renderers.dialogue_renderer import DialogueRenderer


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
        arrow.animation_on(2)
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
        self._timer = QTimer()
        self._draw_pos = QPoint(0, 0)
        self._timer.timeout.connect(self._next_draw_pos)
        self._is_looping = False

        self.sprite = sprite


    def animation_on(self, frames):
        # Game runs @30 FPS, so half frame count b/c that's 60fps
        """Animate frames"""
        self._timer.start((1000/30) * frames)

    def is_animating(self) -> bool:
        return self._timer.isActive()

    def animation_off(self):
        """Draw static frame"""
        self._timer.stop()

    def boundingRect(self) -> QRectF:
        return QRectF(
            0, 
            0, 
            self.sprite.width(), 
            self.sprite.height()
        )

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        painter.drawPixmap(
            self._draw_pos.x(),
            self._draw_pos.y(), 
            self.sprite, 
            0, 
            0, 
            self.sprite.width(), 
            self.sprite.height()
        )

    def _next_draw_pos(self):
        if not self._is_looping:
            if self._draw_pos.y() == 0:
                self._draw_pos.setY(self._draw_pos.y() - 1)
                self.animation_on(2)
            elif  -3 < self._draw_pos.y() < 0:
                self._draw_pos.setY(self._draw_pos.y() - 1)
                self.animation_on(2)
                if self._draw_pos.y() == -3:
                    self.animation_on(4)
            elif self._draw_pos.y() == -3:
                self._draw_pos.setY(self._draw_pos.y() - 1)
                self.animation_on(2)
                self._is_looping = True
        elif self._is_looping:
            if self._draw_pos.y() == 0:
                self._draw_pos.setY(self._draw_pos.y() - 1)
                self.animation_on(2)
                self._is_looping = False
            elif self._draw_pos.y() < 0:
                self._draw_pos.setY(self._draw_pos.y() + 1)
                if self._draw_pos.y() == 0:
                    self.animation_on(4)

        self.update(
            0,
            0,
            self.sprite.width(),
            self.sprite.height()
        )
