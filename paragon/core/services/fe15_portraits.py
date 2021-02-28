from typing import Optional, List, Tuple

from PIL import Image

from paragon.core.services.bch_portraits import BchPortraits
from paragon.model.portrait_info import PortraitInfo


class FE15Portraits(BchPortraits):
    def crop_for_mode(self, image: Image, info: PortraitInfo, mode: str) -> Image:
        if mode == "TK":
            return image.crop((0, 0, 60, 52))
        else:
            return image

    def fsid_to_portrait_info(self, fsid: str) -> Optional[PortraitInfo]:
        if rid := self.data.key_to_rid("portraits", fsid):
            return PortraitInfo(
                body_arc=self.data.string(rid, "portrait_file"),
                blush_coords={
                    "BU": (
                        self.data.int(rid, "blush_bu_x"),
                        self.data.int(rid, "blush_bu_y"),
                    ),
                    "TK": (
                        self.data.int(rid, "blush_tk_x"),
                        self.data.int(rid, "blush_tk_y"),
                    ),
                },
                sweat_coords={
                    "BU": (
                        self.data.int(rid, "sweat_bu_x"),
                        self.data.int(rid, "sweat_bu_y"),
                    ),
                    "TK": (
                        self.data.int(rid, "sweat_tk_x"),
                        self.data.int(rid, "sweat_tk_y"),
                    ),
                },
            )
        else:
            return None

    def default_mode(self) -> str:
        return "BU"

    def modes(self) -> List[str]:
        return ["BU", "TK", "ADV", "HR"]

    def _read_portrait_arc(self, path: str):
        return self.data.read_arc(f"face/face/{path}.arc")

    def _character_to_fid(self, rid: int) -> Optional[str]:
        return self.data.string(rid, "fid")

    def _character_to_job(self, rid: int) -> Optional[int]:
        if jid := self.data.string(rid, "jid"):
            return self.data.key_to_rid("jobs", jid)
        else:
            return None
