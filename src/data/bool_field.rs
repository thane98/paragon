use super::{ReadState, Types, WriteState, Field};
use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Format {
    U8,
    U16,
    U32,
}

#[derive(Clone, Debug, Deserialize)]
pub struct BoolField {
    pub id: String,

    #[serde(default)]
    pub name: Option<String>,

    #[serde(default)]
    pub value: bool,

    #[serde(default)]
    format: Format,
}

impl Default for Format {
    fn default() -> Self {
        Format::U8
    }
}

impl BoolField {
    pub fn read(&mut self, state: &mut ReadState) -> anyhow::Result<()> {
        self.value = match self.format {
            Format::U8 => state.reader.read_u8()? != 0,
            Format::U16 => state.reader.read_u16()? != 0,
            Format::U32 => state.reader.read_u32()? != 0,
        };
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        let output = if self.value { 1 } else { 0 };
        Ok(match self.format {
            Format::U8 => state.writer.write_u8(output as u8)?,
            Format::U16 => state.writer.write_u16(output as u16)?,
            Format::U32 => state.writer.write_u32(output as u32)?,
        })
    }

    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("type", "bool")?;
        dict.set_item("id", self.id.clone())?;
        dict.set_item("name", self.name.clone())?;
        Ok(dict.to_object(py))
    }

    pub fn clone_with_allocations(&self, _types: &mut Types) -> anyhow::Result<Field> {
        Ok(Field::Bool(self.clone()))
    }
}
