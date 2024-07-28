import logging
import os

from PIL import Image, ImageOps, ImageColor


def is_avatar_pid(pid):
    return pid == "PID_プレイヤー男" or pid == "PID_プレイヤー女"


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


def try_open_fe14_route_file(gd, multi_id, root, route_dir, filename):
    path1 = os.path.join(root, route_dir, filename)
    path2 = os.path.join(root, filename)
    if rid := try_multi_open(gd, multi_id, path1):
        return rid, path1
    else:
        return try_multi_open(gd, multi_id, path2), path2


def try_multi_open(gd, multi_id, key):
    try:
        return gd.multi_open(multi_id, key)
    except:
        logging.info(f"Could not open multi file multi='{multi_id}', key='{key}'")
        return None


def try_multi_duplicate(gd, multi_id, source, dest):
    try:
        return gd.multi_duplicate(multi_id, source, dest)
    except:
        logging.exception(
            f"Failed to duplicate multi id={multi_id}, source={source}, dest={dest}"
        )
        return None


# Overlay blending mode seems to work best
# https://en.wikipedia.org/wiki/Blend_modes#Overlay
def image_tint_overlay(src, tint="#ffffff"):
    if src.mode not in ["RGB", "RGBA"]:
        raise TypeError("Unsupported source image mode: {}".format(src.mode))

    tr, tg, tb = ImageColor.getrgb(tint)

    channels = 4 if src.mode == "RGBA" else 3

    lut = []
    for channel in range(channels):
        for a in range(256):
            if channel == 3:
                out = a
            else:
                b = [tr, tg, tb][channel]

                a = a / 256.0
                b = b / 256.0

                if a < 0.5:
                    out = 2 * a * b
                else:
                    out = 1 - 2 * (1 - a) * (1 - b)

                out = int(out * 256)
            lut.append(out)

    return src.point(lut)
