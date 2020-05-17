from PIL import Image
from PySide2.QtGui import QImage

from core.etc1a4 import decompress_etc1a4


class Texture:
    def __init__(self, raw_texture):
        self._filename: str = raw_texture.get_filename()
        self._width: int = raw_texture.get_width()
        self._height: int = raw_texture.get_height()
        self._image = self._convert_raw_pixel_data_to_image(raw_texture.get_pixel_data())

    def _convert_raw_pixel_data_to_image(self, pixel_data: bytes) -> QImage:
        decompressed_pixel_data = decompress_etc1a4(pixel_data, self._height, self._width)
        image = Image.frombytes(
            "RGBA",
            (self._width, self._height),
            decompressed_pixel_data,
            "raw",
            "RGBA"
        )
        return image.toqimage()

    def filename(self) -> str:
        return self._filename

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    def image(self) -> QImage:
        return self._image
