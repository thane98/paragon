from typing import Optional, Dict

from PIL import Image
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGraphicsPixmapItem

from model.texture import Texture
from module.properties.property_container import PropertyContainer
from services.fe14.portrait_service import FE14PortraitService
from services.service_locator import locator


class ConversationBust(QGraphicsPixmapItem):
    def __init__(self, parent=None, left=False):
        super().__init__(parent)
        self._is_left = left
        self._character: Optional[PropertyContainer] = None
        self._portrait_textures: Optional[Dict[str, Texture]] = None
        self._normal_pixmap: Optional[QPixmap] = None
        self._faded_pixmap: Optional[QPixmap] = None

    def clear(self):
        self._character = None
        self._portrait_textures = None
        self._normal_pixmap = None
        self._faded_pixmap = None
        self.setPixmap(QPixmap())

    def set_character(self, character: PropertyContainer):
        self.clear()
        portrait_service: FE14PortraitService = locator.get_scoped("PortraitService")
        portraits = portrait_service.get_portraits_for_character(character, "st")
        if not portraits:
            return
        self._character = character
        self._portrait_textures = portraits

    def set_emotion(self, emotion: str):
        if not self._character or not self._portrait_textures:
            raise ValueError
        if emotion not in self._portrait_textures:
            return
        raw_image = self._portrait_textures[emotion].raw_image()
        if self._is_left:
            image = raw_image.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            image = raw_image
        self._normal_pixmap = image.toqpixmap()
        self._faded_pixmap = locator.get_scoped("ConversationService").fade_pixmap(self._normal_pixmap)

    def show_normal(self):
        if not self._normal_pixmap:
            raise ValueError
        self.setPixmap(self._normal_pixmap)
        self.setVisible(True)

    def show_faded(self):
        if not self._faded_pixmap:
            raise ValueError
        self.setPixmap(self._faded_pixmap)
        self.setVisible(True)
