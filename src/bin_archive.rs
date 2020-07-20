use std::vec::Vec;
use std::collections::HashMap;
use std::io::{Cursor, Result, Error, ErrorKind, Read, Seek, SeekFrom, Write};
use byteorder::{LittleEndian, ReadBytesExt, WriteBytesExt};
use linked_hash_map::LinkedHashMap;
use encoding_rs::SHIFT_JIS;
use pyo3::prelude::*;

#[pyclass (module="fefeditor2")]
#[derive (Debug, Clone)]
pub struct BinArchive {
    data: Vec<u8>,
    text_pointers: HashMap<usize, String>,
    mapped_pointers: HashMap<usize, Vec<String>>,
    internal_pointers: HashMap<usize, usize>,
}

struct BinArchiveHeader {
    file_size: u32,
    data_size: u32,
    normal_pointer_count: u32,
    mapped_pointer_count: u32,
}

struct NormalPointers {
    text_pointers: HashMap<usize, String>,
    internal_pointers: HashMap<usize, usize>,
}

struct SerializationState {
    raw_text: Vec<u8>,
    written_text_offsets: HashMap<String, usize>,
    raw_pointers: Vec<u32>,
    raw_mapped: Vec<u32>,
}

fn read_header(reader: &mut Cursor<&[u8]>) -> Result<BinArchiveHeader> {
    let file_size = reader.read_u32::<LittleEndian>()?;
    let data_size = reader.read_u32::<LittleEndian>()?;
    let normal_pointer_count = reader.read_u32::<LittleEndian>()?;
    let mapped_pointer_count = reader.read_u32::<LittleEndian>()?;
    Ok(BinArchiveHeader{
        file_size,
        data_size,
        normal_pointer_count,
        mapped_pointer_count
    })
}

fn validate_header(header: &BinArchiveHeader, raw_archive: &[u8]) -> Result<()> {
    if header.file_size as usize != raw_archive.len() {
        return Err(Error::new(ErrorKind::Other, "Header and data disagree on archive size."))
    }
    Ok(())
}

fn read_data(header: &BinArchiveHeader, reader: &mut Cursor<&[u8]>) -> Result<Vec<u8>> {
    let mut data = Vec::new();
    data.resize(header.data_size as usize, 0);
    reader.read_exact(data.as_mut_slice())?;
    Ok(data)
}

fn read_string(reader: &mut Cursor<&[u8]>, addr: u64) -> Result<String> {
    let end_addr = reader.position();
    reader.seek(SeekFrom::Start(addr))?;
    let mut buffer: Vec<u8> = Vec::new();
    let mut next = reader.read_u8()?;
    while next != 0 {
        buffer.push(next);
        next = reader.read_u8()?;
    }

    let (result, _enc, errors) = SHIFT_JIS.decode(buffer.as_slice());
    if errors {
        return Err(Error::new(ErrorKind::Other, "Unable to decode shift-jis string."))
    }
    reader.seek(SeekFrom::Start(end_addr))?;
    Ok(result.into())
}

fn read_normal_pointers(header: &BinArchiveHeader, reader: &mut Cursor<&[u8]>) -> Result<NormalPointers> {
    let mut normal_pointers = NormalPointers {
        text_pointers: HashMap::new(),
        internal_pointers: HashMap::new(),
    };
    let text_start = header.data_size
        + header.normal_pointer_count * 4
        + header.mapped_pointer_count * 8;
    for _i in 0..header.normal_pointer_count {
        let ptr = reader.read_u32::<LittleEndian>()?;
        let end_addr = reader.position();
        reader.seek(SeekFrom::Start((ptr + 0x20) as u64))?;
        let data_ptr = reader.read_u32::<LittleEndian>()?;
        if data_ptr >= text_start {
            normal_pointers.text_pointers.insert(
                ptr as usize,
                read_string(reader, (data_ptr + 0x20) as u64)?
            );
        }
        else {
            normal_pointers.internal_pointers.insert(ptr as usize, data_ptr as usize);
        }
        reader.seek(SeekFrom::Start(end_addr))?;
    }
    Ok(normal_pointers)
}

