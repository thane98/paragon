use pyo3::types::PyDict;
use pyo3::{PyObject, PyResult, Python, ToPyObject};
use serde::Deserialize;

use crate::model::diff_value::DiffValue;

use crate::data::fields::field::Field;
use crate::data::Types;
use crate::model::read_state::ReadState;
use crate::model::write_state::WriteState;

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

    #[serde(skip, default)]
    pub value_at_read_time: Option<bool>,

    #[serde(default)]
    pub present_flag: Option<String>,

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
        if let Some(flag) = &self.present_flag {
            if self.value {
                if let Some(set) = state.conditions_stack.last_mut() {
                    set.insert(flag.clone());
                }
            }
        }
        self.value_at_read_time = Some(self.value);
        Ok(())
    }

    pub fn write(&self, state: &mut WriteState) -> anyhow::Result<()> {
        let output = if self.value { 1 } else { 0 };
        if let Some(flag) = &self.present_flag {
            if self.value {
                if let Some(set) = state.conditions_stack.last_mut() {
                    set.insert(flag.clone());
                }
            }
        }
        match self.format {
            Format::U8 => state.writer.write_u8(output as u8)?,
            Format::U16 => state.writer.write_u16(output as u16)?,
            Format::U32 => state.writer.write_u32(output as u32)?,
        };
        Ok(())
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

    pub fn diff(&self) -> Option<DiffValue> {
        if let Some(value) = self.value_at_read_time {
            if self.value == value {
                None
            } else {
                Some(DiffValue::Bool(self.value))
            }
        } else {
            None
        }
    }
}
