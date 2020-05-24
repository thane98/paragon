from typing import Optional, Dict, List

from PIL import Image
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGraphicsPixmapItem, QGraphicsItemGroup

from model.texture import Texture
from services.service_locator import locator


class ConversationBust(QGraphicsItemGroup):
    def __init__(self, parent=None, left=False):
        super().__init__(parent)
        self._is_left = left
        self._portrait_textures: Optional[Dict[str, Texture]] = None

        self._portrait_image: Optional[Image] = None
        self._blush_image: Optional[Image] = None
        self._sweat_image: Optional[Image] = None

        self._blush_x = None
        self._blush_y = None
        self._sweat_x = None
        self._sweat_y = None

        self._portrait_view = QGraphicsPixmapItem()
        self.addToGroup(self._portrait_view)

    def clear(self):
        self._portrait_textures = None
        self._portrait_image = None
        self._blush_image = None
        self._sweat_image = None
        self._blush_x = None
        self._blush_y = None
        self._sweat_x = None
        self._sweat_y = None
        self._portrait_view.setPixmap(QPixmap())

    def set_portraits(self, fid: str):
        self.clear()
        conversation_service = locator.get_scoped("ConversationService")
        portraits = conversation_service.get_portraits_for_fid(fid)
        self._portrait_textures = portraits
        blush_and_sweat_coordinates = conversation_service.get_blush_and_sweat_coordinates(fid, "st")
        if blush_and_sweat_coordinates:
            (self._blush_x, self._blush_y) = blush_and_sweat_coordinates[0]
            (self._sweat_x, self._sweat_y) = blush_and_sweat_coordinates[1]

    def set_emotions(self, emotions: List[str]):
        emotions = emotions.copy()
        if "照" in emotions:
            self.add_blush()
            emotions.remove("照")
        if "汗" in emotions:
            self.add_sweat()
            emotions.remove("汗")
        if emotions:
            self._portrait_image = self._get_image_for_emotion(emotions[0])

    def add_blush(self):
        self._blush_image = self._get_image_for_emotion("照")

    def add_sweat(self):
        self._sweat_image = self._get_image_for_emotion("汗")

    def _get_image_for_emotion(self, emotion: str):
        if not self._portrait_textures:
            return None
        if emotion not in self._portrait_textures:
            return None
        return self._portrait_textures[emotion].raw_image()

    def show_normal(self):
        self._portrait_view.setPixmap(self._assemble_image())

    def show_faded(self):
        self._portrait_view.setPixmap(self._assemble_image(faded=True))

    def _assemble_image(self, faded=False) -> QPixmap:
        if not self._portrait_image:
            return QPixmap()
        image: Image.Image = self._portrait_image.copy()
        if self._blush_image:
            image.paste(self._blush_image, (self._blush_x, self._blush_y), self._blush_image)
        if self._sweat_image:
            image.paste(self._sweat_image, (self._sweat_x, self._sweat_y), self._sweat_image)
        if faded:
            image = locator.get_scoped("ConversationService").fade_image(image)
        if self._is_left:
            return image.transpose(Image.FLIP_LEFT_RIGHT).toqpixmap()
        else:
            return image.toqpixmap()
