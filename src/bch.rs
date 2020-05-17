use std::io::prelude::*;
use std::io::{Cursor, SeekFrom, Seek, Read, Result, Error, ErrorKind};
use byteorder::{LittleEndian, ReadBytesExt};
use encoding_rs::UTF_8;
use pyo3::prelude::*;

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
    raw_ext_address: u32,             // if BackwardCompatibility > 0x20
    relocation_address: u32,
    contents_length: u32,
    strings_length: u32,
    commands_length: u32,
    raw_data_length: u32,
    raw_ext_length: u32,              // if BackwardCompatibility > 0x20
    relocation_length: u32,
    uninit_data_length: u32,
    uninit_commands_length: u32,
}
pub struct ContentTable {
    textures_ptr_table_offset: u32,
    textures_ptr_table_entries: u32,
}
#[allow(dead_code)]
#[pyclass (module="fefeditor2")]
pub struct Texture {
    pub filename: String,
    pub height: usize,
    pub width: usize,
    pub pixel_data: Vec<u8>,
    pixel_format: u32,
}

pub fn read(file: &[u8]) -> Result<Vec<Texture>> {
    let mut reader = Cursor::new(file);

    let header = read_header(&mut reader)?;

    reader.seek(SeekFrom::Start(header.contents_address.into()))?;
    let content_table = read_content_table(&mut reader, header.contents_address)?;

    let mut bch: Vec<Texture> = Vec::new();

    for entry in 0..content_table.textures_ptr_table_entries {
        reader.seek(SeekFrom::Start((content_table.textures_ptr_table_offset + entry * 4).into()))?;

        let dest = reader.read_u32::<LittleEndian>()?;
        reader.seek(SeekFrom::Start((dest + header.contents_address).into()))?;

        let tex_unit0_commands_offset = reader.read_u32::<LittleEndian>()? + header.commands_address;
        reader.seek(SeekFrom::Current(20))?;
        // let tex_unit0_commands_word_count = reader.read_u32::<LittleEndian>()?;
        // let tex_unit1_commands_offset = reader.read_u32::<LittleEndian>()? + header.commands_address;
        // let tex_unit1_commands_word_count = reader.read_u32::<LittleEndian>()?;
        // let tex_unit2_commands_offset = reader.read_u32::<LittleEndian>()? + header.commands_address;
        // let tex_unit2_commands_word_count = reader.read_u32::<LittleEndian>()?;
        reader.read_u32::<LittleEndian>()?; // Don't know; might look at spica
        let name_offset = reader.read_u32::<LittleEndian>()?;

        // Read filename
        reader.seek(SeekFrom::Start((header.strings_address + name_offset).into()))?;
        let mut filename_buffer: Vec<u8> = Vec::new();
        reader.read_until(0x0, &mut filename_buffer)?;
        filename_buffer.pop(); // Get rid of the null terminator.
        let (result, _, errors) = UTF_8.decode(filename_buffer.as_slice());
        if errors {
            return Err(Error::new(ErrorKind::Other, "Failed to decode utf-8 string."))  // Shouldn't be any shift-jis characters
        }
        let filename: String = result.into();

        reader.seek(SeekFrom::Start(tex_unit0_commands_offset.into()))?;
        let height = reader.read_u16::<LittleEndian>()? as usize;
        let width = reader.read_u16::<LittleEndian>()? as usize;
        reader.seek(SeekFrom::Current(0xC))?;        // I'm so crippled after this
        let data_offset = reader.read_u32::<LittleEndian>()? + header.raw_data_address;
        reader.read_u32::<LittleEndian>()?; // Don't know; might look at spica
        let pixel_format = reader.read_u32::<LittleEndian>()?;

        if pixel_format != 0xD {
            return Err(Error::new(ErrorKind::Other, "Texture format not supported"))
        }

        // Everything for FE:IF is ETC1A4... so we can just calculate file length based on BPP; no implementing redudant cases for this game
        reader.seek(SeekFrom::Start(data_offset.into()))?;
        let mut pixel_data: Vec<u8> = vec![0; width * height];
        reader.read_exact(&mut pixel_data)?;
        bch.push(Texture {filename, height, width, pixel_data, pixel_format});
    }
    Ok(bch)
}

fn read_header(reader: &mut Cursor<&[u8]>) -> Result<Header> {
    let mut raw_ext_address = 0;
    let mut raw_ext_length = 0;

    let magic_id = reader.read_u32::<LittleEndian>()?;
    if magic_id != 0x484342 {
        return Err(Error::new(ErrorKind::Other, "Invalid magic number."))
    }
    let backward_compatibility = reader.read_u8()?;
    let forward_compatibility = reader.read_u8()?;
    let version = reader.read_u16::<LittleEndian>()?;
    let contents_address = reader.read_u32::<LittleEndian>()?;
    let strings_address = reader.read_u32::<LittleEndian>()?;
    let commands_address = reader.read_u32::<LittleEndian>()?;
    let raw_data_address = reader.read_u32::<LittleEndian>()?;
    if backward_compatibility > 0x20 {
        raw_ext_address = reader.read_u32::<LittleEndian>()?;
    }
    let relocation_address = reader.read_u32::<LittleEndian>()?;
    let contents_length = reader.read_u32::<LittleEndian>()?;
    let strings_length = reader.read_u32::<LittleEndian>()?;
    let commands_length = reader.read_u32::<LittleEndian>()?;
    let raw_data_length = reader.read_u32::<LittleEndian>()?;
    if backward_compatibility > 0x20 {
        raw_ext_length = reader.read_u32::<LittleEndian>()?;
    }
    let relocation_length = reader.read_u32::<LittleEndian>()?;
    let uninit_data_length = reader.read_u32::<LittleEndian>()?;
    let uninit_commands_length = reader.read_u32::<LittleEndian>()?;

    Ok(Header{
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
    
    Ok(ContentTable{
        textures_ptr_table_offset,
        textures_ptr_table_entries,
    })
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
}