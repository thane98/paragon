import logging
from typing import List, Dict, Optional, Tuple

from PIL import ImageEnhance, Image
from PySide2.QtGui import QPixmap

from paragon.core.services import utils
from paragon.core.textures.texture import Texture


# There are more emotions than this, but we can configure
# the sort to always put them between the standard emotions and
# sweat / blush.
from paragon.model.portrait_info import PortraitInfo

_EMOTION_SORT = {
    "通常": 0,
    "びっくり": 1,
    "怒": 3,
    "苦": 4,
    "笑": 5,
    "キメ": 6,
    "やけくそ": 7,
    "汗": 100,
    "照": 101,
    "頬": 102,
}


_BLUSH_AND_SWEAT = "照汗"


class Portraits:
    def __init__(self, config, data):
        self.config = config
        self.data = data

    def render(
        self, fid: str, emotions: List[str], mode: str, active
    ) -> Optional[QPixmap]:
        # TODO: Other modes?
        if not fid:
            return self.default(mode)
        fsid = self.fid_to_fsid(fid, mode)
        info = self.fsid_to_portrait_info(fsid)
        has_blush = self.blush_label() in emotions or _BLUSH_AND_SWEAT in emotions
        has_sweat = self.sweat_label() in emotions or _BLUSH_AND_SWEAT in emotions
        emotion = next(
            filter(lambda e: e != self.sweat_label() and e != self.blush_label() and e != _BLUSH_AND_SWEAT, emotions),
            "通常"
        )
        portraits = self.from_fid(fid, mode)
        if portraits and emotion in portraits:
            portrait = portraits[emotion].to_pillow_image()
            if has_blush and self.blush_label() in portraits:
                blush = portraits[self.blush_label()].to_pillow_image()
                portrait.paste(blush, info.blush_coords[mode], blush)
            if has_sweat and self.sweat_label() in portraits:
                sweat = portraits[self.sweat_label()].to_pillow_image()
                portrait.paste(sweat, info.sweat_coords[mode], sweat)
        else:
            portrait = self.default_portrait_and_emotion(mode)
            if portrait:
                portrait = portrait.to_pillow_image()
        if not portrait:
            return None
        if not active:
            portrait = self._fade(portrait)
        return self.crop_for_mode(portrait, info, mode).toqpixmap()

    def crop_for_mode(self, image: Image, info: PortraitInfo, mode: str) -> Image:
        raise NotImplementedError

    @staticmethod
    def _fade(image):
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(0.3)

    def default_portrait_and_emotion(self, mode):
        portraits = self.default(mode)
        return portraits["通常"] if portraits and "通常" in portraits else None

    def default(self, mode: str) -> Optional[Dict[str, Texture]]:
        return self.from_fid(self.default_fid(), mode)

    def from_character(self, rid: int, mode: str) -> Optional[Dict[str, Texture]]:
        # Check if we have character specific portraits.
        if fid := self._character_to_fid(rid):
            if portrait := self.from_fid(fid, mode):
                return portrait

        # Nope, try the generic class portraits.
        if job_rid := self._character_to_job(rid):
            if portrait := self.from_job(job_rid, mode):
                return portrait

        # No portraits, so default.
        return self.default(mode)

    def from_job(self, rid: int, mode: str) -> Optional[Dict[str, Texture]]:
        if fid := self._job_to_fid(rid):
            return self.from_fid(fid, mode)
        else:
            return self.default(mode)

    def from_face_data(self, rid: int) -> Optional[Dict[str, Texture]]:
        if fsid := self._face_data_to_fsid(rid):
            return self.from_fsid(fsid)
        else:
            return None

    def from_fid(self, fid: str, mode: str) -> Optional[Dict[str, Texture]]:
        # Try to load portraits from the target fsid.
        fsid = self.fid_to_fsid(fid, mode)
        try:
            return self.from_fsid(fsid)
        except:
            # Loading failed in some way. Try to send back default.
            logging.exception(f"Failed to load portraits for fid {fid}.")
            try:
                if fid != self.default_fid():
                    return self.default(mode)
            except:
                logging.exception("Unable to load default portraits.")

            # Still failing. Send back nothing.
            return None

    def from_fsid(self, fsid: str) -> Optional[Dict[str, Texture]]:
        try:
            # Extract relevant info for constructing the portrait.
            info = self.fsid_to_portrait_info(fsid)
            if not info:
                return None

            # Read the body arc.
            arc = self._read_portrait_arc(info.body_arc)

            # Convert to Texture objects and sort emotions.
            textures = {}
            for k in arc:
                v = arc[k]
                try:
                    texture = Texture.from_core_texture(self._parse_texture(v))
                    textures[self._to_portrait_key(k)] = texture
                except:
                    logging.exception(f"Failed to parse portrait for fsid={fsid}, key={k}")

            # Merge the hair with the body portraits.
            if "髪0" in textures:
                # Awakening stores these with the portraits. Handle this separately.
                textures = self._merge_awakening_hair(textures)
            if accessory_texture := self._read_accessory_file(info):
                textures = self._merge_standard_texture(
                    textures, accessory_texture.to_pillow_image()
                )
            if hair_texture := self._read_hair_file(info):
                if hair_color := info.hair_color:
                    hair_color = self.raw_color_to_rgb_string(hair_color)
                    hair_texture = utils.image_tint(
                        hair_texture.to_pillow_image(), hair_color
                    )
                else:
                    hair_texture = hair_texture.to_pillow_image()
                textures = self._merge_standard_texture(textures, hair_texture)
            output = sorted(textures.items(), key=lambda p: self._emotion_sort(p[0]))
            return {k: v for k, v in output}
        except:
            logging.exception(f"Failed to load portraits for fsid {fsid}.")
            return None

    def _merge_awakening_hair(self, textures: Dict[str, Texture]) -> Dict[str, Texture]:
        hair = textures["髪0"].to_pillow_image()
        textures = {k: v for (k, v) in textures.items() if not k.startswith("髪")}
        return self._merge_standard_texture(textures, hair)

    def _merge_standard_texture(
        self, textures: Dict[str, Texture], to_paste
    ) -> Dict[str, Texture]:
        res = {}
        for key, texture in textures.items():
            if key != self.sweat_label() and key != self.blush_label():
                image = texture.to_pillow_image()
                image.paste(to_paste, mask=to_paste)
                res[key] = Texture.from_pillow_image(key, image)
            else:
                res[key] = texture
        return res

    @staticmethod
    def raw_color_to_rgb_string(raw_color):
        return f"#{raw_color.hex()[:-2]}"  # Cut off the alpha.

    def blush_label(self) -> str:
        raise NotImplementedError

    def sweat_label(self) -> str:
        raise NotImplementedError

    def fsid_to_portrait_info(self, fsid: str) -> Optional[PortraitInfo]:
        raise NotImplementedError

    def fid_to_fsid(self, fid: str, mode: str) -> str:
        raise NotImplementedError

    def default_fid(self) -> str:
        raise NotImplementedError

    def default_mode(self) -> str:
        raise NotImplementedError

    def modes(self) -> List[str]:
        raise NotImplementedError

    def _read_hair_file(self, info: PortraitInfo) -> Optional[Texture]:
        return None

    def _read_accessory_file(self, info: PortraitInfo) -> Optional[Texture]:
        return None

    def _read_portrait_arc(self, path: str):
        raise NotImplementedError

    def _parse_texture(self, contents: bytes):
        raise NotImplementedError

    def _to_portrait_key(self, filename: str):
        raise NotImplementedError

    def _character_to_fid(self, rid: int) -> Optional[str]:
        raise NotImplementedError

    def _character_to_job(self, rid: int) -> Optional[int]:
        raise NotImplementedError

    def _job_to_fid(self, rid: int) -> Optional[str]:
        if jid := self.data.string(rid, "jid"):
            return "FID_" + jid[4:] if len(jid) > 4 else None
        else:
            return None

    def _face_data_to_fsid(self, rid: int) -> Optional[str]:
        return self.data.string(rid, "fsid")

    @staticmethod
    def _emotion_sort(emotion):
        return _EMOTION_SORT[emotion] if emotion in _EMOTION_SORT else 50
