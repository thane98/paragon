use std::sync::Arc;

use anyhow::anyhow;
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

use crate::data::fields::field::Field;
use crate::data::Types;
use crate::model::id::StoreNumber;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;

static AWAKENING_ENC_TABLE: &[u8] = &[
    89, 137, 210, 209, 222, 198, 71, 33, 186, 219, 197, 236, 53, 189, 159, 155, 45, 123, 178, 9,
    247, 83, 153, 143, 196, 144, 250, 52, 248, 25, 148, 2, 237, 86, 64, 108, 244, 136, 79, 43, 180,
    187, 235, 116, 183, 13, 194, 164, 238, 147, 207, 66, 241, 23, 191, 240, 165, 188, 15, 110, 27,
    115, 141, 166, 59, 80, 51, 224, 175, 157, 221, 255, 254, 170, 206, 18, 98, 226, 251, 193, 35,
    73, 214, 205, 4, 47, 65, 21, 26, 50, 3, 138, 20, 88, 10, 163, 208, 113, 125, 211, 160, 82, 190,
    215, 139, 72, 55, 19, 168, 68, 8, 60, 227, 99, 246, 223, 22, 124, 70, 243, 7, 204, 121, 195,
    107, 63, 129, 0, 32, 40, 174, 239, 109, 142, 14, 29, 75, 149, 161, 182, 212, 199, 62, 229, 216,
    90, 67, 38, 122, 228, 78, 156, 48, 76, 200, 151, 253, 84, 104, 192, 252, 54, 28, 117, 1, 150,
    233, 31, 69, 6, 112, 44, 41, 103, 46, 245, 158, 146, 96, 61, 232, 231, 102, 42, 145, 234, 87,
    169, 30, 95, 39, 81, 201, 101, 24, 171, 131, 213, 133, 97, 12, 119, 126, 249, 127, 94, 220,
    132, 92, 106, 57, 77, 135, 91, 218, 105, 230, 93, 17, 130, 16, 85, 217, 203, 140, 114, 134,
    111, 100, 128, 202, 162, 5, 172, 74, 177, 11, 56, 225, 173, 49, 179, 152, 120, 184, 34, 118,
    154, 36, 167, 37, 181, 242, 185, 176, 58,
];

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Transform {
    AwakeningGrowths(AwakeningGrowthsTransform),
}

#[derive(Clone, Debug, Deserialize)]
pub struct AwakeningGrowthsTransform {
    is_character: bool,
}

#[derive(Clone, Debug, Deserialize)]
pub struct BytesFieldInfo {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub transform: Option<Transform>,

    pub length: usize,
}

#[derive(Clone, Debug, Deserialize)]
pub struct BytesField {
    #[serde(flatten)]
    pub info: Arc<BytesFieldInfo>,

    #[serde(default)]
    pub value: Vec<u8>,
}

// Modified version of https://azalea.qyu.be/2020/157/
// Original growth encryption/decryption documentation can be found here:
// https://forums.serenesforest.net/index.php?/topic/70225-fire-emblem-awakening-growth-rate-cipher-documentation/
fn decode(a: i32, b: i32, c: i32, d: i32, j: i32, k: i32, n: i32) -> u8 {
    AWAKENING_ENC_TABLE[((n - ((a * ((j ^ b) - c * k)) ^ d)) & 0xFF) as usize]
}

fn encode(a: i32, b: i32, c: i32, d: i32, j: i32, k: i32, n: i32) -> u8 {
    let index = AWAKENING_ENC_TABLE
        .iter()
        .position(|e| *e == n as u8)
        .unwrap_or_default() as i32;
    ((index + ((a * ((j ^ b) - c * k)) ^ d)) & 0xFF) as u8
}

fn decode_character(j: i32, k: i32, n: i32) -> u8 {
    decode(99, 167, 33, 217, j, k, n)
}

fn decode_class(j: i32, k: i32, n: i32) -> u8 {
    decode(35, 70, 241, 120, j, k, n)
}

fn encode_character(j: i32, k: i32, n: i32) -> u8 {
    encode(99, 167, 33, 217, j, k, n)
}

fn encode_class(j: i32, k: i32, n: i32) -> u8 {
    encode(35, 70, 241, 120, j, k, n)
}

