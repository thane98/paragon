use std::io::prelude::*;
use std::io::{self, Cursor, SeekFrom, Seek, Read, Result};
use std::fs::File;
use byteorder::{LittleEndian, ReadBytesExt};
use std::vec;

pub struct Header {
    magic_ID: str,
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
    unInit_data_length: u32,
    unInit_commands_length: u32,
}
pub struct ContentTable {
    textures_ptr_table_offset: u32,
    textures_ptr_table_entries: u32,
}
pub struct Texture {
    filename: Vec<u8>,
    height: u32,
    width: u32,
    pixel_data: [u8],
    pixel_Format: u32,
}

pub fn Read(file: &[u8]) -> Result<Vec<Texture>> {
    let mut reader = Cursor::new(file);

    let header = read_header(reader)?;

    reader.seek(SeekFrom::Start(header.contents_address));
    let content_table = read_content_table(reader, header.contents_address)?;

    let mut bch: [Texture; content_table.textures_ptr_table_entries];

    for entry in 0..content_table.textures_ptr_table_entries {
        reader.seek(SeekFrom::Start(content_table.textures_ptr_table_offset + entry * 4));
        reader.seek(SeekFrom::Start(reader.read_u32::<LittleEndian>() + header.contents_address));

        let mut tex_unit0_commands_offset = reader.read_u32::<LittleEndian>() + header.commands_address?;
        let mut tex_unit0_commands_word_count = reader.read_u32::<LittleEndian>()?;
        let mut tex_unit1_commands_offset = reader.read_u32::<LittleEndian>() + header.commands_address?;
        let mut tex_unit1_commands_word_count = reader.read_u32::<LittleEndian>()?;
        let mut tex_unit2_commands_offset = reader.read_u32::<LittleEndian>() + header.commands_address?;
        let mut tex_unit2_commands_word_count = reader.read_u32::<LittleEndian>()?;
        reader.read_u32::<LittleEndian>()?; // Don't know; might look at spica
        let mut name_offset = reader.read_u32::<LittleEndian>()?;

        // Read filename
        reader.seek(SeekFrom::Start(header.strings_address + name_offset));
        let mut filename_buffer: Vec<u8> = Vec::new();
        reader.read_until(0x0, &mut filename_buffer)?;
        let (result, _, errors) = SHIFT_JIS.decode(filename_buffer.as_slice());
        if errors {
            return Err(Error::new(ErrorKind::Other, "Failed to decode shift-jis string."))  // Shouldn't be any shift-jis characters
        }
        let mut filename = result.into();

        reader.seek(SeekFrom::Start(tex_unit0_commands_offset));
        let mut height = reader.read_u16::<LittleEndian>()?;
        let mut width = reader.read_u16::<LittleEndian>()?;
        reader.seek(SeekFrom::Current() + 0xC);        // I'm so crippled after this
        let mut data_offset = reader.read_u32::<LittleEndian>() + header.raw_data_address?;
        reader.read_u32::<LittleEndian>()?; // Don't know; might look at spica
        let mut pixel_Format = reader.read_u32::<LittleEndian>()?;

        if (pixel_Format != 0xD)
        {
            Err("Texture format not supported");
        }
        // Everything for FE:IF is ETC1A4... so we can just calculate file length based on BPP; no implementing redudant cases for this game
        reader.seek(SeekFrom::Start(data_offset));
        let mut pixel_data = Vec::with_capacity(width * height);
        reader.read_exact(pixel_data);
        bch[entry] = Texture {filename, height, width, pixel_data, pixel_Format};
    }    
}

fn read_header(reader: &mut Cursor<[u8]>) -> Result<Header> {
    let mut raw_ext_address = 0;
    let mut raw_ext_length = 0;

    let magic_ID: String = reader.read_u32::<LittleEndian>()?;
    if (magic_ID != "BCH") {
        Err("Invalid BCH file");
    }
    let backward_compatibility = reader.read_u32::<LittleEndian>()?;
    let forward_compatibility = reader.read_u32::<LittleEndian>()?;
    let version = reader.read_u16()?;
    let contents_address = reader.read_u32::<LittleEndian>()?;
    let strings_address = reader.read_u32::<LittleEndian>()?;
    let commands_address = reader.read_u32::<LittleEndian>()?;
    let raw_data_address = reader.read_u32::<LittleEndian>()?;
    if (backward_compatibility > 0x20) {
        raw_ext_address = reader.read_u32::<LittleEndian>()?;
    }
    let relocation_address = reader.read_u32::<LittleEndian>()?;
    let contents_length = reader.read_u32::<LittleEndian>()?;
    let strings_length = reader.read_u32::<LittleEndian>()?;
    let commands_length = reader.read_u32::<LittleEndian>()?;
    let raw_data_length = reader.read_u32::<LittleEndian>()?;
    if (backward_compatibility > 0x20){
        raw_ext_length = reader.read_u32::<LittleEndian>()?;
    }
    let relocation_length = reader.read_u32::<LittleEndian>()?;
    let unInit_data_length = reader.read_u32::<LittleEndian>()?;
    let unInit_commands_length = reader.read_u32::<LittleEndian>()?;

    Ok(Header{
        magic_ID,
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
        unInit_data_length,
        unInit_commands_length,
    })
}

fn read_content_table(reader: &mut Cursor<[u8]>, contents_address: u32) -> Result<ContentTable> {
    reader.seek(SeekFrom::Start(contents_address + 0x24));
    let textures_ptr_table_offset = reader.read_u32::<LittleEndian>() + contents_address?;
    let textures_ptr_table_entries = reader.read_u32::<LittleEndian>()?;
    
    Ok(ContentTable{
        textures_ptr_table_offset,
        textures_ptr_table_entries,
    })
}