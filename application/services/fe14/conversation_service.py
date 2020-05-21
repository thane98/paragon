import io

from PIL import Image, ImageEnhance
from PySide2.QtCore import QBuffer
from PySide2.QtGui import QPixmap

from core.loaders.fe14_conversation_assets_loader import FE14ConversationAssetsLoader


class ConversationService:
    def __init__(self):
        self.asset_loader = FE14ConversationAssetsLoader()
        self._talk_windows = None
        self._background = None

    @staticmethod
    def fade_pixmap(image: QPixmap):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        image.save(buffer, "PNG")

        pillow_image = Image.open(io.BytesIO(buffer.data()))
        enhancer = ImageEnhance.Brightness(pillow_image)
        return QPixmap.fromImage(enhancer.enhance(0.3).toqimage())

    def talk_windows(self):
        if not self._talk_windows:
            self._talk_windows = self.asset_loader.load_talk_windows()
        return self._talk_windows

    def background(self):
        if not self._background:
            self._background = self.asset_loader.load_background()
        return self._background
