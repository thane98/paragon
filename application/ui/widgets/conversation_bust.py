from typing import Optional, Dict, List

from PIL import Image
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGraphicsPixmapItem, QGraphicsItemGroup

from model.texture import Texture
from services.fe14.portrait_service import FE14PortraitService
from services.service_locator import locator


class ConversationBust(QGraphicsItemGroup):
    def __init__(self, parent=None, left=False):
        super().__init__(parent)
        self._is_left = left
        self._portrait_textures: Optional[Dict[str, Texture]] = None
        self._normal_pixmap: Optional[QPixmap] = None
        self._faded_pixmap: Optional[QPixmap] = None
        self._blush_pixmap: Optional[QPixmap] = None
        self._faded_blush_pixmap: Optional[QPixmap] = None
        self._sweat_pixmap: Optional[QPixmap] = None
        self._faded_sweat_pixmap: Optional[QPixmap] = None

        self._portrait_view = QGraphicsPixmapItem()
        self._blush_view = QGraphicsPixmapItem()
        self._sweat_view = QGraphicsPixmapItem()
        self.addToGroup(self._portrait_view)
        self.addToGroup(self._blush_view)
        self.addToGroup(self._sweat_view)

    def clear(self):
        self._portrait_textures = None
        self._normal_pixmap = None
        self._faded_pixmap = None
        self._blush_pixmap = None
        self._faded_blush_pixmap = None
        self._sweat_pixmap = None
        self._faded_sweat_pixmap = None
        self._portrait_view.setPixmap(QPixmap())
        self._blush_view.setPixmap(QPixmap())
        self._sweat_view.setPixmap(QPixmap())

    def set_portraits(self, fid: str):
        self.clear()
        portrait_service: FE14PortraitService = locator.get_scoped("PortraitService")
        portraits = portrait_service.get_portraits_for_fid(fid, "st")
        if not portraits:
            return
        self._portrait_textures = portraits

        blush_and_sweat_coordinates = portrait_service.get_blush_and_sweat_coordinates(fid, "st")
        (blush_x, blush_y) = blush_and_sweat_coordinates[0]
        self._blush_view.setPos(blush_x, blush_y)
        (sweat_x, sweat_y) = blush_and_sweat_coordinates[1]
        self._sweat_view.setPos(sweat_x, sweat_y)

    def set_emotions(self, emotions: List[str]):
        if "照" in emotions:
            self.add_blush()
            emotions.remove("照")
        if "汗" in emotions:
            self.add_sweat()
            emotions.remove("汗")
        pixmap = self._get_pixmap_for_emotion(emotions[0])
        if pixmap:
            self._normal_pixmap = pixmap
            self._faded_pixmap = locator.get_scoped("ConversationService").fade_pixmap(pixmap)

    def add_blush(self):
        pixmap = self._get_pixmap_for_emotion("照")
        if pixmap:
            self._blush_pixmap = pixmap
            self._faded_blush_pixmap = locator.get_scoped("ConversationService").fade_pixmap(pixmap)

    def add_sweat(self):
        pixmap = self._get_pixmap_for_emotion("汗")
        if pixmap:
            self._sweat_pixmap = pixmap
            self._faded_sweat_pixmap = locator.get_scoped("ConversationService").fade_pixmap(pixmap)

    def _get_pixmap_for_emotion(self, emotion: str) -> Optional[QPixmap]:
        if not self._portrait_textures:
            raise ValueError
        if emotion not in self._portrait_textures:
            return None
        raw_image = self._portrait_textures[emotion].raw_image()
        if self._is_left:
            image = raw_image.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            image = raw_image
        return image.toqpixmap()

    def show_normal(self):
        if self._normal_pixmap:
            self._portrait_view.setPixmap(self._normal_pixmap)
            if self._blush_pixmap:
                self._blush_view.setPixmap(self._blush_pixmap)
            if self._sweat_pixmap:
                self._sweat_view.setPixmap(self._sweat_pixmap)

    def show_faded(self):
        if self._faded_pixmap:
            self._portrait_view.setPixmap(self._faded_pixmap)
            if self._faded_blush_pixmap:
                self._blush_view.setPixmap(self._faded_blush_pixmap)
            if self._faded_sweat_pixmap:
                self._sweat_view.setPixmap(self._faded_sweat_pixmap)
