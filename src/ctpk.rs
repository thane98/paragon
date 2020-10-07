use crate::texture;
use byteorder::{LittleEndian, ReadBytesExt};
use std::io::prelude::BufRead;
use std::io::{Cursor, Result, Seek, SeekFrom, Error, ErrorKind, Read};
use encoding_rs::UTF_8;
use pyo3::prelude::*;

#[allow(dead_code)]
pub struct Header {
    pub magic_id: u32,
    pub version: u16,
    pub texture_count: u16,
    pub texture_ptr: u32,
    pub texture_length: u32,
    pub hash_ptr: u32,
    pub texture_short_info_ptr: u32,
}

impl Header {
    pub fn new(reader: &mut Cursor<&[u8]>) -> Result<Self> {
        let magic_id = reader.read_u32::<LittleEndian>()?;
        let version = reader.read_u16::<LittleEndian>()?;
        let texture_count = reader.read_u16::<LittleEndian>()?;
        let texture_ptr = reader.read_u32::<LittleEndian>()?;
        let texture_length = reader.read_u32::<LittleEndian>()?;
        let hash_ptr = reader.read_u32::<LittleEndian>()?;
        let texture_short_info_ptr = reader.read_u32::<LittleEndian>()?;
        reader.seek(SeekFrom::Current(0x8))?;    // Skip padding
        Ok(Header {
            magic_id,
            version,
            texture_count,
            texture_ptr,
            texture_length,
            hash_ptr,
            texture_short_info_ptr,
        })
    }
}

pub struct TextureInfo {
    pub filename_ptr: u32,
    pub texture_length: u32,
    pub texture_ptr: u32,
    pub pixel_format: u32,
    pub width: usize,
    pub height: usize,
    pub mipmap_level: u8,
    pub texture_type: u8,
    pub cube_dir: u16,
    pub bitmap_size_ptr: u32,
    pub file_time: u32,
}

impl TextureInfo {
    fn new(reader: &mut Cursor<&[u8]>) -> Result<Self> {
        let filename_ptr = reader.read_u32::<LittleEndian>()?;
        let texture_length = reader.read_u32::<LittleEndian>()?;
        let texture_ptr = reader.read_u32::<LittleEndian>()?;
        let pixel_format = reader.read_u32::<LittleEndian>()?;
        let width = reader.read_u16::<LittleEndian>()? as usize;
        let height = reader.read_u16::<LittleEndian>()? as usize;
        let mipmap_level = reader.read_u8()?;
        let texture_type = reader.read_u8()?;
        let cube_dir = reader.read_u16::<LittleEndian>()?;
        let bitmap_size_ptr = reader.read_u32::<LittleEndian>()?;
        let file_time = reader.read_u32::<LittleEndian>()?;
        Ok(TextureInfo {
            filename_ptr,
            texture_length,
            texture_ptr,
            pixel_format,
            width,
            height,
            mipmap_level,
            texture_type,
            cube_dir,
            bitmap_size_ptr,
            file_time
        })
    }
}

#[allow(dead_code)]
#[pyclass(module = "fefeditor2")]
pub struct Texture {
    pub filename: String,
    pub width: usize,
    pub height: usize,
    pub pixel_data: Vec<u8>,
    pub pixel_format: u32,
}

impl Texture {
    pub fn decode(&self) -> Result<Self> {
        let decoded_pixel_data =
        texture::decode_pixel_data(&self.pixel_data, self.width, self.height, self.pixel_format)?;
        Ok(Texture {
            filename: self.filename.clone(),
            width: self.width,
            height: self.height,
            pixel_data: decoded_pixel_data,
            pixel_format: self.pixel_format,
        })
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

pub fn read(file: &[u8]) -> Result<Vec<Texture>> {
    let mut reader = Cursor::new(file);

    let header = Header::new(&mut reader)?;

    // Read texture info
    let mut texture_info: Vec<TextureInfo> = Vec::new(); 
    for _ in 0..header.texture_count {
        texture_info.push( TextureInfo::new(&mut reader)?);   
    }

    // Read texture
    let mut texture: Vec<Texture> = Vec::new();
    for i in 0..header.texture_count as usize {
        // Read filename
        reader.seek(SeekFrom::Start(texture_info[i].filename_ptr as u64))?;
        let mut filename_buffer: Vec<u8> = Vec::new();
        reader.read_until(0x0, &mut filename_buffer)?;
        filename_buffer.pop(); // Get rid of the null terminator.
        let (result, _, errors) = UTF_8.decode(filename_buffer.as_slice());
        if errors {
            return Err(Error::new(
                ErrorKind::Other,
                "Failed to decode utf-8 string.",
            ));
        }
        let filename: String = result.into();

        // Read pixel data
        reader.seek(SeekFrom::Start((header.texture_ptr + texture_info[i].texture_ptr) as u64))?;
        let mut pixel_data: Vec<u8> = vec![0; texture::calculate_len(texture_info[i].pixel_format, texture_info[i].height, texture_info[i].width)];
        reader.read_exact(&mut pixel_data)?;

        let width = texture_info[i].width;
        let height = texture_info[i].height;
        let pixel_format = texture_info[i].pixel_format;
        texture.push(Texture {
            filename,
            width,
            height,
            pixel_data,
            pixel_format
        })
    }
   Ok(texture)

}