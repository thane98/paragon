from typing import Dict

from PySide2 import QtGui
from PySide2.QtGui import QPixmap, QColor, QTextBlockFormat, QTextCursor, QTransform
from PySide2.QtWidgets import QGraphicsScene

from paragon.model.dialogue_snapshot import DialogueSnapshot
from paragon.ui.renderers.dialogue_renderer import DialogueRenderer


class FatesStandardDialogueRenderer(DialogueRenderer):
    def render(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service,
        snapshot: DialogueSnapshot,
    ):
        # Render portraits first so the window and text paint on top of them.
        for speaker in snapshot.speakers:
            if speaker.is_anonymous():
                continue

            # Render the portrait.
            active = speaker.name == snapshot.active
            pixmap = service.render(speaker, "ST", active)

            # Translate the portrait to the appropriate position.
            if speaker.position == 0 or speaker.position == 3:
                pixmap = pixmap.transformed(QTransform().scale(-1, 1))
                bust = scene.addPixmap(pixmap)
                bust.setX(-30)
            elif speaker.position == 5:
                pixmap = pixmap.transformed(QTransform().scale(-1, 1))
                bust = scene.addPixmap(pixmap)
                bust.setX(72)
            elif speaker.position == 6 or speaker.position == 7:
                bust = scene.addPixmap(pixmap)
                bust.setX(174)
            else:
                raise NotImplementedError(
                    f"Position {speaker.position} is not supported by this renderer."
                )

        position = snapshot.active_speaker().position

        # Draw the window and decorations.
        if snapshot.panicked:
            text_box = scene.addPixmap(textures["talk_window_panicked"])
            text_box.setPos(-4, 180)
        else:
            text_box = scene.addPixmap(textures["talk_window"])
            text_box.setPos(9, 187)
        arrow = scene.addPixmap(textures["arrow"])
        arrow.setPos(367, 214)

        # Draw the actual text.
        font = service.font()
        if position == 0:
            display_text = snapshot.top_text()
        else:
            display_text = snapshot.bottom_text()
        text = scene.addText(display_text, font)
        text.setDefaultTextColor(QColor.fromRgba(0xFF440400))
        text.setPos(38, 194)

        # Draw the nameplate.
        # This works by centering the text within a rectangle.

        speaker_names = service.speaker_names(snapshot)
        speaker_name = speaker_names[0] if position == 0 else speaker_names[1]
        if speaker_name:
            name_box = scene.addPixmap(textures["name_plate"])
            name = scene.addText(speaker_name, font)
            name.setDefaultTextColor(QColor.fromRgba(0xFFFFFFB3))
            name.setTextWidth(112)

            if position == 0 or position == 3 or position == 5:
                name_box.setPos(7, 170)
                name.setPos(7, 170)
            else:
                name_box.setPos(281, 170)
                name.setPos(281, 170)

            # Center the name text.
            block_format = QTextBlockFormat()
            block_format.setAlignment(QtGui.Qt.AlignCenter)
            cursor = name.textCursor()
            cursor.select(QTextCursor.Document)
            cursor.mergeBlockFormat(block_format)
            cursor.clearSelection()
            name.setTextCursor(cursor)
