from paragon.core.textures.texture import Texture

from paragon.core.textures import ctpk


def read_ctpk(gd, path):
    contents = bytes(gd.read_file(path))
    return ctpk.decode_textures(contents)


def read_tpl(gd, path):
    raw_textures = gd.read_tpl_textures(path)
    return {str(i): Texture.from_core_texture(t) for i, t in enumerate(raw_textures)}