fn read_mapped_pointers(header: &BinArchiveHeader, reader: &mut Cursor<&[u8]>) -> Result<HashMap<usize, Vec<String>>> {
    let mut mapped_pointers: HashMap<usize, Vec<String>> = HashMap::new();
    let text_start = header.data_size
        + header.normal_pointer_count * 4
        + header.mapped_pointer_count * 8
        + 0x20;
    for _i in 0..header.mapped_pointer_count {
        let ptr = reader.read_u32::<LittleEndian>()? as usize;
        let text_ptr = text_start + reader.read_u32::<LittleEndian>()?;
        let text = read_string(reader, text_ptr as u64)?;
        if mapped_pointers.contains_key(&ptr) {
            let ptrs = mapped_pointers.get_mut(&ptr).unwrap();
            ptrs.push(text);
        }
        else {
            let mut ptrs: Vec<String> = Vec::new();
            ptrs.push(text);
            mapped_pointers.insert(ptr, ptrs);
        }
    }
    Ok(mapped_pointers)
}

fn adjust_pointer(orig: usize, addr: usize, amount: isize) -> usize {
    if orig >= addr { ((orig as isize) + amount) as usize } else { orig }
}

impl SerializationState {
    pub fn try_add_text(&mut self, text: &str) -> u32 {
        if self.written_text_offsets.contains_key(text) {
            return *self.written_text_offsets.get(text).unwrap() as u32
        }

        let offset = self.raw_text.len();
        let (result, _enc, _errors) = SHIFT_JIS.encode(text);
        let bytes = result.to_vec();
        for byte in bytes {
            self.raw_text.push(byte);
        }
        self.raw_text.push(0);
        self.written_text_offsets.insert(text.into(), offset);
        offset as u32
    }
}

impl BinArchive {
    pub fn new() -> Self {
        BinArchive {
            data: Vec::new(),
            text_pointers: HashMap::new(),
            mapped_pointers: HashMap::new(),
            internal_pointers: HashMap::new(),
        }
    }

    pub fn from_raw_archive(raw_archive: &[u8]) -> Result<Self> {
        let mut reader = Cursor::new(raw_archive);
        let header = read_header(&mut reader)?;
        validate_header(&header, raw_archive)?;
        reader.seek(SeekFrom::Start(0x20))?;

        let data = read_data(&header, &mut reader)?;
        let normal_pointers = read_normal_pointers(&header, &mut reader)?;
        let mapped_pointers = read_mapped_pointers(&header, &mut reader)?;
        Ok(BinArchive {
            data,
            text_pointers: normal_pointers.text_pointers,
            mapped_pointers,
            internal_pointers: normal_pointers.internal_pointers,
        })
    }

    fn process_internal_pointers(&mut self, state: &mut SerializationState) {
        let mut pointers: Vec<(&usize, &usize)> = self.internal_pointers.iter().collect();
        pointers.sort_by(|a, b| a.0.cmp(b.0));
        for pointer_pair in pointers {
            let mut cursor = Cursor::new(&mut self.data);
            cursor.seek(SeekFrom::Start(*pointer_pair.0 as u64)).unwrap();
            cursor.write_u32::<LittleEndian>(*pointer_pair.1 as u32).unwrap();
            state.raw_pointers.push(*pointer_pair.0 as u32);
        }
    }

    fn process_mapped_pointers(&self, state: &mut SerializationState) {
        let mut pointers: Vec<(&usize, &Vec<String>)> = self.mapped_pointers.iter().collect();
        pointers.sort_by(|a, b| a.0.cmp(b.0));
        for pointer_pair in pointers {
            for string in pointer_pair.1 {
                let text_offset = state.try_add_text(string);
                state.raw_mapped.push(*pointer_pair.0 as u32);
                state.raw_mapped.push(text_offset);
            }            
        }
    }

