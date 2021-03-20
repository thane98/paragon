import os
from typing import Optional, List

from PIL import Image

from paragon.core.services import utils
from paragon.core.services.bch_portraits import BchPortraits
from paragon.core.textures.texture import Texture
from paragon.model.portrait_info import PortraitInfo


class FE14Portraits(BchPortraits):
    def crop_for_mode(self, image: Image, info: PortraitInfo, mode: str) -> Image:
        if mode == "BU" and "BU" in info.draw_coords:
            x, y = info.draw_coords["BU"]
            return image.crop((x, y, x + 70, y + 49))
        return image  # TODO

    def fsid_to_portrait_info(self, fsid: str) -> Optional[PortraitInfo]:
        # Crit portraits are a special case.
        # We need to figure out if the files exist without relying
        # on FaceData.
        if fsid.startswith("FSID_CT_"):
            part = fsid[8:]
            filename = part + "_ct"
            # Velouria has a unique case with a mismatch fsid and filename
            if filename == "ベロア_ct":
                filename = "べロア_ct"
            body_path = f"face/face/{filename}.arc"
            hair_path = f"face/hair/{filename}/髪0.bch.lz"
            face_exists = self.data.file_exists(body_path, False)
            hair_exists = self.data.file_exists(hair_path, False)
            if face_exists:
                return PortraitInfo(
                    blush_coords={"CT": (0, 0)},
                    sweat_coords={"CT": (0, 0)},
                    body_arc=filename,
                    hair_file=filename if hair_exists else None,
                )

        if rid := self.data.key_to_rid("portraits", fsid):
            blush_coords = (
                self.data.int(rid, "blush_position_x"),
                self.data.int(rid, "blush_position_y"),
            )
            sweat_coords = (
                self.data.int(rid, "sweat_position_x"),
                self.data.int(rid, "sweat_position_y"),
            )
            portrait_file = self.data.string(rid, "portrait_file")
            hair_file = self.data.string(rid, "hair_file")
            accessory_file = self.data.string(rid, "accessory_file")
            hair_color = self.data.bytes(rid, "hair_color")
            if hair_color:
                hair_color = bytes(hair_color)
            return PortraitInfo(
                body_arc=portrait_file,
                blush_coords={
                    "BU": blush_coords,
                    "ST": blush_coords,
                },
                sweat_coords={
                    "BU": sweat_coords,
                    "ST": sweat_coords,
                },
                draw_coords={
                    "BU": (
                        self.data.int(rid, "bu_position_x"),
                        self.data.int(rid, "bu_position_y"),
                    ),
                    "ST": (
                        self.data.int(rid, "st_position_x"),
                        self.data.int(rid, "st_position_y"),
                    ),
                },
                hair_file=hair_file,
                accessory_file=accessory_file,
                hair_color=hair_color,
            )
        else:
            return None

    def fid_to_fsid(self, fid: str, mode: str) -> str:
        if fid == "FID_username":
            fid = self.config.fe14_avatar.portraits
        fid_part = fid[4:] if len(fid) > 4 else fid
        return f"FSID_{mode}_{fid_part}"

    def default_mode(self) -> str:
        return "ST"

    def modes(self) -> List[str]:
        return ["BU", "ST", "CT"]

    def _read_portrait_arc(self, path: str):
        return self.data.read_arc(f"face/face/{path}.arc")

    def _read_hair_file(self, info: PortraitInfo) -> Optional[Texture]:
        if hair_file := info.hair_file:
            full_path = os.path.join("face", "hair", hair_file, "髪0.bch.lz")
            try:
                textures = self.data.read_bch_textures(full_path)
            except:
                return None
            if textures:
                return Texture.from_core_texture(list(textures.values())[0])
        return None

    def _read_accessory_file(self, info: PortraitInfo) -> Optional[Texture]:
        if path := info.accessory_file:
            acce = self.config.fe14_avatar.accessory
            if not acce:
                return None
            full_path = os.path.join("face", "accessory1", path, f"{acce}.bch.lz")
            try:
                textures = self.data.read_bch_textures(full_path)
            except:
                return None
            if textures:
                return Texture.from_core_texture(list(textures.values())[0])
        return None

    def _character_to_fid(self, rid: int) -> Optional[str]:
        pid = self.data.string(rid, "pid")
        if utils.is_avatar_pid(pid):
            return self.config.fe14_avatar.portraits
        else:
            return self.data.string(rid, "fid")

    def _character_to_job(self, rid: int) -> Optional[int]:
        if job := self.data.rid(rid, "class_1"):
            return job
        else:
            return None

    def _job_to_fid(self, rid: int) -> Optional[str]:
        if jid := self.data.string(rid, "jid"):
            jid = jid.replace("男", "")
            jid = jid.replace("女", "")
            return "FID_" + jid[4:] if len(jid) > 4 else None
        else:
            return None

    def default_fid(self) -> str:
        return "FID_フードマン"
