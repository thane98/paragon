from paragon.core.textures import ctpk


def read_ctpk(gd, path):
    contents = bytes(gd.read_file(path))
    return ctpk.decode_textures(contents)