    fn process_text_pointers(&mut self, state: &mut SerializationState) {
        let mut pointers: Vec<(&usize, &String)> = self.text_pointers.iter().collect();
        pointers.sort_by(|a, b| a.0.cmp(b.0));
        let mut ptr_data_pairs: LinkedHashMap<usize, Vec<u32>> = LinkedHashMap::new();
        let label_start = self.label_start();
        for pointer_pair in pointers {
            let text_offset = state.try_add_text(pointer_pair.1);
            let text_address = label_start + text_offset;
            if !ptr_data_pairs.contains_key(&(text_address as usize)) {
                ptr_data_pairs.insert(text_address as usize, Vec::new());
            }
            let bucket= ptr_data_pairs.get_mut(&(text_address as usize)).unwrap();
            bucket.push(*pointer_pair.0 as u32);

            let mut cursor = Cursor::new(&mut self.data);
            cursor.seek(SeekFrom::Start(*pointer_pair.0 as u64)).unwrap();
            cursor.write_u32::<LittleEndian>(text_address as u32).unwrap();
        }

        for mut ptr_data_pair in ptr_data_pairs {
            ptr_data_pair.1.sort();
            for ptr in ptr_data_pair.1 {
                state.raw_pointers.push(ptr);
            }
        }
    }

    fn mapped_pointer_count(&self) -> u32 {
        let mut mapped_pointer_count = 0;
        for (_, value) in &self.mapped_pointers {
            mapped_pointer_count += value.len();
        }
        mapped_pointer_count as u32
    }

    fn label_start(&self) -> u32 {
        let mapped_start = self.data.len() + self.text_pointers.len() * 4 + self.internal_pointers.len() * 4;
        (mapped_start + (self.mapped_pointer_count() * 8) as usize) as u32
    }

    fn write_header(&self, state: &SerializationState, out: &mut Vec<u8>) {
        let file_size = self.label_start() + 0x20 + state.raw_text.len() as u32;
        out.write_u32::<LittleEndian>(file_size).unwrap();
        out.write_u32::<LittleEndian>(self.data.len() as u32).unwrap();
        out.write_u32::<LittleEndian>(state.raw_pointers.len() as u32).unwrap();
        out.write_u32::<LittleEndian>((state.raw_mapped.len() / 2) as u32).unwrap();
        out.write_u64::<LittleEndian>(0).unwrap();
        out.write_u64::<LittleEndian>(0).unwrap();
    }

    fn write_data(&mut self, out: &mut Vec<u8>) {
        out.write_all(&self.data).unwrap();
    }

    fn write_pointer_region_one(&self, state: &SerializationState, out: &mut Vec<u8>) {
        for ptr in &state.raw_pointers {
            out.write_u32::<LittleEndian>(*ptr).unwrap();
        }
    }

    fn write_pointer_region_two(&self, state: &SerializationState, out: &mut Vec<u8>) {
        for ptr in &state.raw_mapped {
            out.write_u32::<LittleEndian>(*ptr).unwrap();
        }
    }

    fn write_text_region(&self, state: &SerializationState, out: &mut Vec<u8>) {
        out.write_all(&state.raw_text).unwrap();
    }

    fn adjust_pointers(&mut self, addr: usize, amount: isize, anchor: bool) {
        // Adjust internal pointers.
        let mut adjusted_internal_pointers: HashMap<usize, usize> = HashMap::new();
        for (key, value) in &self.internal_pointers {
            if anchor && *value == addr {
                adjusted_internal_pointers.insert(*key, *value);
            }
            else {
                let adjusted_pointer = adjust_pointer(*key, addr, amount);
                let adjusted_data_pointer = adjust_pointer(*value, addr, amount);
                adjusted_internal_pointers.insert(adjusted_pointer, adjusted_data_pointer);
            }
        }

        let mut adjusted_mapped_pointers: HashMap<usize, Vec<String>> = HashMap::new();
        for (key, value) in &self.mapped_pointers {
            let adjusted = adjust_pointer(*key, addr, amount);
            adjusted_mapped_pointers.insert(adjusted, value.clone());
        }

        let mut adjusted_text_pointers: HashMap<usize, String> = HashMap::new();
        for (key, value) in &self.text_pointers {
            let adjusted = adjust_pointer(*key, addr, amount);
            adjusted_text_pointers.insert(adjusted, value.clone());
        }

        self.internal_pointers = adjusted_internal_pointers;
        self.text_pointers = adjusted_text_pointers;
        self.mapped_pointers = adjusted_mapped_pointers;
    }
}

