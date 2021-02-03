use super::{Field, ReadState, Types, WriteState};
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "snake_case", tag = "type")]
enum Format {
    I8,
    I16,
    I32,
    U8,
    U16,
    U32,
}

#[derive(Clone, Debug, Deserialize)]
pub struct IntField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub skip_write: bool,

    #[serde(default)]
    pub value: i64,

    format: Format,
}

impl IntField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value = match self.format {
            Format::I8 => state.reader.read_i8()? as i64,
            Format::I16 => state.reader.read_i16()? as i64,
            Format::I32 => state.reader.read_i32()? as i64,
            Format::U8 => state.reader.read_u8()? as i64,
            Format::U16 => state.reader.read_u16()? as i64,
            Format::U32 => state.reader.read_u32()? as i64,
        };
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        if self.skip_write {
            let skip_amount = match self.format {
                Format::I8 | Format::U8 => 1,
                Format::I16 | Format::U16 => 2,
                Format::I32 | Format::U32 => 4,
            };
            state.writer.skip(skip_amount);
        } else {
            match self.format {
                Format::I8 => state.writer.write_i8(self.value as i8)?,
                Format::I16 => state.writer.write_i16(self.value as i16)?,
                Format::I32 => state.writer.write_i32(self.value as i32)?,
                Format::U8 => state.writer.write_u8(self.value as u8)?,
                Format::U16 => state.writer.write_u16(self.value as u16)?,
                Format::U32 => state.writer.write_u32(self.value as u32)?,
            }
        }
        Ok(())
    }

    pub fn range(&self) -> (i64, i64) {
        match self.format {
            Format::I8 => (i8::MIN as i64, i8::MAX as i64),
            Format::I16 => (i16::MIN as i64, i16::MAX as i64),
            Format::I32 => (i32::MIN as i64, i32::MAX as i64),
            Format::U8 => (u8::MIN as i64, u8::MAX as i64),
            Format::U16 => (u16::MIN as i64, u16::MAX as i64),
            Format::U32 => (u32::MIN as i64, u32::MAX as i64),
        }
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "int")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        dict.set_item("range", self.range())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, _types: &mut Types) -> anyhow::Result<Field> {
        Ok(Field::Int(self.clone()))
    }
}
