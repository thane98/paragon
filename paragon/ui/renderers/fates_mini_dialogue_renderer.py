from typing import Dict

from PySide2 import QtGui
from PySide2.QtGui import QPixmap, QColor, QTextBlockFormat, QTextCursor, QTransform
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


class FatesMiniDialogueRenderer(DialogueRenderer):
    def render(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service,
        sprite_animation_svc,
        snapshot: DialogueSnapshot,
    ):
        # Yes, these are flipped from the snapshot.
        # Fates and SoV flip where portraits show up - the snapshots use SoV terms.
        draw_top = _has_bottom(snapshot)
        draw_bottom = _has_top(snapshot)
        bottom_text = snapshot.top_text()
        top_text = snapshot.bottom_text()
        bottom_name, top_name = service.speaker_names(snapshot)
        active_is_bottom = _active_is_top(snapshot)
        active_is_top = not active_is_bottom

        # Draw the bottom window and decoration.
        if draw_bottom:
            if snapshot.panicked:
                window = scene.addPixmap(textures["talk_window_panicked"])
                window.setPos(-4, 180)
            else:
                window = scene.addPixmap(textures["talk_window"])
                window.setPos(9, 187)
            if active_is_bottom:
                arrow = SceneSpriteItem(
                    textures["arrow"], "arrow", service, sprite_animation_svc
                )
                scene.addItem(arrow)
                arrow.setPos(367, 215)

        # Draw the top window and decoration.
        if draw_top:
            if snapshot.panicked:
                window = scene.addPixmap(textures["talk_window_panicked"])
                window.setPos(-4, -9)
            else:
                window = scene.addPixmap(textures["talk_window"])
                window.setPos(9, -2)
            if active_is_top:
                arrow = SceneSpriteItem(
                    textures["arrow"], "arrow", service, sprite_animation_svc
                )
                scene.addItem(arrow)
                arrow.setPos(367, 24)

        # Render portraits.
        for speaker in snapshot.speakers:
            if speaker.is_anonymous():
                continue

            # Render the portrait.
            pixmap = service.render(speaker, "BU", True)
            pixmap = pixmap.transformed(QTransform().scale(-1, 1))

            # Translate the portrait to the appropriate position.
            if speaker.position == 6:
                if draw_top:
                    bust = scene.addPixmap(pixmap)
                    bust.setPos(11, 0)
            elif speaker.position == 0 or speaker.position == 2:
                if draw_bottom:
                    bust = scene.addPixmap(pixmap)
                    bust.setPos(11, 190)
            else:
                raise NotImplementedError(
                    f"Position {speaker.position} is not supported by this renderer."
                )

        # Draw the actual text.
        font = service.font()
        if bottom_text:
            text = scene.addText(bottom_text, font)
            text.setDefaultTextColor(QColor.fromRgba(0xFF440400))
            text.setPos(85, 194)
        if top_text:
            text = scene.addText(top_text, font)
            text.setDefaultTextColor(QColor.fromRgba(0xFF440400))
            text.setPos(85, 4)

        # Draw the nameplate.
        # This works by centering the text within a rectangle.
        if bottom_name and draw_bottom:
            name_plate = scene.addPixmap(textures["name_plate"])
            name_plate.setPos(7, 170)
            name = scene.addText(bottom_name, font)
            name.setDefaultTextColor(QColor.fromRgba(0xFFFFFFB3))
            name.setTextWidth(110)
            name.setPos(7, 170)
            _center(name)
        if top_name and draw_top:
            name_plate = scene.addPixmap(textures["name_plate"])
            name_plate.setPos(7, 46)
            name = scene.addText(top_name, font)
            name.setDefaultTextColor(QColor.fromRgba(0xFFFFFFB3))
            name.setTextWidth(110)
            name.setPos(7, 46)
            _center(name)
