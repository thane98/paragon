import dataclasses

from PIL import Image
from PySide2.QtGui import QPixmap


@dataclasses.dataclass
class Texture:
    filename: str
    width: int
    height: int
    pixel_data: bytes

    @staticmethod
    def from_core_texture(core_texture):
        return Texture(
            filename=core_texture.filename,
            width=core_texture.width,
            height=core_texture.height,
            pixel_data=bytes(core_texture.pixel_data),
        )

    def to_pillow_image(self) -> Image:
        return Image.frombytes(
            "RGBA", (self.width, self.height), self.pixel_data, "raw", "RGBA"
        )

    @staticmethod
    def from_pillow_image(filename: str, image: Image) -> "Texture":
        width, height = image.size
        return Texture(
            filename=filename,
            width=width,
            height=height,
            pixel_data=image.tobytes()
        )

    def to_qpixmap(self) -> QPixmap:
        return self.to_pillow_image().toqpixmap()

    def crop(self, x, y, width, height) -> "Texture":
        img = self.to_pillow_image()
        raw_img = img.crop((x, y, x + width, y + height)).tobytes()
        return Texture(self.filename, width, height, raw_img)

    def slice(self, cell_width, cell_height):
        image = self.to_pillow_image()
        rows = self.height // cell_height
        columns = self.width // cell_width
        result = []
        for r in range(0, rows):
            for c in range(0, columns):
                x = c * cell_width
                y = r * cell_height
                cropped = image.crop(box=(x, y, x + cell_width, y + cell_height))
                result.append(cropped.toqpixmap())
        return result
