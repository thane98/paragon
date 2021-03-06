from typing import Dict

from PySide2 import QtGui
from PySide2.QtGui import QPixmap, QColor, QTextBlockFormat, QTextCursor
from PySide2.QtWidgets import QGraphicsScene

from paragon.model.dialogue_snapshot import DialogueSnapshot
from paragon.ui.renderers.dialogue_renderer import DialogueRenderer
from paragon.ui.controllers.sprite_item import SceneSpriteItem


def _has_top(snapshot):
    return snapshot.top_speaker() and snapshot.top_text().strip()


def _has_bottom(snapshot):
    return snapshot.bottom_speaker() and snapshot.bottom_text().strip()


def _active_is_top(snapshot):
    active = snapshot.active_speaker()
    return active.is_top() if active else False


def _active_is_bottom(snapshot):
    active = snapshot.active_speaker()
    return active.is_bottom() if active else False


def _center(item):
    block_format = QTextBlockFormat()
    block_format.setAlignment(QtGui.Qt.AlignCenter)
    cursor = item.textCursor()
    cursor.select(QTextCursor.Document)
    cursor.mergeBlockFormat(block_format)
    cursor.clearSelection()
    item.setTextCursor(cursor)


class SOVMiniDialogueRenderer(DialogueRenderer):
    def render(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service,
        sprite_animation_svc,
        snapshot: DialogueSnapshot,
    ):
        draw_top = _has_top(snapshot)
        draw_bottom = _has_bottom(snapshot)

        # Draw the bottom window and decoration.
        if draw_bottom:
            u0 = scene.addPixmap(textures["u0"])
            u0.setY(151)
            if _active_is_bottom(snapshot):
                arrow = SceneSpriteItem(textures["arrow"], "arrow", service, sprite_animation_svc)
                scene.addItem(arrow)

                arrow.setPos(367, 211)

        # Draw the top window and decoration.
        if draw_top:
            scene.addPixmap(textures["u1"])
            if _active_is_top(snapshot):
                arrow = SceneSpriteItem(textures["arrow"], "arrow", service, sprite_animation_svc)
                scene.addItem(arrow)

                arrow.setPos(367, 41)

        # Render portraits.
        for speaker in snapshot.speakers:
            if speaker.is_anonymous():
                continue

            # Render the portrait.
            pixmap = service.render(speaker, "TK", True)

            # Translate the portrait to the appropriate position.
            if speaker.position == 0:
                if draw_top:
                    bust = scene.addPixmap(pixmap)
                    bust.setPos(8, 9)
            elif speaker.position == 6:
                if draw_bottom:
                    bust = scene.addPixmap(pixmap)
                    bust.setPos(8, 180)
            else:
                raise NotImplementedError(
                    f"Position {speaker.position} is not supported by this renderer."
                )

        # Draw the actual text.
        font = service.font()
        top_text = snapshot.top_text()
        bottom_text = snapshot.bottom_text()
        if bottom_text:
            text = scene.addText(bottom_text, font)
            text.setDefaultTextColor(QColor.fromRgba(0xFFF2F1CE))
            text.setPos(72, 185)
        if top_text:
            text = scene.addText(top_text, font)
            text.setDefaultTextColor(QColor.fromRgba(0xFFF2F1CE))
            text.setPos(72, 15)

        # Draw the nameplate.
        # This works by centering the text within a rectangle.
        top_name, bottom_name = service.speaker_names(snapshot)
        if bottom_name and draw_bottom:
            name = scene.addText(bottom_name, font)
            name.setDefaultTextColor(QColor.fromRgba(0xFFF2F1CE))
            name.setTextWidth(110)
            name.setPos(14, 157)
            _center(name)
        if top_name and draw_top:
            name = scene.addText(top_name, font)
            name.setDefaultTextColor(QColor.fromRgba(0xFFF2F1CE))
            name.setTextWidth(110)
            name.setPos(14, 59)
            _center(name)