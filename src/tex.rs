use std::io::{Cursor, SeekFrom, Seek, Read, Result, Error, ErrorKind};
use byteorder::{LittleEndian, ReadBytesExt};
use raster::Color;
use std::f64::*;


const ETC_DIFF_RED1_OFFSET: i32 = 59;
const ETC_DIFF_GREEN1_OFFSET: i32 = 51;
const ETC_DIFF_BLUE_OFFSET: i32 = 43;

const ETC_RED2_OFFSET: i32 = 56;
const ETC_GREEN2_OFFSET: i32 = 48;
const ETC_BLUE2_OFFSET: i32 = 40;

const ETC_TABLE1_OFFSET: i32 = 37;
const ETC_TABLE2_OFFSET: i32 = 34;

const ETC_DIFFERENTIAL_BIT: i32 = 33;

pub fn ETC1Decompress(data: &[u8], height: u16, width: u16) -> Result<Vec<u8>> {
    let ETC_MODIFIERS: [[i32; 2]; 8] = [
        [2, 8],
        [5, 17],
        [9, 29],
        [13, 42],
        [18, 60],
        [24, 80],
        [33, 106],
        [47, 183]
        ];

    let with_alpha = true;  // ETC1A4

    let block_size = 16;    // with alpha

    let pixel_data: Vec<u8> = Vec::with_capacity((width * height * 4) as usize);

    // assert_eq!(((height as f64) / 8.0).ceil(), (height as f64) / 8.0) as f64; hmm
    // (((height as f64) / 8.0).ceil())

    let tile_height = (1 << ((((height as f64) / 8.0).ceil()).log2().ceil() as i32)) as i32;
    let tile_width = (1 << ((((width as f64) / 8.0).ceil()).log2().ceil() as i32)) as i32;

    let mut pos = 0;

    for tile_y in 0..tile_height {
        for tile_x in 0..tile_width {

            for block_y in 0..2 {
                for block_x in 0..2 {
                    let block: Vec<u8> = Vec::new();
                    let alphas: Vec<u8> = Vec::new();
                //    let pixels: Vec<u8> = Vec::new();

                    let mut data_pos = pos;
                    pos += data_pos;

                    block.copy_from_slice(&data[data_pos..(data_pos + block_size)]);

                    // If w/ alpha, which there is

                    alphas.copy_from_slice(&block[0..8]);
                //    pixels.copy_from_slice(&block[8..]);
                    let mut reader = Cursor::new(&*block);
                    let mut pixels = reader.read_u64::<LittleEndian>()?;

                    let mut differential = (pixels >> ETC_DIFFERENTIAL_BIT) & 0x01 == 1;
                    let mut horizontal = (pixels >> ETC_DIFFERENTIAL_BIT) & 0x01 == 1;

                    let mut table1 = ETC_MODIFIERS[(pixels >> ETC_TABLE1_OFFSET) & 0x07];
                    let mut table2 = ETC_MODIFIERS[(pixels >> ETC_TABLE2_OFFSET) & 0x07];

                    let mut color1: Vec<u8> = vec![0, 0, 0];
                    let mut color2: Vec<u8> = vec![0, 0, 0];

                    if differential {
                        let mut r = ((pixels >> ETC_DIFF_RED1_OFFSET) & 0x1F) as u8;
                        let mut g = ((pixels >> ETC_DIFF_GREEN1_OFFSET) & 0x1F) as u8;
                        let mut b = ((pixels >> ETC_DIFF_BLUE_OFFSET) & 0x1F) as u8;

                        color1[0] = (r << 3) | ((r >> 2) & 0x07);
                        color1[1] = (g << 3) | ((g >> 2) & 0x07);
                        color1[2] = (b << 3) | ((b >> 2) & 0x07);

                        r += complement((pixels >> ETC_RED2_OFFSET) & 0x07, 3);
                        g += complement((pixels >> ETC_GREEN2_OFFSET) & 0x07, 3);
                        b += complement((pixels >> ETC_BLUE2_OFFSET) & 0x07, 3);

                        color2[0] = (r << 3) | ((r >> 2) & 0x07);
                        color2[1] = (g << 3) | ((g >> 2) & 0x07);
                        color2[2] = (b << 3) | ((b >> 2) & 0x07);


                    }
                    else {
                        color1[0] = ((pixels >> ETC_INDIV_RED1_OFFSET) & 0x0F) * 0x11;
                        color1[1] = ((pixels >> ETC_INDIV_GREEN1_OFFSET) & 0x0F) * 0x11;
                        color1[2] = ((pixels >> ETC_INDIV_BLUE1_OFFSET) & 0x0F) * 0x11;

                        color2[0] = ((pixels >> ETC_RED2_OFFSET) & 0x0F) * 0x11;
                        color2[1] = ((pixels >> ETC_GREEN2_OFFSET) & 0x0F) * 0x11;
                        color2[2] = ((pixels >> ETC_BLUE2_OFFSET) & 0x0F) * 0x11;
                    }

                    let mut amounts = pixels & 0xFFFF;
                    let mut signs = (pixels >> 16) & 0xFFFF;

                    for pixel_x in 0..4 {
                        for pixel_y in 0..4 {
                            let mut x = pixel_x + (block_x * 4) + (tile_y * 8);
                            let mut y = pixel_y + (block_y * 4) + (tile_y * 8);

                            if x >= width {
                                continue;
                            }
                            if y >= width {
                                continue;
                            }

                            let mut offset = pixel_x * 4 + pixel_y;

                            let mut table;
                            let mut color;
                            if horizontal {
                                if pixel_y < 2 { table = table1 } else {table = table2};
                                if pixel_y < 2 { color = color1} else {color = color2};
                            }
                            else {
                                if pixel_x < 2 { table = table1 } else {table = table2};
                                if pixel_x < 2 { color = color1} else {color = color2};
                            }
                            let mut amount = table[(amounts >> offset) & 0x01];
                            let mut sign = (signs >> offset) & 0x01;

                            if sign == 1 {
                                amount *= -1;
                            }

                            let mut red = max(min(color[0] + amount, 0xFF), 0)?;
                            let mut green = max(min(color[1] + amount, 0xFF), 0)?;
                            let mut blue = max(min(color[2] + amount, 0xFF), 0)?;
                            let mut alpha = ((alphas >> (offset * 4)) & 0x0F) * 0x11 as u8;

                            let mut pixel_pos = (y * width + x) * 4;
                            pixel_data[pixel_pos..(pixel_pos + 4)] = [red, green, blue, alpha];
                        }
                    }
                }
            }
        }
    }
    Ok(pixel_data);
}

fn complement(input: i32, bits: i32) -> Result<i32> {
    if input >> (bits - 1) == 0 { Ok(input);}
    else {Ok(input - (1 << bits));}
}

fn min(value1: u8, value2: u8) -> Result<u8> {
    if value1 > value2 {Ok(value2);}
    else {Ok(value1);}
}

fn max(value1: u8, value2: u8) -> Result<u8> {
    if value1 > value2 {Ok(value1);}
    else {Ok(value2);}
}