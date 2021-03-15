import logging

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


def try_multi_open(gd, multi_id, key):
    try:
        return gd.multi_open(multi_id, key)
    except:
        return None


def try_multi_duplicate(gd, multi_id, source, dest):
    try:
        return gd.multi_duplicate(multi_id, source, dest)
    except:
        logging.exception(
            f"Failed to duplicate multi id={multi_id}, source={source}, dest={dest}"
        )
        return None


# PIL image tinting code pulled from:
# https://stackoverflow.com/questions/29332424/changing-colour-of-an-image
def image_tint(src, tint="#ffffff"):
    if src.mode not in ["RGB", "RGBA"]:
        raise TypeError("Unsupported source image mode: {}".format(src.mode))

    tr, tg, tb = ImageColor.getrgb(tint)
    tl = ImageColor.getcolor(tint, "L")  # tint color's overall luminosity
    if not tl:
        tl = 1  # avoid division by zero
    tl = float(tl)  # compute luminosity preserving tint factors
    sr, sg, sb = map(lambda tv: tv / tl, (tr, tg, tb))  # per component
    # adjustments
    # create look-up tables to map luminosity to adjusted tint
    # (using floating-point math only to compute table)
    luts = (
        tuple(map(lambda lr: int(lr * sr + 0.5), range(256)))
        + tuple(map(lambda lg: int(lg * sg + 0.5), range(256)))
        + tuple(map(lambda lb: int(lb * sb + 0.5), range(256)))
    )
    l = ImageOps.grayscale(src)  # 8-bit luminosity version of whole image
    if Image.getmodebands(src.mode) < 4:
        merge_args = (src.mode, (l, l, l))  # for RGB verion of grayscale
    else:  # include copy of src image's alpha layer
        a = Image.new("L", src.size)
        a.putdata(src.getdata(3))
        merge_args = (src.mode, (l, l, l, a))  # for RGBA verion of grayscale
        luts += tuple(range(256))  # for 1:1 mapping of copied alpha values

    return Image.merge(*merge_args).point(luts)
