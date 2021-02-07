import logging


def safe_texture_load(fn):
    try:
        return fn()
    except:
        logging.exception("Failed to load textures.")
        return {}


def parse_texture_with_uvs(data, texture, uvs):
    return texture.crop(
        data.int(uvs, "left_bound"),
        data.int(uvs, "top_bound"),
        data.int(uvs, "width"),
        data.int(uvs, "height"),
    )
