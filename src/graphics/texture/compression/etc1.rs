use std::io::{Cursor, Result};
use std::num::Wrapping;
use byteorder::{LittleEndian, ReadBytesExt};
use crate::ffi;
use core::{ptr, slice};

const ETC1_BLOCK_SIZE: usize = 8;
const ETC1A4_BLOCK_SIZE: usize = 16;

const ETC_INDIV_RED1_OFFSET: usize = 60;
const ETC_INDIV_GREEN1_OFFSET: usize = 52;
const ETC_INDIV_BLUE1_OFFSET: usize = 44;

const ETC_DIFF_RED1_OFFSET: usize = 59;
const ETC_DIFF_GREEN1_OFFSET: usize = 51;
const ETC_DIFF_BLUE1_OFFSET: usize = 43;

const ETC_RED2_OFFSET: usize = 56;
const ETC_GREEN2_OFFSET: usize = 48;
const ETC_BLUE2_OFFSET: usize = 40;

const ETC_TABLE1_OFFSET: usize = 37;
const ETC_TABLE2_OFFSET: usize = 34;

const ETC_DIFFERENTIAL_BIT: usize = 33;
const ETC_ORIENTATION_BIT: usize = 32;

fn get_etc_modifiers_table() -> Vec<Vec<i32>> {
    vec![
        vec![2, 8],
        vec![5, 17],
        vec![9, 29],
        vec![13, 42],
        vec![18, 60],
        vec![24, 80],
        vec![33, 106],
        vec![47, 183]
    ]
}

fn complement(input: u8, bits: u8) -> u8 {
    if input >> (bits - 1) == 0 {
        input
    }
    else {
        let input = Wrapping(input);
        let other = Wrapping(1 << bits);
        (input - other).0
    }
}

