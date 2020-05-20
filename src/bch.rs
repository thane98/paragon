use crate::etc1;
use byteorder::{LittleEndian, ReadBytesExt};
use encoding_rs::UTF_8;
use pyo3::prelude::*;
use std::io::prelude::*;
use std::io::{Cursor, Error, ErrorKind, Read, Result, Seek, SeekFrom};

static CONVERT_5_TO_8: &'static [u8] = &[
    0x00, 0x08, 0x10, 0x18, 0x20, 0x29, 0x31, 0x39, 0x41, 0x4A, 0x52, 0x5A, 0x62, 0x6A, 0x73, 0x7B,
    0x83, 0x8B, 0x94, 0x9C, 0xA4, 0xAC, 0xB4, 0xBD, 0xC5, 0xCD, 0xD5, 0xDE, 0xE6, 0xEE, 0xF6, 0xFF,
];

static TILE_ORDER: &'static [u8] = &[
    0, 1, 8, 9, 2, 3, 10, 11, 16, 17, 24, 25, 18, 19, 26, 27, 4, 5, 12, 13, 6, 7, 14, 15, 20, 21,
    28, 29, 22, 23, 30, 31, 32, 33, 40, 41, 34, 35, 42, 43, 48, 49, 56, 57, 50, 51, 58, 59, 36, 37,
    44, 45, 38, 39, 46, 47, 52, 53, 60, 61, 54, 55, 62, 63,
];

#[allow(dead_code)]
pub struct Header {
    magic_id: u32,
    backward_compatibility: u8,
    forward_compatibility: u8,
    version: u16,
    contents_address: u32,
    strings_address: u32,
    commands_address: u32,
    raw_data_address: u32,
    raw_ext_address: u32, // if BackwardCompatibility > 0x20
    relocation_address: u32,
    contents_length: u32,
    strings_length: u32,
    commands_length: u32,
    raw_data_length: u32,
    raw_ext_length: u32, // if BackwardCompatibility > 0x20
    relocation_length: u32,
    uninit_data_length: u32,
    uninit_commands_length: u32,
}
pub struct ContentTable {
    textures_ptr_table_offset: u32,
    textures_ptr_table_entries: u32,
}
#[allow(dead_code)]
#[pyclass(module = "fefeditor2")]
pub struct Texture {
    pub filename: String,
    pub height: usize,
    pub width: usize,
    pub pixel_data: Vec<u8>,
    pub pixel_format: u32,
}

