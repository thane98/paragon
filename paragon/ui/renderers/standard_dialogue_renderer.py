from typing import Dict

from PySide2 import QtGui
from PySide2.QtGui import QPixmap, QTransform, QTextBlockFormat, QTextCursor, QFontMetrics
from PySide2.QtWidgets import QGraphicsScene

from paragon.model.dialogue_snapshot import DialogueSnapshot
from paragon.ui.renderers import renderer_utils
from paragon.ui.renderers.dialogue_renderer import DialogueRenderer


class StandardDialogueRenderer(DialogueRenderer):
    def render(self, scene: QGraphicsScene, textures: Dict[str, QPixmap], service, sprite_animation_svc,
               snapshot: DialogueSnapshot):
        self._render_speakers(snapshot, scene, service)
        self._render_text_box(scene, textures, service, sprite_animation_svc, snapshot)
        self._render_text(scene, service, snapshot)
        self._render_name_box(scene, textures, service, snapshot)

    def _render_speakers(self, snapshot: DialogueSnapshot, scene: QGraphicsScene, service):
        for speaker in snapshot.speakers:
            if speaker.is_anonymous():
                continue

            # Render the portrait.
            active = speaker.name == snapshot.active
            pixmap = service.render(speaker, self.standard_portrait_mode(), active)

            # Translate the portrait to the appropriate position.
            position = speaker.position
            if position in self.left_speaker_positions():
                if not speaker.flipped:
                    pixmap = self._flip_portrait(pixmap)
                bust = scene.addPixmap(pixmap)
                bust.setX(self.left_speaker_x())
            elif position in self.center_speaker_positions():
                pixmap = self._flip_portrait(pixmap)
                bust = scene.addPixmap(pixmap)
                bust.setX(self.center_speaker_x())
            elif position in self.right_speaker_positions():
                if speaker.flipped:
                    pixmap = self._flip_portrait(pixmap)
                bust = scene.addPixmap(pixmap)
                bust.setX(self.right_speaker_x())
            else:
                raise NotImplementedError(
                    f"Position {speaker.position} is not supported by this renderer."
                )

    def _render_text_box(
        self,
        scene: QGraphicsScene,
        textures: Dict[str, QPixmap],
        service,
        sprite_animation_svc,
        snapshot: DialogueSnapshot,
    ):
        raise NotImplementedError

    def _render_text(
        self,
        scene: QGraphicsScene,
        service,
        snapshot: DialogueSnapshot,
    ):
        position = snapshot.active_speaker().position
        font = service.font()
        if position == 0:
            display_text = snapshot.top_text()
        else:
            display_text = snapshot.bottom_text()
        lines = display_text.split("\n")
        for i in range(0, min(len(lines), 2)):
            trimmed_text = renderer_utils.trim_to_width(lines[i], font, self.trim_width())
            text = scene.addText(trimmed_text, font)
            text.setDefaultTextColor(self.text_color())
            text.setPos(self.text_x(), self.text_y() + i * QFontMetrics(font).height())

    def _render_name_box(self, scene: QGraphicsScene, textures: Dict[str, QPixmap], service,
                         snapshot: DialogueSnapshot):
        font = service.font()
        position = snapshot.active_speaker().position
        speaker_names = service.speaker_names(snapshot)
        speaker_name = speaker_names[0] if position == 0 else speaker_names[1]
        if speaker_name:
            # Create the items
            name_box = scene.addPixmap(textures[self.name_box_texture()])
            name = scene.addText(speaker_name, font)
            name.setDefaultTextColor(self.name_box_text_color())
            name.setTextWidth(self.name_box_width())

            # Translate to the appropriate position
            if position in self.left_speaker_positions() or position in self.center_speaker_positions():
                name_box.setPos(self.left_name_box_x(), self.left_name_box_y())
                name.setPos(self.left_name_box_x(), self.left_name_box_y())
            else:
                name_box.setPos(self.right_name_box_x(), self.right_name_box_y())
                name.setPos(self.right_name_box_x(), self.right_name_box_y())

            # Center the name text.
            block_format = QTextBlockFormat()
            block_format.setAlignment(QtGui.Qt.AlignCenter)
            cursor = name.textCursor()
            cursor.select(QTextCursor.Document)
            cursor.mergeBlockFormat(block_format)
            cursor.clearSelection()
            name.setTextCursor(cursor)

    def trim_width(self):
        return 312

    def text_x(self):
        raise NotImplementedError

    def text_y(self):
        raise NotImplementedError

    def text_color(self):
        raise NotImplementedError

    def name_box_text_color(self):
        raise NotImplementedError

    def standard_portrait_mode(self):
        raise NotImplementedError

    def name_box_texture(self):
        raise NotImplementedError

    def name_box_width(self):
        raise NotImplementedError

    def left_speaker_x(self):
        return -30

    def center_speaker_x(self):
        return 72

    def right_speaker_x(self):
        return 174

    def left_name_box_x(self):
        raise NotImplementedError

    def left_name_box_y(self):
        raise NotImplementedError

    def right_name_box_x(self):
        raise NotImplementedError

    def right_name_box_y(self):
        raise NotImplementedError

    def left_speaker_positions(self):
        return [0, 3]

    def center_speaker_positions(self):
        return [5]

    def right_speaker_positions(self):
        return [6, 7]

    @staticmethod
    def _flip_portrait(pixmap):
        return pixmap.transformed(QTransform().scale(-1, 1))
