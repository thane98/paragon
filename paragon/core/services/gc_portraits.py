import logging
from abc import ABC
from typing import Optional, List, Dict

from PIL import Image
from PySide2.QtGui import QPixmap

from paragon.core.textures.texture import Texture

from paragon.core.services.portraits import Portraits
from paragon.model.portrait_info import PortraitInfo


# Context: FE9 and FE10 organize portraits differently, so need to load portraits differently.
# This is a band aid fix and bad OOP, so should revisit later.
class GCPortraits(Portraits, ABC):
    def render(
        self, fid: str, emotions: List[str], mode: str, active: bool = True
    ) -> Optional[QPixmap]:
        if not fid:
            return self.render(self.default_fid(), emotions, mode, active)

        fsid = self.fid_to_fsid(fid, mode)
        info = self.fsid_to_portrait_info(fsid)
        if not info:
            return self.render(self.default_fid(), emotions, mode, active)
        if emotions:
            emotion = "happy" if emotions[0] == "happy" else "standard"
        else:
            emotion = "standard"
        portraits = self.from_fsid(fsid, mode=mode)
        if not info.draw_coords and info.file_index == -1 and len(portraits) % 2 != 0:
            image = portraits[str(len(portraits) - 1)].to_pillow_image()
        elif info.draw_coords:
            image = portraits[str(info.file_index)].to_pillow_image()
            if "left_eye" in info.component_indices:
                left_eye = portraits[
                    str(info.component_indices["left_eye"])
                ].to_pillow_image()
                left_eye_coords = info.draw_coords["left_eye"]
                image.paste(left_eye, left_eye_coords, left_eye)
            if "right_eye" in info.component_indices:
                right_eye = portraits[
                    str(info.component_indices["right_eye"])
                ].to_pillow_image()
                right_eye_coords = info.draw_coords["right_eye"]
                image.paste(right_eye, right_eye_coords, right_eye)
            if f"mouth_{emotion}" in info.component_indices:
                mouth = portraits[
                    str(info.component_indices[f"mouth_{emotion}"])
                ].to_pillow_image()
                mouth_coords = info.draw_coords["mouth"]
                image.paste(mouth, mouth_coords, mouth)
        elif fid != self.default_fid():
            return self.render(self.default_fid(), emotions, mode, active)
        else:
            return None

        if not active:
            image = self.fade(image)
        return self.crop_for_mode(image, info, mode).toqpixmap()

    def from_fsid(self, fsid: str, mode=None, **kwargs) -> Optional[Dict[str, Texture]]:
        try:
            info = self.fsid_to_portrait_info(fsid, mode=mode)
            if not info:
                return None
            files = self._read_portrait_arc(info.body_arc)
            return {str(i): Texture.from_core_texture(t) for i, t in enumerate(files)}
        except:
            logging.exception(f"Failed to load GC portrait fsid={fsid}")
            return None

    def crop_for_mode(self, image: Image, info: PortraitInfo, mode: str) -> Image:
        return image

    def blush_label(self) -> str:
        pass

    def sweat_label(self) -> str:
        pass

    def fid_to_fsid(self, fid: str, mode: str) -> str:
        return fid

    def default_fid(self) -> str:
        return "FID_UNKNOWN"

    def default_mode(self) -> str:
        return "Standard"

    def modes(self) -> List[str]:
        return ["Standard"]

    def _face_data_to_fsid(self, rid: int) -> Optional[str]:
        return self.data.string(rid, "fid")

    def _parse_texture(self, contents: bytes):
        pass

    def _to_portrait_key(self, filename: str):
        return filename

    def character_to_fid(self, rid: int) -> Optional[str]:
        return self.data.string(rid, "fid")
