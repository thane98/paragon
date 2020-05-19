from PIL import Image, ImageQt


class Texture:
    def __init__(self, raw_texture):
        self._filename: str = raw_texture.get_filename()
        self._width: int = raw_texture.get_width()
        self._height: int = raw_texture.get_height()
        self._pixel_format: int = raw_texture.get_pixel_format()
        self._image = self._convert_raw_pixel_data_to_image(raw_texture.get_pixel_data())

    def _convert_raw_pixel_data_to_image(self, pixel_data: bytes) -> Image:
        image = Image.frombytes(
            "RGBA",
            (self._width, self._height),
            pixel_data,
            "raw",
            "RGBA"
        )
        return image

    def filename(self) -> str:
        return self._filename

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    def raw_image(self) -> Image:
        return self._image

    def image(self) -> ImageQt:
        return self._image.toqimage()

    def pixel_format(self) -> int:
        return self._pixel_format
