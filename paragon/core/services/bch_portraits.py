from abc import ABC

from paragon.core.services.portraits import Portraits
from paragon.model.portrait_info import PortraitInfo
from paragon import paragon as pgn


class BchPortraits(Portraits, ABC):
    def fsid_to_portrait_info(self, fsid: str) -> PortraitInfo:
        raise NotImplementedError

    def fid_to_fsid(self, fid: str, mode: str) -> str:
        fid_part = fid[4:] if len(fid) > 4 else fid
        return f"FSID_{mode}_{fid_part}"

    def default_fid(self) -> str:
        return "FID_カゲマン"

    def _parse_texture(self, contents: bytes):
        decmp = pgn.decompress_lz13(bytes(contents))
        return pgn.read_bch(decmp)[0]

    def _to_portrait_key(self, filename: str):
        return filename[:-7] if filename.endswith(".bch.lz") else filename
