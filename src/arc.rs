use std::io::{Cursor, SeekFrom, Seek, Read, Result, };
use byteorder::{LittleEndian, ReadBytesExt};

const HEADER_SIZE : u32 = 0x20;

pub struct File {
    filename: str,
    bytes: [u8],
}
pub struct Header {
    file_archive_length: u32,
    metadata_ptr_table_offset: u32,
    file_count: u32,
    IsAwakening: bool,  // I have yet to look at awakening's structure
}

pub struct Metadata {
    filename_ptr: u32,
    index: u32,
    file_length: u32,
    file_ptr: u32,
}

// No repacking cause idk how important that would be since the py script exists + no compression yet 
pub fn unpack(archive: &[u8]) -> Result<Self> {
    let mut reader = Cursor::new(archive);
    let header = read_header(&mut reader)?;
    
    // Initialize array to store files
    let mut file: [File::new(); header.file_count];
    for count in 0..header.file_count {
        // Get metadata
        let mut metadata = read_metadata(&mut reader, count)?;

        // Get Filename
        reader.seek(SeekFrom::Start(metadata.filename_ptr));
        let mut filename = String::new();
        reader.read_to_string(&filename);

        // Get file bytes
        reader.seek(SeekFrom::Start(metadata.file_ptr));
        let mut bytes: [u8; metadata.file_length];
        reader.read_exact(&mut bytes)?;

        // Now store the files
        file = File {filename, bytes};
    }

}

fn read_header(reader: &mut Cursor<&[u8]>) -> Result<Header> {
    let file_archive_length = reader.read_u32::<LittleEndian>()?;
    let metadata_ptr_table_offset = reader.read_u32::<LittleEndian>() + HEADER_SIZE?;
    let file_count = reader.read_u32::<LittleEndian>()?;
    let IsAwakening: bool = reader.read_u8::<LittleEndian>()?;  // Not really a flag; just that Fates uses a 128 byte-alignment struct
    Ok(Header {
        file_archive_length,
        metadata_ptr_table_offset,
        file_count,
        IsAwakening,
    })
}

fn read_metadata(reader: &mut Cursor<&[u8]>, count: u32) -> Result<Metadata> {
    reader.seek(SeekFrom::Start(header.metadata_pointer_table_offset + 4 * count));
    let metadata_pointer = reader.read_u32::<LittleEndian>() + HEADER_SIZE?;
    reader.seek(SeekFrom::Start(metadata_pointer));

    let filename_ptr = reader.read_u32::<LittleEndian>() + HEADER_SIZE?;
    let index = reader.read_u32::<LittleEndian>()?; // Not necessary
    let file_length = reader.read_u32::<LittleEndian>()?;
    let file_ptr = (reader.read_u32::<LittleEndian>() + 0x80 + 0x7F) & - 0x7F?;  // Relative to 128 byte-alignment after header
    Ok(Metadata {
        filename_ptr,
        index,
        file_length,
        file_ptr,
    })
}