impl Transform {
    pub fn apply(&self, value: &[u8], id: i32) -> Vec<u8> {
        match self {
            Transform::AwakeningGrowths(t) => t.apply(value, id),
        }
    }

    pub fn reverse(&self, value: &[u8], id: i32) -> Vec<u8> {
        match self {
            Transform::AwakeningGrowths(t) => t.reverse(value, id),
        }
    }
}

impl AwakeningGrowthsTransform {
    pub fn apply(&self, value: &[u8], id: i32) -> Vec<u8> {
        let func = if self.is_character {
            decode_character
        } else {
            decode_class
        };
        let mut result: Vec<u8> = Vec::new();
        for (i, b) in value.iter().enumerate() {
            result.push(func(id, i as i32, *b as i32))
        }
        result
    }

    pub fn reverse(&self, value: &[u8], id: i32) -> Vec<u8> {
        let func = if self.is_character {
            encode_character
        } else {
            encode_class
        };
        let mut result: Vec<u8> = Vec::new();
        for (i, b) in value.iter().enumerate() {
            result.push(func(id, i as i32, *b as i32))
        }
        result
    }
}

impl BytesField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value = state.reader.read_bytes(self.info.length)?;
        if let Some(t) = &self.info.transform {
            let id = state.list_index[state.list_index.len() - 1];
            self.value = t.apply(&self.value, id as i32);
        }
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        let write_value = if let Some(t) = &self.info.transform {
            let id = state.list_index[state.list_index.len() - 1];
            t.reverse(&self.value, id as i32)
        } else {
            self.value.clone()
        };
        state.writer.write_bytes(&write_value)?;
        Ok(())
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "bytes")?;
        dict.set_item("id", self.info.id.clone())?;
        dict.set_item("name", self.info.name.clone())?;
        dict.set_item("length", self.info.length)?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(
        &self,
        _types: &mut Types,
        _store_number: StoreNumber,
    ) -> anyhow::Result<Field> {
        Ok(Field::Bytes(self.clone()))
    }

    pub fn set_byte(&mut self, index: usize, byte: u8) -> anyhow::Result<()> {
        if index > self.value.len() {
            Err(anyhow!("Index '{}' is out of bounds.", index))
        } else {
            self.value[index] = byte;
            Ok(())
        }
    }

    pub fn get(&self, index: usize) -> anyhow::Result<u8> {
        if index > self.value.len() {
            Err(anyhow!("Index '{}' is out of bounds.", index))
        } else {
            Ok(self.value[index])
        }
    }
}

#[cfg(test)]
mod test {
    use super::AwakeningGrowthsTransform;

    #[test]
    fn decode_awakening_character_growths() {
        let char1 = vec![0xc5, 0xf1, 0x9d, 0x7b, 0x3a, 0xba, 0x53, 0x2a];
        let char1_expected = vec![45, 40, 10, 40, 40, 70, 35, 20];
        let transform = AwakeningGrowthsTransform { is_character: true };
        assert_eq!(transform.apply(&char1, 3), char1_expected);
    }

    #[test]
    fn decode_awakening_class_growths() {
        let c1 = vec![0x98, 0x60, 0x70, 0x4a, 0x37, 0x47, 0x23, 0x9a];
        let c1_expected = vec![40, 20, 0, 20, 20, 0, 10, 5];
        let transform = AwakeningGrowthsTransform {
            is_character: false,
        };
        assert_eq!(transform.apply(&c1, 3), c1_expected);
    }

    #[test]
    fn encode_awakening_character_growths() {
        let char1 = vec![45, 40, 10, 40, 40, 70, 35, 20];
        let char1_expected = vec![0xc5, 0xf1, 0x9d, 0x7b, 0x3a, 0xba, 0x53, 0x2a];
        let transform = AwakeningGrowthsTransform { is_character: true };
        assert_eq!(transform.reverse(&char1, 3), char1_expected);
    }

    #[test]
    fn encode_awakening_class_growths() {
        let c1 = vec![40, 20, 0, 20, 20, 0, 10, 5];
        let c1_expected = vec![0x98, 0x60, 0x70, 0x4a, 0x37, 0x47, 0x23, 0x9a];
        let transform = AwakeningGrowthsTransform {
            is_character: false,
        };
        assert_eq!(transform.reverse(&c1, 3), c1_expected);
    }
}
