use crate::etc1;
use std::io::{Error, ErrorKind, Seek, SeekFrom, Result, Cursor};
use byteorder::{LittleEndian, ReadBytesExt};

static CONVERT_5_TO_8: &'static [u8] = &[
    0x00, 0x08, 0x10, 0x18, 0x20, 0x29, 0x31, 0x39, 0x41, 0x4A, 0x52, 0x5A, 0x62, 0x6A, 0x73, 0x7B,
    0x83, 0x8B, 0x94, 0x9C, 0xA4, 0xAC, 0xB4, 0xBD, 0xC5, 0xCD, 0xD5, 0xDE, 0xE6, 0xEE, 0xF6, 0xFF,
];

static TILE_ORDER: &'static [u8] = &[
    0, 1, 8, 9, 2, 3, 10, 11, 16, 17, 24, 25, 18, 19, 26, 27, 4, 5, 12, 13, 6, 7, 14, 15, 20, 21,
    28, 29, 22, 23, 30, 31, 32, 33, 40, 41, 34, 35, 42, 43, 48, 49, 56, 57, 50, 51, 58, 59, 36, 37,
    44, 45, 38, 39, 46, 47, 52, 53, 60, 61, 54, 55, 62, 63,
];

pub fn decode_color(value: u32, format: u32) -> Vec<u8> {
    let mut color: Vec<u8> = vec![0, 0, 0, 0];
    match format {
        0 => {
            // RGBA8
            color[0] = ((value >> 24) & 0xFF) as u8;
            color[1] = ((value >> 16) & 0xFF) as u8;
            color[2] = ((value >> 8) & 0xFF) as u8;
            color[3] = (value & 0xFF) as u8;
        }
        1 => {
            // RGB8
            color[0] = ((value >> 16) & 0xFF) as u8;
            color[1] = ((value >> 8) & 0xFF) as u8;
            color[2] = (value & 0xFF) as u8;
            color[3] = 0xFF;
        }
        2 => {
            // RGB 5551
            color[0] = CONVERT_5_TO_8[((value >> 11) & 0x1F) as usize];
            color[1] = CONVERT_5_TO_8[((value >> 6) & 0x1F) as usize];
            color[2] = CONVERT_5_TO_8[((value >> 1) & 0x1F) as usize];
            color[3] = if value & 1 == 1 { 0xFF } else { 0 };
        }
        3 => {
            // RGB565
            color[0] = CONVERT_5_TO_8[((value >> 11) & 0x1F) as usize];
            color[1] = (((value >> 5) & 0x3F) * 4) as u8;
            color[2] = CONVERT_5_TO_8[(value & 0x1F) as usize];
            color[3] = 0xFF;
        }
        4 => {
            // RGBA4
            let r = (value >> 12) & 0xF;
            let g = (value >> 8) & 0xF;
            let b = (value >> 4) & 0xF;
            let a = value & 0xF;
            color[0] = (r | (r << 4)) as u8;
            color[1] = (g | (g << 4)) as u8;
            color[2] = (b | (b << 4)) as u8;
            color[3] = (a | (a << 4)) as u8;
        }
        5 => {
            // LA8
            let red = ((value >> 8) & 0xFF) as u8;
            color[0] = red;
            color[1] = red;
            color[2] = red;
            color[3] = (value & 0xFF) as u8;
        }
        6 => {
            // HILO8
            let red = (value >> 8) as u8;
            color[0] = red;
            color[1] = red;
            color[2] = red;
            color[3] = 0xFF;
        }
        7 => {
            // L8
            color[0] = value as u8;
            color[1] = value as u8;
            color[2] = value as u8;
            color[3] = 0xFF;
        }
        8 => {
            // A8
            color[0] = 0xFF;
            color[1] = 0xFF;
            color[2] = 0xFF;
            color[3] = value as u8;
        }
        9 => {
            // LA4
            let red = (value >> 4) as u8;
            color[0] = red;
            color[1] = red;
            color[2] = red;
            color[3] = (value & 0xF) as u8;
        }
        10 => {
            // L4
            let red = (value * 0x11) as u8;
            color[0] = red;
            color[1] = red;
            color[2] = red;
            color[3] = 0xFF;
        }
        11 => {
            // A4
            color[0] = 0xFF;
            color[1] = 0xFF;
            color[2] = 0xFF;
            color[3] = (value * 0x11) as u8;
        }
        _ => {}
    }
    color
}

fn decode_rgba_pixel_data(
    data: &[u8],
    width: usize,
    height: usize,
    format: u32,
) -> Result<Vec<u8>> {
    let num_pixels = width * height;
    let mut bmp: Vec<u8> = Vec::new();
    bmp.resize(4 * num_pixels, 0);
    let mut cursor = Cursor::new(data);

    for tile_y in 0..height / 8 {
        for tile_x in 0..width / 8 {
            for pixel in 0..64 {
                let x = (TILE_ORDER[pixel] % 8) as usize;
                let y = (TILE_ORDER[pixel] as usize - x) / 8;
                let output_index = (tile_x * 8 + x + ((tile_y * 8 + y) * width)) * 4;
            
                let color = match format {
                    0 => decode_color(cursor.read_u32::<LittleEndian>()?, format),
                    1 => {
                        let value = cursor.read_u32::<LittleEndian>()?;
                        let value = value & 0xFFFFFF;
                        cursor.seek(SeekFrom::Current(-1))?;
                        decode_color(value, format)
                    }
                    2 | 3 | 4 | 5 => decode_color(cursor.read_u16::<LittleEndian>()? as u32, format),
                    6 | 7 | 8 | 9 => decode_color(cursor.read_u8()? as u32, format),
                    _ => decode_color(0, format),
                };
                bmp[output_index..output_index + 4].copy_from_slice(&color[..]);
            }
        }
    }
    Ok(bmp)
}

pub fn decode_pixel_data(data: &[u8], width: usize, height: usize, format: u32) -> Result<Vec<u8>> {
    match format {
        0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 => {
            decode_rgba_pixel_data(data, width, height, format)
        }
        12 | 13 => etc1::decompress(data, width, height, format == 13),
        _ => Err(Error::new(ErrorKind::Other, "Unsupported texture format.")),
    }
}

pub fn get_pixel_format_bpp(pixel_format: u32) -> f32 {
    match pixel_format {
        0x0 => 4.0,
        0x1 => 3.0,
        0x2 | 0x3 | 0x4 | 0x5 => 2.0,
        0x6 | 0x7 | 0x8 | 0x9 | 0xB | 0xD => 1.0,
        0xA | 0xC => 0.5,
        _ => Err(Error::new(ErrorKind::Other, "Unsupported texture format.")),
    }
}