fn decode_color(value: u32, format: u32) -> Vec<u8> {
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

fn decode_pixel_data(data: &[u8], width: usize, height: usize, format: u32) -> Result<Vec<u8>> {
    match format {
        0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 => {
            decode_rgba_pixel_data(data, width, height, format)
        }
        12 | 13 => etc1::decompress(data, width, height, format == 13),
        _ => Err(Error::new(ErrorKind::Other, "Unsupported texture format.")),
    }
}

pub fn read(file: &[u8]) -> Result<Vec<Texture>> {
    let mut reader = Cursor::new(file);

    let header = read_header(&mut reader)?;

    reader.seek(SeekFrom::Start(header.contents_address.into()))?;
    let content_table = read_content_table(&mut reader, header.contents_address)?;

    let mut bch: Vec<Texture> = Vec::new();

    for entry in 0..content_table.textures_ptr_table_entries {
        reader.seek(SeekFrom::Start(
            (content_table.textures_ptr_table_offset + entry * 4).into(),
        ))?;

        let dest = reader.read_u32::<LittleEndian>()?;
        reader.seek(SeekFrom::Start((dest + header.contents_address).into()))?;

        let tex_unit0_commands_offset = reader.read_u32::<LittleEndian>()? + header.commands_address;
        reader.seek(SeekFrom::Current(24))?;

        let name_offset = reader.read_u32::<LittleEndian>()?;

        // Read filename
        reader.seek(SeekFrom::Start(
            (header.strings_address + name_offset).into(),
        ))?;
        let mut filename_buffer: Vec<u8> = Vec::new();
        reader.read_until(0x0, &mut filename_buffer)?;
        filename_buffer.pop(); // Get rid of the null terminator.
        let (result, _, errors) = UTF_8.decode(filename_buffer.as_slice());
        if errors {
            return Err(Error::new(
                ErrorKind::Other,
                "Failed to decode utf-8 string.",
            )); // Shouldn't be any shift-jis characters
        }
        let filename: String = result.into();

        reader.seek(SeekFrom::Start(tex_unit0_commands_offset.into()))?;
        let height = reader.read_u16::<LittleEndian>()? as usize;
        let width = reader.read_u16::<LittleEndian>()? as usize;
        reader.seek(SeekFrom::Current(0xC))?;
        let data_offset = reader.read_u32::<LittleEndian>()? + header.raw_data_address;
        reader.seek(SeekFrom::Current(0x4))?;
        let pixel_format = reader.read_u32::<LittleEndian>()?;

        reader.seek(SeekFrom::Start(data_offset.into()))?;
        let mut pixel_data: Vec<u8> = vec![0; (get_pixel_format_bpp(pixel_format) * width as f32 * height as f32) as usize];
        reader.read_exact(&mut pixel_data)?;
        bch.push(Texture {
            filename,
            height,
            width,
            pixel_data,
            pixel_format,
        });
    }
    Ok(bch)
}

fn read_header(reader: &mut Cursor<&[u8]>) -> Result<Header> {
    let magic_id = reader.read_u32::<LittleEndian>()?;
    if magic_id != 0x484342 {
        return Err(Error::new(ErrorKind::Other, "Invalid magic number."));
    }
    let backward_compatibility = reader.read_u8()?;
    let forward_compatibility = reader.read_u8()?;
    let version = reader.read_u16::<LittleEndian>()?;
    let contents_address = reader.read_u32::<LittleEndian>()?;
    let strings_address = reader.read_u32::<LittleEndian>()?;
    let commands_address = reader.read_u32::<LittleEndian>()?;
    let raw_data_address = reader.read_u32::<LittleEndian>()?;
    let raw_ext_address = if backward_compatibility {reader.read_u32::<LittleEndian>()?} else {0};
    let relocation_address = reader.read_u32::<LittleEndian>()?;
    let contents_length = reader.read_u32::<LittleEndian>()?;
    let strings_length = reader.read_u32::<LittleEndian>()?;
    let commands_length = reader.read_u32::<LittleEndian>()?;
    let raw_data_length = reader.read_u32::<LittleEndian>()?;
    let raw_ext_length = if backward_compatibility > 0x20 {reader.read_u32::<LittleEndian>()?} else {0};
    let relocation_length = reader.read_u32::<LittleEndian>()?;
    let uninit_data_length = reader.read_u32::<LittleEndian>()?;
    let uninit_commands_length = reader.read_u32::<LittleEndian>()?;

    Ok(Header {
        magic_id,
        backward_compatibility,
        forward_compatibility,
        version,
        contents_address,
        strings_address,
        commands_address,
        raw_data_address,
        raw_ext_address,
        relocation_address,
        contents_length,
        strings_length,
        commands_length,
        raw_data_length,
        raw_ext_length,
        relocation_length,
        uninit_data_length,
        uninit_commands_length,
    })
}

fn read_content_table(reader: &mut Cursor<&[u8]>, contents_address: u32) -> Result<ContentTable> {
    reader.seek(SeekFrom::Start((contents_address + 0x24).into()))?;
    let textures_ptr_table_offset = reader.read_u32::<LittleEndian>()? + contents_address;
    let textures_ptr_table_entries = reader.read_u32::<LittleEndian>()?;

    Ok(ContentTable {
        textures_ptr_table_offset,
        textures_ptr_table_entries,
    })
}

fn get_pixel_format_bpp(pixel_format: u32) -> f32 {
    match pixel_format {
        0x0 => 4.0,
        0x1 => 3.0,
        0x2 | 0x3 | 0x4 | 0x5 => 2.0,
        0x6 | 0x7 | 0x8 | 0x9 | 0xB | 0xD => 1.0,
        0xA | 0xC => 0.5,
        _ => 0.0,
    }
}

#[pymethods]
impl Texture {
    fn get_filename(&self) -> &str {
        &self.filename
    }

    fn get_width(&self) -> usize {
        self.width
    }

    fn get_height(&self) -> usize {
        self.height
    }

    fn get_pixel_data(&self) -> &[u8] {
        &self.pixel_data
    }

    fn get_pixel_format(&self) -> u32 {
        self.pixel_format
    }
}

impl Texture {
    pub fn decode(&self) -> Result<Self> {
        let decoded_pixel_data =
            decode_pixel_data(&self.pixel_data, self.width, self.height, self.pixel_format)?;
        Ok(Texture {
            filename: self.filename.clone(),
            width: self.width,
            height: self.height,
            pixel_data: decoded_pixel_data,
            pixel_format: self.pixel_format,
        })
    }
}
