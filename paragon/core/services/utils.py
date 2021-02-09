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


def try_multi_open(gd, multi_id, key):
    try:
        return gd.multi_open(multi_id, key)
    except:
        logging.exception(f"Failed to open multi id={multi_id}, key={key}")
        return None


def try_multi_duplicate(gd, multi_id, source, dest):
    try:
        return gd.multi_duplicate(multi_id, source, dest)
    except:
        logging.exception(
            f"Failed to duplicate multi id={multi_id}, source={source}, dest={dest}"
        )
        return None