pub fn decompress(pixel_data: &[u8], width: usize, height: usize, with_alpha: bool) -> Result<Vec<u8>> {
    let mut bmp: Vec<u8> = Vec::new();
    bmp.resize(4 * width * height, 0);
    let modifiers = get_etc_modifiers_table();

    let tile_width: usize = 1 << (((width as f64) / 8.0).ceil().log2() as usize);
    let tile_height: usize = 1<< (((height as f64) / 8.0).ceil().log2() as usize);
    let mut pos = 0;
    for tile_y in 0..tile_height {
        for tile_x in 0..tile_width {
            for block_y in 0..2 {
                for block_x in 0..2 {
                    let data_pos = pos;
                    pos += if with_alpha {
                        ETC1A4_BLOCK_SIZE
                    }
                    else {
                        ETC1_BLOCK_SIZE
                    };

                    let block = if with_alpha {
                        &pixel_data[data_pos..data_pos + ETC1A4_BLOCK_SIZE]
                    }
                    else {
                        &pixel_data[data_pos..data_pos + ETC1_BLOCK_SIZE]
                    };
                    let mut cursor = Cursor::new(block);
                    let alphas = if with_alpha {
                        cursor.read_u64::<LittleEndian>()?
                    }
                    else {
                        0xFFFFFFFFFFFFFFFF
                    };
                    let pixels = cursor.read_u64::<LittleEndian>()?;

                    let differential = (pixels >> ETC_DIFFERENTIAL_BIT) & 1 == 1;
                    let horizontal = (pixels >> ETC_ORIENTATION_BIT) & 1 == 1;
                    let table1_index = (pixels >> ETC_TABLE1_OFFSET) & 7;
                    let table2_index = (pixels >> ETC_TABLE2_OFFSET) & 7;
                    let table1 = &modifiers[table1_index as usize];
                    let table2 = &modifiers[table2_index as usize];

                    let mut color1: Vec<u8> = vec![0, 0, 0];
                    let mut color2: Vec<u8> = vec![0, 0, 0];
                    if differential {
                        let r = ((pixels >> ETC_DIFF_RED1_OFFSET) & 0x1F) as u8;
                        let g = ((pixels >> ETC_DIFF_GREEN1_OFFSET) & 0x1F) as u8;
                        let b = ((pixels >> ETC_DIFF_BLUE1_OFFSET) & 0x1F) as u8;

                        color1[0] = (r << 3) | ((r >> 2) & 7);
                        color1[1] = (g << 3) | ((g >> 2) & 7);
                        color1[2] = (b << 3) | ((b >> 2) & 7);

                        let r_comp_input = ((pixels >> ETC_RED2_OFFSET) & 7) as u8;
                        let g_comp_input = ((pixels >> ETC_GREEN2_OFFSET) & 7) as u8;
                        let b_comp_input = ((pixels >> ETC_BLUE2_OFFSET) & 7) as u8;

                        let r2 = r + complement(r_comp_input, 3);
                        let g2 = g + complement(g_comp_input, 3);
                        let b2 = b + complement(b_comp_input, 3);

                        color2[0] = (r2 << 3) | ((r2 >> 2) & 7);
                        color2[1] = (g2 << 3) | ((g2 >> 2) & 7);
                        color2[2] = (b2 << 3) | ((b2 >> 2) & 7);
                    }
                    else {
                        color1[0] = (((pixels >> ETC_INDIV_RED1_OFFSET) & 0xF) * 0x11) as u8;
                        color1[1] = (((pixels >> ETC_INDIV_GREEN1_OFFSET) & 0xF) * 0x11) as u8;
                        color1[2] = (((pixels >> ETC_INDIV_BLUE1_OFFSET) & 0xF) * 0x11) as u8;
                    
                        color2[0] = (((pixels >> ETC_RED2_OFFSET) & 0xF) * 0x11) as u8;
                        color2[1] = (((pixels >> ETC_GREEN2_OFFSET) & 0xF) * 0x11) as u8;
                        color2[2] = (((pixels >> ETC_BLUE2_OFFSET) & 0xF) * 0x11) as u8;
                    }

                    let amounts = pixels & 0xFFFF;
                    let signs = (pixels >> 16) & 0xFFFF;

                    for pixel_y in 0..4 {
                        for pixel_x in 0..4 {
                            let x = pixel_x + (block_x * 4) + (tile_x * 8);
                            let y = pixel_y + (block_y * 4) + (tile_y * 8);

                            if x >= width || y >= height {
                                continue;
                            }

                            let offset = pixel_x * 4 + pixel_y;

                            let table = if horizontal {
                                if pixel_y < 2 { table1 } else { table2 }
                            }
                            else {
                                if pixel_x < 2 { table1 } else { table2 }
                            };
                            let color = if horizontal {
                                if pixel_y < 2 { &color1 } else { &color2 }
                            }
                            else {
                                if pixel_x < 2 { &color1 } else { &color2 }
                            };

                            let sign = (signs >> offset) & 1;
                            let amount = if sign == 1 {
                                table[((amounts >> offset) & 1) as usize] * -1
                            }
                            else {
                                table[((amounts >> offset) & 1) as usize]
                            };

                            let red = (color[0] as i32 + amount).min(0xFF).max(0) as u8;
                            let green = (color[1] as i32 + amount).min(0xFF).max(0) as u8;
                            let blue = (color[2] as i32 + amount).min(0xFF).max(0) as u8;
                            let alpha = (((alphas >> (offset * 4)) & 0xF) * 0x11) as u8;
                            let pixel_pos = (y * width + x) * 4;
                            bmp[pixel_pos] = red;
                            bmp[pixel_pos + 1] = green;
                            bmp[pixel_pos + 2] = blue;
                            bmp[pixel_pos + 3] = alpha;
                        }
                    }
                }
            }
        }
    }
    Ok(bmp)
}

// Can add compression options later
pub fn compress(pixel_data: &[u8], width: usize, height: usize, has_alpha: bool) -> Result<Vec<u8>> {
    let mut output_data: *mut u8 = core::ptr::null_mut();
    unsafe {
        ffi::etc1_encoder::encodeETC1(pixel_data.as_ptr(), &mut output_data, width as u16, height as u16, has_alpha);
    }
    let output_data_ptr: ptr::NonNull<u8> = ptr::NonNull::new(output_data)
        .expect("Error: got NULL ptr");
    let output_data_len = ((width * height * 4)/8) as usize;

    // Assign ptr to result
    let result: &mut [u8];
    unsafe {
        result = slice::from_raw_parts_mut(output_data_ptr.as_ptr(), output_data_len);
        // Free pointer from memory
        ffi::etc1_encoder::free_ptr(output_data_ptr.as_ptr());
     };
     Ok(result.to_vec())
}