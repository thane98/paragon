use std::io::{Cursor, Result};
use byteorder::{LittleEndian, ReadBytesExt};
use raster::Color;

pub fn ETC1Decompress(pixel_data: &[u8], height: u16, width: u16) -> Result<Vec<u8>> {
    let mut reader = Cursor::new(pixel_data);
    let mut output: Vec<u8> = Vec::with_capacity((width * height * 4) as usize);
    
    let XT: Vec<u8> = vec![0, 4, 0, 4];
    let YT: Vec<u8> = vec![0, 0, 4, 4];
    // Texture is 8x8 tiles
    for TY in (0..height).step_by(8) {
        for TX in (0..width).step_by(8) {
            // ETC1 tiles are 2x2 compressed sub-titles 
            for T in 0..4 {
                // let mut alpha_block: u64 = 0xffffffffffffffff;
                
                let mut alpha_block;    // If there's alpha, which there is 
                
                let mut color_block = Swap64(reader.read_u64::<LittleEndian>()?)?;
                
                let mut tile = ETC1Tile(color_block)?;

                let mut tile_offset = 0;

                for PY in YT[T]..(4 + YT[T]) {
                    for PX in XT[T]..(4+ XT[T]) {
                        let mut OOffs = (((height - 1 - (TY + PY)) * width + TX + PX) * 4) as i32;

                        output[OOffs..(OOffs+3)].copy_from_slice(&tile[tile_offset..(tile_offset+3)]);

                        let mut alpha_shift: i32 = ((PX & 3) * 4 + (PY & 3)) << 2;
                        
                        let mut A = ((alpha_block >> alpha_shift) & 0xf) as u8;

                        output[OOffs + 3] = ((A << 4) | A) as u8;

                        tile_offset += 4;
                    }
                }
            }
        }
    }
    Ok(output);
}

pub fn ETC1Tile(block: u64) -> Result<Vec<u8>> {
    let block_low = (block >> 32) as u32;
    let block_high = (block >> 0) as u32;

    let flip = ((block_high & 0x1000000) != 0) as bool;
    let diff = ((block_high & 0x2000000) != 0) as bool;

    let R1: u32; let G1: u32; let B1: u32;
    let R2: u32; let G2: u32; let B2: u32;

    if (diff) {
        B1 = (block_high & 0x0000f8) >> 0;
        G1 = (block_high & 0x00f800) >> 8;
        R1 = (block_high & 0xf80000) >> 16;

        B2 = (((B1 >> 3) as i8) + (((block_high & 0x000007) << 5) as i8) >> 5) as u32; 
        B2 = (((B1 >> 3) as i8) + (((block_high & 0x000007) << 5) as i8) >> 5) as u32;
        G2 = (((G1 >> 3) as i8) + (((block_high & 0x000700) >> 3) as i8) >> 5) as u32;
        R2 = (((R1 >> 3) as i8) + (((block_high & 0x070000) >> 11) as i8) >> 5) as u32;
        
        B1 |= B1 >> 5;
        G1 |= G1 >> 5;
        R1 |= R1 >> 5;

        B2 = (B2 << 3) | (B2 >> 2);
        G2 = (G2 << 3) | (G2 >> 2);
        R2 = (R2 << 3) | (R2 >> 2);
    }
    else
    {
        B1 = (block_high & 0x0000f0) >> 0;
        G1 = (block_high & 0x00f000) >> 8;
        R1 = (block_high & 0xf00000) >> 16;

        B2 = (block_high & 0x00000f) << 4;
        G2 = (block_high & 0x000f00) >> 4;
        R2 = (block_high & 0x0f0000) >> 12;

        B1 |= B1 >> 4;
        G1 |= G1 >> 4;
        R1 |= R1 >> 4;

        B2 |= B2 >> 4;
        G2 |= G2 >> 4;
        R2 |= R2 >> 4;
    }

    let table1= (block_high >> 29) & 7;
    let table2 = (block_high >> 26) & 7;

    let output: Vec<u8> = Vec::with_capacity(64);    // 4^3 bit

    if !flip {
        for Y in 0..4 {
            for X in 0..2 {

                let mut color1 = etc1Pixel(R1, G1, B1, X + 0, Y, block_low, table1)?;
                let mut color2 = etc1Pixel(R1, G1, B1, X + 2, Y, block_low, table2)?;
                
                let mut offset1 = (Y * 4 + X) * 4;

                // I DONT'T UNDERSTAND
                output[offset1 + 0] = color1.b;
                output[offset1 + 1] = color1.g;
                output[offset1 + 2] = color1.r;

                let mut offset2 = (Y * 4 + X + 2) * 4;

                // I DON"T UNDERSTAND
                output[offset2 + 0] = color1.b;
                output[offset2 + 1] = color1.g;
                output[offset2 + 2] = color1.r;
            }
        }
    }
    else {
        for Y in 0..2 {
            for X in 0..4 {
                let mut color1 = etc1Pixel(R1, G1, B1, X, Y + 0, block_low, table1)?;
                let mut color2 = etc1Pixel(R1, G1, B1, X, Y + 2, block_low, table2)?;
                
                let mut offset1 = (Y * 4 + X) * 4;

                // I DON"T UNDERSTAND
                output[offset1 + 0] = color1.b;
                output[offset1 + 1] = color1.g;
                output[offset1 + 2] = color1.r;

                let mut offset2 = ((Y + 2) * 4 + X) * 4;

                // I DON"T UNDERSTAND
                output[offset2 + 0] = color1.b;
                output[offset2 + 1] = color1.g;
                output[offset2 + 2] = color1.r;
            }
        }
    }
    Ok(output);
}

pub fn etc1Pixel(r: u32, g: u32, b: u32, x: i32, y: i32, block: u32, table: u32) -> Result<Color> {
    let ETC1LUT: [[i32; 4]; 8] = [
        [2, 8, -2, -8], 
        [5, 17, -5, -17], 
        [9, 29, -9, -29], 
        [13, 42, -13, -42], 
        [18, 60, -18, -60], 
        [24, 80, -24, -80],
        [33, 106, -33, -106],
        [47, 183, -47, -183]
        ];
    
    let index = x * 4 + y;
    let MSB = block << 1;

    let pixel: i32;
    if index < 8 {
        // ???
        pixel = ETC1LUT[table][((block >> (index + 24)) & 1) + ((MSB >> (index + 8)) & 2)];
    }
    else {
        // ???
        pixel = ETC1LUT[table][((block >> (index +  8)) & 1) + ((MSB >> (index - 8)) & 2)];
    }

    // ??
    r = saturate((r + pixel) as i32);
    g = saturate((g + pixel) as i32);
    b = saturate((b + pixel) as i32);

    let color = Color::rgb(r as u8, g as u8, b as u8);    // If bug try rgba with 255 for alpha
    Ok(color);
}

// UGH
pub fn saturate(value: i32) -> Result<u8> {
    if value > 255 {  // Byte max value
         Ok(255);
    }
    if value < 0  {
        Ok(0);
    }
}
// BitUtil
pub fn Swap64(value: u64) -> Result<u64> {
    value = ((value & 0xffffffff00000000) >> 32) | ((value & 0x00000000ffffffff) << 32);
    value = ((value & 0xffff0000ffff0000) >> 16) | ((value & 0x0000ffff0000ffff) << 16);
    ((value & 0xff00ff00ff00ff00) >>  8) | ((value & 0x00ff00ff00ff00ff) <<  8);
    Ok(value);
}