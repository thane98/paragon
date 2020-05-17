#!/usr/bin/python
# Credits: https://github.com/ObsidianX/3dstools
import math
import struct

# FINF = Font Info
# TGLP = Texture Glyph
# CWDH = Character Widths
# CMAP = Character Mapping

VERSIONS = (0x03000000,)

FFNT_HEADER_SIZE = 0x14
FINF_HEADER_SIZE = 0x20
TGLP_HEADER_SIZE = 0x20
CWDH_HEADER_SIZE = 0x10
CMAP_HEADER_SIZE = 0x14

FFNT_HEADER_MAGIC = (b'CFNT', b'CFNU')
FINF_HEADER_MAGIC = b'FINF'
TGLP_HEADER_MAGIC = b'TGLP'
CWDH_HEADER_MAGIC = b'CWDH'
CMAP_HEADER_MAGIC = b'CMAP'

FFNT_HEADER_STRUCT = '%s4s2H3I'
FINF_HEADER_STRUCT = '%s4sI2BH4B3I4B'
TGLP_HEADER_STRUCT = '%s4sI4BI6HI'
CWDH_HEADER_STRUCT = '%s4sI2HI'
CMAP_HEADER_STRUCT = '%s4sI4HI'

FORMAT_RGBA8 = 0x00
FORMAT_RGB8 = 0x01
FORMAT_RGBA5551 = 0x02
FORMAT_RGB565 = 0x03
FORMAT_RGBA4 = 0x04
FORMAT_LA8 = 0x05
FORMAT_HILO8 = 0x06
FORMAT_L8 = 0x07
FORMAT_A8 = 0x08
FORMAT_LA4 = 0x09
FORMAT_L4 = 0x0A
FORMAT_A4 = 0x0B
FORMAT_ETC1 = 0x0C
FORMAT_ETC1A4 = 0x0D

PIXEL_FORMATS = {
    FORMAT_RGBA8: 'RGBA8',
    FORMAT_RGB8: 'RGB8',
    FORMAT_RGBA5551: 'RGBA5551',
    FORMAT_RGB565: 'RGB565',
    FORMAT_RGBA4: 'RGBA4',
    FORMAT_LA8: 'LA8',
    FORMAT_HILO8: 'HILO8',
    FORMAT_L8: 'L8',
    FORMAT_A8: 'A8',
    FORMAT_LA4: 'LA4',
    FORMAT_L4: 'L4',
    FORMAT_A4: 'A4',
    FORMAT_ETC1: 'ETC1',
    FORMAT_ETC1A4: 'ETC1A4'
}

PIXEL_FORMAT_SIZE = {
    FORMAT_RGBA8: 32,
    FORMAT_RGB8: 24,
    FORMAT_RGBA5551: 16,
    FORMAT_RGB565: 16,
    FORMAT_RGBA4: 16,
    FORMAT_LA8: 16,
    FORMAT_HILO8: 16,
    FORMAT_L8: 8,
    FORMAT_A8: 8,
    FORMAT_LA4: 8,
    FORMAT_L4: 4,
    FORMAT_A4: 4,
    FORMAT_ETC1: 64,
    FORMAT_ETC1A4: 128
}

ETC_INDIV_RED1_OFFSET = 60
ETC_INDIV_GREEN1_OFFSET = 52
ETC_INDIV_BLUE1_OFFSET = 44

ETC_DIFF_RED1_OFFSET = 59
ETC_DIFF_GREEN1_OFFSET = 51
ETC_DIFF_BLUE_OFFSET = 43

ETC_RED2_OFFSET = 56
ETC_GREEN2_OFFSET = 48
ETC_BLUE2_OFFSET = 40

ETC_TABLE1_OFFSET = 37
ETC_TABLE2_OFFSET = 34

ETC_DIFFERENTIAL_BIT = 33
ETC_ORIENTATION_BIT = 32

ETC_MODIFIERS = [
    [2, 8],
    [5, 17],
    [9, 29],
    [13, 42],
    [18, 60],
    [24, 80],
    [33, 106],
    [47, 183]
]

MAPPING_DIRECT = 0x00
MAPPING_TABLE = 0x01
MAPPING_SCAN = 0x02

MAPPING_METHODS = {
    MAPPING_DIRECT: 'Direct',
    MAPPING_TABLE: 'Table',
    MAPPING_SCAN: 'Scan'
}

TGLP_DATA_OFFSET = 0x2000

ETC_RED2_OFFSET = 56
ETC_GREEN2_OFFSET = 48
ETC_BLUE2_OFFSET = 40


