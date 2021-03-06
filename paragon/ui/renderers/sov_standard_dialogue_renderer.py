from typing import Dict

from PySide2 import QtGui
from PySide2.QtGui import QPixmap, QColor, QTextBlockFormat, QTextCursor
from PySide2.QtWidgets import QGraphicsScene

from paragon.model.dialogue_snapshot import DialogueSnapshot
from paragon.ui.renderers.dialogue_renderer import DialogueRenderer
from paragon.ui.controllers.sprite_item import SceneSpriteItem

class SOVStandardDialogueRenderer(DialogueRenderer):
    def render(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service,
        sprite_animation_svc,
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
        arrow = SceneSpriteItem(textures["arrow"], "arrow", service, sprite_animation_svc)
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