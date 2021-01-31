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
        12 | 13 => etc1::compress(data, width, height, format == 13),
        _ => Err(Error::new(ErrorKind::Other, "Unsupported texture format.")),
    }
}

fn encode_rgba_pixel_data(
    data: &[u8], 
    width: usize, 
    height: usize, 
    format: u32
) -> Result<Vec<u8>> {
    let mut output: Vec<u8> = Vec::with_capacity(calculate_len(format, height, width));
    
    // Assumes texture is read in order of RGBA
    // Tile 8x8 first
    let tiled_data = tile_data(data, width, height);
    for input_offset in (0..tiled_data.len()).step_by(4) {
        // Encode
        match format {
            // RGBA8
            0 => {
                return Ok(data.to_vec());
            }
            // RGB8
            1 => {
                output.push(tiled_data[input_offset]);
                output.push(tiled_data[input_offset + 1]);
                output.push(tiled_data[input_offset + 2]);
            }
            // RGBA5551
            2 => {
                let r = (convert_8_to_5(tiled_data[input_offset]) as u16) << 11;
                let g = (convert_8_to_5(tiled_data[input_offset + 1]) as u16) << 6;
                let b = (convert_8_to_5(tiled_data[input_offset + 2]) as u16) << 1;
                let a = convert_8_to_1(tiled_data[input_offset + 3]) as u16;
                    let pixel = r | g | b | a;
                // Split the color to 8-bits to push in the order of LE
                output.push((pixel & 0x00FF) as u8);
                output.push(((pixel & 0xFF00) >> 8) as u8);

            }
            // RGB565
            3 => {
                let r = (convert_8_to_5(tiled_data[input_offset]) as u16) << 11;
                let g = (convert_8_to_6(tiled_data[input_offset + 1]) as u16) << 5;
                let b = convert_8_to_5(tiled_data[input_offset + 2]) as u16;
                let pixel = r | g | b;
                // Split the color to 8-bits to push in the order of LE
                output.push((pixel & 0x00FF) as u8);
                output.push(((pixel & 0xFF00) >> 8) as u8);

            }
            // RGBA4
            4 => {
                let r = (convert_8_to_4(tiled_data[input_offset]) as u16) << 12;
                let g = (convert_8_to_4(tiled_data[input_offset + 1]) as u16) << 8;
                let b = (convert_8_to_4(tiled_data[input_offset + 2]) as u16) << 4;
                let a = convert_8_to_4(tiled_data[input_offset + 3]) as u16;
                let pixel = r | g | b | a;
                // Split the color to 8-bits to push in the order of LE
                output.push((pixel & 0x00FF) as u8);
                output.push(((pixel & 0xFF00) >> 8) as u8);
            }
            // LA8
            5 => {
                output.push(tiled_data[input_offset + 3]);
                output.push(rgb8_to_luminance(tiled_data[input_offset], tiled_data[input_offset + 1], tiled_data[input_offset + 2]));
            }
            // HILO8
            6 => {
                output.push(tiled_data[input_offset + 1]);
                output.push(tiled_data[input_offset]);
            }
            // L8
            7 => {
                output.push(rgb8_to_luminance(tiled_data[input_offset], tiled_data[input_offset + 1], tiled_data[input_offset + 2]));
            }
            // A8
            8 => {
                output.push(tiled_data[input_offset + 3]);
            }
            // LA4
            9 => {
                let l = rgb8_to_luminance(tiled_data[input_offset], tiled_data[input_offset + 1], tiled_data[input_offset + 2]) & 0xF0;
                let a = convert_8_to_4(tiled_data[input_offset + 3]);
                output.push(l | a);
            }
            // L4
            10 => {
                // Override the loop
                for _input_offset in (0..tiled_data.len()).step_by(8) {
                    let l1 = convert_8_to_4(rgb8_to_luminance(tiled_data[_input_offset], tiled_data[_input_offset + 1], tiled_data[_input_offset + 2]));
                    let l2 = rgb8_to_luminance(tiled_data[_input_offset + 4 ], tiled_data[_input_offset + 5], tiled_data[_input_offset + 6]) & 0xF0;
                    output.push(l1 | l2);    
                }
                break;
            }
            // A4
            11 => {
                // Override the loop
                for _input_offset in (0..tiled_data.len()).step_by(8) {
                    let a1 = convert_8_to_4(tiled_data[_input_offset + 3]);
                    let a2 = data[_input_offset + 7] & 0xF0;
                    output.push(a1 | a2);
                }
                break;
            }
            _ => {
                Error::new(ErrorKind::Other, "Unsupported format");
                break;
            }
        }
    }
    Ok(output)
}

fn tile_data(pixel_data: &[u8], width: usize, height: usize) -> Vec<u8> {
    let mut tiled_data: Vec<u8> = Vec::new();
    for tile_y in (0..height).step_by(8) {
        for tile_x in (0..width).step_by(8) {
            for pixel in 0..64 {
                let x = (TILE_ORDER[pixel]  & 7) as usize;
                let y = (TILE_ORDER[pixel] as usize - x) >> 3;

                let input_offset = ((tile_x + x + ((tile_y + y) * width)) * 4) as usize;

                // R
                tiled_data.push(pixel_data[input_offset]);
                // G
                tiled_data.push(pixel_data[input_offset + 1]);
                // B
                tiled_data.push(pixel_data[input_offset + 2]);
                // A
                tiled_data.push(pixel_data[input_offset + 3]);
            }
        }
    }
    tiled_data
}

pub fn calculate_len(pixel_format: u32, height: usize, width: usize) -> usize {
    let bpp = match pixel_format {
        0x0 => 4.0,
        0x1 => 3.0,
        0x2 | 0x3 | 0x4 | 0x5 => 2.0,
        0x6 | 0x7 | 0x8 | 0x9 | 0xB | 0xD => 1.0,
        0xA | 0xC => 0.5,
        _ => panic!(Error::new(ErrorKind::Other, "Unsupported format"))
    };
    (bpp * height as f32 * width as f32) as usize
}

fn convert_8_to_1(pixel: u8) -> u8 {
    pixel >> 7
}

fn convert_8_to_4(pixel: u8) -> u8 {
    pixel >> 4
}

fn convert_8_to_5(pixel: u8) -> u8 {
    pixel >> 3
}

fn convert_8_to_6(pixel: u8) -> u8 {
    pixel >> 2
}

fn rgb8_to_luminance(r: u8, g: u8, b: u8) -> u8 {
    let mut l = (r as u32) << 1;
    l += ((g as u32) << 2) + (g as u32);
    l += b as u32;
    (l >> 3) as u8
}