def decompress_etc1a4(data, height, width):
    with_alpha = True  # It's ETC1A4

    block_size = 16 if with_alpha else 8

    bmp = bytearray(4 * width * height)

    tile_width = int(math.ceil(width / 8.0))
    tile_height = int(math.ceil(height / 8.0))

    # here's the kicker: there will always be a power-of-two amount of tiles
    tile_width = 1 << int(math.ceil(math.log(tile_width, 2)))
    tile_height = 1 << int(math.ceil(math.log(tile_height, 2)))

    pos = 0

    # texture is composed of 8x8 tiles
    for tile_y in range(tile_height):
        for tile_x in range(tile_width):

            # in ETC1 mode each tile is composed of 2x2, compressed sub-tiles, 4x4 pixels each
            for block_y in range(2):
                for block_x in range(2):
                    data_pos = pos
                    pos += block_size

                    block = data[data_pos:data_pos + block_size]

                    alphas = 0xFFffFFffFFffFFff
                    if with_alpha:
                        alphas = struct.unpack('<Q', block[:8])[0]
                        block = block[8:]

                    pixels = struct.unpack('<Q', block)[0]

                    # how colors are stored in the high-order 32 bits
                    differential = (pixels >> ETC_DIFFERENTIAL_BIT) & 0x01 == 1
                    # how the sub blocks are divided, 0 = 2x4, 1 = 4x2
                    horizontal = (pixels >> ETC_ORIENTATION_BIT) & 0x01 == 1
                    # once the colors are decoded for the sub block this determines how to shift the colors
                    # which modifier row to use for sub block 1
                    table1 = ETC_MODIFIERS[(pixels >> ETC_TABLE1_OFFSET) & 0x07]
                    # which modifier row to use for sub block 2
                    table2 = ETC_MODIFIERS[(pixels >> ETC_TABLE2_OFFSET) & 0x07]

                    color1 = [0, 0, 0]
                    color2 = [0, 0, 0]

                    if differential:
                        # grab the 5-bit code words
                        r = ((pixels >> ETC_DIFF_RED1_OFFSET) & 0x1F)
                        g = ((pixels >> ETC_DIFF_GREEN1_OFFSET) & 0x1F)
                        b = ((pixels >> ETC_DIFF_BLUE_OFFSET) & 0x1F)

                        # extends from 5 to 8 bits by duplicating the 3 most significant bits
                        color1[0] = (r << 3) | ((r >> 2) & 0x07)
                        color1[1] = (g << 3) | ((g >> 2) & 0x07)
                        color1[2] = (b << 3) | ((b >> 2) & 0x07)

                        # add the 2nd block, 3-bit code words to the original words (2's complement!)
                        r += _complement((pixels >> ETC_RED2_OFFSET) & 0x07, 3)
                        g += _complement((pixels >> ETC_GREEN2_OFFSET) & 0x07, 3)
                        b += _complement((pixels >> ETC_BLUE2_OFFSET) & 0x07, 3)

                        # extend from 5 to 8 bits like before
                        color2[0] = (r << 3) | ((r >> 2) & 0x07)
                        color2[1] = (g << 3) | ((g >> 2) & 0x07)
                        color2[2] = (b << 3) | ((b >> 2) & 0x07)
                    else:
                        # 4 bits per channel, 16 possible values

                        # 1st block
                        color1[0] = ((pixels >> ETC_INDIV_RED1_OFFSET) & 0x0F) * 0x11
                        color1[1] = ((pixels >> ETC_INDIV_GREEN1_OFFSET) & 0x0F) * 0x11
                        color1[2] = ((pixels >> ETC_INDIV_BLUE1_OFFSET) & 0x0F) * 0x11

                        # 2nd block
                        color2[0] = ((pixels >> ETC_RED2_OFFSET) & 0x0F) * 0x11
                        color2[1] = ((pixels >> ETC_GREEN2_OFFSET) & 0x0F) * 0x11
                        color2[2] = ((pixels >> ETC_BLUE2_OFFSET) & 0x0F) * 0x11

                    # now that we have two sub block pixel colors to start from,
                    # each pixel is read as a modifier value

                    # 16 pixels are described with 2 bits each,
                    # one selecting the sign, the second the value

                    amounts = pixels & 0xFFFF
                    signs = (pixels >> 16) & 0xFFFF

                    for pixel_y in range(4):
                        for pixel_x in range(4):
                            x = pixel_x + (block_x * 4) + (tile_x * 8)
                            y = pixel_y + (block_y * 4) + (tile_y * 8)

                            if x >= width:
                                continue
                            if y >= height:
                                continue

                            offset = pixel_x * 4 + pixel_y

                            if horizontal:
                                table = table1 if pixel_y < 2 else table2
                                color = color1 if pixel_y < 2 else color2
                            else:
                                table = table1 if pixel_x < 2 else table2
                                color = color1 if pixel_x < 2 else color2

                            # determine the amount to shift the color
                            amount = table[(amounts >> offset) & 0x01]
                            # and in which direction. 1 = -, 0 = +
                            sign = (signs >> offset) & 0x01

                            if sign == 1:
                                amount *= -1

                            red = max(min(color[0] + amount, 0xFF), 0)
                            green = max(min(color[1] + amount, 0xFF), 0)
                            blue = max(min(color[2] + amount, 0xFF), 0)
                            alpha = ((alphas >> (offset * 4)) & 0x0F) * 0x11

                            pixel_pos = (y * width + x) * 4
                            bmp[pixel_pos:pixel_pos + 4] = [red, green, blue, alpha]
    return bytes(bmp)


def _complement(input_, bits):
    if input_ >> (bits - 1) == 0:
        return input_
    return input_ - (1 << bits)
