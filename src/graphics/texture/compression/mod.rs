pub mod etc1;

use std::io::{Error, ErrorKind, Seek, SeekFrom, Result, Cursor};
use byteorder::{LittleEndian, ReadBytesExt};

pub static CONVERT_5_TO_8: &'static [u8] = &[
    0x00, 0x08, 0x10, 0x18, 0x20, 0x29, 0x31, 0x39, 0x41, 0x4A, 0x52, 0x5A, 0x62, 0x6A, 0x73, 0x7B,
    0x83, 0x8B, 0x94, 0x9C, 0xA4, 0xAC, 0xB4, 0xBD, 0xC5, 0xCD, 0xD5, 0xDE, 0xE6, 0xEE, 0xF6, 0xFF,
];

pub static TILE_ORDER: &'static [u8] = &[
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

pub fn encode_pixel_data(data: &[u8], width: usize, height: usize, format: u32) -> Result<Vec<u8>> {
    match format {
        0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 => {
            encode_rgba_pixel_data(data, width, height, format)
        }
        12 | 13 => etc1::compress(data, width as u16, height as u16, format == 13),
        _ => Err(Error::new(ErrorKind::Other, "Unsupported texture format.")),
    }
}

fn encode_rgba_pixel_data(data: &[u8], width: usize, height: usize, format: u32) -> Result<Vec<u8>> {
    let mut output: Vec<u8> = Vec::new();

    // Assumes texture is read in order of RGBA
    // Swizzle 8x8 tiles first
    for tile_y in (0..height).step_by(8) {
        for tile_x in (0..width).step_by(8) {
            for pixel in 0..64 {
                let x = (TILE_ORDER[pixel]  & 7) as usize;
                let y = (TILE_ORDER[pixel] as usize - x) >> 3;

                let input_offset = ((tile_x + x + ((tile_y + y) * width)) * 4) as usize;

                // Encode
                match format {
                    // RGBA8
                    0 => {
                        let r = data[input_offset];
                        let g = data[input_offset + 1];
                        let b = data[input_offset + 2];
                        let a = data[input_offset + 3];
                        output.push(r);
                        output.push(g);
                        output.push(b);
                        output.push(a);
                    }
                    // RGB8
                    1 => {
                        let r = data[input_offset];
                        let g = data[input_offset + 1];
                        let b = data[input_offset + 2];
                        output.push(r);
                        output.push(g);
                        output.push(b);
                    }
                    // RGBA5551
                    2 => {
                        let r = (data[input_offset] as u16 >> 3) << 11;
                        let g = (data[input_offset + 1] as u16 >> 3) << 6;
                        let b = (data[input_offset + 2] as u16 >> 3) << 1;
                        let a = (data[input_offset + 3] as u16) >> 7;
                        let color = r | g | b | a;
                        // Split the color to 8-bits to push in the order of LE
                        output.push((color & 0x00FF) as u8);
                        output.push(((color & 0xFF00) >> 8) as u8);
                    }
                    // RGB565
                    3 => {
                        let r = (data[input_offset] as u16 >> 3) << 11;
                        let g = (data[input_offset + 1] as u16 >> 2) << 5;
                        let b = data[input_offset + 2] as u16 >> 3;
                        let color = r | g | b;
                        // Split the color to 8-bits to push in the order of LE
                        output.push((color & 0x00FF) as u8);
                        output.push(((color & 0xFF00) >> 8) as u8);

                    }
                    // RGBA4
                    4 => {
                        let r = (data[input_offset] as u16 >> 4) << 12;
                        let g = (data[input_offset + 1] as u16 >> 4) << 8;
                        let b = (data[input_offset + 2] as u16 >> 4) << 4;
                        let a = (data[input_offset + 3] as u16) >> 4;
                        let color = r | g | b | a;
                        // Split the color to 8-bits to push in the order of LE
                        output.push((color & 0x00FF) as u8);
                        output.push(((color & 0xFF00) >> 8) as u8);
                    }
                    // http://www.songho.ca/dsp/luminance/luminance.html
                    // LA8 ; I'm unsure if this is what it should be, but it seems okay
                    5 => {
                        let mut l = (data[input_offset] as u32) << 1;
                        l += ((data[input_offset] as u32) << 2) + (data[input_offset + 1] as u32);
                        l += data[input_offset + 2] as u32;
                        output.push((l >> 3) as u8);
                        output.push(data[input_offset + 3]);
                    }
                    // HiLo8
                    // https://github.com/Cruel/3dstex/blob/5cdd9a149239a54242368e604810ed0de6ae040c/src/Encoder.cpp
                    6 => {
                        Error::new(ErrorKind::Other, "Unsupported texture format");
                    }
                    // L8
                    7 => {
                        let mut l = (data[input_offset] as u32) << 1;
                        l += ((data[input_offset] as u32) << 2) + (data[input_offset + 1] as u32);
                        l += data[input_offset + 2] as u32;
                        output.push((l >> 3) as u8);
                    }
                    // A8
                    8 => {
                        output.push(data[input_offset + 3]);
                    }
                    // LA44
                    9 => {
                        let mut l = (data[input_offset] as u32) << 1;
                        l += ((data[input_offset] as u32) << 2) + (data[input_offset + 1] as u32);
                        l += data[input_offset + 2] as u32;
                        l >>= 3;
                        // Now make it 4 bit
                        l = (l >> 4) << 4;
                        let a = data[input_offset + 3] >> 4;
                        output.push((l as u8) | a);
                    }
                    // L4; need to check
                    10 => {
                        let mut l1 = (data[input_offset] as u32) << 1;
                        l1 += ((data[input_offset] as u32) << 2) + (data[input_offset + 1] as u32);
                        l1 += data[input_offset + 2] as u32;
                        l1 >>= 3;
                        // Now make it 4 bit
                        l1 >>= 4;

                        if data.len() < (input_offset + 4) {
                            let mut l2 = (data[input_offset + 4] as u32) << 1;
                            l2 += ((data[input_offset + 4] as u32) << 2) + (data[input_offset + 5] as u32);
                            l2 += data[input_offset + 6] as u32;
                            l2 >>= 3;

                            l1 <<= 4;
                            l2 >>= 4;
                            output.push((l1 as u8) | (l2 as u8));
                        }
                        else {
                            output.push(l1 as u8);
                        }
                    }
                    // A4; need to check
                    11 => {
                        let mut a1 = (data[input_offset + 3] >> 4) as u32;
                        if data.len() < (input_offset + 4) {
                            let a2 = (data[input_offset + 7] >> 4) as u32;
                            a1 <<= 4;
                            output.push((a1 as u8) | (a2 as u8));
                        }
                        else {
                            output.push(a1 as u8);
                        }
                    }
                    _ => {
                        Error::new(ErrorKind::Other, "Unsupported format");
                        break;
                    }
                }
            }
        }
    }
    Ok(output)
}

pub fn calculate_len(pixel_format: u32, height: usize, width: usize) -> usize {
    let bpp = match pixel_format {
        0x0 => 4.0,
        0x1 => 3.0,
        0x2 | 0x3 | 0x4 | 0x5 => 2.0,
        0x6 | 0x7 | 0x8 | 0x9 | 0xB | 0xD => 1.0,
        0xA | 0xC => 0.5,
        _ => 0.0,
    };
    (bpp * height as f32 * width as f32) as usize
}