use nintendo_lz::*;
use std::io::{Result, Error, ErrorKind};
use std::cmp::min;

fn get_occurrence_length(bytes: &[u8], new_ptr: usize, new_length: usize, old_ptr: usize, old_length: usize) -> (i32, usize) {
    if new_length == 0 || old_length == 0 {
        return (0, 0)
    }

    let mut disp = 0;
    let mut max_length = 0;
    for i in 0..(old_length - 1) {
        let current_old_start = old_ptr + i;
        let mut current_length = 0;
        for j in 0..new_length {
            if bytes[current_old_start + j] != bytes[new_ptr + j] {
                break
            }
            current_length += 1;
        }
        if current_length > max_length {
            max_length = current_length;
            disp = old_length - i;
            if max_length == new_length {
                break;
            }
        }
    }
    (max_length as i32, disp)
}

pub fn compress_lz13(contents: &[u8]) -> Vec<u8> {
    // First, create the header.
    let mut result: Vec<u8> = Vec::new();
    result.reserve(contents.len()); // For performance, reserve space to avoid resizing.
    let length = contents.len();
    result.push(0x13);
    result.push(((length & 0xFF) + 1) as u8);
    result.push(((length >> 8) & 0xFF) as u8);
    result.push(((length >> 16) & 0xFF) as u8);
    result.push(0x11);
    result.push((length & 0xFF) as u8);
    result.push(((length >> 8) & 0xFF) as u8);
    result.push(((length >> 16) & 0xFF) as u8);

    // Begin compressing using the DSDecmp algorithm.
    let mut out_buffer: Vec<u8> = Vec::new();
    out_buffer.reserve_exact(8 * 4 + 1);
    out_buffer.push(0);
    let mut buffered_blocks = 0;
    let mut read_bytes = 0;
    while read_bytes < contents.len() {
        // Dump out buffer contents
        if buffered_blocks == 8 {
            result.append(&mut out_buffer);
            out_buffer.push(0);
            buffered_blocks = 0;
        }

        let old_length = min(read_bytes, 0x1000);
        let (length, disp) = get_occurrence_length(
            contents, 
            read_bytes, 
            min(contents.len() - read_bytes, 0x1000), 
            read_bytes - old_length, 
            old_length
        );

        if length < 3 {
            out_buffer.push(contents[read_bytes]);
            read_bytes += 1;
        }
        else {
            read_bytes += length as usize;
            out_buffer[0] |= (1 << (7 - buffered_blocks)) as u8;
            if length > 0x110 {
                out_buffer.push(0x10 | (((length - 0x111) >> 12) & 0x0F) as u8);
                out_buffer.push((((length - 0x111) >> 4) & 0xFF) as u8);
                out_buffer.push((((length - 0x111) << 4) & 0xF0) as u8);
            }
            else if length > 0x10 {
                out_buffer.push((((length - 0x111) >> 4) & 0x0F) as u8);
                out_buffer.push((((length - 0x111) << 4) & 0xF0) as u8);
            }
            else {
                out_buffer.push((((length - 1) << 4) & 0xF0) as u8);
            }
            let last_index = out_buffer.len() - 1;
            out_buffer[last_index] |= (((disp - 1) >> 8) & 0x0F) as u8;
            out_buffer.push(((disp - 1) & 0xFF) as u8);
        }
        buffered_blocks += 1;
    }
    if buffered_blocks > 0 {
        result.append(&mut out_buffer);
    }
    result
}

pub fn decompress_lz13(input: &[u8]) -> Result<Vec<u8>> {
    let truncated_input = if input[0] == 0x13 {
        &input[4..]
    }
    else {
        input
    };
    let decompression_result = decompress_arr(&truncated_input);
    match decompression_result {
        Ok(decompressed_data) => return Ok(decompressed_data),
        Err(_) => return Err(Error::new(ErrorKind::Other, "Invalid compressed file"))
    }
}
