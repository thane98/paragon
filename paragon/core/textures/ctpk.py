from typing import Dict

from paragon.core.textures import Texture

from paragon import paragon as paragon_core


def decode_textures(raw_ctpk: bytes) -> Dict[str, Texture]:
    return {
        k.filename: Texture.from_core_texture(k)
        for k in paragon_core.read_ctpk(raw_ctpk)
    }
