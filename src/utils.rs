use byteorder::ReadBytesExt;
use encoding_rs::SHIFT_JIS;
use pyo3::PyResult;
use std::io::Cursor;

pub trait EncodedStringReader {
    fn read_shift_jis_string(&mut self) -> PyResult<String>;
}

impl EncodedStringReader for Cursor<&[u8]> {
    fn read_shift_jis_string(&mut self) -> PyResult<String> {
        let mut buffer: Vec<u8> = Vec::new();
        loop {
            match self.read_u8() {
                Ok(value) => {
                    if value == 0 {
                        break;
                    } else {
                        buffer.push(value);
                    }
                }
                Err(_) => {
                    return Err(pyo3::exceptions::ValueError::py_err(
                        "Fell out of buffer while reading shift-jis string.",
                    ));
                }
            }
        }
        let (result, _, has_errors) = SHIFT_JIS.decode(buffer.as_slice());
        if has_errors {
            Err(pyo3::exceptions::ValueError::py_err(
                "Error decoding shift-jis string.",
            ))
        } else {
            Ok(result.into())
        }
    }
}
