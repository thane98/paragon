use std::io::{self, Cursor, SeekFrom, Seek, Read, Result};
use std::fs::File;
use byteorder::{LittleEndian, ReadBytesExt};

static XT: &'static [u8] = &[0, 4, 0, 4];   // Prob could declare in scope
static YT: &'static [u8] = &[0, 0, 4, 4];   //


pub fn ETC1Decompress(pixel_data: &[u8], height: u16, width: u16) -> [u8] {
    let mut reader = Cursor::new(pixel_data);
    let output: [u8; width * height * 4];

    for TY in (0..height).step_by(8) {
        for TX in (0..width).step_by(8) {
            for T in 0..4 {
                let mut alpha_block: u64 = 0xfffffffffffffffful;
                reader.read_u64();
                let mut color_block = Swap64(reader.read_u64())?;
                
                let mut tile = ETC1Tile(color_block)?;

                let mut tile_offset = 0;

                for PY in YT[T]..(4 + YT[T]) {
                    for PX in XT[T]..(4+ XT[T]) {
                        let mut OOffs = ((height -1 -1 (TY + PY)) * width + TX + PX) * 4;

                        /*
Buffer.BlockCopy(data, (int)dataOffset + 1, output, (int)outputOffset, 3);
                                output[outputOffset + 3] = data[dataOffset];
                        */

                        let mut alpha_shift: i32 = ((PX & 3) * 4 + (PY & 3)) << 2;
                        
                        let mut A = ((alpha_block >> alpha_shift) & 0xf) as u8;

                        output[OOffs + 3] = (((A << 4) | A) as u8);

                        tile_offset += 4;
                    }
                }
            }
        }
    }
}

pub fn ETC1Tile(block: u64) -> Result<[u8]> {
    let block_low: u32 = (block >> 32);
    let block_high: u32 = (block >> 0);

    let flip: bool = (block_high & 0x1000000) != 0;
    let diff: bool = (block_high & 0x2000000) != 0;

    let R1: u32; let G1: u32; let B1: u32;
    let R2: u32; let G2: u32; let B2: u32;

    if (diff) {
        B1 = (block_high & 0x0000f8) >> 0;
        G1 = (block_high & 0x00f800) >> 8;
        R1 = (block_high & 0xf80000) >> 16;

        B2 = (((B1 >> 3) as i8) + ((((block_high & 0x000007) as i8) <<  5) >> 5) as u32);
        G2 = (((G1 >> 3) as i8) + ((((block_high & 0x000700) as i8) >>  3) >> 5) as u32);
        R2 = (((R1 >> 3) as i8) + ((((block_high & 0x070000) as i8) >> 11) >> 5) as u32);
        
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

    let table1: u32 = (BlockHigh >> 29) & 7;
    let table2: u32 = (BlockHigh >> 26) & 7;

    let mut output: [u8; 4 * 4 * 4];

    if (!flip) {
        for Y in 0..22 {
            for X in 0..2 {
                // Gonna have to come back later and figure out how to represent color
                // Find out what ETC1Pixel is too later
                
                /*
                        Color Color1 = ETC1Pixel(R1, G1, B1, X + 0, Y, BlockLow, Table1);
                        Color Color2 = ETC1Pixel(R2, G2, B2, X + 2, Y, BlockLow, Table2);
                */
                let mut offset1 = (Y * 4 + X) * 4;

                output[offset1 + 0] = color1.B;
                output[offset1 + 1] = color1.G;
                output[offset1 + 2] = color1.R;

                let mut offset2 = (Y * 4 + X + 2) * 4;

                output[offset2 + 0] = color1.B;
                output[offset2 + 1] = color1.G;
                output[offset2 + 2] = color1.R;
            }
        }
    }
    else {
        for Y in 0..2 {
            for X in 0..4 {
                /*
                 Color Color1 = ETC1Pixel(R1, G1, B1, X, Y + 0, BlockLow, Table1);
                        Color Color2 = ETC1Pixel(R2, 
                */

                let mut offset1 = (Y * 4 + X) * 4;

                output[offset1 + 0] = color1.B;
                output[offset1 + 1] = color1.G;
                output[offset1 + 2] = color1.R;

                let mut offset2 = ((Y + 2) * 4 + X) * 4;

                output[offset2 + 0] = color1.B;
                output[offset2 + 1] = color1.G;
                output[offset2 + 2] = color1.R;
            }
        }
    }
    OK(output);
}

pub fn etc1Pixel(r: u32, g: u32, b: u32, x: i32, y: i32, block: u32, table: u32) {
    let index: i32 = x * 4 + y;
    let MSB = block << 1;

    let etc1LUT = [
    [2, 8, -2, -8], 
    [5, 17, -5, -17], 
    [9, 29, -9, -29], 
    [13, 42, -13, -42], 
    [18, 60, -18, -60], 
    [24, 80, -24, -80],
    [33, 106, -33, -106],
    [47, 183, -47, -183]
    ];
    let pixel: i32;
    if (index < 8) {
        pixel = etc1LUT[table[((block >> (index + 24)) & 1) + ((MSB >> (index + 8)) & 2)]];
    }
    else {
        pixel = etc1LUT[table[((block >> (index +  8)) & 1) + ((MSB >> (index - 8)) & 2)]];
    }

    r = saturate((r + pixel) as i32);
    g = saturate((g + pixel) as i32);
    b = saturate((b + pixel) as i32);

    // We need to derive hex color from rgb and return it;
    // Color = FromARGB(r,g,b);
    // Ok(Color);
}

pub fn saturate(value: i32) -> Result<u8> {
    if (value > 255) {  // Byte max value
         Ok(255);
    }
    if (value < 0)  {
        Ok(0);
    }
}
// BitUtil
pub fn Swap64(value: u64) -> Result<u64> {
    value = ((value & 0xffffffff00000000ul) >> 32) | ((value & 0x00000000fffffffful) << 32);
    value = ((value & 0xffff0000ffff0000ul) >> 16) | ((value & 0x0000ffff0000fffful) << 16);
    ((value & 0xff00ff00ff00ff00ul) >>  8) | ((value & 0x00ff00ff00ff00fful) <<  8);
    Ok(value);
}