use crate::texture;
use byteorder::{LittleEndian, ReadBytesExt};
use std::io::prelude::BufRead;
use std::io::{Cursor, Result, Seek, SeekFrom, Error, ErrorKind, Read};
use encoding_rs::UTF_8;
use pyo3::prelude::*;
// Source: https://www.3dbrew.org/wiki/CGFX

#[allow(dead_code)]
struct Header {
    magic_id: u32,
    byte_order_mark: u16,
    struct_size: u16,
    revision: u32,
    file_size: u32,
    entry_count: u32
}

impl Header {
    fn new(reader: &mut Cursor<&[u8]>) -> Result<Self> {
        let magic_id = reader.read_u32::<LittleEndian>()?;
        if magic_id != 0x58464743 {
            return Err(Error::new(ErrorKind::Other, "Invalid magic number."));
        }
        let byte_order_mark = reader.read_u16::<LittleEndian>()?;   // Redudant
        let struct_size = reader.read_u16::<LittleEndian>()?;
        let revision = reader.read_u32::<LittleEndian>()?;
        let file_size = reader.read_u32::<LittleEndian>()?;
        let entry_count = reader.read_u32::<LittleEndian>()?;

        Ok(Header {
            magic_id,
            byte_order_mark,
            struct_size,
            revision,
            file_size,
            entry_count
        })
    }
}

#[allow(dead_code)]
struct DATA {
    magic_id: u32,
    struct_size: u32,
    entry: Vec<DATAEntry>
}

impl DATA {
    fn new(reader: &mut Cursor<&[u8]>) -> Result<Self> {
        let magic_id = reader.read_u32::<LittleEndian>()?;
        let struct_size = reader.read_u32::<LittleEndian>()?;
        let mut entry: Vec<DATAEntry> = Vec::new();
        for _i in 0..16 {
            let entry_count = reader.read_u32::<LittleEndian>()?;
            let offset = reader.position() as u32 + reader.read_u32::<LittleEndian>()?;
            entry.push(DATAEntry {
                entry_count,
                offset
            });
        }
        Ok(DATA {
            magic_id,
            struct_size,
            entry
        })
    }
}

#[allow(dead_code)]
struct DATAEntry {
    entry_count: u32,
    offset: u32,
}

#[allow(dead_code)]	
struct DICT {
    pub magic_id: u32,
    pub struct_size: u32,
    pub entry_count: u32,
    pub entry: Vec<DICTEntry>
}

impl DICT {
    fn new(reader: &mut Cursor<&[u8]>) -> Result<Self> {
        let magic_id = reader.read_u32::<LittleEndian>()?;
        let struct_size = reader.read_u32::<LittleEndian>()?;
        let entry_count = reader.read_u32::<LittleEndian>()?;
        reader.seek(SeekFrom::Current(0x10))?;
        let mut entry: Vec<DICTEntry> = Vec::new();
        for _i in 0..entry_count {
            reader.seek(SeekFrom::Current(0x8))?;
            let filename_offset = reader.position() as u32 + reader.read_u32::<LittleEndian>()?;
            let object_offset = reader.position() as u32 + reader.read_u32::<LittleEndian>()?;
            entry.push(DICTEntry {
                filename_offset,
                object_offset
            })
        }
        Ok(DICT {
            magic_id,
            struct_size,
            entry_count,
            entry
        })
    }
}

#[allow(dead_code)]	
struct DICTEntry {
    pub filename_offset: u32,
    pub object_offset: u32,
}

// Binary Texture
#[allow(dead_code)]
struct TXOB {
    flags: u32,
    magic_id: u32,
    filename_offset: u32,
    height: usize,
    width: usize,
    mipmap_levels: u32,
    pixel_format: u32,
    size: usize,
    texture_offset: u32,
}

impl TXOB {
    fn new(reader: &mut Cursor<&[u8]>, dict: DICT) -> Result<Vec<TXOB>> {
        let mut txob: Vec<TXOB> = Vec::new();
        for i in 0.. dict.entry_count as usize {
            reader.seek(SeekFrom::Start(dict.entry[i].object_offset as u64))?;
            let flags = reader.read_u32::<LittleEndian>()?;
            let magic_id = reader.read_u32::<LittleEndian>()?;
            reader.seek(SeekFrom::Current(0x4))?;
            let filename_offset = reader.position() as u32 + reader.read_u32::<LittleEndian>()?;
            reader.seek(SeekFrom::Current(0x8))?;
            let height = reader.read_u32::<LittleEndian>()? as usize;
            let width = reader.read_u32::<LittleEndian>()? as usize;
            reader.seek(SeekFrom::Current(0x8))?;
            let mipmap_levels = reader.read_u32::<LittleEndian>()?;
            reader.seek(SeekFrom::Current(0x8))?;
            let pixel_format = reader.read_u32::<LittleEndian>()?;
            reader.seek(SeekFrom::Current(0xC))?;
            let size = reader.read_u32::<LittleEndian>()? as usize;
            let texture_offset = reader.position() as u32 + reader.read_u32::<LittleEndian>()?;
            txob.push(TXOB {
                flags,
                magic_id,
                filename_offset,
                height,
                width,
                mipmap_levels,
                pixel_format,
                size,
                texture_offset
            });
        }
        Ok(txob)
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

impl Texture {
    fn new(reader: &mut Cursor<&[u8]>, txob: Vec<TXOB>) -> Result<Vec<Texture>> {
        let mut textures: Vec<Texture> = Vec::new();
        // Read pixel data
        for txob_file in txob {
            let mut pixel_data: Vec<u8> = vec![0; txob_file.size];
            reader.seek(SeekFrom::Start(txob_file.texture_offset as u64))?;
            reader.read_exact(&mut pixel_data)?;
    
            // Read filename
            reader.seek(SeekFrom::Start(txob_file.filename_offset as u64))?;
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
            let width = txob_file.width;
            let height = txob_file.height;
            let pixel_format = txob_file.pixel_format;
            textures.push(Texture {
                filename,
                width,
                height,
                pixel_data,
                pixel_format
            });
        }
        Ok(textures)
    }
}

pub fn read(file: &[u8]) -> Result<Vec<Texture>> {
    let mut reader = Cursor::new(file);
    
    let _header = Header::new(&mut reader)?;
    let data = DATA::new(&mut reader)?;

    // Going to skip a recursive loop of DICT and just access the texture entry;
    reader.seek(SeekFrom::Start(data.entry[1].offset as u64))?;
    let dict = DICT::new(&mut reader)?;
    let txob = TXOB::new(&mut reader, dict)?;
    let texture = Texture::new(&mut reader, txob)?;
    Ok(texture)
}