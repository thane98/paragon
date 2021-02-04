from typing import Optional, List

from PIL import Image

from paragon.core.services.portraits import Portraits
from paragon.model.portrait_info import PortraitInfo
from paragon import paragon as pgn


class FE13Portraits(Portraits):
    def crop_for_mode(self, image: Image, mode: str) -> Image:
        return image  # TODO: Revisit when we hit t0 dialogue.

    def fsid_to_portrait_info(self, fsid: str) -> Optional[PortraitInfo]:
        if rid := self.data.key_to_rid("portraits", fsid):
            # TODO: Parse blush/sweat coords.
            blush_coords = (
                self.data.int(rid, "blush_position_x"),
                self.data.int(rid, "blush_position_y")
            )
            sweat_coords = (
                self.data.int(rid, "sweat_position_x"),
                self.data.int(rid, "sweat_position_y")
            )
            return PortraitInfo(
                body_arc=self.data.string(rid, "portrait_file"),
                blush_coords={
                    "BU": blush_coords,
                    "FC": blush_coords,
                },
                sweat_coords={
                    "BU": sweat_coords,
                    "FC": sweat_coords,
                },
            )
        else:
            return None

    def fid_to_fsid(self, fid: str, mode: str) -> str:
        fid_part = fid[4:] if len(fid) > 4 else fid
        return f"FSID_{mode}_{fid_part}_通常"

    def default_fid(self) -> str:
        return "FID_カゲマン"

    def default_mode(self) -> str:
        return "BU"

    def modes(self) -> List[str]:
        return ["BU", "FC"]

    def _read_portrait_arc(self, path: str):
        return self.data.read_arc(f"face/{path}")

    def _parse_texture(self, contents: bytes):
        decmp = pgn.decompress_lz13(bytes(contents))
        return pgn.read_ctpk(decmp)[0]

    def _to_portrait_key(self, filename: str):
        return filename[:-8] if filename.endswith(".ctpk.lz") else filename

    def _character_to_fid(self, rid: int) -> Optional[str]:
        return self.data.string(rid, "fid")

    def _character_to_job(self, rid: int) -> Optional[int]:
        if jid := self.data.string(rid, "jid"):
            return self.data.key_to_rid("jobs", jid)
        else:
            return None