#[pymethods]
impl BinArchive {
    pub fn serialize(&mut self) -> PyResult<Vec<u8>> {
        // Construct text and pointer regions from the archive.
        let mut state = SerializationState {
            raw_text: Vec::new(),
            written_text_offsets: HashMap::new(),
            raw_pointers: Vec::new(),
            raw_mapped: Vec::new(),
        };
        self.process_internal_pointers(&mut state);
        self.process_mapped_pointers(&mut state);
        self.process_text_pointers(&mut state);

        // Assemble the serialized bin.
        let mut result: Vec<u8> = Vec::new();
        self.write_header(&state, &mut result);
        self.write_data(&mut result);
        self.write_pointer_region_one(&state, &mut result);
        self.write_pointer_region_two(&state, &mut result);
        self.write_text_region(&state, &mut result);
        Ok(result)
    }

    pub fn put_u8(&mut self, addr: usize, value: u8) {
        self.data[addr] = value;
    }

    pub fn put_i8(&mut self, addr: usize, value: i8) {
        self.data[addr] = value as u8;
    }

    pub fn put_u16(&mut self, addr: usize, value: u16) -> PyResult<()> {
        let mut cursor = Cursor::new(&mut self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        cursor.write_u16::<LittleEndian>(value)?;
        Ok(())
    }

    pub fn put_i16(&mut self, addr: usize, value: i16) -> PyResult<()> {
        let mut cursor = Cursor::new(&mut self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        cursor.write_i16::<LittleEndian>(value)?;
        Ok(())
    }

    pub fn put_u32(&mut self, addr: usize, value: u32) -> PyResult<()> {
        let mut cursor = Cursor::new(&mut self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        cursor.write_u32::<LittleEndian>(value)?;
        Ok(())
    }

    pub fn put_i32(&mut self, addr: usize, value: i32) -> PyResult<()> {
        let mut cursor = Cursor::new(&mut self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        cursor.write_i32::<LittleEndian>(value)?;
        Ok(())
    }

    pub fn put_f32(&mut self, addr: usize, value: f32) -> PyResult<()> {
        let mut cursor = Cursor::new(&mut self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        cursor.write_f32::<LittleEndian>(value)?;
        Ok(())
    }

    pub fn read_u8(&self, addr: usize) -> PyResult<u8> {
        let mut cursor = Cursor::new(&self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        let value = cursor.read_u8()?;
        Ok(value)
    }

    pub fn read_i8(&self, addr: usize) -> PyResult<i8> {
        let mut cursor = Cursor::new(&self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        let value = cursor.read_u8()?;
        Ok(value as i8)
    }

    pub fn read_u16(&self, addr: usize) -> PyResult<u16> {
        let mut cursor = Cursor::new(&self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        let value = cursor.read_u16::<LittleEndian>()?;
        Ok(value)
    }

    pub fn read_i16(&self, addr: usize) -> PyResult<i16> {
        let mut cursor = Cursor::new(&self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        let value = cursor.read_i16::<LittleEndian>()?;
        Ok(value)
    }

    pub fn read_u32(&self, addr: usize) -> PyResult<u32> {
        let mut cursor = Cursor::new(&self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        let value = cursor.read_u32::<LittleEndian>()?;
        Ok(value)
    }

    pub fn read_i32(&self, addr: usize) -> PyResult<i32> {
        let mut cursor = Cursor::new(&self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        let value = cursor.read_i32::<LittleEndian>()?;
        Ok(value)
    }

    pub fn read_f32(&self, addr: usize) -> PyResult<f32> {
        let mut cursor = Cursor::new(&self.data);
        cursor.seek(SeekFrom::Start(addr as u64))?;
        let value = cursor.read_f32::<LittleEndian>()?;
        Ok(value)
    }

    pub fn read_string(&self, addr: usize) -> PyResult<Option<&String>> {
        Ok(self.text_pointers.get(&addr))
    }

    pub fn read_mapped(&self, addr: usize, index: usize) -> PyResult<Option<&String>> {
        match self.mapped_pointers.get(&addr) {
            Some(value) => {
                Ok(value.get(index))
            }
            None => Ok(None)
        }
    }

    pub fn read_internal(&self, addr: usize) -> PyResult<Option<usize>> {
        let opt = self.internal_pointers.get(&addr);
        Ok(match opt {
            Some(value) => Some(*value),
            None => None
        })
    }

    pub fn set_text_pointer(&mut self, addr: usize, text: Option<&str>) {
        match text {
            Some(value) => {
                self.text_pointers.insert(
                    addr,
                    value.to_string()
                );
            }
            None => self.clear_text_pointer(addr)
        }
    }

    pub fn set_mapped_pointer(&mut self, addr: usize, text: Option<&str>) {
        match text {
            Some(value) => {
                let bucket = self.mapped_pointers.get_mut(&addr);
                match bucket {
                    Some(bucket_value) => {
                        let string_value = value.to_string();
                        if !bucket_value.contains(&string_value) {
                            bucket_value.push(string_value);
                        }
                    },
                    None => {
                        let mut bucket: Vec<String> = Vec::new();
                        bucket.push(value.to_string());
                        self.mapped_pointers.insert(addr, bucket);
                    }
                }
            },
            _ => {}
        }
    }

    pub fn set_internal_pointer(&mut self, addr: usize, dest: usize) {
        self.internal_pointers.insert(
            addr,
            dest
        );
    }

    pub fn clear_internal_pointer(&mut self, addr: usize) {
        self.internal_pointers.remove(&addr);
    }

    pub fn clear_text_pointer(&mut self, addr: usize) {
        self.text_pointers.remove(&addr);
    }

    pub fn clear_mapped_pointers(&mut self, addr: usize) {
        self.mapped_pointers.remove(&addr);
    }

    pub fn clear_mapped_pointer(&mut self, addr: usize, value: Option<&str>) {
        match value {
            Some(unwrapped_value) => {
                let bucket_optional = self.mapped_pointers.get_mut(&addr);
                match bucket_optional {
                    Some(bucket) => {
                        let index_optional = bucket.iter().position(|x| *x == unwrapped_value);
                        match index_optional {
                            Some(index) => { 
                                bucket.remove(index);
                            },
                            None => {} // Pointer doesn't exist in the bucket.
                        }
                    }
                    None => {} // The bucket doesn't exist, so the pointer doesn't exist either.
                }
            }
            None => {} // None will never end up in a bucket, so it's already been cleared.
        }
    }

    pub fn size(&self) -> PyResult<usize> {
        Ok(self.data.len())
    }

    pub fn allocate_at_end(&mut self, amount: isize) {
        for _ in 0..amount {
            self.data.push(0)
        }
    }

    pub fn allocate(&mut self, addr: usize, amount: isize, anchor: bool) {
        self.adjust_pointers(addr, amount, anchor);
        
        let mut range_to_add: Vec<u8> = Vec::new();
        for _ in 0..amount {
            range_to_add.push(0);
        }
        self.data.splice(addr..addr, range_to_add);
    }

    pub fn deallocate(&mut self, addr: usize, amount: isize, anchor: bool) {
        let end = addr + (amount as usize);
        self.text_pointers.retain(|&k, _| !(k >= addr && k < end));
        self.mapped_pointers.retain(|&k, _| !(k >= addr && k  <end));
        self.internal_pointers.retain(|&k, &mut v| {
            !(k >= addr && k < end) && !(v >= addr && v < end && !(anchor && v == addr))
        });

        let empty: Vec<u8> = Vec::new();
        self.data.splice(addr..end, empty);
        self.adjust_pointers(addr, -amount, anchor);
    }

    pub fn addr_of_mapped_pointer(&self, mapped: Option<&str>) -> Option<usize> {
        match mapped {
            Some(unwrapped_mapped) => {
                for (key, value) in &self.mapped_pointers {
                    for string in value {
                        if string == unwrapped_mapped {
                            return Some(*key);
                        }
                    }
                }
                None
            },
            None => None
        }
    }
}
